"""
Downloads endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from datetime import datetime, timezone, timedelta

from app.core.security import get_current_user
from app.core.firebase import get_firestore_client, get_storage_client
from app.models.download import (
    DownloadRequest,
    DownloadResponse,
    DownloadsListResponse,
    DownloadUrls,
    DownloadInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_DOWNLOADS = 50  # Maximum downloads per user


@router.post("/{song_id}", response_model=DownloadResponse)
async def prepare_download(
    song_id: str,
    request: DownloadRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Prepare song for offline download.
    
    Generates signed URLs for audio and notation files.
    URLs expire in 1 hour.
    Maximum 50 songs per user.
    """
    user_id = current_user['user_id']
    logger.info(f"Prepare download for song: {song_id}, user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Check download limit
        downloads_ref = db.collection('offline_downloads').where('userId', '==', user_id)
        current_downloads = list(downloads_ref.stream())
        
        if len(current_downloads) >= MAX_DOWNLOADS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Download limit reached. Maximum {MAX_DOWNLOADS} songs allowed."
            )
        
        # Check if already downloaded
        download_id = f"{user_id}_{song_id}"
        existing_download = db.collection('offline_downloads').document(download_id).get()
        
        if existing_download.exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Song already downloaded"
            )
        
        # Get song document
        song_doc = db.collection('songs').document(song_id).get()
        
        if not song_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        song_data = song_doc.to_dict()
        
        # Check if user has access
        if not song_data.get('isPublic', False) and song_data.get('createdBy') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Generate signed URLs
        bucket = get_storage_client()
        download_urls = DownloadUrls()
        total_size = 0
        
        # Audio file URL
        if request.include_audio:
            audio_path = song_data.get('audioFiles', {}).get('original')
            if audio_path:
                try:
                    blob = bucket.blob(audio_path)
                    if blob.exists():
                        download_urls.audio = blob.generate_signed_url(
                            expiration=3600,  # 1 hour
                            method='GET'
                        )
                        total_size += blob.size
                except Exception as e:
                    logger.warning(f"Error generating audio URL: {e}")
        
        # Notation files URLs
        download_urls.notations = {}
        
        # Get transcriptions for requested instruments
        transcriptions_ref = db.collection('transcriptions').where('songId', '==', song_id)
        
        for trans_doc in transcriptions_ref.stream():
            trans_data = trans_doc.to_dict()
            instrument = trans_data.get('instrument')
            
            if instrument not in request.instruments:
                continue
            
            # For each requested notation format, prepare the data
            for format in request.notation_formats:
                notation_key = f"{instrument}_{format}"
                
                # Notation data is stored in Firestore, not as files
                # We'll return the transcription ID so the client can fetch it
                download_urls.notations[notation_key] = {
                    'transcription_id': trans_data.get('transcriptionId', trans_doc.id),
                    'format': format,
                    'instrument': instrument
                }
        
        # Create download document
        download_data = {
            'downloadId': download_id,
            'userId': user_id,
            'songId': song_id,
            'downloadedAt': datetime.now(timezone.utc),
            'fileSize': total_size,
            'includesAudio': request.include_audio,
            'includesNotations': request.notation_formats,
            'instruments': request.instruments
        }
        
        db.collection('offline_downloads').document(download_id).set(download_data)
        
        # Update song download count
        song_ref = db.collection('songs').document(song_id)
        current_count = song_data.get('downloadCount', 0)
        song_ref.update({'downloadCount': current_count + 1})
        
        logger.info(f"Prepared download {download_id}, size: {total_size} bytes")
        
        return DownloadResponse(
            download_id=download_id,
            download_urls=download_urls,
            total_size=total_size,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preparing download: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare download"
        )


@router.get("", response_model=DownloadsListResponse)
async def get_downloads(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's downloaded songs.
    
    Returns list of downloads with total size and remaining slots.
    """
    user_id = current_user['user_id']
    logger.info(f"Get downloads for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Query downloads
        downloads_ref = db.collection('offline_downloads').where('userId', '==', user_id)
        
        downloads = []
        total_size = 0
        
        for dl_doc in downloads_ref.stream():
            dl_data = dl_doc.to_dict()
            song_id = dl_data.get('songId')
            
            # Get song details
            song_doc = db.collection('songs').document(song_id).get()
            song_title = 'Unknown'
            if song_doc.exists:
                song_title = song_doc.to_dict().get('title', 'Unknown')
            
            file_size = dl_data.get('fileSize', 0)
            total_size += file_size
            
            downloads.append(DownloadInfo(
                song_id=song_id,
                title=song_title,
                downloaded_at=dl_data.get('downloadedAt'),
                file_size=file_size
            ))
        
        # Sort by download date (most recent first)
        downloads.sort(key=lambda x: x.downloaded_at, reverse=True)
        
        remaining_slots = MAX_DOWNLOADS - len(downloads)
        
        logger.info(f"Found {len(downloads)} downloads for user {user_id}, total size: {total_size} bytes")
        
        return DownloadsListResponse(
            downloads=downloads,
            total_size=total_size,
            remaining_slots=remaining_slots,
        )
        
    except Exception as e:
        logger.error(f"Error getting downloads: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get downloads"
        )


@router.delete("/{song_id}", status_code=204)
async def remove_download(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove song from downloads.
    
    Frees up a download slot.
    """
    user_id = current_user['user_id']
    logger.info(f"Remove download: {song_id} for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Delete download document
        download_id = f"{user_id}_{song_id}"
        download_ref = db.collection('offline_downloads').document(download_id)
        
        if not download_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Download not found"
            )
        
        download_ref.delete()
        
        # Decrement song download count
        song_ref = db.collection('songs').document(song_id)
        song_doc = song_ref.get()
        if song_doc.exists:
            song_data = song_doc.to_dict()
            current_count = song_data.get('downloadCount', 0)
            song_ref.update({'downloadCount': max(0, current_count - 1)})
        
        logger.info(f"Removed download {download_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing download: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove download"
        )
