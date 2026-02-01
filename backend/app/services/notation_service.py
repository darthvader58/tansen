"""
Notation conversion service.
Converts transcriptions to different notation formats: Sargam, Western, Alphabetical.
"""
import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class NotationFormat(str, Enum):
    """Supported notation formats."""
    SARGAM = "sargam"
    WESTERN = "western"
    ALPHABETICAL = "alphabetical"


class SargamStyle(str, Enum):
    """Sargam notation styles."""
    HINDUSTANI = "hindustani"
    CARNATIC = "carnatic"


class NotationService:
    """Service for converting transcriptions to different notation formats."""
    
    # Sargam mappings
    HINDUSTANI_SARGAM_MAP = {
        'C': 'Sa', 'C#': 'Re♭', 'D': 'Re', 'D#': 'Ga♭',
        'E': 'Ga', 'F': 'Ma', 'F#': 'Ma♯',
        'G': 'Pa', 'G#': 'Dha♭', 'A': 'Dha', 'A#': 'Ni♭', 'B': 'Ni'
    }
    
    CARNATIC_SARGAM_MAP = {
        'C': 'S', 'C#': 'R1', 'D': 'R2', 'D#': 'G1',
        'E': 'G2', 'F': 'M1', 'F#': 'M2',
        'G': 'P', 'G#': 'D1', 'A': 'D2', 'A#': 'N1', 'B': 'N2'
    }
    
    def __init__(self):
        """Initialize notation service."""
        pass
    
    def convert_to_sargam(
        self,
        notes: List[Dict],
        style: SargamStyle = SargamStyle.HINDUSTANI,
        base_key: str = 'C'
    ) -> List[Dict]:
        """
        Convert notes to Sargam notation.
        
        Args:
            notes: List of note dictionaries with pitch, startTime, duration, velocity
            style: Sargam style (hindustani or carnatic)
            base_key: Base key for Sa (default: C)
            
        Returns:
            List of Sargam notes
        """
        logger.info(f"Converting {len(notes)} notes to {style} Sargam notation")
        
        sargam_map = (self.HINDUSTANI_SARGAM_MAP if style == SargamStyle.HINDUSTANI 
                     else self.CARNATIC_SARGAM_MAP)
        
        sargam_notes = []
        
        for note in notes:
            pitch = note.get('pitch', '')
            
            # Parse pitch (e.g., 'C4' -> note='C', octave=4)
            if len(pitch) < 2:
                continue
                
            if pitch[1].isdigit():
                note_name = pitch[0]
                octave = int(pitch[1])
            elif len(pitch) >= 3 and pitch[2].isdigit():
                note_name = pitch[:2]
                octave = int(pitch[2])
            else:
                continue
            
            # Get Sargam note
            sargam_note = sargam_map.get(note_name, 'Sa')
            
            # Add octave indicators
            # Octave 4 is Madhya (middle), no modifier
            # Octave < 4 is Mandra (lower), use lowercase
            # Octave > 4 is Taar (upper), add apostrophe
            if octave < 4:
                if style == SargamStyle.HINDUSTANI:
                    sargam_note = sargam_note.lower()
                else:
                    sargam_note = sargam_note.lower()
            elif octave > 4:
                sargam_note = sargam_note + "'"
            
            sargam_notes.append({
                'note': sargam_note,
                'startTime': note.get('startTime', 0),
                'duration': note.get('duration', 0),
                'velocity': note.get('velocity', 64)
            })
        
        logger.info(f"Converted to {len(sargam_notes)} Sargam notes")
        return sargam_notes
    
    def convert_to_western(
        self,
        notes: List[Dict]
    ) -> Dict:
        """
        Convert notes to Western notation format (MusicXML-like structure).
        
        Args:
            notes: List of note dictionaries
            
        Returns:
            Western notation data structure
        """
        logger.info(f"Converting {len(notes)} notes to Western notation")
        
        # For now, return a simplified structure
        # In production, you'd use music21 to generate proper MusicXML
        western_notes = []
        
        for note in notes:
            pitch = note.get('pitch', '')
            
            # Parse pitch
            if len(pitch) < 2:
                continue
            
            if pitch[1].isdigit():
                note_name = pitch[0]
                octave = int(pitch[1])
            elif len(pitch) >= 3 and pitch[2].isdigit():
                note_name = pitch[:2]
                octave = int(pitch[2])
            else:
                continue
            
            western_notes.append({
                'pitch': pitch,
                'noteName': note_name,
                'octave': octave,
                'startTime': note.get('startTime', 0),
                'duration': note.get('duration', 0),
                'velocity': note.get('velocity', 64)
            })
        
        logger.info(f"Converted to {len(western_notes)} Western notes")
        
        return {
            'format': 'western',
            'notes': western_notes,
            'timeSignature': '4/4',
            'keySignature': 'C'
        }
    
    def convert_to_alphabetical(
        self,
        notes: List[Dict]
    ) -> List[Dict]:
        """
        Convert notes to Alphabetical notation (simple note names).
        
        Args:
            notes: List of note dictionaries
            
        Returns:
            List of alphabetical notes
        """
        logger.info(f"Converting {len(notes)} notes to Alphabetical notation")
        
        alphabetical_notes = []
        
        for note in notes:
            pitch = note.get('pitch', '')
            
            alphabetical_notes.append({
                'note': pitch,  # e.g., 'C4', 'A#5'
                'startTime': note.get('startTime', 0),
                'duration': note.get('duration', 0),
                'velocity': note.get('velocity', 64)
            })
        
        logger.info(f"Converted to {len(alphabetical_notes)} Alphabetical notes")
        return alphabetical_notes
    
    def convert_notes(
        self,
        notes: List[Dict],
        format: NotationFormat,
        sargam_style: SargamStyle = SargamStyle.HINDUSTANI
    ) -> Dict:
        """
        Convert notes to specified format.
        
        Args:
            notes: List of note dictionaries
            format: Target notation format
            sargam_style: Sargam style (if format is sargam)
            
        Returns:
            Converted notation data
        """
        if format == NotationFormat.SARGAM:
            return {
                'format': 'sargam',
                'style': sargam_style,
                'notes': self.convert_to_sargam(notes, sargam_style)
            }
        elif format == NotationFormat.WESTERN:
            return self.convert_to_western(notes)
        elif format == NotationFormat.ALPHABETICAL:
            return {
                'format': 'alphabetical',
                'notes': self.convert_to_alphabetical(notes)
            }
        else:
            raise ValueError(f"Unsupported notation format: {format}")

