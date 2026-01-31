"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import logging

from app.models.auth import GoogleAuthRequest, AuthResponse
from app.core.firebase import verify_firebase_token, get_user_document, create_user_document, update_user_document
from app.core.security import create_access_token, get_current_user
from app.core.exceptions import AuthenticationError
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/google", response_model=AuthResponse)
async def authenticate_with_google(request: GoogleAuthRequest):
    """
    Authenticate user with Google OAuth token.
    
    Args:
        request: Google authentication request with ID token
        
    Returns:
        Authentication response with session token
    """
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(request.id_token)
        
        user_id = decoded_token['uid']
        email = decoded_token.get('email')
        display_name = decoded_token.get('name', email)
        photo_url = decoded_token.get('picture')
        
        # Check if user exists
        user_doc = await get_user_document(user_id)
        
        now = datetime.utcnow()
        
        if user_doc is None:
            # Create new user
            user_data = {
                "userId": user_id,
                "email": email,
                "displayName": display_name,
                "photoURL": photo_url,
                "createdAt": now,
                "lastLoginAt": now,
                "preferences": {
                    "skillLevel": "beginner",
                    "primaryInstrument": None,
                    "secondaryInstruments": [],
                    "notationFormat": "western",
                    "sargamStyle": "hindustani",
                    "theme": "system"
                },
                "stats": {
                    "totalPracticeTime": 0,
                    "songsLearned": 0,
                    "currentStreak": 0,
                    "longestStreak": 0
                },
                "rateLimits": {
                    "transcriptionsToday": 0,
                    "lastTranscriptionReset": now,
                    "activeJobs": 0
                }
            }
            await create_user_document(user_id, user_data)
            logger.info(f"Created new user: {user_id}")
        else:
            # Update last login
            await update_user_document(user_id, {"lastLoginAt": now})
            logger.info(f"User logged in: {user_id}")
        
        # Create session token
        session_token = create_access_token(user_id, email)
        expires_at = now.replace(microsecond=0) + \
                    datetime.timedelta(days=settings.jwt_expiration_days)
        
        return AuthResponse(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            user={
                "email": email,
                "displayName": display_name,
                "photoURL": photo_url
            }
        )
        
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: Since we're using JWT tokens, actual logout is handled client-side
    by removing the token. This endpoint is for logging purposes.
    """
    logger.info(f"User logged out: {current_user['user_id']}")
    return None
