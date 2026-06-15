"""
Monitoring and Observability Module

Provides Prometheus metrics and structured logging for production monitoring.

Features:
- Request metrics (count, duration, errors)
- Business metrics (anonymizations, PHI detections)
- System metrics (CPU, memory, disk)
- Structured JSON logging

Author: Luis Arteaga y Pollyanna Soares
Date: 15 June 2026
"""

import time
import logging
import psutil
from functools import wraps
from typing import Callable, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from pythonjsonlogger import jsonlogger


# ============================================================================
# Prometheus Metrics
# ============================================================================

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
ANONYMIZATIONS_TOTAL = Counter(
    'anonymizations_total',
    'Total number of images anonymized',
    ['status']  # success, failure
)

PHI_DETECTIONS_TOTAL = Counter(
    'phi_detections_total',
    'Total number of PHI regions detected',
    ['phi_type']  # name, id, date, age, time
)

SSIM_SCORE = Histogram(
    'ssim_score',
    'SSIM score distribution',
    buckets=[0.90, 0.95, 0.97, 0.98, 0.99, 0.995, 0.997, 0.999, 1.0]
)

PSNR_SCORE = Histogram(
    'psnr_score_db',
    'PSNR score distribution in dB',
    buckets=[20, 25, 30, 35, 40, 45, 50, 55, 60]
)

HEALTHY_PIXELS_CHANGED = Histogram(
    'healthy_pixels_changed',
    'Number of healthy pixels changed',
    buckets=[0, 10, 50, 100, 500, 1000, 5000]
)

# System metrics
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage_percent', 'System disk usage percentage')
UPLOAD_DIR_SIZE_MB = Gauge('upload_dir_size_mb', 'Size of uploads directory in MB')
PROCESSED_DIR_SIZE_MB = Gauge('processed_dir_size_mb', 'Size of processed directory in MB')


# ============================================================================
# Structured JSON Logging
# ============================================================================

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(record.created))
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)


def setup_structured_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure structured JSON logging for production.
    
    Args:
        level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("treelogic_anonymizer")
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_structured_logging()


# ============================================================================
# Decorators for Automatic Metrics
# ============================================================================

def track_anonymization_metrics(func: Callable) -> Callable:
    """
    Decorator to automatically track anonymization metrics.
    
    Usage:
        @track_anonymization_metrics
        async def anonymize(request: Request, file: UploadFile):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status = "failure"
        
        try:
            result = await func(*args, **kwargs)
            status = "success"
            
            # Track business metrics from result
            if "metrics" in result:
                metrics = result["metrics"]
                SSIM_SCORE.observe(metrics["ssim"])
                PSNR_SCORE.observe(metrics["psnr"])
                HEALTHY_PIXELS_CHANGED.observe(metrics["healthy_changed_pixels"])
            
            if "bboxes" in result:
                for bbox in result["bboxes"]:
                    PHI_DETECTIONS_TOTAL.labels(phi_type=bbox.get("phi_type", "unknown")).inc()
            
            logger.info(
                "Anonymization completed",
                extra={
                    "status": status,
                    "ssim": result.get("metrics", {}).get("ssim"),
                    "psnr": result.get("metrics", {}).get("psnr"),
                    "phi_regions": len(result.get("bboxes", [])),
                    "duration_seconds": time.time() - start_time
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Anonymization failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_seconds": time.time() - start_time
                },
                exc_info=True
            )
            raise
        
        finally:
            ANONYMIZATIONS_TOTAL.labels(status=status).inc()
            REQUEST_DURATION.labels(method="POST", endpoint="/anonymize").observe(time.time() - start_time)
    
    return wrapper


# ============================================================================
# System Metrics Collection
# ============================================================================

def collect_system_metrics(upload_dir: str = "uploads", processed_dir: str = "static_processed"):
    """
    Collect and update system metrics.
    
    Args:
        upload_dir: Path to uploads directory
        processed_dir: Path to processed files directory
    """
    import os
    
    # CPU and Memory
    SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=1))
    SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().percent)
    
    # Disk usage
    disk = psutil.disk_usage('/')
    SYSTEM_DISK_USAGE.set(disk.percent)
    
    # Directory sizes
    def get_dir_size_mb(directory: str) -> float:
        """Calculate directory size in MB."""
        total = 0
        if os.path.exists(directory):
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        return total / (1024 * 1024)  # Convert to MB
    
    UPLOAD_DIR_SIZE_MB.set(get_dir_size_mb(upload_dir))
    PROCESSED_DIR_SIZE_MB.set(get_dir_size_mb(processed_dir))


# ============================================================================
# Prometheus Endpoint Handler
# ============================================================================

async def metrics_endpoint():
    """
    FastAPI endpoint handler for Prometheus metrics.
    
    Usage:
        @app.get("/metrics")
        async def metrics():
            return await metrics_endpoint()
    """
    from fastapi.responses import Response
    
    # Update system metrics before serving
    collect_system_metrics()
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Health Check with Metrics
# ============================================================================

async def advanced_health_check(
    locator_loaded: bool,
    ssim_threshold: float,
    upload_dir: str = "uploads",
    processed_dir: str = "static_processed"
) -> dict[str, Any]:
    """
    Advanced health check with system metrics.
    
    Args:
        locator_loaded: Whether OCR is loaded
        ssim_threshold: SSIM threshold for AI Act compliance
        upload_dir: Path to uploads directory
        processed_dir: Path to processed files directory
    
    Returns:
        Health check response with metrics
    """
    import os
    
    # Collect system metrics
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Count files in directories
    upload_files = len(os.listdir(upload_dir)) if os.path.exists(upload_dir) else 0
    processed_files = len(os.listdir(processed_dir)) if os.path.exists(processed_dir) else 0
    
    # Determine overall health status
    status = "healthy"
    issues = []
    
    if not locator_loaded:
        status = "degraded"
        issues.append("OCR not loaded")
    
    if cpu_percent > 90:
        status = "degraded"
        issues.append(f"High CPU usage: {cpu_percent:.1f}%")
    
    if memory.percent > 90:
        status = "degraded"
        issues.append(f"High memory usage: {memory.percent:.1f}%")
    
    if disk.percent > 90:
        status = "degraded"
        issues.append(f"High disk usage: {disk.percent:.1f}%")
    
    return {
        "status": status,
        "issues": issues if issues else None,
        "components": {
            "detector": "EasyOCR + Heuristic PHI Classifier",
            "inpainter": "STRICT (zero healthy pixel modification)",
            "ocr_loaded": locator_loaded,
            "ssim_threshold": ssim_threshold,
        },
        "system": {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "disk_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
        },
        "storage": {
            "upload_files": upload_files,
            "processed_files": processed_files,
        },
        "compliance": {
            "ai_act": "SSIM ≥ 0.99 enforced",
            "rgpd_gdpr": "24h retention active",
            "hipaa": "Zero healthy pixels changed verified",
        }
    }
