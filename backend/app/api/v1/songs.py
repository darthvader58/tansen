"""
Song library endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
import logging
import os

from app.core.security import get_current_user
from app.core.rate_limiter import check_rate_limit, check_concurrent_jobs, increment_rate_limit
from app.core.firebase import get_firestore_client
from app.services.song_library_service import SongLibraryService
from app.tasks.instrumental import generate_instrumental_task
from app.models.song import (
    SongResponse,
    SongSearchResult,
    Difficulty,
    Source,
    SongMetadata,
)
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter()
song_service = SongLibraryService()


@router.get("", response_model=dict)
async def browse_songs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    difficulty: Optional[Difficulty] = Query(None, description="Filter by difficulty"),
    instrument: Optional[str] = Query(None, description="Filter by instrument"),
    sort_by: str = Query("popularity", description="Sort by: popularity, title, artist, date"),
    current_user: dict = Depends(get_current_user),
):
    """
    Browse song library with pagination and filters.
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Results per page (default: 20, max: 100)
    - genre: Filter by genre
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)
    - instrument: Filter by available instrument
    - sort_by: Sort by field (popularity, title, artist, date)
    """
    user_id = current_user['user_id']
    logger.info(f"Browse songs request from user: {user_id}, page: {page}, limit: {limit}")
    
    try:
        db = get_firestore_client()
        
        # Search songs with filters
        songs, total_count = song_service.search_songs_in_firestore(
            db=db,
            genre=genre,
            difficulty=difficulty.value if difficulty else None,
            instrument=instrument,
            page=page,
            limit=limit
        )
        
        # Get user's favorites for is_favorite flag
        favorites_ref = db.collection('user_favorites').where('userId', '==', user_id)
        favorite_song_ids = set()
        for fav_doc in favorites_ref.stream():
            favorite_song_ids.add(fav_doc.to_dict().get('songId'))
        
        # Get user's downloads for is_downloaded flag
        downloads_ref = db.collection('offline_downloads').where('userId', '==', user_id)
        downloaded_song_ids = set()
        for dl_doc in downloads_ref.stream():
            downloaded_song_ids.add(dl_doc.to_dict().get('songId'))
        
        # Format response
        song_responses = []
        for song in songs:
            song_id = song.get('songId')
            
            song_responses.append({
                'song_id': song_id,
                'title': song.get('title'),
                'artist': song.get('artist'),
                'album': song.get('album'),
                'duration': song.get('duration', 0),
                'genre': song.get('genre'),
                'difficulty': song.get('difficulty', 'beginner'),
                'original_key': song.get('originalKey'),
                'tempo': song.get('tempo'),
                'time_signature': song.get('timeSignature'),
                'metadata': song.get('metadata', {}),
                'available_instruments': song.get('transcription', {}).get('instruments', []),
                'is_favorite': song_id in favorite_song_ids,
                'is_downloaded': song_id in downloaded_song_ids,
            })
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'songs': song_responses,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
            }
        }
        
    except Exception as e:
        logger.error(f"Error browsing songs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to browse songs"
        )


@router.get("/search", response_model=dict)
async def search_songs(
    q: str = Query(..., description="Search query"),
    source: Optional[Source] = Query(None, description="Search source: library, youtube, spotify"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search songs by title or artist.
    
    Query Parameters:
    - q: Search query (required)
    - source: Search source (library, youtube, spotify) - default: library
    - limit: Max results (default: 20, max: 100)
    """
    user_id = current_user['user_id']
    logger.info(f"Search songs request from user: {user_id}, query: {q}, source: {source}")
    
    try:
        results = []
        
        if source == Source.SPOTIFY or source is None:
            # Search Spotify
            spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
            spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if spotify_client_id and spotify_client_secret:
                spotify_results = song_service.search_spotify(
                    query=q,
                    client_id=spotify_client_id,
                    client_secret=spotify_client_secret,
                    limit=limit
                )
                results.extend(spotify_results)
        
        if source == Source.LIBRARY or source is None:
            # Search local library
            db = get_firestore_client()
            library_songs, _ = song_service.search_songs_in_firestore(
                db=db,
                query=q,
                limit=limit
            )
            
            for song in library_songs:
                results.append({
                    'songId': song.get('songId'),
                    'title': song.get('title'),
                    'artist': song.get('artist'),
                    'albumArt': song.get('metadata', {}).get('albumArt'),
                    'duration': song.get('duration', 0),
                    'source': 'library'
                })
        
        # Limit total results
        results = results[:limit]
        
        logger.info(f"Found {len(results)} songs for query: {q}")
        
        return {
            'results': results,
            'query': q,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching songs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search songs"
        )


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get song details by ID.
    
    Path Parameters:
    - song_id: Song ID
    """
    user_id = current_user['user_id']
    logger.info(f"Get song request from user: {user_id}, song_id: {song_id}")
    
    try:
        db = get_firestore_client()
        
        # Get song document
        song_doc = db.collection('songs').document(song_id).get()
        
        if not song_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        song_data = song_doc.to_dict()
        
        # Check if user has access (public or owner)
        if not song_data.get('isPublic', False) and song_data.get('createdBy') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if favorited
        favorite_doc = db.collection('user_favorites').document(f"{user_id}_{song_id}").get()
        is_favorite = favorite_doc.exists
        
        # Check if downloaded
        download_doc = db.collection('offline_downloads').document(f"{user_id}_{song_id}").get()
        is_downloaded = download_doc.exists
        
        return SongResponse(
            song_id=song_id,
            title=song_data.get('title'),
            artist=song_data.get('artist'),
            album=song_data.get('album'),
            duration=song_data.get('duration', 0),
            genre=song_data.get('genre'),
            difficulty=Difficulty(song_data.get('difficulty', 'beginner')),
            original_key=song_data.get('originalKey'),
            tempo=song_data.get('tempo'),
            time_signature=song_data.get('timeSignature'),
            metadata=SongMetadata(**song_data.get('metadata', {})),
            available_instruments=song_data.get('transcription', {}).get('instruments', []),
            is_favorite=is_favorite,
            is_downloaded=is_downloaded,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting song: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get song"
        )


@router.post("/{song_id}/instrumental", response_model=dict)
async def generate_instrumental(
    song_id: str,
    remove_vocals: bool = Query(True, description="Remove vocals"),
    remove_drums: bool = Query(False, description="Remove drums"),
    remove_bass: bool = Query(False, description="Remove bass"),
    format: str = Query("mp3", description="Output format: mp3 or wav"),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate instrumental version of a song.
    
    Uses Demucs for source separation and mixes selected sources.
    Rate limited (counts toward 10 requests/24h limit).
    """
    user_id = current_user['user_id']
    logger.info(f"Generate instrumental request from user: {user_id}, song_id: {song_id}")
    
    try:
        # Check rate limits (instrumental generation counts toward transcription limit)
        can_generate, limit_message = await check_rate_limit(user_id)
        if not can_generate:
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
        
        # Get song document
        db = get_firestore_client()
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
        
        # Get audio file path
        audio_path = song_data.get('audioFiles', {}).get('original')
        if not audio_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Song has no audio file"
            )
        
        # Validate format
        if format not in ['mp3', 'wav']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format must be 'mp3' or 'wav'"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job document in Firestore
        job_data = {
            'jobId': job_id,
            'songId': song_id,
            'userId': user_id,
            'status': 'queued',
            'progress': 0,
            'removeVocals': remove_vocals,
            'removeDrums': remove_drums,
            'removeBass': remove_bass,
            'format': format,
            'createdAt': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        db.collection('instrumental_jobs').document(job_id).set(job_data)
        
        # Increment rate limit counter
        await increment_rate_limit(user_id)
        
        # Queue Celery task
        generate_instrumental_task.delay(
            job_id=job_id,
            song_id=song_id,
            user_id=user_id,
            audio_path=audio_path,
            remove_vocals=remove_vocals,
            remove_drums=remove_drums,
            remove_bass=remove_bass,
            format=format
        )
        
        logger.info(f"Queued instrumental generation job {job_id} for song {song_id}")
        
        return {
            'job_id': job_id,
            'status': 'queued',
            'estimated_time': 300  # 5 minutes estimate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating instrumental: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate instrumental"
        )


@router.get("/{song_id}/instrumental/{job_id}", response_model=dict)
async def get_instrumental_status(
    song_id: str,
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get instrumental generation status and download URL.
    
    Returns job status, progress, and download URL when completed.
    Download URL expires in 1 hour.
    """
    user_id = current_user['user_id']
    logger.info(f"Get instrumental status from user: {user_id}, job_id: {job_id}")
    
    try:
        db = get_firestore_client()
        
        # Get job document
        job_doc = db.collection('instrumental_jobs').document(job_id).get()
        
        if not job_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job_data = job_doc.to_dict()
        
        # Verify user owns this job
        if job_data.get('userId') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Verify song ID matches
        if job_data.get('songId') != song_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job does not belong to this song"
            )
        
        response = {
            'job_id': job_id,
            'status': job_data.get('status', 'queued'),
            'progress': job_data.get('progress', 0),
        }
        
        # Add download URL if completed
        if job_data.get('status') == 'completed':
            response['download_url'] = job_data.get('downloadUrl')
            response['file_size'] = job_data.get('fileSize')
            response['format'] = job_data.get('format')
        
        # Add error if failed
        if job_data.get('status') == 'failed':
            response['error'] = job_data.get('error')
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting instrumental status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get instrumental status"
        )

