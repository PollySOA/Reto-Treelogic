"""
Tests for TextLocator class - PHI detection and classification.

Tests cover:
- OCR multi-pass detection
- PHI classification (name, id, date, age, time)
- Whitelist preservation (clinical metadata)
- Edge cases (empty images, no text, mixed content)
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import sys

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from text_locator import TextLocator


@pytest.fixture
def text_locator():
    """Fixture to create TextLocator instance."""
    return TextLocator()


@pytest.fixture
def synthetic_image_with_phi():
    """Create synthetic medical image with PHI text."""
    # Create blank white image
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    
    # Add PHI text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "JOHN DOE", (50, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "ID: 123456", (50, 100), font, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "45 YRS", (50, 150), font, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "01/15/2024", (50, 200), font, 0.8, (0, 0, 0), 2)
    
    # Add clinical metadata (should NOT be marked as PHI)
    cv2.putText(img, "PA", (500, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "120KV", (500, 100), font, 0.8, (0, 0, 0), 2)
    
    return img


@pytest.fixture
def synthetic_image_clinical_only():
    """Create synthetic image with only clinical metadata (no PHI)."""
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "PA", (50, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(img, "120KV", (50, 100), font, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "CHEST", (50, 150), font, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "LEFT", (50, 200), font, 0.8, (0, 0, 0), 2)
    
    return img


class TestTextLocatorClassification:
    """Test PHI classification logic."""
    
    def test_classify_phi_name(self, text_locator):
        """Test name detection."""
        phi_type, confidence = text_locator._classify_phi("JOHN DOE")
        assert phi_type == "name"
        assert confidence > 0.5
    
    def test_classify_phi_id(self, text_locator):
        """Test ID detection."""
        phi_type, confidence = text_locator._classify_phi("123456")
        assert phi_type == "id"
        assert confidence == 1.0
    
    def test_classify_phi_date(self, text_locator):
        """Test date detection."""
        phi_type, confidence = text_locator._classify_phi("01/15/2024")
        assert phi_type == "date"
        assert confidence == 1.0
    
    def test_classify_phi_age(self, text_locator):
        """Test age detection."""
        phi_type, confidence = text_locator._classify_phi("45 YRS")
        assert phi_type == "age"
        assert confidence == 1.0
    
    def test_classify_phi_time(self, text_locator):
        """Test time detection."""
        phi_type, confidence = text_locator._classify_phi("14:30")
        assert phi_type == "time"
        assert confidence == 1.0
    
    def test_whitelist_clinical_pa(self, text_locator):
        """Test that PA is whitelisted (not PHI)."""
        phi_type, confidence = text_locator._classify_phi("PA")
        assert phi_type == "clinical"
        assert confidence == 1.0
    
    def test_whitelist_clinical_kv(self, text_locator):
        """Test that 120KV is whitelisted (not PHI)."""
        phi_type, confidence = text_locator._classify_phi("120KV")
        assert phi_type == "clinical"
        assert confidence == 1.0
    
    def test_whitelist_clinical_chest(self, text_locator):
        """Test that CHEST is whitelisted (not PHI)."""
        phi_type, confidence = text_locator._classify_phi("CHEST")
        assert phi_type == "clinical"
        assert confidence == 1.0


class TestTextLocatorOCR:
    """Test OCR detection capabilities."""
    
    def test_ocr_detects_phi_text(self, text_locator, synthetic_image_with_phi, tmp_path):
        """Test that OCR detects PHI text in synthetic image."""
        # Save temporary image
        img_path = tmp_path / "test_phi.png"
        cv2.imwrite(str(img_path), synthetic_image_with_phi)
        
        # Run OCR
        mask, bboxes, detections = text_locator.get_phi_mask(str(img_path))
        
        # Should detect at least some PHI
        assert len(bboxes) > 0, "Should detect at least one PHI region"
        assert mask.max() == 255, "Mask should have PHI regions marked"
    
    def test_ocr_preserves_clinical_metadata(self, text_locator, synthetic_image_clinical_only, tmp_path):
        """Test that clinical metadata is NOT marked as PHI."""
        # Save temporary image
        img_path = tmp_path / "test_clinical.png"
        cv2.imwrite(str(img_path), synthetic_image_clinical_only)
        
        # Run OCR
        mask, bboxes, detections = text_locator.get_phi_mask(str(img_path))
        
        # Should have minimal or no PHI detections
        phi_detections = [d for d in detections if d['phi_type'] != 'clinical']
        assert len(phi_detections) == 0, "Clinical-only image should have no PHI detections"


class TestTextLocatorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_image(self, text_locator, tmp_path):
        """Test handling of completely blank image."""
        # Create blank image
        blank_img = np.ones((800, 600, 3), dtype=np.uint8) * 255
        img_path = tmp_path / "blank.png"
        cv2.imwrite(str(img_path), blank_img)
        
        # Should not crash
        mask, bboxes, detections = text_locator.get_phi_mask(str(img_path))
        
        assert len(bboxes) == 0
        assert len(detections) == 0
    
    def test_invalid_image_path(self, text_locator):
        """Test handling of non-existent file."""
        with pytest.raises(Exception):
            text_locator.get_phi_mask("/nonexistent/path/image.png")


class TestTextLocatorIntegration:
    """Integration tests for complete pipeline."""
    
    def test_full_pipeline_with_phi(self, text_locator, synthetic_image_with_phi, tmp_path):
        """Test complete detection pipeline with PHI present."""
        img_path = tmp_path / "test_full.png"
        cv2.imwrite(str(img_path), synthetic_image_with_phi)
        
        mask, bboxes, detections = text_locator.get_phi_mask(str(img_path))
        
        # Assertions
        assert mask is not None
        assert mask.shape[:2] == synthetic_image_with_phi.shape[:2]
        assert len(bboxes) > 0
        assert len(detections) > 0
        
        # Verify PHI types detected
        phi_types = {d['phi_type'] for d in detections if d['phi_type'] != 'clinical'}
        assert len(phi_types) > 0, "Should detect at least one PHI type"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
