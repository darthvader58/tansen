"""
Scale transposition service.
Handles transposing musical notes between different keys and scales.
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TranspositionService:
    """Service for transposing musical notes between keys."""
    
    # Note names in chromatic scale
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Alternative note names (flats)
    NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    
    # Major scale intervals (in semitones from root)
    MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
    
    # Minor scale intervals (natural minor)
    MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
    
    def __init__(self):
        """Initialize transposition service."""
        pass
    
    def calculate_semitone_difference(self, from_key: str, to_key: str) -> int:
        """
        Calculate semitone difference between two keys.
        
        Args:
            from_key: Source key (e.g., 'C', 'D#', 'Bb')
            to_key: Target key
            
        Returns:
            Number of semitones to transpose (can be negative)
        """
        # Normalize keys
        from_key = self._normalize_key(from_key)
        to_key = self._normalize_key(to_key)
        
        # Find positions in chromatic scale
        try:
            from_pos = self.NOTE_NAMES.index(from_key)
        except ValueError:
            from_pos = self.NOTE_NAMES_FLAT.index(from_key)
            from_key = self.NOTE_NAMES[from_pos]
        
        try:
            to_pos = self.NOTE_NAMES.index(to_key)
        except ValueError:
            to_pos = self.NOTE_NAMES_FLAT.index(to_key)
        
        # Calculate difference
        semitone_diff = to_pos - from_pos
        
        logger.info(f"Transposition: {from_key} -> {to_key} = {semitone_diff} semitones")
        return semitone_diff
    
    def transpose_pitch(self, pitch: str, semitones: int) -> str:
        """
        Transpose a single pitch by given semitones.
        
        Args:
            pitch: Original pitch (e.g., 'C4', 'A#5')
            semitones: Number of semitones to transpose
            
        Returns:
            Transposed pitch
        """
        # Parse pitch
        if len(pitch) < 2:
            return pitch
        
        if pitch[1].isdigit():
            note_name = pitch[0]
            octave = int(pitch[1])
        elif len(pitch) >= 3 and pitch[2].isdigit():
            note_name = pitch[:2]
            octave = int(pitch[2])
        else:
            return pitch
        
        # Normalize note name
        note_name = self._normalize_key(note_name)
        
        # Find position in chromatic scale
        try:
            note_pos = self.NOTE_NAMES.index(note_name)
        except ValueError:
            try:
                note_pos = self.NOTE_NAMES_FLAT.index(note_name)
                note_name = self.NOTE_NAMES[note_pos]
            except ValueError:
                return pitch
        
        # Transpose
        new_pos = note_pos + semitones
        
        # Handle octave changes
        octave_change = 0
        while new_pos < 0:
            new_pos += 12
            octave_change -= 1
        while new_pos >= 12:
            new_pos -= 12
            octave_change += 1
        
        new_note = self.NOTE_NAMES[new_pos]
        new_octave = octave + octave_change
        
        return f"{new_note}{new_octave}"
    
    def transpose_notes(
        self,
        notes: List[Dict],
        from_key: str,
        to_key: str,
        mode: str = 'major'
    ) -> List[Dict]:
        """
        Transpose a list of notes from one key to another.
        
        Args:
            notes: List of note dictionaries with 'pitch' field
            from_key: Source key
            to_key: Target key
            mode: Scale mode ('major' or 'minor')
            
        Returns:
            List of transposed notes
        """
        logger.info(f"Transposing {len(notes)} notes from {from_key} to {to_key} ({mode})")
        
        # Calculate semitone difference
        semitone_diff = self.calculate_semitone_difference(from_key, to_key)
        
        # Transpose each note
        transposed_notes = []
        for note in notes:
            original_pitch = note.get('pitch', '')
            
            if not original_pitch:
                transposed_notes.append(note.copy())
                continue
            
            transposed_pitch = self.transpose_pitch(original_pitch, semitone_diff)
            
            transposed_note = note.copy()
            transposed_note['pitch'] = transposed_pitch
            
            # Update pitchMidi if present
            if 'pitchMidi' in note:
                transposed_note['pitchMidi'] = note['pitchMidi'] + semitone_diff
            
            transposed_notes.append(transposed_note)
        
        # Apply mode adjustments if needed
        if mode == 'minor':
            transposed_notes = self._apply_minor_scale_adjustments(transposed_notes, to_key)
        
        logger.info(f"Transposition complete: {len(transposed_notes)} notes")
        return transposed_notes
    
    def _normalize_key(self, key: str) -> str:
        """
        Normalize key name (handle enharmonic equivalents).
        
        Args:
            key: Key name
            
        Returns:
            Normalized key name
        """
        # Convert flats to sharps for consistency
        flat_to_sharp = {
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        
        return flat_to_sharp.get(key, key)
    
    def _apply_minor_scale_adjustments(
        self,
        notes: List[Dict],
        key: str
    ) -> List[Dict]:
        """
        Apply minor scale adjustments to transposed notes.
        
        This is a simplified implementation. In production, you'd want
        more sophisticated harmonic analysis.
        
        Args:
            notes: Transposed notes
            key: Target key
            
        Returns:
            Adjusted notes
        """
        # For now, just return notes as-is
        # TODO: Implement proper minor scale adjustments
        return notes
    
    def validate_transposition(
        self,
        original_notes: List[Dict],
        transposed_notes: List[Dict],
        semitones: int
    ) -> bool:
        """
        Validate that transposition was performed correctly.
        
        Property: Transposing by N semitones and back by -N semitones
        should return the original notes.
        
        Args:
            original_notes: Original notes
            transposed_notes: Transposed notes
            semitones: Number of semitones transposed
            
        Returns:
            True if validation passes
        """
        if len(original_notes) != len(transposed_notes):
            return False
        
        for orig, trans in zip(original_notes, transposed_notes):
            orig_pitch = orig.get('pitch', '')
            trans_pitch = trans.get('pitch', '')
            
            if not orig_pitch or not trans_pitch:
                continue
            
            # Transpose back
            back_pitch = self.transpose_pitch(trans_pitch, -semitones)
            
            if back_pitch != orig_pitch:
                logger.warning(
                    f"Transposition validation failed: {orig_pitch} -> {trans_pitch} -> {back_pitch}"
                )
                return False
        
        return True

