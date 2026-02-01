"""
Recommendation service for personalized song suggestions.
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized song recommendations."""
    
    def __init__(self):
        """Initialize recommendation service."""
        pass
    
    def get_recommendations(
        self,
        db,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Generate personalized song recommendations for a user.
        
        Args:
            db: Firestore client
            user_id: User ID
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended songs with scores and reasons
        """
        logger.info(f"Generating recommendations for user: {user_id}")
        
        # Get user profile
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            logger.warning(f"User {user_id} not found")
            return []
        
        user_data = user_doc.to_dict()
        preferences = user_data.get('preferences', {})
        stats = user_data.get('stats', {})
        
        skill_level = preferences.get('skillLevel', 'beginner')
        primary_instrument = preferences.get('primaryInstrument')
        
        # Get user's practice history
        practice_history = self._get_practice_history(db, user_id)
        practiced_songs = set(h.get('songId') for h in practice_history)
        
        # Get user's favorites
        favorites_ref = db.collection('user_favorites').where('userId', '==', user_id)
        favorited_songs = set(fav.to_dict().get('songId') for fav in favorites_ref.stream())
        
        # Get all public songs
        songs_ref = db.collection('songs').where('isPublic', '==', True)
        
        recommendations = []
        
        for song_doc in songs_ref.stream():
            song_data = song_doc.to_dict()
            song_id = song_data.get('songId')
            
            # Skip if already practiced or favorited
            if song_id in practiced_songs or song_id in favorited_songs:
                continue
            
            # Calculate recommendation score
            score, reason = self._calculate_recommendation_score(
                song_data,
                skill_level,
                primary_instrument,
                practice_history
            )
            
            if score > 0:
                recommendations.append({
                    'song_id': song_id,
                    'title': song_data.get('title'),
                    'artist': song_data.get('artist'),
                    'album_art': song_data.get('metadata', {}).get('albumArt'),
                    'difficulty': song_data.get('difficulty'),
                    'genre': song_data.get('genre'),
                    'duration': song_data.get('duration'),
                    'score': score,
                    'reason': reason
                })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit results
        recommendations = recommendations[:limit]
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        
        return recommendations
    
    def _calculate_recommendation_score(
        self,
        song_data: Dict,
        skill_level: str,
        primary_instrument: str,
        practice_history: List[Dict]
    ) -> tuple:
        """
        Calculate recommendation score for a song.
        
        Returns:
            Tuple of (score, reason)
        """
        score = 0.0
        reasons = []
        
        # 1. Skill level match (weight: 0.4)
        song_difficulty = song_data.get('difficulty', 'beginner')
        if song_difficulty == skill_level:
            score += 0.4
            reasons.append(f"Matches your {skill_level} skill level")
        elif self._is_adjacent_difficulty(song_difficulty, skill_level):
            score += 0.2
            reasons.append("Slightly challenging for your level")
        
        # 2. Instrument availability (weight: 0.3)
        available_instruments = song_data.get('transcription', {}).get('instruments', [])
        if primary_instrument and primary_instrument in available_instruments:
            score += 0.3
            reasons.append(f"Available for {primary_instrument}")
        elif available_instruments:
            score += 0.1
        
        # 3. Genre preference (weight: 0.2)
        # Check if user has practiced songs in this genre
        song_genre = song_data.get('genre')
        if song_genre:
            practiced_genres = [h.get('genre') for h in practice_history if h.get('genre')]
            if song_genre in practiced_genres:
                score += 0.2
                reasons.append(f"You enjoy {song_genre}")
        
        # 4. Popularity (weight: 0.1)
        favorite_count = song_data.get('favoriteCount', 0)
        if favorite_count > 10:
            score += 0.1
            reasons.append("Popular among users")
        elif favorite_count > 5:
            score += 0.05
        
        # Combine reasons
        reason = reasons[0] if reasons else "Recommended for you"
        
        return score, reason
    
    def _is_adjacent_difficulty(self, difficulty1: str, difficulty2: str) -> bool:
        """Check if two difficulty levels are adjacent."""
        levels = ['beginner', 'intermediate', 'advanced']
        try:
            idx1 = levels.index(difficulty1)
            idx2 = levels.index(difficulty2)
            return abs(idx1 - idx2) == 1
        except ValueError:
            return False
    
    def _get_practice_history(self, db, user_id: str) -> List[Dict]:
        """Get user's practice history."""
        try:
            history_ref = db.collection('practice_history').where('userId', '==', user_id).limit(50)
            
            history = []
            for hist_doc in history_ref.stream():
                hist_data = hist_doc.to_dict()
                song_id = hist_data.get('songId')
                
                # Get song details
                song_doc = db.collection('songs').document(song_id).get()
                if song_doc.exists:
                    song_data = song_doc.to_dict()
                    hist_data['genre'] = song_data.get('genre')
                
                history.append(hist_data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting practice history: {e}")
            return []

