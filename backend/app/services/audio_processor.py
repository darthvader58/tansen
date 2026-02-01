"""
Audio processing service for transcription pipeline.
"""
import os
import tempfile
from typing import Dict, List, Optional, Tuple
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for audio file processing and analysis."""
    
    SUPPORTED_FORMATS = ['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac']
    MAX_FILE_SIZE_MB = 50
    TARGET_SAMPLE_RATE = 44100
    
    @staticmethod
    def validate_audio_file(file_path: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file format and size.
        
        Args:
            file_path: Path to audio file
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        max_size_bytes = AudioProcessor.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File size exceeds maximum of {AudioProcessor.MAX_FILE_SIZE_MB}MB"
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if file_ext not in AudioProcessor.SUPPORTED_FORMATS:
            return False, f"Unsupported format. Supported: {', '.join(AudioProcessor.SUPPORTED_FORMATS)}"
        
        # Try to load audio to verify it's valid
        try:
            y, sr = librosa.load(file_path, sr=None, duration=1.0)
            if len(y) == 0:
                return False, "Audio file appears to be empty"
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False, f"Invalid audio file: {str(e)}"
        
        return True, None
    
    @staticmethod
    def load_and_normalize(file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and normalize.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        logger.info(f"Loading audio file: {file_path}")
        
        # Load audio with librosa
        y, sr = librosa.load(file_path, sr=AudioProcessor.TARGET_SAMPLE_RATE, mono=True)
        
        # Normalize audio to [-1, 1]
        if np.max(np.abs(y)) > 0:
            y = y / np.max(np.abs(y))
        
        logger.info(f"Audio loaded: duration={len(y)/sr:.2f}s, sample_rate={sr}")
        return y, sr
    
    @staticmethod
    def detect_tempo(audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Detect tempo (BPM) of audio.
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate
            
        Returns:
            Tempo in BPM
        """
        logger.info("Detecting tempo...")
        
        try:
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            # Convert to scalar if it's an array
            if isinstance(tempo, np.ndarray):
                tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
            else:
                tempo = float(tempo)
            
            logger.info(f"Detected tempo: {tempo:.2f} BPM")
            return tempo
        except Exception as e:
            logger.warning(f"Tempo detection failed: {e}, using default 120 BPM")
            return 120.0
    
    @staticmethod
    def estimate_key(audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Estimate musical key of audio.
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate
            
        Returns:
            Estimated key (e.g., 'C', 'Am')
        """
        logger.info("Estimating key...")
        
        try:
            # Use chroma features for key estimation
            chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
            
            # Average chroma across time
            chroma_mean = np.mean(chroma, axis=1)
            
            # Find dominant pitch class
            dominant_pitch = np.argmax(chroma_mean)
            
            # Map to key names
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            estimated_key = key_names[dominant_pitch]
            
            logger.info(f"Estimated key: {estimated_key}")
            return estimated_key
        except Exception as e:
            logger.warning(f"Key estimation failed: {e}, using default 'C'")
            return 'C'
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict:
        """
        Extract audio metadata.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary of metadata
        """
        logger.info("Extracting audio metadata...")
        
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=AudioProcessor.TARGET_SAMPLE_RATE)
            
            # Calculate duration
            duration = len(y) / sr
            
            # Detect tempo
            tempo = AudioProcessor.detect_tempo(y, sr)
            
            # Estimate key
            key = AudioProcessor.estimate_key(y, sr)
            
            metadata = {
                'duration': duration,
                'sample_rate': sr,
                'tempo': tempo,
                'key': key,
                'channels': 1,  # We convert to mono
            }
            
            logger.info(f"Metadata extracted: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {
                'duration': 0,
                'sample_rate': AudioProcessor.TARGET_SAMPLE_RATE,
                'tempo': 120.0,
                'key': 'C',
                'channels': 1,
            }
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to WAV format.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output WAV file (optional)
            
        Returns:
            Path to output WAV file
        """
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.wav'
        
        logger.info(f"Converting {input_path} to WAV format...")
        
        try:
            # Load and convert using pydub
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1)  # Convert to mono
            audio = audio.set_frame_rate(AudioProcessor.TARGET_SAMPLE_RATE)
            audio.export(output_path, format='wav')
            
            logger.info(f"Converted to WAV: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            raise
