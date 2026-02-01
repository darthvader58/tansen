"""Song data models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Difficulty(str, Enum):
    """Song difficulty level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Source(str, Enum):
    """Song source."""
    LIBRARY = "library"
    USER_UPLOAD = "user_upload"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"


class TranscriptionStatus(str, Enum):
    """Transcription status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SongMetadata(BaseModel):
    """Song metadata."""
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None
    musicbrainz_id: Optional[str] = None
    album_art: Optional[str] = None
    source: Source = Source.LIBRARY


class AudioFiles(BaseModel):
    """Audio file paths."""
    original: Optional[str] = None
    instrumental: Optional[str] = None
    separated: Optional[dict] = None  # {vocals, drums, bass, other}


class TranscriptionInfo(BaseModel):
    """Transcription information."""
    status: TranscriptionStatus = TranscriptionStatus.PENDING
    processed_at: Optional[datetime] = None
    instruments: List[str] = []


class Song(BaseModel):
    """Song model."""
    song_id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: int  # seconds
    genre: Optional[str] = None
    difficulty: Difficulty = Difficulty.BEGINNER
    original_key: Optional[str] = None
    tempo: Optional[int] = None  # BPM
    time_signature: Optional[str] = None
    metadata: SongMetadata = SongMetadata()
    audio_files: AudioFiles = AudioFiles()
    transcription: TranscriptionInfo = TranscriptionInfo()
    created_by: Optional[str] = None
    created_at: datetime
    is_public: bool = True
    download_count: int = 0
    favorite_count: int = 0


class SongCreate(BaseModel):
    """Song creation request."""
    title: str
    artist: str
    album: Optional[str] = None
    duration: int
    genre: Optional[str] = None
    difficulty: Difficulty = Difficulty.BEGINNER


class SongResponse(BaseModel):
    """Song response."""
    song_id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: int
    genre: Optional[str] = None
    difficulty: Difficulty
    original_key: Optional[str] = None
    tempo: Optional[int] = None
    time_signature: Optional[str] = None
    metadata: SongMetadata
    available_instruments: List[str]
    is_favorite: bool = False
    is_downloaded: bool = False


class SongSearchResult(BaseModel):
    """Song search result."""
    song_id: str
    title: str
    artist: str
    album_art: Optional[str] = None
    duration: int
    source: Source
