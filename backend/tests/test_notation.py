"""
Tests for notation conversion and transposition services.
"""
import pytest
from app.services.notation_service import NotationService, NotationFormat, SargamStyle
from app.services.transposition_service import TranspositionService


class TestNotationService:
    """Test notation conversion service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.notation_service = NotationService()
        self.sample_notes = [
            {'pitch': 'C4', 'startTime': 0.0, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'D4', 'startTime': 0.5, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'E4', 'startTime': 1.0, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'F4', 'startTime': 1.5, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'G4', 'startTime': 2.0, 'duration': 0.5, 'velocity': 80},
        ]
    
    def test_convert_to_sargam_hindustani(self):
        """Test conversion to Hindustani Sargam notation."""
        result = self.notation_service.convert_to_sargam(
            self.sample_notes,
            style=SargamStyle.HINDUSTANI
        )
        
        assert len(result) == 5
        assert result[0]['note'] == 'Sa'
        assert result[1]['note'] == 'Re'
        assert result[2]['note'] == 'Ga'
        assert result[3]['note'] == 'Ma'
        assert result[4]['note'] == 'Pa'
    
    def test_convert_to_sargam_carnatic(self):
        """Test conversion to Carnatic Sargam notation."""
        result = self.notation_service.convert_to_sargam(
            self.sample_notes,
            style=SargamStyle.CARNATIC
        )
        
        assert len(result) == 5
        assert result[0]['note'] == 'S'
        assert result[1]['note'] == 'R2'
        assert result[2]['note'] == 'G2'
        assert result[3]['note'] == 'M1'
        assert result[4]['note'] == 'P'
    
    def test_convert_to_sargam_octaves(self):
        """Test Sargam octave indicators."""
        notes_with_octaves = [
            {'pitch': 'C3', 'startTime': 0.0, 'duration': 0.5, 'velocity': 80},  # Lower
            {'pitch': 'C4', 'startTime': 0.5, 'duration': 0.5, 'velocity': 80},  # Middle
            {'pitch': 'C5', 'startTime': 1.0, 'duration': 0.5, 'velocity': 80},  # Upper
        ]
        
        result = self.notation_service.convert_to_sargam(notes_with_octaves)
        
        assert result[0]['note'] == 'sa'  # Lower octave (lowercase)
        assert result[1]['note'] == 'Sa'  # Middle octave (normal)
        assert result[2]['note'] == "Sa'"  # Upper octave (apostrophe)
    
    def test_convert_to_western(self):
        """Test conversion to Western notation."""
        result = self.notation_service.convert_to_western(self.sample_notes)
        
        assert result['format'] == 'western'
        assert len(result['notes']) == 5
        assert result['notes'][0]['pitch'] == 'C4'
        assert result['notes'][0]['noteName'] == 'C'
        assert result['notes'][0]['octave'] == 4
    
    def test_convert_to_alphabetical(self):
        """Test conversion to Alphabetical notation."""
        result = self.notation_service.convert_to_alphabetical(self.sample_notes)
        
        assert len(result) == 5
        assert result[0]['note'] == 'C4'
        assert result[1]['note'] == 'D4'
        assert result[2]['note'] == 'E4'
    
    def test_convert_notes_wrapper(self):
        """Test the main convert_notes method."""
        # Test Sargam
        sargam_result = self.notation_service.convert_notes(
            self.sample_notes,
            NotationFormat.SARGAM,
            SargamStyle.HINDUSTANI
        )
        assert sargam_result['format'] == 'sargam'
        assert sargam_result['style'] == SargamStyle.HINDUSTANI
        
        # Test Western
        western_result = self.notation_service.convert_notes(
            self.sample_notes,
            NotationFormat.WESTERN
        )
        assert western_result['format'] == 'western'
        
        # Test Alphabetical
        alpha_result = self.notation_service.convert_notes(
            self.sample_notes,
            NotationFormat.ALPHABETICAL
        )
        assert alpha_result['format'] == 'alphabetical'


class TestTranspositionService:
    """Test transposition service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transposition_service = TranspositionService()
        self.sample_notes = [
            {'pitch': 'C4', 'startTime': 0.0, 'duration': 0.5, 'velocity': 80, 'pitchMidi': 60},
            {'pitch': 'E4', 'startTime': 0.5, 'duration': 0.5, 'velocity': 80, 'pitchMidi': 64},
            {'pitch': 'G4', 'startTime': 1.0, 'duration': 0.5, 'velocity': 80, 'pitchMidi': 67},
        ]
    
    def test_calculate_semitone_difference(self):
        """Test semitone difference calculation."""
        # C to D = 2 semitones
        assert self.transposition_service.calculate_semitone_difference('C', 'D') == 2
        
        # C to G = 7 semitones
        assert self.transposition_service.calculate_semitone_difference('C', 'G') == 7
        
        # G to C = -7 semitones
        assert self.transposition_service.calculate_semitone_difference('G', 'C') == -7
        
        # C to C = 0 semitones
        assert self.transposition_service.calculate_semitone_difference('C', 'C') == 0
    
    def test_transpose_pitch_up(self):
        """Test transposing pitch upward."""
        # C4 + 2 semitones = D4
        result = self.transposition_service.transpose_pitch('C4', 2)
        assert result == 'D4'
        
        # C4 + 7 semitones = G4
        result = self.transposition_service.transpose_pitch('C4', 7)
        assert result == 'G4'
        
        # B4 + 1 semitone = C5 (octave change)
        result = self.transposition_service.transpose_pitch('B4', 1)
        assert result == 'C5'
    
    def test_transpose_pitch_down(self):
        """Test transposing pitch downward."""
        # D4 - 2 semitones = C4
        result = self.transposition_service.transpose_pitch('D4', -2)
        assert result == 'C4'
        
        # C4 - 1 semitone = B3 (octave change)
        result = self.transposition_service.transpose_pitch('C4', -1)
        assert result == 'B3'
    
    def test_transpose_notes(self):
        """Test transposing a list of notes."""
        # Transpose from C to D (up 2 semitones)
        result = self.transposition_service.transpose_notes(
            self.sample_notes,
            from_key='C',
            to_key='D'
        )
        
        assert len(result) == 3
        assert result[0]['pitch'] == 'D4'
        assert result[1]['pitch'] == 'F#4'
        assert result[2]['pitch'] == 'A4'
        assert result[0]['pitchMidi'] == 62
    
    def test_transpose_reversibility(self):
        """Test Property 2.1: Transposing up and down returns original."""
        # Transpose up 5 semitones
        transposed_up = self.transposition_service.transpose_notes(
            self.sample_notes,
            from_key='C',
            to_key='F'
        )
        
        # Transpose back down 5 semitones
        transposed_back = self.transposition_service.transpose_notes(
            transposed_up,
            from_key='F',
            to_key='C'
        )
        
        # Should match original
        for orig, back in zip(self.sample_notes, transposed_back):
            assert orig['pitch'] == back['pitch']
    
    def test_transpose_octave_preservation(self):
        """Test Property 2.2: Transposing by 12 semitones preserves pitch class."""
        # Transpose up one octave (12 semitones)
        result = self.transposition_service.transpose_pitch('C4', 12)
        assert result == 'C5'
        
        result = self.transposition_service.transpose_pitch('G4', 12)
        assert result == 'G5'
        
        # Transpose down one octave
        result = self.transposition_service.transpose_pitch('C4', -12)
        assert result == 'C3'
    
    def test_validate_transposition(self):
        """Test transposition validation."""
        # Transpose and validate
        transposed = self.transposition_service.transpose_notes(
            self.sample_notes,
            from_key='C',
            to_key='G'
        )
        
        is_valid = self.transposition_service.validate_transposition(
            self.sample_notes,
            transposed,
            semitones=7
        )
        
        assert is_valid is True


class TestNotationRoundTrip:
    """Test notation format round-trip conversions (Property 1.3)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.notation_service = NotationService()
        self.sample_notes = [
            {'pitch': 'C4', 'startTime': 0.0, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'D4', 'startTime': 0.5, 'duration': 0.5, 'velocity': 80},
            {'pitch': 'E4', 'startTime': 1.0, 'duration': 0.5, 'velocity': 80},
        ]
    
    def test_alphabetical_to_western_to_alphabetical(self):
        """Test Alphabetical -> Western -> Alphabetical preserves pitches."""
        # Convert to Western
        western = self.notation_service.convert_to_western(self.sample_notes)
        
        # Convert back to Alphabetical
        alphabetical = self.notation_service.convert_to_alphabetical(western['notes'])
        
        # Check pitches match
        for orig, result in zip(self.sample_notes, alphabetical):
            assert orig['pitch'] == result['note']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

