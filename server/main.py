from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import shutil
import os
import uuid
import cv2
import numpy as np
from text_locator import TextLocator
from medical_inpainter import MedicalInpainter
from pipeline_validator import PipelineValidator
from cleanup_service import start_cleanup_background
from monitoring import (
    logger,
    track_anonymization_metrics,
    metrics_endpoint,
    advanced_health_check,
    REQUEST_COUNT
)

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
STATIC_DIR = "static_processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Security configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.dicom', '.dcm'}
ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 
    'image/tiff', 'application/dicom'
}

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

locator = TextLocator()
# Use 'strict' method for AI Act compliance (healthy_changed_pixels = 0)
inpainter = MedicalInpainter(method='strict', blur_radius=0)
validator = PipelineValidator()

@app.get("/health")
async def health():
    """Advanced health check with system metrics and compliance info."""
    return await advanced_health_check(
        locator_loaded=locator.reader is not None,
        ssim_threshold=validator.ssim_threshold,
        upload_dir=UPLOAD_DIR,
        processed_dir=STATIC_DIR
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for monitoring."""
    logger.info("Metrics endpoint accessed")
    return await metrics_endpoint()

@app.post("/api/v1/anonymize")
@limiter.limit("10/minute")  # Max 10 anonymizations per minute per IP
@track_anonymization_metrics
async def anonymize(request: Request, file: UploadFile = File(...)):
    try:
        # Track request
        REQUEST_COUNT.labels(method="POST", endpoint="/anonymize", status="started").inc()
        # Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"MIME type {file.content_type} not allowed"
            )
        
        # Read file content and validate size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file_size / 1024 / 1024:.2f} MB exceeds maximum {MAX_FILE_SIZE / 1024 / 1024} MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Save file
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        
        with open(input_path, "wb") as buffer:
            buffer.write(file_content)
            
        mask, bboxes = locator.get_phi_mask(input_path)
        clean_img = inpainter.inpaint(input_path, mask)
        original_img = cv2.imread(input_path)
        metrics = validator.validate(original_img, clean_img, mask)
        
        output_filename = f"clean_{file_id}.png"
        output_path = os.path.join(STATIC_DIR, output_filename)
        cv2.imwrite(output_path, clean_img)
        
        return {
            "status": "Success",
            "metrics": {
                "ssim": metrics["ssim"],
                "psnr": metrics["psnr"],
                "healthy_changed_pixels": metrics["healthy_changed_pixels"]
            },
            "ai_act_compliant": metrics["ai_act_compliant"],
            "clean_image_url": f"/api/python/static/{output_filename}",
            "original_image_url": f"/api/python/uploads/{file_id}{ext}",
            "bboxes": bboxes
        }
        
    except Exception as e:
        print(f"Error in pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup."""
    import asyncio
    from cleanup_service import cleanup_loop
    
    # Start cleanup background task (every hour, delete files older than 24h)
    asyncio.create_task(cleanup_loop(max_age_hours=24, check_interval=3600))
    logger.info("Cleanup background task started (24h retention, check every 1h)")
    logger.info("Treelogic Medical Image Anonymizer - Production server started")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
