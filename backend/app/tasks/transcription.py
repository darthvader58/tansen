"""
Celery tasks for audio transcription.
"""
import os
import tempfile
from typing import Dict, List
import logging
from datetime import datetime

from app.celery_app import celery_app
from app.services.audio_processor import AudioProcessor
from app.services.transcription_service import TranscriptionService
from app.core.firebase import get_firestore_client, get_storage_client

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='transcribe_audio')
def transcribe_audio_task(
    self,
    job_id: str,
    song_id: str,
    user_id: str,
    audio_path: str,
    instruments: List[str]
) -> Dict:
    """
    Celery task to transcribe audio file.
    
    Args:
        self: Task instance (bound)
        job_id: Unique job identifier
        song_id: Song document ID
        user_id: User ID
        audio_path: Path to audio file in Firebase Storage
        instruments: List of instruments to transcribe
        
    Returns:
        Dictionary with transcription results
    """
    logger.info(f"Starting transcription job {job_id} for song {song_id}")
    
    try:
        # Update job status to processing
        update_job_status(job_id, 'processing', 0)
        
        # Download audio file from Firebase Storage
        local_audio_path = download_audio_from_storage(audio_path)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 10})
        update_job_status(job_id, 'processing', 10)
        
        # Load and preprocess audio
        audio_data, sample_rate = AudioProcessor.load_and_normalize(local_audio_path)
        
        # Extract metadata
        metadata = AudioProcessor.extract_metadata(local_audio_path)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'progress': 20})
        update_job_status(job_id, 'processing', 20)
        
        # Initialize transcription service
        transcription_service = TranscriptionService()
        
        # Transcribe for each instrument
        transcriptions = {}
        progress_per_instrument = 60 / len(instruments)
        
        for idx, instrument in enumerate(instruments):
            logger.info(f"Transcribing for instrument: {instrument}")
            
            # Perform transcription
            notes = transcription_service.transcribe_with_basic_pitch(
                audio_data,
                sample_rate
            )
            
            # Store transcription
            transcription_id = store_transcription(
                song_id=song_id,
                user_id=user_id,
                instrument=instrument,
                notes=notes,
                metadata=metadata
            )
            
            transcriptions[instrument] = transcription_id
            
            # Update progress
            progress = 20 + int((idx + 1) * progress_per_instrument)
            self.update_state(state='PROGRESS', meta={'progress': progress})
            update_job_status(job_id, 'processing', progress)
        
        # Update song document with transcription info
        update_song_transcription_status(song_id, metadata, transcriptions)
        
        # Update progress to 90%
        self.update_state(state='PROGRESS', meta={'progress': 90})
        update_job_status(job_id, 'processing', 90)
        
        # Clean up local file
        if os.path.exists(local_audio_path):
            os.remove(local_audio_path)
        
        # Mark job as completed
        update_job_status(job_id, 'completed', 100, song_id=song_id)
        
        logger.info(f"Transcription job {job_id} completed successfully")
        
        return {
            'job_id': job_id,
            'song_id': song_id,
            'status': 'completed',
            'transcriptions': transcriptions,
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Transcription job {job_id} failed: {e}", exc_info=True)
        
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
    song_id: str = None,
    error: str = None
):
    """Update job status in Firestore."""
    try:
        db = get_firestore_client()
        job_ref = db.collection('transcription_jobs').document(job_id)
        
        update_data = {
            'status': status,
            'progress': progress,
            'updatedAt': datetime.utcnow()
        }
        
        if song_id:
            update_data['songId'] = song_id
        
        if error:
            update_data['error'] = error
        
        job_ref.update(update_data)
        logger.info(f"Updated job {job_id} status to {status} ({progress}%)")
        
    except Exception as e:
        logger.error(f"Error updating job status: {e}")


def store_transcription(
    song_id: str,
    user_id: str,
    instrument: str,
    notes: List[Dict],
    metadata: Dict
) -> str:
    """Store transcription in Firestore."""
    try:
        db = get_firestore_client()
        
        transcription_data = {
            'songId': song_id,
            'userId': user_id,
            'instrument': instrument,
            'notationData': {
                'notes': notes,
                'chords': []  # TODO: Implement chord detection
            },
            'metadata': metadata,
            'createdAt': datetime.utcnow(),
            'processingTime': metadata.get('processing_time', 0)
        }
        
        # Add transcription document
        transcription_ref = db.collection('transcriptions').add(transcription_data)
        transcription_id = transcription_ref[1].id
        
        logger.info(f"Stored transcription {transcription_id} for song {song_id}")
        return transcription_id
        
    except Exception as e:
        logger.error(f"Error storing transcription: {e}")
        raise


def update_song_transcription_status(
    song_id: str,
    metadata: Dict,
    transcriptions: Dict[str, str]
):
    """Update song document with transcription status."""
    try:
        db = get_firestore_client()
        song_ref = db.collection('songs').document(song_id)
        
        song_ref.update({
            'transcription.status': 'completed',
            'transcription.processedAt': datetime.utcnow(),
            'transcription.instruments': list(transcriptions.keys()),
            'tempo': metadata.get('tempo', 120),
            'originalKey': metadata.get('key', 'C'),
            'duration': metadata.get('duration', 0)
        })
        
        logger.info(f"Updated song {song_id} transcription status")
        
    except Exception as e:
        logger.error(f"Error updating song transcription status: {e}")
