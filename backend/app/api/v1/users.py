"""
Users endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging

from app.core.security import get_current_user
from app.core.firebase import get_firestore_client
from app.models.user import UserResponse, UserUpdate, UserPreferences, UserStats
from app.models.favorites import FavoriteResponse
from app.models.practice import PracticeSessionCreate, PracticeHistoryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user profile with preferences and stats.
    """
    user_id = current_user['user_id']
    logger.info(f"Get profile for user: {user_id}")
    
    try:
        db = get_firestore_client()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        
        return UserResponse(
            user_id=user_id,
            email=user_data.get('email', current_user.get('email', '')),
            display_name=user_data.get('displayName', ''),
            photo_url=user_data.get('photoURL'),
            preferences=UserPreferences(**user_data.get('preferences', {})),
            stats=UserStats(**user_data.get('stats', {})),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Update user preferences.
    """
    user_id = current_user['user_id']
    logger.info(f"Update profile for user: {user_id}")
    
    try:
        db = get_firestore_client()
        user_ref = db.collection('users').document(user_id)
        
        # Get current user data
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Update preferences if provided
        if updates.preferences:
            user_ref.update({
                'preferences': updates.preferences.dict()
            })
            user_data['preferences'] = updates.preferences.dict()
        
        return UserResponse(
            user_id=user_id,
            email=user_data.get('email', current_user.get('email', '')),
            display_name=user_data.get('displayName', ''),
            photo_url=user_data.get('photoURL'),
            preferences=UserPreferences(**user_data.get('preferences', {})),
            stats=UserStats(**user_data.get('stats', {})),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/me/favorites", response_model=dict)
async def get_favorites(
    current_user: dict = Depends(get_current_user),
):
    """
    Get user's favorite songs with full song details.
    """
    user_id = current_user['user_id']
    logger.info(f"Get favorites for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Query favorites
        favorites_ref = db.collection('user_favorites').where('userId', '==', user_id)
        favorites = []
        
        for fav_doc in favorites_ref.stream():
            fav_data = fav_doc.to_dict()
            song_id = fav_data.get('songId')
            
            # Get song details
            song_doc = db.collection('songs').document(song_id).get()
            if song_doc.exists:
                song_data = song_doc.to_dict()
                favorites.append({
                    'song_id': song_id,
                    'title': song_data.get('title'),
                    'artist': song_data.get('artist'),
                    'album': song_data.get('album'),
                    'duration': song_data.get('duration'),
                    'genre': song_data.get('genre'),
                    'album_art': song_data.get('metadata', {}).get('albumArt'),
                    'added_at': fav_data.get('addedAt')
                })
        
        # Sort by added date (most recent first)
        favorites.sort(key=lambda x: x.get('added_at', datetime.min), reverse=True)
        
        logger.info(f"Found {len(favorites)} favorites for user {user_id}")
        
        return {
            "favorites": favorites,
            "count": len(favorites)
        }
        
    except Exception as e:
        logger.error(f"Error getting favorites: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get favorites"
        )


@router.post("/me/favorites/{song_id}", status_code=201)
async def add_favorite(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Add song to favorites.
    """
    user_id = current_user['user_id']
    logger.info(f"Add favorite: {song_id} for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Check if song exists
        song_doc = db.collection('songs').document(song_id).get()
        if not song_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        # Check if already favorited
        favorite_id = f"{user_id}_{song_id}"
        favorite_ref = db.collection('user_favorites').document(favorite_id)
        
        if favorite_ref.get().exists:
            return {"message": "Already in favorites"}
        
        # Create favorite document
        favorite_ref.set({
            'favoriteId': favorite_id,
            'userId': user_id,
            'songId': song_id,
            'addedAt': datetime.now(timezone.utc)
        })
        
        # Increment song favorite count
        song_ref = db.collection('songs').document(song_id)
        song_data = song_doc.to_dict()
        current_count = song_data.get('favoriteCount', 0)
        song_ref.update({'favoriteCount': current_count + 1})
        
        logger.info(f"Added favorite: {song_id} for user {user_id}")
        
        return {"message": "Added to favorites"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add favorite"
        )


@router.delete("/me/favorites/{song_id}", status_code=204)
async def remove_favorite(
    song_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove song from favorites.
    """
    user_id = current_user['user_id']
    logger.info(f"Remove favorite: {song_id} for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Delete favorite document
        favorite_id = f"{user_id}_{song_id}"
        favorite_ref = db.collection('user_favorites').document(favorite_id)
        
        if not favorite_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )
        
        favorite_ref.delete()
        
        # Decrement song favorite count
        song_ref = db.collection('songs').document(song_id)
        song_doc = song_ref.get()
        if song_doc.exists:
            song_data = song_doc.to_dict()
            current_count = song_data.get('favoriteCount', 0)
            song_ref.update({'favoriteCount': max(0, current_count - 1)})
        
        logger.info(f"Removed favorite: {song_id} for user {user_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove favorite"
        )


@router.get("/me/history", response_model=PracticeHistoryResponse)
async def get_practice_history(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get practice history with statistics.
    """
    user_id = current_user['user_id']
    logger.info(f"Get practice history for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Query practice history
        history_ref = db.collection('practice_history').where('userId', '==', user_id)
        
        # Apply date filters
        if start_date:
            history_ref = history_ref.where('practiceDate', '>=', start_date)
        if end_date:
            history_ref = history_ref.where('practiceDate', '<=', end_date)
        
        # Get history documents
        history = []
        total_practice_time = 0
        songs_practiced = set()
        
        for hist_doc in history_ref.stream():
            hist_data = hist_doc.to_dict()
            
            # Get song details
            song_id = hist_data.get('songId')
            song_doc = db.collection('songs').document(song_id).get()
            song_title = song_doc.to_dict().get('title', 'Unknown') if song_doc.exists else 'Unknown'
            
            history.append({
                'history_id': hist_data.get('historyId'),
                'song_id': song_id,
                'song_title': song_title,
                'instrument': hist_data.get('instrument'),
                'practice_date': hist_data.get('practiceDate'),
                'duration': hist_data.get('duration', 0),
                'notation_format': hist_data.get('notationFormat'),
                'scale': hist_data.get('scale'),
                'completion_percentage': hist_data.get('completionPercentage', 0)
            })
            
            total_practice_time += hist_data.get('duration', 0)
            songs_practiced.add(song_id)
        
        # Sort by date (most recent first)
        history.sort(key=lambda x: x.get('practice_date', datetime.min), reverse=True)
        
        # Calculate streak
        current_streak = calculate_practice_streak(db, user_id)
        
        # Get user stats
        user_doc = db.collection('users').document(user_id).get()
        user_stats = user_doc.to_dict().get('stats', {}) if user_doc.exists else {}
        
        logger.info(f"Found {len(history)} practice sessions for user {user_id}")
        
        return PracticeHistoryResponse(
            history=history,
            stats={
                'total_practice_time': user_stats.get('totalPracticeTime', total_practice_time),
                'songs_learned': user_stats.get('songsLearned', len(songs_practiced)),
                'current_streak': current_streak,
                'longest_streak': user_stats.get('longestStreak', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting practice history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practice history"
        )


@router.post("/me/history", status_code=201)
async def record_practice_session(
    session: PracticeSessionCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    Record practice session and update user stats.
    """
    user_id = current_user['user_id']
    logger.info(f"Record practice session for user: {user_id}")
    
    try:
        db = get_firestore_client()
        
        # Verify song exists
        song_doc = db.collection('songs').document(session.song_id).get()
        if not song_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        # Create practice history document
        import uuid
        history_id = str(uuid.uuid4())
        
        history_data = {
            'historyId': history_id,
            'userId': user_id,
            'songId': session.song_id,
            'instrument': session.instrument,
            'practiceDate': datetime.now(timezone.utc),
            'duration': session.duration,
            'notationFormat': session.notation_format,
            'scale': session.scale,
            'completionPercentage': session.completion_percentage
        }
        
        db.collection('practice_history').document(history_id).set(history_data)
        
        # Update user stats
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            stats = user_data.get('stats', {})
            
            # Update total practice time
            total_time = stats.get('totalPracticeTime', 0) + session.duration
            
            # Calculate new streak
            current_streak = calculate_practice_streak(db, user_id)
            longest_streak = max(stats.get('longestStreak', 0), current_streak)
            
            # Update songs learned (if completion >= 80%)
            songs_learned = stats.get('songsLearned', 0)
            if session.completion_percentage >= 80:
                songs_learned += 1
            
            user_ref.update({
                'stats.totalPracticeTime': total_time,
                'stats.songsLearned': songs_learned,
                'stats.currentStreak': current_streak,
                'stats.longestStreak': longest_streak
            })
        
        logger.info(f"Recorded practice session {history_id} for user {user_id}")
        
        return {"message": "Practice session recorded", "history_id": history_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording practice session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record practice session"
        )


def calculate_practice_streak(db, user_id: str) -> int:
    """
    Calculate current practice streak (consecutive days).
    """
    try:
        # Get practice history sorted by date
        history_ref = db.collection('practice_history').where('userId', '==', user_id).order_by('practiceDate', direction='DESCENDING')
        
        streak = 0
        last_date = None
        
        for hist_doc in history_ref.stream():
            hist_data = hist_doc.to_dict()
            practice_date = hist_data.get('practiceDate')
            
            if not practice_date:
                continue
            
            # Convert to date only (ignore time)
            practice_day = practice_date.date() if hasattr(practice_date, 'date') else practice_date
            
            if last_date is None:
                # First entry
                today = datetime.now(timezone.utc).date()
                if practice_day == today or practice_day == today - timedelta(days=1):
                    streak = 1
                    last_date = practice_day
                else:
                    break
            else:
                # Check if consecutive day
                expected_date = last_date - timedelta(days=1)
                if practice_day == expected_date:
                    streak += 1
                    last_date = practice_day
                elif practice_day == last_date:
                    # Same day, don't increment
                    continue
                else:
                    # Streak broken
                    break
        
        return streak
        
    except Exception as e:
        logger.error(f"Error calculating streak: {e}")
        return 0
