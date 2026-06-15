import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

class PipelineValidator:
    def __init__(self, ssim_threshold=0.99):
        self.ssim_threshold = ssim_threshold

    def validate(self, original_img, clean_img, mask):
        if len(original_img.shape) == 3:
            orig_gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
            clean_gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
        else:
            orig_gray = original_img
            clean_gray = clean_img

        healthy_mask = (mask == 0).astype(np.uint8)
        
        score, diff = ssim(orig_gray, clean_gray, full=True)
        
        healthy_orig = orig_gray[healthy_mask == 1]
        healthy_clean = clean_gray[healthy_mask == 1]
        
        if len(healthy_orig) > 0:
            psnr_value = psnr(healthy_orig, healthy_clean)
            if not np.isfinite(psnr_value):
                psnr_value = 100.0
            diff_healthy = diff[healthy_mask == 1]
            ssim_healthy = np.mean(diff_healthy)
        else:
            psnr_value = 0
            ssim_healthy = 0

        healthy_changed_pixels = int(np.count_nonzero(healthy_orig != healthy_clean))
        ai_act_compliant = ssim_healthy >= self.ssim_threshold and healthy_changed_pixels == 0
        
        return {
            "ssim": float(ssim_healthy),
            "psnr": float(psnr_value),
            "healthy_changed_pixels": healthy_changed_pixels,
            "ai_act_compliant": bool(ai_act_compliant)
        }
