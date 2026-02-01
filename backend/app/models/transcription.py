"""Transcription data models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Transcription job status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Instrument(str, Enum):
    """Supported instruments."""
    PIANO = "piano"
    GUITAR = "guitar"
    BASS = "bass"
    DRUMS = "drums"
    VOCALS = "vocals"
    VIOLIN = "violin"
    SAXOPHONE = "saxophone"


class Note(BaseModel):
    """Musical note."""
    pitch: str  # e.g., 'C4', 'Sa'
    start_time: float  # seconds
    duration: float  # seconds
    velocity: int = 64  # 0-127


class Chord(BaseModel):
    """Musical chord."""
    name: str  # e.g., 'Cmaj7'
    start_time: float
    duration: float


class NotationData(BaseModel):
    """Notation data."""
    notes: List[Note] = []
    chords: List[Chord] = []


class NotationFormats(BaseModel):
    """Notation format file paths."""
    sargam: Optional[str] = None
    western: Optional[str] = None
    alphabetical: Optional[str] = None
    midi: Optional[str] = None


class Transcription(BaseModel):
    """Transcription model."""
    transcription_id: str
    song_id: str
    user_id: str
    instrument: Instrument
    notation_data: NotationData
    formats: NotationFormats = NotationFormats()
    created_at: datetime
    processing_time: Optional[float] = None  # seconds


class TranscriptionJob(BaseModel):
    """Transcription job."""
    job_id: str
    song_id: Optional[str] = None
    user_id: str
    status: JobStatus
    progress: int = 0  # 0-100
    instruments: List[Instrument]
    estimated_time: Optional[int] = None  # seconds
    queue_position: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TranscriptionUploadRequest(BaseModel):
    """Transcription upload request."""
    instruments: List[Instrument]


class TranscriptionYouTubeRequest(BaseModel):
    """YouTube transcription request."""
    youtube_url: str
    instruments: List[Instrument]


class TranscriptionJobResponse(BaseModel):
    """Transcription job response."""
    job_id: str
    song_id: Optional[str] = None
    status: JobStatus
    estimated_time: Optional[int] = None
    queue_position: Optional[int] = None


class TranscriptionStatusResponse(BaseModel):
    """Transcription status response."""
    job_id: str
    status: JobStatus
    progress: int
    song_id: Optional[str] = None
    error: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Transcription response."""
    transcription_id: str
    song_id: str
    instrument: Instrument
    format: str
    scale: Optional[str] = None
    notation_data: NotationData
