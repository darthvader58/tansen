"""
Source separation service using Demucs.
"""
import os
import logging
import tempfile
import numpy as np
import soundfile as sf
from typing import Dict, List, Optional, Tuple
import subprocess

logger = logging.getLogger(__name__)


class SourceSeparationService:
    """Service for audio source separation using Demucs."""
    
    def __init__(self):
        """Initialize source separation service."""
        self.model_name = 'htdemucs'  # High-quality Demucs model
    
    def separate_sources(
        self,
        audio_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Separate audio into vocals, drums, bass, and other using Demucs.
        
        Args:
            audio_path: Path to input audio file
            output_dir: Output directory (temp dir if None)
            
        Returns:
            Dictionary with paths to separated sources
        """
        logger.info(f"Separating sources from: {audio_path}")
        
        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Run Demucs separation
            # Demucs CLI: demucs -n htdemucs --two-stems=vocals audio.mp3 -o output_dir
            cmd = [
                'demucs',
                '-n', self.model_name,
                audio_path,
                '-o', output_dir
            ]
            
            logger.info(f"Running Demucs: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Demucs failed: {result.stderr}")
                raise RuntimeError(f"Source separation failed: {result.stderr}")
            
            # Demucs outputs to: output_dir/htdemucs/audio_name/vocals.wav, drums.wav, etc.
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            separated_dir = os.path.join(output_dir, self.model_name, audio_name)
            
            # Check if separated files exist
            sources = {}
            for source_name in ['vocals', 'drums', 'bass', 'other']:
                source_path = os.path.join(separated_dir, f'{source_name}.wav')
                if os.path.exists(source_path):
                    sources[source_name] = source_path
                    logger.info(f"  ✓ Separated {source_name}: {source_path}")
                else:
                    logger.warning(f"  ✗ Missing {source_name}")
            
            if not sources:
                raise RuntimeError("No separated sources found")
            
            logger.info(f"Source separation complete: {len(sources)} sources")
            return sources
            
        except subprocess.TimeoutExpired:
            logger.error("Demucs timed out after 10 minutes")
            raise RuntimeError("Source separation timed out")
        except Exception as e:
            logger.error(f"Error in source separation: {e}", exc_info=True)
            raise
    
    def generate_instrumental(
        self,
        audio_path: str,
        output_path: str,
        remove_vocals: bool = True,
        remove_drums: bool = False,
        remove_bass: bool = False,
        format: str = 'mp3',
        bitrate: str = '320k'
    ) -> str:
        """
        Generate instrumental version by mixing selected sources.
        
        Args:
            audio_path: Path to input audio file
            output_path: Path for output file
            remove_vocals: Remove vocals
            remove_drums: Remove drums
            remove_bass: Remove bass
            format: Output format (mp3 or wav)
            bitrate: Bitrate for MP3 (e.g., '320k')
            
        Returns:
            Path to generated instrumental file
        """
        logger.info(f"Generating instrumental: vocals={not remove_vocals}, drums={not remove_drums}, bass={not remove_bass}")
        
        # Separate sources
        with tempfile.TemporaryDirectory() as temp_dir:
            sources = self.separate_sources(audio_path, temp_dir)
            
            # Load and mix selected sources
            mixed_audio = None
            sample_rate = None
            
            for source_name, source_path in sources.items():
                # Determine if we should include this source
                include = True
                if source_name == 'vocals' and remove_vocals:
                    include = False
                elif source_name == 'drums' and remove_drums:
                    include = False
                elif source_name == 'bass' and remove_bass:
                    include = False
                
                if include:
                    logger.info(f"  Including {source_name}")
                    audio, sr = sf.read(source_path)
                    
                    if mixed_audio is None:
                        mixed_audio = audio
                        sample_rate = sr
                    else:
                        # Ensure same length
                        min_len = min(len(mixed_audio), len(audio))
                        mixed_audio = mixed_audio[:min_len] + audio[:min_len]
            
            if mixed_audio is None:
                raise RuntimeError("No sources selected for instrumental")
            
            # Normalize to prevent clipping
            max_val = np.abs(mixed_audio).max()
            if max_val > 0:
                mixed_audio = mixed_audio / max_val * 0.95
            
            # Save as WAV first
            temp_wav = os.path.join(temp_dir, 'instrumental.wav')
            sf.write(temp_wav, mixed_audio, sample_rate)
            
            # Convert to requested format
            if format == 'mp3':
                self._convert_to_mp3(temp_wav, output_path, bitrate)
            elif format == 'wav':
                # Ensure 16-bit/44.1kHz for WAV
                if sample_rate != 44100:
                    self._resample_audio(temp_wav, output_path, 44100)
                else:
                    import shutil
                    shutil.copy(temp_wav, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Instrumental generated: {output_path}")
            return output_path
    
    def _convert_to_mp3(
        self,
        input_path: str,
        output_path: str,
        bitrate: str = '320k'
    ):
        """Convert audio to MP3 using ffmpeg."""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-codec:a', 'libmp3lame',
            '-b:a', bitrate,
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {result.stderr}")
            raise RuntimeError(f"MP3 conversion failed: {result.stderr}")
    
    def _resample_audio(
        self,
        input_path: str,
        output_path: str,
        target_sr: int = 44100
    ):
        """Resample audio to target sample rate."""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ar', str(target_sr),
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg resampling failed: {result.stderr}")
            raise RuntimeError(f"Resampling failed: {result.stderr}")
    
    def validate_audio_quality(
        self,
        audio_path: str,
        format: str = 'mp3',
        min_bitrate: int = 320000
    ) -> Tuple[bool, str]:
        """
        Validate audio quality meets requirements.
        
        Args:
            audio_path: Path to audio file
            format: Expected format
            min_bitrate: Minimum bitrate in bps
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Use ffprobe to check audio properties
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=bit_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, "Failed to probe audio file"
            
            bitrate = int(result.stdout.strip())
            
            if bitrate < min_bitrate:
                return False, f"Bitrate {bitrate} is below minimum {min_bitrate}"
            
            return True, f"Audio quality validated: {bitrate} bps"
            
        except Exception as e:
            logger.error(f"Error validating audio quality: {e}")
            return False, str(e)

