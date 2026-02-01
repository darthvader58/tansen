"""
Downloads endpoints.
"""
from fastapi import APIRouter, Depends
import logging

from app.core.security import get_current_user
from app.models.download import (
    DownloadRequest,
    DownloadResponse,
    DownloadsListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{song_id}", response_model=DownloadResponse)
async def prepare_download(
    song_id: str,
    request: DownloadRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Prepare song for offline download.
    
    TODO: Implement in Phase 7
    - Check download limit (50 songs)
    - Generate signed URLs for files
    - Package notation data
    - Return download URLs
    """
    logger.info(f"Prepare download for song: {song_id}")
    
    from datetime import datetime, timedelta
    
    return DownloadResponse(
        download_id=f"{current_user['user_id']}_{song_id}",
        download_urls={
            "audio": None,
            "notations": {},
        },
        total_size=0,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )


@router.get("", response_model=DownloadsListResponse)
async def get_downloads(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's downloaded songs.
    
    TODO: Implement in Phase 7
    - Query OfflineDownloads collection
    - Calculate total size
    - Calculate remaining slots
    - Return downloads list
    """
    logger.info(f"Get downloads for user: {current_user['user_id']}")
    
    return DownloadsListResponse(
        downloads=[],
        total_size=0,
        remaining_slots=50,
    )


@router.delete("/{song_id}", status_code=204)
async def remove_download(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove song from downloads.
    
    TODO: Implement in Phase 7
    - Delete download document from Firestore
    - Update user's download count
    - Return success
    """
    logger.info(f"Remove download: {song_id} for user: {current_user['user_id']}")
    
    return None
