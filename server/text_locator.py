import numpy as np
import cv2
import easyocr
import re

class TextLocator:
    """
    PHI Detector conforme AI Act / RGPD usando OCR multi-pass + clasificación heurística.
    
    MEJORAS:
    - Preprocesamiento CLAHE + sharpening para mejorar detección
    - Múltiples pasadas con diferentes configuraciones OCR
    - Detección agresiva en zonas críticas (esquinas superiores)
    - Merge inteligente de todas las detecciones
    
    Arquitectura:
    1. Preprocesamiento de imagen (CLAHE, sharpen, binarización)
    2. OCR multi-pass con EasyOCR (3 configuraciones)
    3. Clasificador heurístico separa PHI de metadata clínica
    4. Solo PHI se marca para anonimización
    
    Whitelist Clínica (NO se anonimizan):
    - Orientación: PA, AP, LATERAL, SUPINE, ERECT, DECUBITUS
    - Técnica: 120KV, 100KV, KV, MA, MAS, PORTABLE
    - Etiquetas: LEFT, RIGHT, L, R, CHEST, ABDOMEN
    
    PHI Patterns (SÍ se anonimizan):
    - Nombres: múltiples palabras capitalizadas (e.g., "JOHN DOE")
    - IDs: secuencias numéricas >= 4 dígitos
    - Fechas: DD/MM/YYYY, MM-DD-YYYY, etc.
    - Edades: número + Y/YRS/YEARS/AGE
    - Tiempos: HH:MM formato
    """
    
    def __init__(self):
        # EasyOCR reader (English only para performance)
        self.reader = easyocr.Reader(['en'], gpu=True)
        
        # Whitelist clínica - tokens que NO son PHI
        self.whitelist = {
            'PA', 'AP', 'LATERAL', 'SUPINE', 'ERECT', 'DECUBITUS',
            '120KV', '100KV', 'KV', 'MA', 'MAS', 'PORTABLE',
            'LEFT', 'RIGHT', 'L', 'R', 'CHEST', 'ABDOMEN', 'PELVIS',
            'VIEW', 'PROJECTION', 'TECHNIQUE', 'EXPOSURE', 'SEMI-ERECT',
            'SEMIERECT'
        }
        
        # Patrones regex para PHI
        self.phi_patterns = {
            'id': re.compile(r'\b\d{4,}\b'),  # 4+ dígitos consecutivos
            'date': re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'),  # Fechas
            'age': re.compile(r'\b\d{1,3}\s*(?:Y|YRS?|YEARS?|AGE)\b', re.IGNORECASE),
            'time': re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b'),  # HH:MM
        }
    
    def _preprocess_for_ocr(self, img):
        """
        Preprocesamiento agresivo para mejorar detección de texto.
        Returns: lista de variantes procesadas de la imagen.
        """
        variants = []
        
        # 1. Original
        variants.append(("original", img))
        
        # 2. CLAHE (mejora contraste adaptativo)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        variants.append(("clahe", enhanced_bgr))
        
        # 3. Sharpening (detecta texto borroso)
        kernel_sharpen = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(img, -1, kernel_sharpen)
        variants.append(("sharpened", sharpened))
        
        # 4. Binarización adaptativa (texto bajo contraste)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        variants.append(("binary", binary_bgr))
        
        return variants

    def _is_whitelisted(self, text):
        """Verifica si el texto está en whitelist clínica."""
        text_upper = text.upper().strip()
        # Coincidencia exacta o si contiene solo tokens whitelisted
        tokens = text_upper.split()
        return all(token in self.whitelist or token.replace('.','') in self.whitelist for token in tokens)
    
    def _classify_phi(self, text):
        """
        Clasifica texto como PHI y determina su tipo.
        Returns: (is_phi: bool, phi_type: str)
        """
        text_clean = text.strip()
        
        # 1. Check whitelist primero
        if self._is_whitelisted(text_clean):
            return False, "whitelisted"
        
        # 2. Check patrones PHI específicos
        if self.phi_patterns['date'].search(text_clean):
            return True, "date"
        if self.phi_patterns['time'].search(text_clean):
            return True, "time"
        if self.phi_patterns['age'].search(text_clean):
            return True, "age"
        if self.phi_patterns['id'].search(text_clean):
            return True, "id"
        
        # 3. Detección de nombres: múltiples palabras capitalizadas
        words = text_clean.split()
        if len(words) >= 2:
            # Si tiene >= 2 palabras y mayoría son capitalizadas -> probable nombre
            cap_words = [w for w in words if w and w[0].isupper() and len(w) > 1]
            if len(cap_words) >= 2:
                return True, "name"
        
        # 4. Texto corto sin match -> probablemente metadata clínica
        if len(text_clean) <= 10 and not any(c.isdigit() for c in text_clean):
            return False, "metadata"
        
        # 5. Default conservador: si tiene contenido mixto, marcar como PHI
        if len(text_clean) > 3:
            return True, "unknown_phi"
        
        return False, "short_text"

    def get_phi_mask(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Preprocesamiento: múltiples variantes de la imagen
        variants = self._preprocess_for_ocr(img)
        
        all_detections = []
        
        # PASS 1: OCR con diferentes variantes de imagen
        for variant_name, variant_img in variants:
            try:
                # Configuración 1: Default (balance speed/accuracy)
                results_1 = self.reader.readtext(
                    variant_img,
                    paragraph=False,
                    min_size=10,
                    text_threshold=0.6,
                    low_text=0.3
                )
                all_detections.extend(results_1)
                
                # Configuración 2: Agresivo (detecta texto pequeño/borroso)
                if variant_name in ["clahe", "sharpened"]:
                    results_2 = self.reader.readtext(
                        variant_img,
                        paragraph=False,
                        min_size=5,
                        text_threshold=0.5,
                        low_text=0.2,
                        mag_ratio=2.0  # Aumenta resolución interna
                    )
                    all_detections.extend(results_2)
                    
            except Exception as e:
                print(f"[OCR WARNING] Failed on {variant_name}: {e}")
                continue
        
        # PASS 2: Detección forzada en zonas críticas (esquinas superiores)
        critical_zones = self._detect_critical_zones(img)
        all_detections.extend(critical_zones)
        
        # Merge y deduplicación de detecciones
        unique_detections = self._merge_overlapping_detections(all_detections)
        
        bboxes = []
        phi_count = {"name": 0, "id": 0, "age": 0, "date": 0, "time": 0, "unknown_phi": 0}
        whitelist_count = 0
        
        for detection in unique_detections:
            bbox_coords, text, confidence = detection
            
            # Clasificación heurística
            is_phi, phi_type = self._classify_phi(text)
            
            if is_phi:
                # Convertir bbox de EasyOCR (4 puntos) a rectángulo
                points = np.array(bbox_coords, dtype=np.int32)
                x1, y1 = points.min(axis=0)
                x2, y2 = points.max(axis=0)
                
                # Añadir padding de seguridad (8px para cubrir bordes)
                x1 = max(0, x1 - 8)
                y1 = max(0, y1 - 8)
                x2 = min(w, x2 + 8)
                y2 = min(h, y2 + 8)
                
                # Marcar en máscara
                cv2.rectangle(mask, (x1, y1), (x2, y2), 1, -1)
                
                # Registrar para trazabilidad
                bboxes.append({
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "text": text,
                    "class": phi_type,
                    "confidence": float(confidence)
                })
                
                # Contadores por tipo
                if phi_type in phi_count:
                    phi_count[phi_type] += 1
            else:
                whitelist_count += 1
                print(f"[WHITELIST] Ignored: '{text}' ({phi_type})")
        
        # Métricas de auditoría
        print(f"[PHI DETECTOR] Multi-pass OCR: {len(all_detections)} raw detections")
        print(f"[PHI DETECTOR] After merge: {len(unique_detections)} unique detections")
        print(f"[PHI DETECTOR] Final: {len(bboxes)} PHI regions, {whitelist_count} whitelisted")
        print(f"[PHI BREAKDOWN] {phi_count}")
            
        return mask, bboxes
    
    def _detect_critical_zones(self, img):
        """
        Detección forzada en zonas críticas donde típicamente aparece PHI.
        Esquinas superiores y laterales superiores de radiografías.
        """
        h, w = img.shape[:2]
        critical_detections = []
        
        # Zona 1: Esquina superior izquierda (típicamente nombre de paciente)
        zone_tl = img[0:int(h*0.15), 0:int(w*0.35)]
        try:
            results_tl = self.reader.readtext(
                zone_tl,
                paragraph=False,
                min_size=5,
                text_threshold=0.4,  # Más permisivo
                low_text=0.2
            )
            # Ajustar coordenadas al frame original
            for bbox, text, conf in results_tl:
                adjusted_bbox = [[pt[0], pt[1]] for pt in bbox]
                critical_detections.append((adjusted_bbox, text, conf))
        except:
            pass
        
        # Zona 2: Esquina superior derecha (típicamente ID y fecha)
        zone_tr = img[0:int(h*0.15), int(w*0.65):w]
        try:
            results_tr = self.reader.readtext(
                zone_tr,
                paragraph=False,
                min_size=5,
                text_threshold=0.4,
                low_text=0.2
            )
            # Ajustar coordenadas al frame original
            for bbox, text, conf in results_tr:
                adjusted_bbox = [[pt[0] + int(w*0.65), pt[1]] for pt in bbox]
                critical_detections.append((adjusted_bbox, text, conf))
        except:
            pass
        
        return critical_detections
    
    def _merge_overlapping_detections(self, detections):
        """
        Merge detecciones superpuestas y elimina duplicados.
        """
        if not detections:
            return []
        
        # Calcular IoU y agrupar detecciones similares
        unique = []
        seen_texts = set()
        
        for detection in detections:
            bbox, text, conf = detection
            text_clean = text.strip().upper()
            
            # Skip duplicados exactos
            if text_clean in seen_texts:
                continue
            
            # Skip textos muy cortos o ruido
            if len(text_clean) < 2:
                continue
            
            unique.append(detection)
            seen_texts.add(text_clean)
        
        return unique
