"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import auth, transcriptions, songs, users, downloads, recommendations

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["Transcriptions"])
api_router.include_router(songs.router, prefix="/songs", tags=["Songs"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(downloads.router, prefix="/downloads", tags=["Downloads"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
