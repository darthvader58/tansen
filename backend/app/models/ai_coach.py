"""
AI Coach data models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AudioAnalysisRequest(BaseModel):
    """Request model for audio analysis."""
    song_id: str = Field(..., description="Reference song ID to compare against")
    instrument: str = Field(..., description="Instrument being played (piano, guitar, vocals, etc.)")
    audio_data: str = Field(..., description="Base64 encoded audio data")
    duration: int = Field(..., description="Duration of recording in seconds")


class ImprovementSuggestion(BaseModel):
    """Model for improvement suggestions."""
    measure: str = Field(..., description="Measure or time range (e.g., '12-16', '0:24')")
    issue: str = Field(..., description="Description of the issue")
    suggestion: str = Field(..., description="Specific suggestion for improvement")
    severity: str = Field(default="medium", description="Severity: low, medium, high")


class AudioAnalysisResponse(BaseModel):
    """Response model for audio analysis."""
    analysis_id: str = Field(..., description="Unique analysis ID")
    overall_score: int = Field(..., ge=0, le=100, description="Overall performance score (0-100)")
    note_accuracy: int = Field(..., ge=0, le=100, description="Note accuracy score (0-100)")
    tempo_consistency: int = Field(..., ge=0, le=100, description="Tempo consistency score (0-100)")
    rhythm_precision: int = Field(..., ge=0, le=100, description="Rhythm precision score (0-100)")
    feedback: List[str] = Field(default_factory=list, description="Positive feedback messages")
    improvements: List[ImprovementSuggestion] = Field(default_factory=list, description="Areas to improve")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")


class PracticeSessionAnalysis(BaseModel):
    """Model for storing practice session analysis in Firestore."""
    analysis_id: str
    user_id: str
    song_id: str
    instrument: str
    duration: int
    overall_score: int
    note_accuracy: int
    tempo_consistency: int
    rhythm_precision: int
    feedback: List[str]
    improvements: List[Dict[str, Any]]
    timestamp: datetime
    audio_url: Optional[str] = None  # URL to stored audio file if needed
