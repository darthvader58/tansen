"""
Recommendations endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
import logging

from app.core.security import get_current_user
from app.core.firebase import get_firestore_client
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter()
recommendation_service = RecommendationService()


@router.get("", response_model=dict)
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get personalized song recommendations.
    
    Recommendations are based on:
    - User skill level
    - Preferred instruments
    - Practice history
    - Genre preferences
    - Song popularity
    """
    user_id = current_user['user_id']
    logger.info(f"Get recommendations for user: {user_id}, limit: {limit}")
    
    try:
        db = get_firestore_client()
        
        recommendations = recommendation_service.get_recommendations(
            db=db,
            user_id=user_id,
            limit=limit
        )
        
        return {
            'recommendations': recommendations,
            'count': len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )

