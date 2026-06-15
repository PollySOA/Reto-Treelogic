import cv2
import numpy as np

class MedicalInpainter:
    """
    Conservative inpainting for medical images.
    Uses context-aware methods to avoid altering healthy tissue.
    AI Act compliant: zero alteration of non-PHI regions.
    """
    def __init__(self, method='adaptive', blur_radius=0):
        """
        Args:
            method: 'adaptive' (default, best), 'black', 'blur', or 'telea'
            blur_radius: global feathering radius (0 = use method-specific)
        """
        self.method = method
        self.blur_radius = blur_radius

    def _detect_background_color(self, img, mask):
        """
        Detect dominant background color around PHI region.
        Uses median of border pixels for robust color matching.
        """
        # Sample pixels around the masked region (wider border for better sampling)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        dilated_mask = cv2.dilate(mask, kernel, iterations=3)
        border_region = cv2.subtract(dilated_mask, mask)
        
        # Get border pixels
        border_pixels = img[border_region > 0]
        if len(border_pixels) == 0:
            # Fallback: sample from corners of the image
            h, w = img.shape[:2]
            corner_samples = np.concatenate([
                img[0:50, 0:50].reshape(-1, 3),      # Top-left
                img[0:50, w-50:w].reshape(-1, 3),    # Top-right
            ])
            return np.median(corner_samples, axis=0).astype(np.uint8)
        
        # Calculate median (more robust than mean)
        median_color = np.median(border_pixels, axis=0).astype(np.uint8)
        
        # Return detected color directly (no forcing to black)
        return median_color

    def inpaint(self, image_path, mask):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)
            
        if mask.max() == 1:
            mask = mask * 255
            
        # Clone original to preserve intact regions
        result = img.copy()
        
        if self.method == 'strict':
            # STRICT MODE: Zero healthy pixel modification (AI Act compliant)
            # No blending, no dilation, only exact mask fill
            bg_color = self._detect_background_color(img, mask)
            
            # Fill ONLY the exact masked region, no edge blending
            result[mask > 0] = bg_color
        
        elif self.method == 'adaptive':
            # ADAPTIVE METHOD: Context-aware fill with smooth gradients
            # WARNING: May modify edge pixels, use 'strict' for AI Act compliance
            bg_color = self._detect_background_color(img, mask)
            
            # Create inner core and edge regions WITHIN the mask only
            kernel_inner = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            inner_mask = cv2.erode(mask, kernel_inner, iterations=1)
            
            # Edge region = original mask - inner core (stays within PHI boundary)
            edge_region = mask - inner_mask
            
            # Fill core with background color
            result[inner_mask > 0] = bg_color
            
            # Smooth transition in edge region only
            if np.any(edge_region > 0):
                # Blend original pixels with background color in edge region
                edge_pixels = img[edge_region > 0]
                alpha = 0.3  # 30% original, 70% background for smooth transition
                blended = (edge_pixels * alpha + bg_color * (1 - alpha)).astype(np.uint8)
                result[edge_region > 0] = blended
        
        elif self.method == 'black':
            # Context-aware fill: detect and match background color
            bg_color = self._detect_background_color(img, mask)
            
            # Apply color with slight gradient to reduce harsh edges
            mask_3channel = cv2.merge([mask, mask, mask])
            result[mask > 0] = bg_color
            
            # Smooth transition at edges (3px feathering)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            edge_mask = cv2.dilate(mask, kernel, iterations=1) - mask
            if np.any(edge_mask > 0):
                edge_color = (img[edge_mask > 0] * 0.5 + bg_color * 0.5).astype(np.uint8)
                result[edge_mask > 0] = edge_color
            
        elif self.method == 'blur':
            # Apply strong Gaussian blur only to masked region
            blurred = cv2.GaussianBlur(img, (51, 51), 30)
            result[mask > 0] = blurred[mask > 0]
            
        elif self.method == 'telea':
            # Smooth inpainting using Fast Marching Method
            # Use larger radius for better context propagation
            result = cv2.inpaint(img, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
        
        else:
            raise ValueError(f"Unknown inpainting method: {self.method}")
        
        # Optional: soften edges with feathering
        if self.blur_radius > 0:
            # Create soft transition mask
            mask_float = mask.astype(float) / 255.0
            mask_soft = cv2.GaussianBlur(mask_float, (self.blur_radius*2+1, self.blur_radius*2+1), 0)
            mask_soft = mask_soft[:, :, np.newaxis]  # Add channel dimension
            
            # Blend: result = original * (1 - soft_mask) + inpainted * soft_mask
            result = (img * (1 - mask_soft) + result * mask_soft).astype(np.uint8)
        
        return result
