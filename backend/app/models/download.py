"""Download data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class Download(BaseModel):
    """Download model."""
    download_id: str
    user_id: str
    song_id: str
    downloaded_at: datetime
    file_size: int  # bytes
    local_path: Optional[str] = None
    includes_audio: bool = True
    includes_notations: List[str] = []


class DownloadRequest(BaseModel):
    """Download request."""
    include_audio: bool = True
    notation_formats: List[str] = ["sargam", "western", "alphabetical"]
    instruments: List[str] = ["piano"]


class DownloadUrls(BaseModel):
    """Download URLs."""
    audio: Optional[str] = None
    notations: dict = {}


class DownloadResponse(BaseModel):
    """Download response."""
    download_id: str
    download_urls: DownloadUrls
    total_size: int  # bytes
    expires_at: datetime


class DownloadInfo(BaseModel):
    """Download info."""
    song_id: str
    title: str
    downloaded_at: datetime
    file_size: int


class DownloadsListResponse(BaseModel):
    """Downloads list response."""
    downloads: List[DownloadInfo]
    total_size: int
    remaining_slots: int  # out of 50
