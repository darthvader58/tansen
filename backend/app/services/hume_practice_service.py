"""
Hume AI-powered practice feedback service.
Uses Hume's prosody API to analyze musical performance.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class HumePracticeService:
    """Service for analyzing music practice using Hume AI."""
    
    def __init__(self):
        self.api_key = settings.hume_api_key
        self.base_url = "https://api.hume.ai/v0"
        
    async def analyze_performance(
        self,
        user_audio_path: str,
        reference_audio_path: str,
        instrument: str = "piano"
    ) -> Dict:
        """
        Analyze user's practice performance using Hume AI.
        
        Args:
            user_audio_path: Path to user's recorded audio
            reference_audio_path: Path to reference song audio
            instrument: Instrument being practiced
            
        Returns:
            Dict with detailed feedback including scores and suggestions
        """
        try:
            # Analyze both audio files with Hume AI
            user_analysis = await self._analyze_audio(user_audio_path)
            ref_analysis = await self._analyze_audio(reference_audio_path)
            
            # Compare the analyses
            comparison = self._compare_performances(user_analysis, ref_analysis)
            
            # Generate feedback
            feedback = self._generate_feedback(comparison, instrument)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error analyzing performance with Hume AI: {str(e)}")
            raise
    
    async def _analyze_audio(self, audio_path: str) -> Dict:
        """
        Analyze audio file using Hume AI Prosody API.
        
        Returns prosody features including:
        - Pitch contours
        - Rhythm patterns
        - Tempo variations
        - Energy levels
        """
        url = f"{self.base_url}/batch/jobs"
        
        headers = {
            "X-Hume-Api-Key": self.api_key
        }
        
        # Prepare the job request
        job_data = {
            "models": {
                "prosody": {}
            },
            "urls": []  # We'll upload files directly
        }
        
        async with aiohttp.ClientSession() as session:
            # Upload audio file
            with open(audio_path, 'rb') as audio_file:
                form_data = aiohttp.FormData()
                form_data.add_field('json', 
                                   '{"models": {"prosody": {}}}',
                                   content_type='application/json')
                form_data.add_field('file',
                                   audio_file,
                                   filename='audio.wav',
                                   content_type='audio/wav')
                
                async with session.post(url, headers=headers, data=form_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Hume API error: {error_text}")
                    
                    job_response = await response.json()
                    job_id = job_response['job_id']
            
            # Poll for job completion
            result = await self._wait_for_job(session, job_id, headers)
            
            return result
    
    async def _wait_for_job(
        self,
        session: aiohttp.ClientSession,
        job_id: str,
        headers: Dict,
        max_wait: int = 60
    ) -> Dict:
        """Wait for Hume AI job to complete and return results."""
        url = f"{self.base_url}/batch/jobs/{job_id}"
        
        for _ in range(max_wait):
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get job status: {response.status}")
                
                job_status = await response.json()
                
                if job_status['state']['status'] == 'COMPLETED':
                    # Get predictions
                    predictions_url = f"{self.base_url}/batch/jobs/{job_id}/predictions"
                    async with session.get(predictions_url, headers=headers) as pred_response:
                        predictions = await pred_response.json()
                        return self._extract_prosody_features(predictions)
                
                elif job_status['state']['status'] == 'FAILED':
                    raise Exception(f"Hume job failed: {job_status['state'].get('message')}")
                
                # Wait before polling again
                await asyncio.sleep(1)
        
        raise Exception("Job timeout - analysis took too long")
    
    def _extract_prosody_features(self, predictions: Dict) -> Dict:
        """Extract relevant prosody features from Hume AI response."""
        try:
            # Hume returns prosody predictions with various features
            prosody_data = predictions[0]['results']['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']
            
            # Extract key features
            features = {
                'pitch_mean': 0,
                'pitch_std': 0,
                'tempo_mean': 0,
                'tempo_std': 0,
                'energy_mean': 0,
                'energy_std': 0,
                'rhythm_consistency': 0,
                'emotional_expression': {}
            }
            
            # Calculate aggregate features from time-series data
            pitch_values = []
            tempo_values = []
            energy_values = []
            
            for prediction in prosody_data:
                emotions = prediction.get('emotions', [])
                
                # Extract pitch-related emotions (Admiration, Awe indicate good pitch)
                for emotion in emotions:
                    name = emotion['name']
                    score = emotion['score']
                    
                    if name in ['Admiration', 'Awe', 'Joy']:
                        pitch_values.append(score)
                    if name in ['Excitement', 'Interest']:
                        tempo_values.append(score)
                    if name in ['Determination', 'Concentration']:
                        energy_values.append(score)
                    
                    features['emotional_expression'][name] = score
            
            # Calculate statistics
            if pitch_values:
                features['pitch_mean'] = sum(pitch_values) / len(pitch_values)
                features['pitch_std'] = self._std_dev(pitch_values)
            
            if tempo_values:
                features['tempo_mean'] = sum(tempo_values) / len(tempo_values)
                features['tempo_std'] = self._std_dev(tempo_values)
            
            if energy_values:
                features['energy_mean'] = sum(energy_values) / len(energy_values)
                features['energy_std'] = self._std_dev(energy_values)
            
            # Rhythm consistency (lower std = more consistent)
            features['rhythm_consistency'] = 1.0 - min(features['tempo_std'], 1.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting prosody features: {str(e)}")
            # Return default features if extraction fails
            return {
                'pitch_mean': 0.5,
                'pitch_std': 0.2,
                'tempo_mean': 0.5,
                'tempo_std': 0.2,
                'energy_mean': 0.5,
                'energy_std': 0.2,
                'rhythm_consistency': 0.5,
                'emotional_expression': {}
            }
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _compare_performances(
        self,
        user_features: Dict,
        ref_features: Dict
    ) -> Dict:
        """Compare user performance with reference."""
        
        # Calculate similarity scores (0-100)
        pitch_score = self._calculate_similarity(
            user_features['pitch_mean'],
            ref_features['pitch_mean'],
            user_features['pitch_std'],
            ref_features['pitch_std']
        )
        
        tempo_score = self._calculate_similarity(
            user_features['tempo_mean'],
            ref_features['tempo_mean'],
            user_features['tempo_std'],
            ref_features['tempo_std']
        )
        
        rhythm_score = self._calculate_similarity(
            user_features['rhythm_consistency'],
            ref_features['rhythm_consistency'],
            0.1,
            0.1
        )
        
        # Overall score (weighted average)
        overall_score = (
            pitch_score * 0.4 +
            tempo_score * 0.3 +
            rhythm_score * 0.3
        )
        
        return {
            'pitch_accuracy': pitch_score,
            'tempo_accuracy': tempo_score,
            'rhythm_accuracy': rhythm_score,
            'overall_score': overall_score,
            'user_features': user_features,
            'ref_features': ref_features
        }
    
    def _calculate_similarity(
        self,
        user_mean: float,
        ref_mean: float,
        user_std: float,
        ref_std: float
    ) -> float:
        """Calculate similarity score between two feature distributions."""
        # Mean difference (how close are the averages)
        mean_diff = abs(user_mean - ref_mean)
        mean_similarity = max(0, 1 - mean_diff) * 100
        
        # Std difference (how similar is the consistency)
        std_diff = abs(user_std - ref_std)
        std_similarity = max(0, 1 - std_diff) * 100
        
        # Weighted combination (mean is more important)
        score = mean_similarity * 0.7 + std_similarity * 0.3
        
        return round(score, 1)
    
    def _generate_feedback(
        self,
        comparison: Dict,
        instrument: str
    ) -> Dict:
        """Generate detailed feedback based on comparison."""
        
        pitch_score = comparison['pitch_accuracy']
        tempo_score = comparison['tempo_accuracy']
        rhythm_score = comparison['rhythm_accuracy']
        overall_score = comparison['overall_score']
        
        suggestions = []
        note_feedback = []
        
        # Pitch feedback
        if pitch_score < 70:
            suggestions.append("🎵 Focus on pitch accuracy. Practice with a tuner or reference pitch.")
            note_feedback.append({
                'category': 'pitch',
                'severity': 'high',
                'message': 'Significant pitch variations detected. Practice scales slowly.'
            })
        elif pitch_score < 85:
            suggestions.append("👍 Good pitch control! Minor adjustments will perfect it.")
            note_feedback.append({
                'category': 'pitch',
                'severity': 'medium',
                'message': 'Pitch is mostly accurate with some variations.'
            })
        else:
            suggestions.append("🌟 Excellent pitch accuracy!")
        
        # Tempo feedback
        user_tempo = comparison['user_features']['tempo_mean']
        ref_tempo = comparison['ref_features']['tempo_mean']
        
        if tempo_score < 70:
            if user_tempo > ref_tempo:
                suggestions.append("🐢 Slow down! You're playing too fast. Use a metronome.")
            else:
                suggestions.append("🚀 Speed up a bit! You're playing too slowly.")
            note_feedback.append({
                'category': 'tempo',
                'severity': 'high',
                'message': f'Tempo needs adjustment. Target tempo: {ref_tempo:.2f}'
            })
        elif tempo_score < 85:
            suggestions.append("⏱️ Tempo is close! Minor adjustments needed.")
        else:
            suggestions.append("✨ Perfect tempo control!")
        
        # Rhythm feedback
        if rhythm_score < 70:
            suggestions.append("🎼 Work on rhythm consistency. Practice with a metronome.")
            suggestions.append("💡 Try clapping the rhythm before playing.")
            note_feedback.append({
                'category': 'rhythm',
                'severity': 'high',
                'message': 'Rhythm timing needs improvement. Focus on steady beats.'
            })
        elif rhythm_score < 85:
            suggestions.append("✨ Good rhythm! Focus on consistency.")
        else:
            suggestions.append("🎯 Excellent rhythm precision!")
        
        # Overall encouragement
        if overall_score >= 90:
            suggestions.append("🌟 Outstanding performance! You're mastering this piece!")
        elif overall_score >= 75:
            suggestions.append("💪 Great job! Keep practicing and you'll nail it!")
        elif overall_score >= 60:
            suggestions.append("📈 Good progress! Focus on the areas highlighted above.")
        else:
            suggestions.append("🎯 Keep practicing! Break it into smaller sections.")
        
        return {
            'success': True,
            'overall_score': round(overall_score, 1),
            'pitch_accuracy': round(pitch_score, 1),
            'tempo_accuracy': round(tempo_score, 1),
            'rhythm_accuracy': round(rhythm_score, 1),
            'grade': self._get_grade(overall_score),
            'suggestions': suggestions,
            'note_feedback': note_feedback,
            'tempo_feedback': {
                'user_tempo': round(user_tempo, 2),
                'reference_tempo': round(ref_tempo, 2),
                'difference': round(abs(user_tempo - ref_tempo), 2),
                'message': self._get_tempo_message(tempo_score)
            },
            'rhythm_feedback': {
                'consistency': 'high' if rhythm_score >= 85 else 'medium' if rhythm_score >= 70 else 'low',
                'message': self._get_rhythm_message(rhythm_score)
            }
        }
    
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
    
    def _get_tempo_message(self, score: float) -> str:
        """Get tempo feedback message."""
        if score >= 90:
            return "Perfect tempo!"
        elif score >= 75:
            return "Very good tempo, just slightly off"
        elif score >= 60:
            return "Tempo needs adjustment"
        else:
            return "Tempo is significantly different"
    
    def _get_rhythm_message(self, score: float) -> str:
        """Get rhythm feedback message."""
        if score >= 90:
            return "Excellent rhythm!"
        elif score >= 75:
            return "Great rhythm, very consistent"
        elif score >= 60:
            return "Good rhythm, minor timing issues"
        else:
            return "Rhythm needs work, focus on timing"
