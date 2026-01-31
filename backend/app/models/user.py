"""User data models."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """User skill level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class NotationFormat(str, Enum):
    """Notation format preference."""
    SARGAM = "sargam"
    WESTERN = "western"
    ALPHABETICAL = "alphabetical"


class SargamStyle(str, Enum):
    """Sargam notation style."""
    HINDUSTANI = "hindustani"
    CARNATIC = "carnatic"


class Theme(str, Enum):
    """App theme."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class UserPreferences(BaseModel):
    """User preferences."""
    skill_level: SkillLevel = SkillLevel.BEGINNER
    primary_instrument: Optional[str] = None
    secondary_instruments: List[str] = []
    notation_format: NotationFormat = NotationFormat.WESTERN
    sargam_style: SargamStyle = SargamStyle.HINDUSTANI
    theme: Theme = Theme.SYSTEM


class UserStats(BaseModel):
    """User statistics."""
    total_practice_time: int = 0  # minutes
    songs_learned: int = 0
    current_streak: int = 0  # days
    longest_streak: int = 0  # days


class RateLimits(BaseModel):
    """User rate limits."""
    transcriptions_today: int = 0
    last_transcription_reset: Optional[datetime] = None
    active_jobs: int = 0


class User(BaseModel):
    """User model."""
    user_id: str
    email: EmailStr
    display_name: str
    photo_url: Optional[str] = None
    created_at: datetime
    last_login_at: datetime
    preferences: UserPreferences = UserPreferences()
    stats: UserStats = UserStats()
    rate_limits: RateLimits = RateLimits()


class UserUpdate(BaseModel):
    """User update request."""
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    """User response."""
    user_id: str
    email: str
    display_name: str
    photo_url: Optional[str] = None
    preferences: UserPreferences
    stats: UserStats
