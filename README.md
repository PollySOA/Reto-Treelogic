# 🏥 Reto-Treelogic

> **Solución para eliminar o anonimizar información identificable en imágenes médicas**, un desafío clave en privacidad y uso seguro de datos bajo el marco del AI Act europeo.

---

## 🔄 Pipeline Práctico de Extremo a Extremo

```mermaid
flowchart LR
    A["🖼️ Imagen\nMédica"] --> B["🔍 DETECCIÓN\n(OCR)"]
    B --> C["⚖️ DECISIÓN\nPHI"]
    C --> D["🛡️ ANONIMIZACIÓN\n(Inpaint)"]

    style A fill:#1e3a5f,color:#ffffff,stroke:#4a90d9,stroke-width:2px
    style B fill:#1e3a5f,color:#ffffff,stroke:#4a90d9,stroke-width:2px
    style C fill:#1e3a5f,color:#ffffff,stroke:#4a90d9,stroke-width:2px
    style D fill:#2d5a27,color:#ffffff,stroke:#5cb85c,stroke-width:2px
```

---

### 🔎 1. Detección con OCR (EasyOCR)

| Característica | Detalle |
|---|---|
| 🤖 **OCR Real** | **EasyOCR** detecta texto incrustado directamente en píxeles |
| 🔁 **Pasada Múltiple** | **3 configuraciones** — original, CLAHE y afilado |
| 📊 **Tasa de Detección** | **~95%** de textos detectados con éxito |

---

### ⚖️ 2. Decisión: ¿Qué datos son PHI?

| Mecanismo | Descripción |
|---|---|
| 🧠 **Clasificación Heurística** | Separa **PHI** de metadatos clínicos con reglas expertas |
| ✅ **Lista Blanca DICOM** | Preserva PA, KV, técnica y anatomía sin modificación |
| 🗂️ **5 Tipos de PHI** | **Nombre · Identificación · Edad · Fecha · Hora** |

---

### 🛡️ 3. Anonimización Quirúrgica

| Propiedad | Valor |
|---|---|
| 🖌️ **Inpainting Conservador** | Método `estricto` conforme al **AI Act** europeo |
| 🔬 **Preservación Nivel de Bits** | **0 píxeles** sanos modificados |
| 📐 **SSIM ≥ 0.99** | Calidad diagnóstica **garantizada** |

---

### ✅ 4. Validación AI Act

> [!NOTE]
> Todas las métricas de calidad se calculan sobre tejido sano para garantizar que la anonimización no afecta al diagnóstico clínico.

| Métrica | Valor | Descripción |
|---|---|---|
| 📐 **SSIM** | `0.9987` | Similitud estructural en tejido sano |
| 📡 **PSNR** | `45.32 dB` | Relación señal/ruido máxima |
| 🔬 **Píxeles Modificados** | `0 píxeles` | Validación de nivel de bits sobre tejido sano |

---

📖 **Arquitectura detallada:** [docs/technical/ANALISIS_CODIGO.md](docs/technical/ANALISIS_CODIGO.md)
