"""
Transcription service using Basic Pitch and MT3.
"""
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for audio-to-MIDI transcription."""
    
    def __init__(self):
        """Initialize transcription service."""
        self.basic_pitch_model = None
        self.mt3_model = None
    
    def _load_basic_pitch_model(self):
        """Lazy load Basic Pitch model."""
        if self.basic_pitch_model is None:
            try:
                from basic_pitch.inference import predict
                from basic_pitch import ICASSP_2022_MODEL_PATH
                logger.info("Basic Pitch model loaded successfully")
                self.basic_pitch_model = predict
            except Exception as e:
                logger.error(f"Error loading Basic Pitch model: {e}")
                raise
    
    def transcribe_with_basic_pitch(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        minimum_note_length: float = 0.127,
        minimum_frequency: float = 32.0,
        maximum_frequency: float = 2093.0
    ) -> List[Dict]:
        """
        Transcribe audio using Spotify's Basic Pitch.
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate
            onset_threshold: Threshold for note onset detection
            frame_threshold: Threshold for frame-level note detection
            minimum_note_length: Minimum note length in seconds
            minimum_frequency: Minimum frequency in Hz
            maximum_frequency: Maximum frequency in Hz
            
        Returns:
            List of note dictionaries with pitch, start_time, duration, velocity
        """
        logger.info("Transcribing audio with Basic Pitch...")
        start_time = time.time()
        
        try:
            self._load_basic_pitch_model()
            
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            
            # Run Basic Pitch inference
            model_output, midi_data, note_events = predict(
                audio_path=None,
                audio_array=audio_data,
                sample_rate=sample_rate,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
                minimum_note_length=minimum_note_length,
                minimum_frequency=minimum_frequency,
                maximum_frequency=maximum_frequency,
                model_or_model_path=ICASSP_2022_MODEL_PATH
            )
            
            # Convert note events to our format
            notes = []
            for note in note_events:
                # Note format: [start_time, end_time, pitch, velocity, (optional) pitch_bend]
                start_time_sec = note[0]
                end_time_sec = note[1]
                pitch_midi = int(note[2])
                velocity = int(note[3]) if len(note) > 3 else 80
                
                # Convert MIDI pitch to note name
                note_name = self._midi_to_note_name(pitch_midi)
                
                notes.append({
                    'pitch': note_name,
                    'pitchMidi': pitch_midi,
                    'startTime': start_time_sec,
                    'duration': end_time_sec - start_time_sec,
                    'velocity': velocity
                })
            
            processing_time = time.time() - start_time
            logger.info(f"Basic Pitch transcription completed: {len(notes)} notes in {processing_time:.2f}s")
            
            return notes
            
        except Exception as e:
            logger.error(f"Error in Basic Pitch transcription: {e}", exc_info=True)
            # Return empty list on error rather than failing completely
            return []
    
    def transcribe_with_mt3(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> List[Dict]:
        """
        Transcribe audio using Google's MT3 (Multi-Track Music Transcription).
        
        Note: MT3 is more complex and requires additional setup.
        This is a placeholder for future implementation.
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate
            
        Returns:
            List of note dictionaries
        """
        logger.warning("MT3 transcription not yet implemented, using Basic Pitch instead")
        return self.transcribe_with_basic_pitch(audio_data, sample_rate)
    
    def ensemble_transcription(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        methods: List[str] = ['basic_pitch']
    ) -> List[Dict]:
        """
        Perform ensemble transcription using multiple methods.
        
        Args:
            audio_data: Audio time series
            sample_rate: Sample rate
            methods: List of transcription methods to use
            
        Returns:
            Combined and refined list of notes
        """
        logger.info(f"Performing ensemble transcription with methods: {methods}")
        
        all_notes = []
        
        for method in methods:
            if method == 'basic_pitch':
                notes = self.transcribe_with_basic_pitch(audio_data, sample_rate)
                all_notes.extend(notes)
            elif method == 'mt3':
                notes = self.transcribe_with_mt3(audio_data, sample_rate)
                all_notes.extend(notes)
        
        # TODO: Implement note merging and refinement logic
        # For now, just return all notes from the first method
        if all_notes:
            # Sort by start time
            all_notes.sort(key=lambda x: x['startTime'])
        
        return all_notes
    
    @staticmethod
    def _midi_to_note_name(midi_pitch: int) -> str:
        """
        Convert MIDI pitch number to note name.
        
        Args:
            midi_pitch: MIDI pitch number (0-127)
            
        Returns:
            Note name (e.g., 'C4', 'A#5')
        """
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_pitch // 12) - 1
        note = note_names[midi_pitch % 12]
        return f"{note}{octave}"
    
    @staticmethod
    def _note_name_to_midi(note_name: str) -> int:
        """
        Convert note name to MIDI pitch number.
        
        Args:
            note_name: Note name (e.g., 'C4', 'A#5')
            
        Returns:
            MIDI pitch number (0-127)
        """
        note_names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                     'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        
        # Parse note name
        if len(note_name) == 2:
            note, octave = note_name[0], int(note_name[1])
        elif len(note_name) == 3:
            note, octave = note_name[:2], int(note_name[2])
        else:
            raise ValueError(f"Invalid note name: {note_name}")
        
        midi_pitch = (octave + 1) * 12 + note_names[note]
        return midi_pitch
