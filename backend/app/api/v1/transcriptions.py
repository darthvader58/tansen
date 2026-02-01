"""
Transcription endpoints.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import List
import logging
import json
import os
import tempfile
import uuid
from datetime import datetime

from app.core.security import get_current_user
from app.core.rate_limiter import check_rate_limit, check_concurrent_jobs, increment_rate_limit
from app.core.firebase import get_firestore_client, get_storage_client
from app.services.audio_processor import AudioProcessor
from app.services.notation_service import NotationService, NotationFormat, SargamStyle
from app.services.transposition_service import TranspositionService
from app.tasks.transcription import transcribe_audio_task
from app.models.transcription import (
    TranscriptionJobResponse,
    TranscriptionStatusResponse,
    TranscriptionResponse,
    TranscriptionYouTubeRequest,
    Instrument,
    NotationData,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=TranscriptionJobResponse)
async def upload_audio_for_transcription(
    file: UploadFile = File(...),
    instruments: str = Form(...),  # JSON string of instruments
    current_user: dict = Depends(get_current_user),
):
    """
    Upload audio file for transcription.
    
    Rate limits:
    - 10 transcriptions per 24 hours
    - Maximum 2 concurrent jobs
    """
    user_id = current_user['user_id']
    logger.info(f"Upload transcription request from user: {user_id}")
    
    try:
        # Parse instruments
        try:
            instruments_list = json.loads(instruments)
            if not isinstance(instruments_list, list) or not instruments_list:
                raise ValueError("Instruments must be a non-empty list")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid instruments format: {str(e)}"
            )
        
        # Check rate limits
        can_transcribe, limit_message = await check_rate_limit(user_id)
        if not can_transcribe:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=limit_message
            )
        
        # Check concurrent jobs
        can_start, concurrent_message = await check_concurrent_jobs(user_id)
        if not can_start:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=concurrent_message
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            file_size = len(content)
        
        try:
            # Validate audio file
            is_valid, error_message = AudioProcessor.validate_audio_file(tmp_file_path, file_size)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
            
            # Generate IDs
            job_id = str(uuid.uuid4())
            song_id = str(uuid.uuid4())
            
            # Upload to Firebase Storage
            storage_path = f"audio/{user_id}/{song_id}/{file.filename}"
            bucket = get_storage_client()
            blob = bucket.blob(storage_path)
            blob.upload_from_filename(tmp_file_path)
            logger.info(f"Uploaded audio to Firebase Storage: {storage_path}")
            
            # Create song document in Firestore
            db = get_firestore_client()
            song_data = {
                'songId': song_id,
                'title': file.filename,
                'createdBy': user_id,
                'createdAt': datetime.utcnow(),
                'audioFiles': {
                    'original': storage_path
                },
                'transcription': {
                    'status': 'pending',
                    'instruments': instruments_list
                },
                'metadata': {
                    'source': 'user_upload'
                }
            }
            db.collection('songs').document(song_id).set(song_data)
            
            # Create transcription job document
            job_data = {
                'jobId': job_id,
                'songId': song_id,
                'userId': user_id,
                'status': 'queued',
                'progress': 0,
                'instruments': instruments_list,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            db.collection('transcription_jobs').document(job_id).set(job_data)
            
            # Increment rate limit counter
            await increment_rate_limit(user_id)
            
            # Queue Celery task
            transcribe_audio_task.delay(
                job_id=job_id,
                song_id=song_id,
                user_id=user_id,
                audio_path=storage_path,
                instruments=instruments_list
            )
            
            logger.info(f"Queued transcription job {job_id} for song {song_id}")
            
            return TranscriptionJobResponse(
                job_id=job_id,
                song_id=song_id,
                status="queued",
                estimated_time=120,
                queue_position=1,
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload transcription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process audio upload"
        )


@router.post("/youtube", response_model=TranscriptionJobResponse)
async def transcribe_from_youtube(
    request: TranscriptionYouTubeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Transcribe audio from YouTube URL.
    
    Rate limits:
    - 10 transcriptions per 24 hours
    - Maximum 2 concurrent jobs
    """
    user_id = current_user['user_id']
    logger.info(f"YouTube transcription request from user: {user_id}, URL: {request.youtube_url}")
    
    try:
        # Check rate limits
        can_transcribe, limit_message = await check_rate_limit(user_id)
        if not can_transcribe:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=limit_message
            )
        
        # Check concurrent jobs
        can_start, concurrent_message = await check_concurrent_jobs(user_id)
        if not can_start:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=concurrent_message
            )
        
        # Validate YouTube URL
        if not ('youtube.com' in request.youtube_url or 'youtu.be' in request.youtube_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube URL"
            )
        
        # Download audio from YouTube
        import yt_dlp
        
        # Generate IDs
        job_id = str(uuid.uuid4())
        song_id = str(uuid.uuid4())
        
        # Create temp directory for download
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_template = os.path.join(tmp_dir, '%(title)s.%(ext)s')
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(request.youtube_url, download=True)
                    title = info.get('title', 'Unknown')
                    artist = info.get('uploader', 'Unknown')
                    duration = info.get('duration', 0)
                    thumbnail = info.get('thumbnail', '')
                    
                    # Find downloaded file
                    downloaded_file = None
                    for file in os.listdir(tmp_dir):
                        if file.endswith('.mp3'):
                            downloaded_file = os.path.join(tmp_dir, file)
                            break
                    
                    if not downloaded_file:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to download audio from YouTube"
                        )
                    
                    # Upload to Firebase Storage
                    storage_path = f"audio/{user_id}/{song_id}/{title}.mp3"
                    bucket = get_storage_client()
                    blob = bucket.blob(storage_path)
                    blob.upload_from_filename(downloaded_file)
                    logger.info(f"Uploaded YouTube audio to Firebase Storage: {storage_path}")
                    
            except Exception as e:
                logger.error(f"Error downloading from YouTube: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to download audio from YouTube: {str(e)}"
                )
        
        # Create song document in Firestore
        db = get_firestore_client()
        song_data = {
            'songId': song_id,
            'title': title,
            'artist': artist,
            'duration': duration,
            'createdBy': user_id,
            'createdAt': datetime.utcnow(),
            'audioFiles': {
                'original': storage_path
            },
            'transcription': {
                'status': 'pending',
                'instruments': request.instruments
            },
            'metadata': {
                'source': 'youtube',
                'youtubeUrl': request.youtube_url,
                'albumArt': thumbnail
            }
        }
        db.collection('songs').document(song_id).set(song_data)
        
        # Create transcription job document
        job_data = {
            'jobId': job_id,
            'songId': song_id,
            'userId': user_id,
            'status': 'queued',
            'progress': 0,
            'instruments': request.instruments,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        db.collection('transcription_jobs').document(job_id).set(job_data)
        
        # Increment rate limit counter
        await increment_rate_limit(user_id)
        
        # Queue Celery task
        transcribe_audio_task.delay(
            job_id=job_id,
            song_id=song_id,
            user_id=user_id,
            audio_path=storage_path,
            instruments=request.instruments
        )
        
        logger.info(f"Queued YouTube transcription job {job_id} for song {song_id}")
        
        return TranscriptionJobResponse(
            job_id=job_id,
            song_id=song_id,
            status="queued",
            estimated_time=180,
            queue_position=1,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in YouTube transcription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process YouTube transcription request"
        )


@router.get("/{job_id}/status", response_model=TranscriptionStatusResponse)
async def get_transcription_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get transcription job status.
    """
    user_id = current_user['user_id']
    logger.info(f"Status check for job: {job_id} by user: {user_id}")
    
    try:
        # Get job from Firestore
        db = get_firestore_client()
        job_doc = db.collection('transcription_jobs').document(job_id).get()
        
        if not job_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcription job not found"
            )
        
        job_data = job_doc.to_dict()
        
        # Verify user owns this job
        if job_data.get('userId') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return TranscriptionStatusResponse(
            job_id=job_id,
            status=job_data.get('status', 'queued'),
            progress=job_data.get('progress', 0),
            song_id=job_data.get('songId'),
            error=job_data.get('error'),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status"
        )


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: str,
    format: str = "western",
    scale: str = None,
    sargam_style: str = "hindustani",
    instrument: Instrument = Instrument.PIANO,
    current_user: dict = Depends(get_current_user),
):
    """
    Get transcription data with optional format conversion and transposition.
    
    Args:
        transcription_id: ID of the transcription
        format: Notation format (sargam, western, alphabetical)
        scale: Target scale for transposition (e.g., 'C', 'D', 'F#')
        sargam_style: Sargam style (hindustani or carnatic) - only used if format=sargam
        instrument: Instrument filter
    """
    user_id = current_user['user_id']
    logger.info(f"Get transcription: {transcription_id}, format: {format}, scale: {scale}")
    
    try:
        # Get transcription from Firestore
        db = get_firestore_client()
        trans_doc = db.collection('transcriptions').document(transcription_id).get()
        
        if not trans_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcription not found"
            )
        
        trans_data = trans_doc.to_dict()
        
        # Verify user has access (owner or public song)
        if trans_data.get('userId') != user_id:
            # Check if song is public
            song_id = trans_data.get('songId')
            song_doc = db.collection('songs').document(song_id).get()
            if not song_doc.exists or not song_doc.to_dict().get('isPublic', False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # Get notation data
        notation_data = trans_data.get('notationData', {})
        notes = notation_data.get('notes', [])
        chords = notation_data.get('chords', [])
        
        if not notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No notation data available"
            )
        
        # Get original key from song
        song_id = trans_data.get('songId')
        song_doc = db.collection('songs').document(song_id).get()
        original_key = 'C'  # Default
        if song_doc.exists:
            original_key = song_doc.to_dict().get('originalKey', 'C')
        
        # Apply transposition if requested
        if scale and scale != original_key:
            transposition_service = TranspositionService()
            notes = transposition_service.transpose_notes(
                notes=notes,
                from_key=original_key,
                to_key=scale,
                mode='major'
            )
            logger.info(f"Transposed from {original_key} to {scale}")
        
        # Convert to requested format
        notation_service = NotationService()
        
        try:
            notation_format = NotationFormat(format.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notation format: {format}. Must be one of: sargam, western, alphabetical"
            )
        
        try:
            sargam_style_enum = SargamStyle(sargam_style.lower())
        except ValueError:
            sargam_style_enum = SargamStyle.HINDUSTANI
        
        converted_notation = notation_service.convert_notes(
            notes=notes,
            format=notation_format,
            sargam_style=sargam_style_enum
        )
        
        # Build response
        return TranscriptionResponse(
            transcription_id=transcription_id,
            song_id=trans_data.get('songId'),
            instrument=Instrument(trans_data.get('instrument', 'piano')),
            format=format,
            scale=scale or original_key,
            notation_data=NotationData(
                notes=converted_notation.get('notes', []),
                chords=chords
            ),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transcription"
        )
