"""
Song library service with external API integrations.
"""
import logging
from typing import List, Dict, Optional, Tuple
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SongLibraryService:
    """Service for managing song library and external API integrations."""
    
    def __init__(self):
        """Initialize song library service."""
        self.spotify_token = None
        self.spotify_token_expires = None
    
    def search_songs_in_firestore(
        self,
        db,
        query: str = None,
        genre: str = None,
        difficulty: str = None,
        instrument: str = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """
        Search songs in Firestore with filters.
        
        Args:
            db: Firestore client
            query: Search query for title/artist
            genre: Genre filter
            difficulty: Difficulty filter
            instrument: Instrument filter
            page: Page number (1-indexed)
            limit: Results per page
            
        Returns:
            Tuple of (songs list, total count)
        """
        logger.info(f"Searching songs: query={query}, genre={genre}, difficulty={difficulty}")
        
        # Start with base query
        songs_ref = db.collection('songs')
        
        # Apply filters
        if genre:
            songs_ref = songs_ref.where('genre', '==', genre)
        
        if difficulty:
            songs_ref = songs_ref.where('difficulty', '==', difficulty)
        
        if instrument:
            songs_ref = songs_ref.where('transcription.instruments', 'array_contains', instrument)
        
        # Only show public songs or user's own songs
        songs_ref = songs_ref.where('isPublic', '==', True)
        
        # Get total count (before pagination)
        all_docs = songs_ref.stream()
        all_songs = []
        
        for doc in all_docs:
            song_data = doc.to_dict()
            
            # Apply text search filter if query provided
            if query:
                query_lower = query.lower()
                title_lower = song_data.get('title', '').lower()
                artist_lower = song_data.get('artist', '').lower()
                
                if query_lower not in title_lower and query_lower not in artist_lower:
                    continue
            
            all_songs.append(song_data)
        
        total_count = len(all_songs)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_songs = all_songs[start_idx:end_idx]
        
        logger.info(f"Found {total_count} songs, returning page {page} ({len(paginated_songs)} songs)")
        return paginated_songs, total_count
    
    def fuzzy_search_songs(
        self,
        db,
        query: str,
        threshold: float = 0.6
    ) -> List[Dict]:
        """
        Fuzzy search for songs (simple implementation).
        
        Args:
            db: Firestore client
            query: Search query
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of matching songs
        """
        # For now, use simple substring matching
        # In production, use a proper search engine like Algolia or Elasticsearch
        songs_ref = db.collection('songs').where('isPublic', '==', True)
        
        results = []
        query_lower = query.lower()
        
        for doc in songs_ref.stream():
            song_data = doc.to_dict()
            title = song_data.get('title', '').lower()
            artist = song_data.get('artist', '').lower()
            
            # Simple fuzzy matching: check if query words are in title or artist
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in title or word in artist)
            similarity = matches / len(query_words) if query_words else 0
            
            if similarity >= threshold:
                song_data['similarity'] = similarity
                results.append(song_data)
        
        # Sort by similarity
        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return results
    
    def get_spotify_token(self, client_id: str, client_secret: str) -> Optional[str]:
        """
        Get Spotify API access token.
        
        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret
            
        Returns:
            Access token or None
        """
        # Check if we have a valid cached token
        if self.spotify_token and self.spotify_token_expires:
            if datetime.now() < self.spotify_token_expires:
                return self.spotify_token
        
        # Request new token
        try:
            auth_url = 'https://accounts.spotify.com/api/token'
            auth_response = requests.post(auth_url, {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
            })
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                self.spotify_token = auth_data['access_token']
                expires_in = auth_data.get('expires_in', 3600)
                self.spotify_token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info("Spotify token obtained successfully")
                return self.spotify_token
            else:
                logger.error(f"Failed to get Spotify token: {auth_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Spotify token: {e}")
            return None
    
    def search_spotify(
        self,
        query: str,
        client_id: str,
        client_secret: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search songs on Spotify.
        
        Args:
            query: Search query
            client_id: Spotify client ID
            client_secret: Spotify client secret
            limit: Max results
            
        Returns:
            List of song results
        """
        token = self.get_spotify_token(client_id, client_secret)
        if not token:
            logger.warning("No Spotify token available")
            return []
        
        try:
            search_url = 'https://api.spotify.com/v1/search'
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'q': query,
                'type': 'track',
                'limit': limit
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', {}).get('items', [])
                
                results = []
                for track in tracks:
                    results.append({
                        'songId': track['id'],
                        'title': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'albumArt': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'duration': track['duration_ms'] // 1000,
                        'source': 'spotify',
                        'spotifyId': track['id'],
                        'previewUrl': track.get('preview_url')
                    })
                
                logger.info(f"Found {len(results)} songs on Spotify")
                return results
            else:
                logger.error(f"Spotify search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return []
    
    def get_spotify_track_details(
        self,
        track_id: str,
        client_id: str,
        client_secret: str
    ) -> Optional[Dict]:
        """
        Get detailed track information from Spotify.
        
        Args:
            track_id: Spotify track ID
            client_id: Spotify client ID
            client_secret: Spotify client secret
            
        Returns:
            Track details or None
        """
        token = self.get_spotify_token(client_id, client_secret)
        if not token:
            return None
        
        try:
            track_url = f'https://api.spotify.com/v1/tracks/{track_id}'
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.get(track_url, headers=headers)
            
            if response.status_code == 200:
                track = response.json()
                
                # Get audio features for tempo and key
                features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
                features_response = requests.get(features_url, headers=headers)
                features = features_response.json() if features_response.status_code == 200 else {}
                
                return {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'albumArt': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'duration': track['duration_ms'] // 1000,
                    'tempo': int(features.get('tempo', 120)),
                    'key': self._spotify_key_to_note(features.get('key', 0)),
                    'timeSignature': f"{features.get('time_signature', 4)}/4",
                    'spotifyId': track['id']
                }
            else:
                logger.error(f"Failed to get Spotify track: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Spotify track details: {e}")
            return None
    
    def search_musicbrainz(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search songs on MusicBrainz.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of song results
        """
        try:
            search_url = 'https://musicbrainz.org/ws/2/recording'
            headers = {'User-Agent': 'MusicTranscriptionApp/1.0'}
            params = {
                'query': query,
                'limit': limit,
                'fmt': 'json'
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                
                results = []
                for recording in recordings:
                    artist_credit = recording.get('artist-credit', [])
                    artist = artist_credit[0]['name'] if artist_credit else 'Unknown'
                    
                    results.append({
                        'songId': recording['id'],
                        'title': recording['title'],
                        'artist': artist,
                        'duration': recording.get('length', 0) // 1000 if recording.get('length') else 0,
                        'source': 'musicbrainz',
                        'musicbrainzId': recording['id']
                    })
                
                logger.info(f"Found {len(results)} songs on MusicBrainz")
                return results
            else:
                logger.error(f"MusicBrainz search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching MusicBrainz: {e}")
            return []
    
    def get_musicbrainz_recording_details(
        self,
        recording_id: str
    ) -> Optional[Dict]:
        """
        Get detailed recording information from MusicBrainz.
        
        Args:
            recording_id: MusicBrainz recording ID
            
        Returns:
            Recording details or None
        """
        try:
            recording_url = f'https://musicbrainz.org/ws/2/recording/{recording_id}'
            headers = {'User-Agent': 'MusicTranscriptionApp/1.0'}
            params = {
                'inc': 'artists+releases',
                'fmt': 'json'
            }
            
            response = requests.get(recording_url, headers=headers, params=params)
            
            if response.status_code == 200:
                recording = response.json()
                
                artist_credit = recording.get('artist-credit', [])
                artist = artist_credit[0]['name'] if artist_credit else 'Unknown'
                
                releases = recording.get('releases', [])
                album = releases[0]['title'] if releases else None
                
                return {
                    'title': recording['title'],
                    'artist': artist,
                    'album': album,
                    'duration': recording.get('length', 0) // 1000 if recording.get('length') else 0,
                    'musicbrainzId': recording['id']
                }
            else:
                logger.error(f"Failed to get MusicBrainz recording: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting MusicBrainz recording details: {e}")
            return None
    
    @staticmethod
    def _spotify_key_to_note(key: int) -> str:
        """Convert Spotify key number to note name."""
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return keys[key % 12] if 0 <= key < 12 else 'C'

