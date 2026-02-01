"""
Tests for recommendation service.
"""
import pytest
from app.services.recommendation_service import RecommendationService


class TestRecommendationService:
    """Test recommendation service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.recommendation_service = RecommendationService()
    
    def test_initialization(self):
        """Test service initialization."""
        assert self.recommendation_service is not None
    
    def test_is_adjacent_difficulty(self):
        """Test difficulty adjacency check."""
        # Adjacent levels
        assert self.recommendation_service._is_adjacent_difficulty('beginner', 'intermediate') is True
        assert self.recommendation_service._is_adjacent_difficulty('intermediate', 'advanced') is True
        assert self.recommendation_service._is_adjacent_difficulty('intermediate', 'beginner') is True
        
        # Non-adjacent levels
        assert self.recommendation_service._is_adjacent_difficulty('beginner', 'advanced') is False
        assert self.recommendation_service._is_adjacent_difficulty('beginner', 'beginner') is False
    
    def test_calculate_recommendation_score_skill_match(self):
        """Test recommendation score calculation for skill level match."""
        song_data = {
            'difficulty': 'beginner',
            'transcription': {'instruments': ['piano']},
            'genre': 'Rock',
            'favoriteCount': 5
        }
        
        score, reason = self.recommendation_service._calculate_recommendation_score(
            song_data=song_data,
            skill_level='beginner',
            primary_instrument='piano',
            practice_history=[]
        )
        
        # Should have high score for skill + instrument match
        assert score >= 0.7
        assert 'skill level' in reason.lower() or 'piano' in reason.lower()
    
    def test_calculate_recommendation_score_no_match(self):
        """Test recommendation score for poor match."""
        song_data = {
            'difficulty': 'advanced',
            'transcription': {'instruments': ['drums']},
            'genre': 'Jazz',
            'favoriteCount': 0
        }
        
        score, reason = self.recommendation_service._calculate_recommendation_score(
            song_data=song_data,
            skill_level='beginner',
            primary_instrument='piano',
            practice_history=[]
        )
        
        # Should have low score
        assert score < 0.5


class TestPracticeStreakCalculation:
    """Test practice streak calculation logic."""
    
    def test_streak_calculation_logic(self):
        """Test streak calculation with mock data."""
        # This would require mocking Firestore
        # For now, just verify the function exists
        from app.api.v1.users import calculate_practice_streak
        assert callable(calculate_practice_streak)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

