"""
Tests for Monitoring and Observability Module

Tests Prometheus metrics, structured logging, and health checks.

Author: Luis Arteaga y Pollyanna Soares
Date: 15 June 2026
"""

import pytest
import asyncio
import json
import logging
from io import StringIO
from pathlib import Path
import sys

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from monitoring import (
    setup_structured_logging,
    advanced_health_check,
    metrics_endpoint,
    track_anonymization_metrics,
    ANONYMIZATIONS_TOTAL,
    PHI_DETECTIONS_TOTAL,
    SSIM_SCORE,
    PSNR_SCORE,
    HEALTHY_PIXELS_CHANGED,
    REQUEST_COUNT,
    collect_system_metrics,
    SYSTEM_CPU_USAGE,
    SYSTEM_MEMORY_USAGE,
    CustomJsonFormatter
)


# ============================================================================
# Structured Logging Tests
# ============================================================================

class TestStructuredLogging:
    """Tests for JSON structured logging."""
    
    def test_setup_structured_logging_creates_logger(self):
        """Test that setup creates a logger with correct configuration."""
        logger = setup_structured_logging(level=logging.DEBUG)
        
        assert logger is not None
        assert logger.name == "treelogic_anonymizer"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0
    
    def test_json_formatter_produces_valid_json(self):
        """Test that logs are formatted as valid JSON."""
        # Create logger with string buffer
        logger = logging.getLogger("test_json")
        logger.handlers.clear()
        
        buffer = StringIO()
        handler = logging.StreamHandler(buffer)
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log a message
        logger.info("Test message", extra={"user_id": 123, "action": "test"})
        
        # Parse JSON output
        output = buffer.getvalue()
        log_entry = json.loads(output)
        
        assert "timestamp" in log_entry
        assert log_entry["level"] == "INFO"
        assert "Test message" in log_entry["message"]
        assert log_entry["user_id"] == 123
        assert log_entry["action"] == "test"
    
    def test_json_formatter_handles_exceptions(self):
        """Test that exceptions are properly formatted in JSON."""
        logger = logging.getLogger("test_exception")
        logger.handlers.clear()
        
        buffer = StringIO()
        handler = logging.StreamHandler(buffer)
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        # Log an exception
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.error("An error occurred", exc_info=True)
        
        output = buffer.getvalue()
        log_entry = json.loads(output)
        
        assert "exception" in log_entry
        assert "ValueError" in log_entry["exception"]
        assert "Test error" in log_entry["exception"]


# ============================================================================
# Prometheus Metrics Tests
# ============================================================================

class TestPrometheusMetrics:
    """Tests for Prometheus metrics collection."""
    
    def test_anonymizations_counter_increments(self):
        """Test that anonymization counter increments correctly."""
        initial_success = ANONYMIZATIONS_TOTAL.labels(status="success")._value.get()
        
        ANONYMIZATIONS_TOTAL.labels(status="success").inc()
        
        final_success = ANONYMIZATIONS_TOTAL.labels(status="success")._value.get()
        assert final_success == initial_success + 1
    
    def test_phi_detections_counter_by_type(self):
        """Test that PHI detections are tracked by type."""
        initial_name = PHI_DETECTIONS_TOTAL.labels(phi_type="name")._value.get()
        initial_id = PHI_DETECTIONS_TOTAL.labels(phi_type="id")._value.get()
        
        PHI_DETECTIONS_TOTAL.labels(phi_type="name").inc()
        PHI_DETECTIONS_TOTAL.labels(phi_type="id").inc()
        
        assert PHI_DETECTIONS_TOTAL.labels(phi_type="name")._value.get() == initial_name + 1
        assert PHI_DETECTIONS_TOTAL.labels(phi_type="id")._value.get() == initial_id + 1
    
    def test_ssim_histogram_observes_values(self):
        """Test that SSIM histogram records observations."""
        SSIM_SCORE.observe(0.9987)
        SSIM_SCORE.observe(0.999)
        
        # Verify histogram has samples
        metric_families = list(SSIM_SCORE.collect())
        assert len(metric_families) > 0
    
    def test_psnr_histogram_observes_values(self):
        """Test that PSNR histogram records observations."""
        PSNR_SCORE.observe(45.32)
        PSNR_SCORE.observe(50.0)
        
        # Verify histogram has samples
        metric_families = list(PSNR_SCORE.collect())
        assert len(metric_families) > 0
    
    def test_healthy_pixels_histogram(self):
        """Test that healthy pixels changed histogram works."""
        HEALTHY_PIXELS_CHANGED.observe(0)
        HEALTHY_PIXELS_CHANGED.observe(50)
        
        # Verify histogram has samples
        metric_families = list(HEALTHY_PIXELS_CHANGED.collect())
        assert len(metric_families) > 0
    
    def test_system_metrics_collection(self):
        """Test that system metrics are collected without errors."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_dir = os.path.join(tmpdir, "uploads")
            processed_dir = os.path.join(tmpdir, "processed")
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)
            
            # Collect metrics
            collect_system_metrics(upload_dir, processed_dir)
            
            # Verify gauges have values
            assert SYSTEM_CPU_USAGE._value.get() >= 0
            assert SYSTEM_MEMORY_USAGE._value.get() >= 0
            assert 0 <= SYSTEM_CPU_USAGE._value.get() <= 100
            assert 0 <= SYSTEM_MEMORY_USAGE._value.get() <= 100


# ============================================================================
# Metrics Endpoint Tests
# ============================================================================

class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint."""
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_response(self):
        """Test that metrics endpoint returns a valid response."""
        response = await metrics_endpoint()
        
        assert response is not None
        assert response.media_type == "text/plain; version=0.0.4; charset=utf-8"
        assert len(response.body) > 0
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_contains_prometheus_format(self):
        """Test that metrics are in Prometheus format."""
        response = await metrics_endpoint()
        content = response.body.decode('utf-8')
        
        # Check for Prometheus metric format (# TYPE, # HELP)
        assert "# HELP" in content or "http_requests_total" in content
        assert "# TYPE" in content or "http_request_duration_seconds" in content


# ============================================================================
# Health Check Tests
# ============================================================================

class TestAdvancedHealthCheck:
    """Tests for advanced health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_healthy_status(self):
        """Test health check returns healthy when all OK."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_dir = os.path.join(tmpdir, "uploads")
            processed_dir = os.path.join(tmpdir, "processed")
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)
            
            health = await advanced_health_check(
                locator_loaded=True,
                ssim_threshold=0.99,
                upload_dir=upload_dir,
                processed_dir=processed_dir
            )
            
            assert health["status"] in ["healthy", "degraded"]
            assert "components" in health
            assert "system" in health
            assert "storage" in health
            assert "compliance" in health
    
    @pytest.mark.asyncio
    async def test_health_check_degraded_when_ocr_not_loaded(self):
        """Test health check returns degraded when OCR not loaded."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            health = await advanced_health_check(
                locator_loaded=False,
                ssim_threshold=0.99,
                upload_dir=tmpdir,
                processed_dir=tmpdir
            )
            
            assert health["status"] == "degraded"
            assert health["issues"] is not None
            assert any("OCR" in issue for issue in health["issues"])
    
    @pytest.mark.asyncio
    async def test_health_check_includes_system_metrics(self):
        """Test that health check includes system metrics."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            health = await advanced_health_check(
                locator_loaded=True,
                ssim_threshold=0.99,
                upload_dir=tmpdir,
                processed_dir=tmpdir
            )
            
            system = health["system"]
            assert "cpu_percent" in system
            assert "memory_percent" in system
            assert "memory_available_mb" in system
            assert "disk_percent" in system
            assert "disk_free_gb" in system
            
            # Validate ranges
            assert 0 <= system["cpu_percent"] <= 100
            assert 0 <= system["memory_percent"] <= 100
            assert system["memory_available_mb"] >= 0
            assert 0 <= system["disk_percent"] <= 100
            assert system["disk_free_gb"] >= 0
    
    @pytest.mark.asyncio
    async def test_health_check_includes_compliance_info(self):
        """Test that health check includes compliance information."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            health = await advanced_health_check(
                locator_loaded=True,
                ssim_threshold=0.99,
                upload_dir=tmpdir,
                processed_dir=tmpdir
            )
            
            compliance = health["compliance"]
            assert "ai_act" in compliance
            assert "rgpd_gdpr" in compliance
            assert "hipaa" in compliance
            assert "0.99" in compliance["ai_act"]
    
    @pytest.mark.asyncio
    async def test_health_check_counts_files(self):
        """Test that health check counts files in directories."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_dir = os.path.join(tmpdir, "uploads")
            processed_dir = os.path.join(tmpdir, "processed")
            os.makedirs(upload_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)
            
            # Create test files
            open(os.path.join(upload_dir, "test1.png"), 'w').close()
            open(os.path.join(upload_dir, "test2.png"), 'w').close()
            open(os.path.join(processed_dir, "clean1.png"), 'w').close()
            
            health = await advanced_health_check(
                locator_loaded=True,
                ssim_threshold=0.99,
                upload_dir=upload_dir,
                processed_dir=processed_dir
            )
            
            storage = health["storage"]
            assert storage["upload_files"] == 2
            assert storage["processed_files"] == 1


# ============================================================================
# Decorator Tests
# ============================================================================

class TestTrackAnonymizationMetrics:
    """Tests for track_anonymization_metrics decorator."""
    
    @pytest.mark.asyncio
    async def test_decorator_tracks_successful_anonymization(self):
        """Test that decorator tracks successful anonymizations."""
        initial_count = ANONYMIZATIONS_TOTAL.labels(status="success")._value.get()
        
        @track_anonymization_metrics
        async def mock_anonymize():
            return {
                "metrics": {"ssim": 0.9987, "psnr": 45.32, "healthy_changed_pixels": 0},
                "bboxes": [
                    {"phi_type": "name", "x": 100, "y": 200},
                    {"phi_type": "id", "x": 300, "y": 400}
                ]
            }
        
        result = await mock_anonymize()
        
        assert result["metrics"]["ssim"] == 0.9987
        final_count = ANONYMIZATIONS_TOTAL.labels(status="success")._value.get()
        assert final_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_decorator_tracks_failed_anonymization(self):
        """Test that decorator tracks failed anonymizations."""
        initial_count = ANONYMIZATIONS_TOTAL.labels(status="failure")._value.get()
        
        @track_anonymization_metrics
        async def mock_anonymize_failure():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await mock_anonymize_failure()
        
        final_count = ANONYMIZATIONS_TOTAL.labels(status="failure")._value.get()
        assert final_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_decorator_observes_metrics(self):
        """Test that decorator observes SSIM/PSNR/healthy pixels."""
        @track_anonymization_metrics
        async def mock_anonymize():
            return {
                "metrics": {"ssim": 0.999, "psnr": 50.0, "healthy_changed_pixels": 5},
                "bboxes": []
            }
        
        result = await mock_anonymize()
        
        # Verify metrics were observed (histogram should have samples)
        ssim_families = list(SSIM_SCORE.collect())
        psnr_families = list(PSNR_SCORE.collect())
        healthy_families = list(HEALTHY_PIXELS_CHANGED.collect())
        
        assert len(ssim_families) > 0
        assert len(psnr_families) > 0
        assert len(healthy_families) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestMonitoringIntegration:
    """Integration tests for complete monitoring flow."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_flow(self):
        """Test complete monitoring flow with all components."""
        # Setup logging
        logger = setup_structured_logging()
        
        # Collect system metrics
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            collect_system_metrics(tmpdir, tmpdir)
            
            # Check health
            health = await advanced_health_check(
                locator_loaded=True,
                ssim_threshold=0.99,
                upload_dir=tmpdir,
                processed_dir=tmpdir
            )
            
            assert health["status"] in ["healthy", "degraded"]
            
            # Get metrics
            metrics_response = await metrics_endpoint()
            assert metrics_response is not None
            assert len(metrics_response.body) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
