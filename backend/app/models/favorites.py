"""Favorites data models."""
from pydantic import BaseModel
from datetime import datetime


class Favorite(BaseModel):
    """Favorite model."""
    favorite_id: str
    user_id: str
    song_id: str
    added_at: datetime


class FavoriteResponse(BaseModel):
    """Favorite response."""
    song_id: str
    title: str
    artist: str
    added_at: datetime
