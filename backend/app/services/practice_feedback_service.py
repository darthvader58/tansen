"""
AI-powered practice feedback service that compares user's performance
with the original song and provides detailed feedback on notes, tempo, and rhythm.
"""
import numpy as np
import librosa
from typing import Dict, List, Tuple, Optional
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import tensorflow as tf

class PracticeFeedbackService:
    def __init__(self):
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model only when needed."""
        if self._model is None:
            self._model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))
        return self._model
    
    def analyze_performance(
        self,
        user_audio_path: str,
        reference_audio_path: str,
        instrument: str = "piano"
    ) -> Dict:
        """
        Compare user's performance with reference audio and provide feedback.
        
        Returns:
            Dict with feedback including:
            - overall_score: 0-100
            - pitch_accuracy: 0-100
            - tempo_accuracy: 0-100
            - rhythm_accuracy: 0-100
            - note_feedback: List of specific note corrections
            - tempo_feedback: Tempo comparison
            - suggestions: List of improvement suggestions
        """
        # Load both audio files
        user_audio, user_sr = librosa.load(user_audio_path, sr=22050, mono=True)
        ref_audio, ref_sr = librosa.load(reference_audio_path, sr=22050, mono=True)
        
        # Transcribe both performances
        user_notes = self._transcribe_audio(user_audio, user_sr)
        ref_notes = self._transcribe_audio(ref_audio, ref_sr)
        
        # Analyze pitch accuracy
        pitch_score, pitch_feedback = self._analyze_pitch(user_notes, ref_notes)
        
        # Analyze tempo
        tempo_score, tempo_feedback = self._analyze_tempo(user_audio, ref_audio, user_sr, ref_sr)
        
        # Analyze rhythm
        rhythm_score, rhythm_feedback = self._analyze_rhythm(user_notes, ref_notes)
        
        # Calculate overall score
        overall_score = (pitch_score * 0.4 + tempo_score * 0.3 + rhythm_score * 0.3)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            pitch_score, tempo_score, rhythm_score,
            pitch_feedback, tempo_feedback, rhythm_feedback
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "pitch_accuracy": round(pitch_score, 1),
            "tempo_accuracy": round(tempo_score, 1),
            "rhythm_accuracy": round(rhythm_score, 1),
            "note_feedback": pitch_feedback,
            "tempo_feedback": tempo_feedback,
            "rhythm_feedback": rhythm_feedback,
            "suggestions": suggestions,
            "grade": self._get_grade(overall_score)
        }
    
    def _transcribe_audio(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """Transcribe audio to notes using Basic Pitch."""
        model_output, midi_data, note_events = predict(
            audio,
            sr,
            model_or_model_path=self.model
        )
        
        notes = []
        for note in note_events:
            notes.append({
                'start_time': note[0],
                'end_time': note[1],
                'pitch': note[2],
                'velocity': note[3],
                'duration': note[1] - note[0]
            })
        
        return sorted(notes, key=lambda x: x['start_time'])
    
    def _analyze_pitch(
        self,
        user_notes: List[Dict],
        ref_notes: List[Dict]
    ) -> Tuple[float, List[Dict]]:
        """
        Analyze pitch accuracy by comparing user notes with reference.
        Returns score (0-100) and detailed feedback.
        """
        if not ref_notes:
            return 100.0, []
        
        feedback = []
        correct_notes = 0
        total_notes = len(ref_notes)
        
        # Match user notes to reference notes by time
        for ref_note in ref_notes:
            ref_time = ref_note['start_time']
            ref_pitch = ref_note['pitch']
            
            # Find closest user note in time
            closest_user_note = self._find_closest_note(user_notes, ref_time)
            
            if closest_user_note:
                user_pitch = closest_user_note['pitch']
                pitch_diff = abs(user_pitch - ref_pitch)
                
                if pitch_diff == 0:
                    correct_notes += 1
                elif pitch_diff <= 2:  # Within 2 semitones
                    correct_notes += 0.5
                    feedback.append({
                        'time': ref_time,
                        'expected_pitch': ref_pitch,
                        'played_pitch': user_pitch,
                        'error': 'slightly_off',
                        'message': f'Note at {ref_time:.2f}s is {pitch_diff} semitone(s) off'
                    })
                else:
                    feedback.append({
                        'time': ref_time,
                        'expected_pitch': ref_pitch,
                        'played_pitch': user_pitch,
                        'error': 'wrong_note',
                        'message': f'Wrong note at {ref_time:.2f}s. Expected {self._pitch_to_note(ref_pitch)}, played {self._pitch_to_note(user_pitch)}'
                    })
            else:
                feedback.append({
                    'time': ref_time,
                    'expected_pitch': ref_pitch,
                    'played_pitch': None,
                    'error': 'missed_note',
                    'message': f'Missed note {self._pitch_to_note(ref_pitch)} at {ref_time:.2f}s'
                })
        
        score = (correct_notes / total_notes) * 100 if total_notes > 0 else 100
        return score, feedback[:10]  # Return top 10 issues
    
    def _analyze_tempo(
        self,
        user_audio: np.ndarray,
        ref_audio: np.ndarray,
        user_sr: int,
        ref_sr: int
    ) -> Tuple[float, Dict]:
        """Analyze tempo accuracy."""
        # Detect tempo for both
        user_tempo, _ = librosa.beat.beat_track(y=user_audio, sr=user_sr)
        ref_tempo, _ = librosa.beat.beat_track(y=ref_audio, sr=ref_sr)
        
        tempo_diff = abs(user_tempo - ref_tempo)
        tempo_ratio = tempo_diff / ref_tempo if ref_tempo > 0 else 0
        
        # Score based on tempo difference
        if tempo_ratio < 0.05:  # Within 5%
            score = 100
            feedback_msg = "Perfect tempo!"
        elif tempo_ratio < 0.10:  # Within 10%
            score = 90
            feedback_msg = "Very good tempo, just slightly off"
        elif tempo_ratio < 0.20:  # Within 20%
            score = 70
            feedback_msg = "Tempo needs adjustment"
        else:
            score = 50
            feedback_msg = "Tempo is significantly different"
        
        feedback = {
            'user_tempo': float(user_tempo),
            'reference_tempo': float(ref_tempo),
            'difference': float(tempo_diff),
            'percentage_off': round(tempo_ratio * 100, 1),
            'message': feedback_msg
        }
        
        return score, feedback
    
    def _analyze_rhythm(
        self,
        user_notes: List[Dict],
        ref_notes: List[Dict]
    ) -> Tuple[float, Dict]:
        """Analyze rhythm accuracy (timing of notes)."""
        if not ref_notes:
            return 100.0, {}
        
        timing_errors = []
        
        for ref_note in ref_notes:
            ref_time = ref_note['start_time']
            closest_user_note = self._find_closest_note(user_notes, ref_time)
            
            if closest_user_note:
                time_diff = abs(closest_user_note['start_time'] - ref_time)
                timing_errors.append(time_diff)
        
        if not timing_errors:
            return 50.0, {'message': 'Many notes were missed'}
        
        avg_timing_error = np.mean(timing_errors)
        
        # Score based on average timing error
        if avg_timing_error < 0.05:  # Within 50ms
            score = 100
            feedback_msg = "Excellent rhythm!"
        elif avg_timing_error < 0.1:  # Within 100ms
            score = 90
            feedback_msg = "Great rhythm, very consistent"
        elif avg_timing_error < 0.2:  # Within 200ms
            score = 75
            feedback_msg = "Good rhythm, minor timing issues"
        else:
            score = 60
            feedback_msg = "Rhythm needs work, focus on timing"
        
        feedback = {
            'average_timing_error': round(avg_timing_error * 1000, 1),  # in ms
            'message': feedback_msg,
            'consistency': 'high' if avg_timing_error < 0.1 else 'medium' if avg_timing_error < 0.2 else 'low'
        }
        
        return score, feedback
    
    def _find_closest_note(
        self,
        notes: List[Dict],
        target_time: float,
        max_distance: float = 0.5
    ) -> Optional[Dict]:
        """Find the note closest to target time within max_distance."""
        closest = None
        min_distance = max_distance
        
        for note in notes:
            distance = abs(note['start_time'] - target_time)
            if distance < min_distance:
                min_distance = distance
                closest = note
        
        return closest
    
    def _pitch_to_note(self, midi_pitch: int) -> str:
        """Convert MIDI pitch to note name."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_pitch // 12) - 1
        note = notes[midi_pitch % 12]
        return f"{note}{octave}"
    
    def _generate_suggestions(
        self,
        pitch_score: float,
        tempo_score: float,
        rhythm_score: float,
        pitch_feedback: List[Dict],
        tempo_feedback: Dict,
        rhythm_feedback: Dict
    ) -> List[str]:
        """Generate personalized practice suggestions."""
        suggestions = []
        
        # Pitch suggestions
        if pitch_score < 70:
            suggestions.append("🎵 Focus on hitting the correct notes. Practice slowly and use a reference pitch.")
            if pitch_feedback:
                wrong_notes = [f for f in pitch_feedback if f['error'] == 'wrong_note']
                if wrong_notes:
                    suggestions.append(f"⚠️ You played {len(wrong_notes)} wrong notes. Review the notation carefully.")
        elif pitch_score < 85:
            suggestions.append("👍 Good pitch accuracy! A bit more practice will make it perfect.")
        
        # Tempo suggestions
        if tempo_score < 70:
            if tempo_feedback.get('user_tempo', 0) > tempo_feedback.get('reference_tempo', 0):
                suggestions.append("🐢 Slow down! You're playing too fast. Use a metronome to maintain steady tempo.")
            else:
                suggestions.append("🚀 Speed up a bit! You're playing too slowly. Practice with a metronome.")
        elif tempo_score < 85:
            suggestions.append("⏱️ Tempo is close! Minor adjustments will perfect your timing.")
        
        # Rhythm suggestions
        if rhythm_score < 70:
            suggestions.append("🎼 Work on your rhythm. Practice with a metronome and count beats out loud.")
            suggestions.append("💡 Try clapping the rhythm first before playing the notes.")
        elif rhythm_score < 85:
            suggestions.append("✨ Rhythm is good! Focus on consistency in your timing.")
        
        # Overall encouragement
        overall = (pitch_score + tempo_score + rhythm_score) / 3
        if overall >= 90:
            suggestions.append("🌟 Excellent performance! You're mastering this piece!")
        elif overall >= 75:
            suggestions.append("💪 Great job! Keep practicing and you'll nail it soon!")
        elif overall >= 60:
            suggestions.append("📈 Good progress! Focus on the areas highlighted above.")
        else:
            suggestions.append("🎯 Keep practicing! Break the piece into smaller sections and master each one.")
        
        return suggestions
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        else:
            return "D"
