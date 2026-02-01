"""
Users endpoints.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.models.user import UserResponse, UserUpdate
from app.models.favorites import FavoriteResponse
from app.models.practice import PracticeSessionCreate, PracticeHistoryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user profile.
    
    TODO: Implement in Phase 6
    - Retrieve user document from Firestore
    - Return user profile
    """
    logger.info(f"Get profile for user: {current_user['user_id']}")
    
    return UserResponse(
        user_id=current_user['user_id'],
        email=current_user['email'],
        display_name="Placeholder User",
        preferences={},
        stats={},
    )


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Update user preferences.
    
    TODO: Implement in Phase 6
    - Update user document in Firestore
    - Return updated profile
    """
    logger.info(f"Update profile for user: {current_user['user_id']}")
    
    return UserResponse(
        user_id=current_user['user_id'],
        email=current_user['email'],
        display_name="Placeholder User",
        preferences=updates.preferences or {},
        stats={},
    )


@router.get("/me/favorites", response_model=dict)
async def get_favorites(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's favorite songs.
    
    TODO: Implement in Phase 6
    - Query UserFavorites collection
    - Join with Songs collection
    - Return favorites list
    """
    logger.info(f"Get favorites for user: {current_user['user_id']}")
    
    return {
        "favorites": []
    }


@router.post("/me/favorites/{song_id}", status_code=201)
async def add_favorite(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Add song to favorites.
    
    TODO: Implement in Phase 6
    - Create favorite document in Firestore
    - Update song favorite count
    - Return success
    """
    logger.info(f"Add favorite: {song_id} for user: {current_user['user_id']}")
    
    return {"message": "Added to favorites"}


@router.delete("/me/favorites/{song_id}", status_code=204)
async def remove_favorite(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove song from favorites.
    
    TODO: Implement in Phase 6
    - Delete favorite document from Firestore
    - Update song favorite count
    - Return success
    """
    logger.info(f"Remove favorite: {song_id} for user: {current_user['user_id']}")
    
    return None


@router.get("/me/history", response_model=PracticeHistoryResponse)
async def get_practice_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get practice history.
    
    TODO: Implement in Phase 6
    - Query PracticeHistory collection
    - Calculate statistics
    - Return history and stats
    """
    logger.info(f"Get practice history for user: {current_user['user_id']}")
    
    return PracticeHistoryResponse(
        history=[],
        stats={
            "total_practice_time": 0,
            "songs_learned": 0,
            "current_streak": 0,
        }
    )


@router.post("/me/history", status_code=201)
async def record_practice_session(
    session: PracticeSessionCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    Record practice session.
    
    TODO: Implement in Phase 6
    - Create practice history document
    - Update user stats
    - Calculate streaks
    - Return success
    """
    logger.info(f"Record practice session for user: {current_user['user_id']}")
    
    return {"message": "Practice session recorded"}
