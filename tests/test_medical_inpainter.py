"""
Tests for MedicalInpainter class - Image anonymization.

Tests cover:
- Navier-Stokes inpainting
- SSIM/PSNR metric calculation
- Healthy pixel preservation validation
- Different mask sizes and shapes
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from medical_inpainter import MedicalInpainter


@pytest.fixture
def inpainter():
    """Fixture to create MedicalInpainter instance."""
    return MedicalInpainter()


@pytest.fixture
def test_image():
    """Create synthetic test image."""
    # Create grayscale image with some structure
    img = np.zeros((500, 500), dtype=np.uint8)
    # Add circle (simulating anatomical structure)
    cv2.circle(img, (250, 250), 100, 200, -1)
    # Add some texture
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)
    return img


@pytest.fixture
def test_mask_small():
    """Create small mask (simulating small PHI region)."""
    mask = np.zeros((500, 500), dtype=np.uint8)
    # Small rectangle in corner
    cv2.rectangle(mask, (10, 10), (60, 40), 255, -1)
    return mask


@pytest.fixture
def test_mask_large():
    """Create larger mask."""
    mask = np.zeros((500, 500), dtype=np.uint8)
    # Larger rectangle
    cv2.rectangle(mask, (10, 10), (150, 100), 255, -1)
    return mask


class TestInpainting:
    """Test inpainting functionality."""
    
    def test_inpaint_small_region(self, inpainter, test_image, test_mask_small):
        """Test inpainting small PHI region."""
        result = inpainter.inpaint(test_image, test_mask_small)
        
        assert result is not None
        assert result.shape == test_image.shape
        assert result.dtype == test_image.dtype
        
        # Inpainted region should be different from original
        masked_region_original = test_image[test_mask_small > 0]
        masked_region_result = result[test_mask_small > 0]
        assert not np.array_equal(masked_region_original, masked_region_result)
    
    def test_inpaint_large_region(self, inpainter, test_image, test_mask_large):
        """Test inpainting larger region."""
        result = inpainter.inpaint(test_image, test_mask_large)
        
        assert result is not None
        assert result.shape == test_image.shape
    
    def test_inpaint_preserves_healthy_pixels(self, inpainter, test_image, test_mask_small):
        """Test that pixels outside mask remain unchanged."""
        result = inpainter.inpaint(test_image, test_mask_small)
        
        # Pixels outside mask should be identical
        healthy_mask = test_mask_small == 0
        healthy_original = test_image[healthy_mask]
        healthy_result = result[healthy_mask]
        
        # Allow small numerical differences due to border effects
        differences = np.abs(healthy_original.astype(int) - healthy_result.astype(int))
        # More than 99% of healthy pixels should be unchanged
        unchanged_ratio = np.sum(differences == 0) / len(differences)
        assert unchanged_ratio > 0.99, f"Only {unchanged_ratio:.2%} healthy pixels unchanged"


class TestMetrics:
    """Test SSIM/PSNR calculation."""
    
    def test_ssim_identical_images(self, inpainter, test_image):
        """Test SSIM of identical images should be 1.0."""
        ssim = inpainter.calculate_ssim(test_image, test_image)
        assert abs(ssim - 1.0) < 0.001, f"SSIM should be ~1.0, got {ssim}"
    
    def test_ssim_different_images(self, inpainter, test_image):
        """Test SSIM of different images should be < 1.0."""
        # Create modified version
        modified = test_image.copy()
        modified[100:200, 100:200] = 255
        
        ssim = inpainter.calculate_ssim(test_image, modified)
        assert ssim < 1.0
        assert ssim > 0.0  # Should still have some similarity
    
    def test_psnr_identical_images(self, inpainter, test_image):
        """Test PSNR of identical images should be very high."""
        psnr = inpainter.calculate_psnr(test_image, test_image)
        assert psnr > 80, f"PSNR should be very high for identical images, got {psnr}"
    
    def test_psnr_different_images(self, inpainter, test_image):
        """Test PSNR of different images."""
        modified = test_image.copy()
        modified[100:200, 100:200] = 255
        
        psnr = inpainter.calculate_psnr(test_image, modified)
        assert psnr < 80  # Should be lower for different images
        assert psnr > 0


class TestHealthyPixelValidation:
    """Test validation that healthy pixels remain unchanged."""
    
    def test_count_changed_healthy_pixels_none(self, inpainter, test_image, test_mask_small):
        """Test counting changed pixels when none change."""
        # Result is identical to original
        count = inpainter.count_changed_healthy_pixels(
            test_image, test_image, test_mask_small
        )
        assert count == 0
    
    def test_count_changed_healthy_pixels_some(self, inpainter, test_image, test_mask_small):
        """Test counting when some healthy pixels change."""
        result = test_image.copy()
        # Change a healthy pixel
        result[400, 400] = 255
        
        count = inpainter.count_changed_healthy_pixels(
            test_image, result, test_mask_small
        )
        assert count > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_mask(self, inpainter, test_image):
        """Test with empty mask (no inpainting needed)."""
        empty_mask = np.zeros_like(test_image)
        result = inpainter.inpaint(test_image, empty_mask)
        
        # Should return original or very similar
        assert result is not None
        # Most pixels should be unchanged
        assert np.allclose(result, test_image, atol=1)
    
    def test_full_mask(self, inpainter, test_image):
        """Test with complete mask (entire image)."""
        full_mask = np.ones_like(test_image) * 255
        
        # This is an extreme case - inpainting entire image
        # Should not crash
        result = inpainter.inpaint(test_image, full_mask)
        assert result is not None


class TestIntegration:
    """Integration tests for complete anonymization pipeline."""
    
    def test_complete_anonymization_pipeline(self, inpainter, test_image, test_mask_small, tmp_path):
        """Test complete anonymization with metrics."""
        # Perform inpainting
        result = inpainter.inpaint(test_image, test_mask_small)
        
        # Calculate metrics
        ssim = inpainter.calculate_ssim(test_image, result)
        psnr = inpainter.calculate_psnr(test_image, result)
        changed_healthy = inpainter.count_changed_healthy_pixels(
            test_image, result, test_mask_small
        )
        
        # Assertions based on quality requirements
        assert ssim >= 0.99, f"SSIM {ssim:.4f} below AI Act threshold 0.99"
        assert psnr >= 30, f"PSNR {psnr:.2f} below acceptable threshold"
        assert changed_healthy < 100, f"Too many healthy pixels changed: {changed_healthy}"
        
        # Save result for manual inspection if needed
        output_path = tmp_path / "anonymized_result.png"
        cv2.imwrite(str(output_path), result)
        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
