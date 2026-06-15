"""
Automatic cleanup service for temporary files.

Removes old files from uploads/ and static_processed/ directories to prevent
disk space exhaustion in production.

Configuration:
- MAX_AGE_HOURS: Files older than this are deleted (default: 24h)
- CHECK_INTERVAL_SECONDS: How often to run cleanup (default: 3600s = 1h)
- Can run as background task or scheduled job

Usage:
    # As background task in FastAPI
    from cleanup_service import start_cleanup_background
    start_cleanup_background(app)
    
    # As standalone script (cron job)
    python cleanup_service.py
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Tuple
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MAX_AGE_HOURS = 24  # Delete files older than 24 hours
CHECK_INTERVAL_SECONDS = 3600  # Check every hour
UPLOAD_DIR = "uploads"
STATIC_DIR = "static_processed"


def cleanup_directory(directory: str, max_age_hours: int) -> Tuple[int, int, float]:
    """
    Remove files older than max_age_hours from directory.
    
    Args:
        directory: Path to directory to clean
        max_age_hours: Maximum age of files in hours
    
    Returns:
        Tuple of (files_removed, files_kept, mb_freed)
    """
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist")
        return 0, 0, 0.0
    
    now = datetime.now()
    max_age = timedelta(hours=max_age_hours)
    
    files_removed = 0
    files_kept = 0
    bytes_freed = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        try:
            # Get file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            file_age = now - file_mtime
            
            if file_age > max_age:
                # File is too old, delete it
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                files_removed += 1
                bytes_freed += file_size
                logger.info(f"Removed old file: {filename} (age: {file_age.total_seconds() / 3600:.1f}h)")
            else:
                files_kept += 1
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
    
    mb_freed = bytes_freed / (1024 * 1024)
    return files_removed, files_kept, mb_freed


def cleanup_all_directories(max_age_hours: int = MAX_AGE_HOURS) -> dict:
    """
    Run cleanup on all temporary directories.
    
    Args:
        max_age_hours: Maximum age of files in hours
    
    Returns:
        Dictionary with cleanup statistics
    """
    logger.info(f"Starting cleanup (max age: {max_age_hours}h)")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'max_age_hours': max_age_hours,
        'directories': {}
    }
    
    for directory in [UPLOAD_DIR, STATIC_DIR]:
        removed, kept, mb_freed = cleanup_directory(directory, max_age_hours)
        results['directories'][directory] = {
            'files_removed': removed,
            'files_kept': kept,
            'mb_freed': round(mb_freed, 2)
        }
        logger.info(
            f"{directory}: Removed {removed} files ({mb_freed:.2f} MB), "
            f"Kept {kept} files"
        )
    
    total_removed = sum(d['files_removed'] for d in results['directories'].values())
    total_mb_freed = sum(d['mb_freed'] for d in results['directories'].values())
    
    logger.info(
        f"Cleanup complete: {total_removed} files removed, "
        f"{total_mb_freed:.2f} MB freed"
    )
    
    return results


async def cleanup_loop(max_age_hours: int = MAX_AGE_HOURS, 
                       check_interval: int = CHECK_INTERVAL_SECONDS):
    """
    Infinite loop that runs cleanup periodically.
    
    Args:
        max_age_hours: Maximum age of files in hours
        check_interval: Seconds between cleanup runs
    """
    logger.info(
        f"Starting cleanup loop (check every {check_interval}s, "
        f"delete files older than {max_age_hours}h)"
    )
    
    while True:
        try:
            cleanup_all_directories(max_age_hours)
        except Exception as e:
            logger.error(f"Error in cleanup loop: {str(e)}")
        
        await asyncio.sleep(check_interval)


def start_cleanup_background(app, max_age_hours: int = MAX_AGE_HOURS,
                             check_interval: int = CHECK_INTERVAL_SECONDS):
    """
    Start cleanup as FastAPI background task.
    
    Args:
        app: FastAPI app instance
        max_age_hours: Maximum age of files in hours
        check_interval: Seconds between cleanup runs
    
    Usage:
        from fastapi import FastAPI
        from cleanup_service import start_cleanup_background
        
        app = FastAPI()
        
        @app.on_event("startup")
        async def startup_event():
            start_cleanup_background(app)
    """
    import asyncio
    
    @app.on_event("startup")
    async def start_cleanup():
        asyncio.create_task(cleanup_loop(max_age_hours, check_interval))
        logger.info("Cleanup background task started")


if __name__ == "__main__":
    # Run as standalone script (for cron job)
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup temporary files")
    parser.add_argument(
        '--max-age-hours',
        type=int,
        default=MAX_AGE_HOURS,
        help=f'Maximum age of files in hours (default: {MAX_AGE_HOURS})'
    )
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Run in loop mode (keeps running)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=CHECK_INTERVAL_SECONDS,
        help=f'Seconds between checks in loop mode (default: {CHECK_INTERVAL_SECONDS})'
    )
    
    args = parser.parse_args()
    
    if args.loop:
        # Run in loop mode
        asyncio.run(cleanup_loop(args.max_age_hours, args.check_interval))
    else:
        # Run once and exit
        cleanup_all_directories(args.max_age_hours)
