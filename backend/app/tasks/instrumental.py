"""
Celery tasks for instrumental generation.
"""
import os
import tempfile
from typing import Dict
import logging
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.services.source_separation_service import SourceSeparationService
from app.core.firebase import get_firestore_client, get_storage_client

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='generate_instrumental')
def generate_instrumental_task(
    self,
    job_id: str,
    song_id: str,
    user_id: str,
    audio_path: str,
    remove_vocals: bool = True,
    remove_drums: bool = False,
    remove_bass: bool = False,
    format: str = 'mp3'
) -> Dict:
    """
    Celery task to generate instrumental version of a song.
    
    Args:
        self: Task instance (bound)
        job_id: Unique job identifier
        song_id: Song document ID
        user_id: User ID
        audio_path: Path to audio file in Firebase Storage
        remove_vocals: Remove vocals
        remove_drums: Remove drums
        remove_bass: Remove bass
        format: Output format (mp3 or wav)
        
    Returns:
        Dictionary with generation results
    """
    logger.info(f"Starting instrumental generation job {job_id} for song {song_id}")
    
    try:
        # Update job status to processing
        update_job_status(job_id, 'processing', 0)
        
        # Download audio file from Firebase Storage
        local_audio_path = download_audio_from_storage(audio_path)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10})
        update_job_status(job_id, 'processing', 10)
        
        # Initialize source separation service
        separation_service = SourceSeparationService()
        
        # Generate instrumental
        with tempfile.TemporaryDirectory() as temp_dir:
            output_filename = f"instrumental_{song_id}.{format}"
            output_path = os.path.join(temp_dir, output_filename)
            
            logger.info(f"Generating instrumental: {output_path}")
            
            # Update progress
            self.update_state(state='PROGRESS', meta={'progress': 20})
            update_job_status(job_id, 'processing', 20)
            
            # Generate instrumental (this takes most of the time)
            separation_service.generate_instrumental(
                audio_path=local_audio_path,
                output_path=output_path,
                remove_vocals=remove_vocals,
                remove_drums=remove_drums,
                remove_bass=remove_bass,
                format=format,
                bitrate='320k' if format == 'mp3' else None
            )
            
            # Update progress
            self.update_state(state='PROGRESS', meta={'progress': 80})
            update_job_status(job_id, 'processing', 80)
            
            # Validate audio quality
            is_valid, message = separation_service.validate_audio_quality(
                output_path,
                format=format,
                min_bitrate=320000 if format == 'mp3' else 0
            )
            
            if not is_valid:
                logger.warning(f"Audio quality validation failed: {message}")
            
            # Upload to Firebase Storage
            storage_path = f"instrumentals/{user_id}/{song_id}/{output_filename}"
            bucket = get_storage_client()
            blob = bucket.blob(storage_path)
            blob.upload_from_filename(output_path)
            
            # Make blob publicly accessible with signed URL (expires in 1 hour)
            download_url = blob.generate_signed_url(
                expiration=3600,  # 1 hour
                method='GET'
            )
            
            logger.info(f"Uploaded instrumental to Firebase Storage: {storage_path}")
            
            # Get file size
            file_size = os.path.getsize(output_path)
        
        # Update progress to 90%
        self.update_state(state='PROGRESS', meta={'progress': 90})
        update_job_status(job_id, 'processing', 90)
        
        # Clean up local file
        if os.path.exists(local_audio_path):
            os.remove(local_audio_path)
        
        # Mark job as completed
        update_job_status(
            job_id,
            'completed',
            100,
            download_url=download_url,
            file_size=file_size,
            storage_path=storage_path
        )
        
        logger.info(f"Instrumental generation job {job_id} completed successfully")
        
        return {
            'job_id': job_id,
            'song_id': song_id,
            'status': 'completed',
            'download_url': download_url,
            'file_size': file_size,
            'format': format
        }
        
    except Exception as e:
        logger.error(f"Instrumental generation job {job_id} failed: {e}", exc_info=True)
        
        # Mark job as failed
        update_job_status(job_id, 'failed', 0, error=str(e))
        
        # Clean up
        if 'local_audio_path' in locals() and os.path.exists(local_audio_path):
            os.remove(local_audio_path)
        
        raise


def download_audio_from_storage(storage_path: str) -> str:
    """Download audio file from Firebase Storage to local temp file."""
    try:
        bucket = get_storage_client()
        blob = bucket.blob(storage_path)
        
        # Create temp file
        suffix = os.path.splitext(storage_path)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            blob.download_to_filename(tmp_file.name)
            logger.info(f"Downloaded audio from {storage_path} to {tmp_file.name}")
            return tmp_file.name
            
    except Exception as e:
        logger.error(f"Error downloading audio from storage: {e}")
        raise


def update_job_status(
    job_id: str,
    status: str,
    progress: int,
    download_url: str = None,
    file_size: int = None,
    storage_path: str = None,
    error: str = None
):
    """Update instrumental generation job status in Firestore."""
    try:
        db = get_firestore_client()
        job_ref = db.collection('instrumental_jobs').document(job_id)
        
        update_data = {
            'status': status,
            'progress': progress,
            'updatedAt': datetime.now(timezone.utc)
        }
        
        if download_url:
            update_data['downloadUrl'] = download_url
        
        if file_size:
            update_data['fileSize'] = file_size
        
        if storage_path:
            update_data['storagePath'] = storage_path
        
        if error:
            update_data['error'] = error
        
        job_ref.update(update_data)
        logger.info(f"Updated instrumental job {job_id} status to {status} ({progress}%)")
        
    except Exception as e:
        logger.error(f"Error updating job status: {e}")

