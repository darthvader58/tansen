"""Practice history data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PracticeSession(BaseModel):
    """Practice session model."""
    history_id: str
    user_id: str
    song_id: str
    instrument: str
    practice_date: datetime
    duration: int  # minutes
    notation_format: str
    scale: Optional[str] = None
    completion_percentage: int = 0  # 0-100


class PracticeSessionCreate(BaseModel):
    """Practice session creation request."""
    song_id: str
    instrument: str
    duration: int
    completion_percentage: int = 0


class PracticeStats(BaseModel):
    """Practice statistics."""
    total_practice_time: int  # minutes
    songs_learned: int
    current_streak: int  # days
    longest_streak: int = 0


class PracticeHistoryResponse(BaseModel):
    """Practice history response."""
    history: list
    stats: PracticeStats
