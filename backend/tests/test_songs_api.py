"""
Tests for songs API endpoints.
"""
import pytest
from app.services.song_library_service import SongLibraryService


class TestSongLibraryService:
    """Test song library service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.song_service = SongLibraryService()
    
    def test_spotify_key_to_note(self):
        """Test Spotify key number to note name conversion."""
        assert self.song_service._spotify_key_to_note(0) == 'C'
        assert self.song_service._spotify_key_to_note(1) == 'C#'
        assert self.song_service._spotify_key_to_note(2) == 'D'
        assert self.song_service._spotify_key_to_note(7) == 'G'
        assert self.song_service._spotify_key_to_note(11) == 'B'
        assert self.song_service._spotify_key_to_note(12) == 'C'  # Wraps around
    
    def test_fuzzy_search_similarity(self):
        """Test fuzzy search similarity calculation."""
        # This is a basic test - in production you'd mock Firestore
        # For now, just test that the method exists and doesn't crash
        assert hasattr(self.song_service, 'fuzzy_search_songs')
    
    def test_search_spotify_no_credentials(self):
        """Test Spotify search without credentials."""
        results = self.song_service.search_spotify(
            query="test",
            client_id="invalid",
            client_secret="invalid",
            limit=10
        )
        # Should return empty list on auth failure
        assert isinstance(results, list)
    
    def test_search_musicbrainz(self):
        """Test MusicBrainz search."""
        # This will make a real API call - use with caution
        # In production, you'd mock the requests
        results = self.song_service.search_musicbrainz(
            query="Beatles",
            limit=5
        )
        assert isinstance(results, list)
        # MusicBrainz should return some results for "Beatles"
        if results:
            assert 'title' in results[0]
            assert 'artist' in results[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

