"""
Tests for PipelineValidator - End-to-end validation.

Tests cover:
- Complete pipeline execution
- Metric validation (SSIM >= 0.99)
- Healthy pixel preservation
- Integration of all components
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline_validator import PipelineValidator


@pytest.fixture
def validator():
    """Fixture to create PipelineValidator instance."""
    return PipelineValidator()


@pytest.fixture
def synthetic_medical_image_with_phi(tmp_path):
    """Create realistic synthetic medical image with PHI."""
    # Create grayscale medical-like image
    img = np.zeros((1024, 768), dtype=np.uint8)
    
    # Simulate anatomical structure (circle for chest X-ray)
    cv2.circle(img, (384, 512), 200, 150, -1)
    cv2.circle(img, (384, 512), 180, 180, -1)
    
    # Add texture/noise
    noise = np.random.normal(0, 15, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Add PHI text in corner
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "JOHN DOE", (50, 50), font, 1, 255, 2)
    cv2.putText(img, "ID: 123456", (50, 100), font, 0.8, 255, 2)
    cv2.putText(img, "45 YRS", (50, 150), font, 0.8, 255, 2)
    
    # Add clinical metadata (should be preserved)
    cv2.putText(img, "PA", (650, 50), font, 1, 255, 2)
    cv2.putText(img, "120KV", (650, 100), font, 0.8, 255, 2)
    
    # Save to file
    img_path = tmp_path / "test_medical.png"
    cv2.imwrite(str(img_path), img)
    
    return str(img_path)


class TestPipelineExecution:
    """Test complete pipeline execution."""
    
    def test_pipeline_executes_successfully(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test that pipeline completes without errors."""
        output_path = tmp_path / "anonymized.png"
        
        result = validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        assert result is not None
        assert 'ssim' in result
        assert 'psnr' in result
        assert 'healthy_changed_pixels' in result
        assert output_path.exists()


class TestMetricThresholds:
    """Test that metrics meet required thresholds."""
    
    def test_ssim_meets_ai_act_threshold(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test SSIM >= 0.99 (AI Act requirement)."""
        output_path = tmp_path / "anonymized.png"
        
        result = validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        assert result['ssim'] >= 0.99, (
            f"SSIM {result['ssim']:.4f} below AI Act threshold 0.99"
        )
    
    def test_psnr_acceptable(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test PSNR is in acceptable range."""
        output_path = tmp_path / "anonymized.png"
        
        result = validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        assert result['psnr'] >= 30, (
            f"PSNR {result['psnr']:.2f} below acceptable threshold"
        )
    
    def test_healthy_pixels_minimally_changed(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test that healthy pixels are preserved."""
        output_path = tmp_path / "anonymized.png"
        
        result = validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        # Should have very few or zero healthy pixel changes
        assert result['healthy_changed_pixels'] < 1000, (
            f"Too many healthy pixels changed: {result['healthy_changed_pixels']}"
        )


class TestOutputQuality:
    """Test quality of anonymized output."""
    
    def test_output_image_exists(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test that output file is created."""
        output_path = tmp_path / "anonymized.png"
        
        validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_output_image_loadable(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test that output image can be loaded."""
        output_path = tmp_path / "anonymized.png"
        
        validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        # Should be able to load the image
        img = cv2.imread(str(output_path), cv2.IMREAD_GRAYSCALE)
        assert img is not None
        assert img.shape[0] > 0 and img.shape[1] > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_input_path(self, validator, tmp_path):
        """Test handling of non-existent input file."""
        output_path = tmp_path / "output.png"
        
        with pytest.raises(Exception):
            validator.validate_anonymization(
                "/nonexistent/file.png",
                str(output_path)
            )
    
    def test_output_directory_creation(self, validator, synthetic_medical_image_with_phi, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_path = tmp_path / "subdir" / "nested" / "output.png"
        
        # Directory doesn't exist yet
        assert not output_path.parent.exists()
        
        validator.validate_anonymization(
            str(synthetic_medical_image_with_phi),
            str(output_path)
        )
        
        # Directory should be created
        assert output_path.parent.exists()
        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
