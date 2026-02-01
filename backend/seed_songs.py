"""
Seed script to populate initial song library.
"""
import os
import sys
from datetime import datetime, timezone
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.firebase import initialize_firebase, get_firestore_client
from app.services.song_library_service import SongLibraryService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Sample songs to seed (popular songs for learning)
SEED_SONGS = [
    {
        'title': 'Imagine',
        'artist': 'John Lennon',
        'album': 'Imagine',
        'duration': 183,
        'genre': 'Rock',
        'difficulty': 'beginner',
        'originalKey': 'C',
        'tempo': 76,
        'timeSignature': '4/4',
    },
    {
        'title': 'Let It Be',
        'artist': 'The Beatles',
        'album': 'Let It Be',
        'duration': 243,
        'genre': 'Rock',
        'difficulty': 'beginner',
        'originalKey': 'C',
        'tempo': 73,
        'timeSignature': '4/4',
    },
    {
        'title': 'Hotel California',
        'artist': 'Eagles',
        'album': 'Hotel California',
        'duration': 391,
        'genre': 'Rock',
        'difficulty': 'intermediate',
        'originalKey': 'Bm',
        'tempo': 74,
        'timeSignature': '4/4',
    },
    {
        'title': 'Bohemian Rhapsody',
        'artist': 'Queen',
        'album': 'A Night at the Opera',
        'duration': 354,
        'genre': 'Rock',
        'difficulty': 'advanced',
        'originalKey': 'Bb',
        'tempo': 72,
        'timeSignature': '4/4',
    },
    {
        'title': 'Stairway to Heaven',
        'artist': 'Led Zeppelin',
        'album': 'Led Zeppelin IV',
        'duration': 482,
        'genre': 'Rock',
        'difficulty': 'advanced',
        'originalKey': 'Am',
        'tempo': 82,
        'timeSignature': '4/4',
    },
    {
        'title': 'Yesterday',
        'artist': 'The Beatles',
        'album': 'Help!',
        'duration': 125,
        'genre': 'Pop',
        'difficulty': 'beginner',
        'originalKey': 'F',
        'tempo': 97,
        'timeSignature': '4/4',
    },
    {
        'title': 'Wonderwall',
        'artist': 'Oasis',
        'album': '(What\'s the Story) Morning Glory?',
        'duration': 258,
        'genre': 'Rock',
        'difficulty': 'beginner',
        'originalKey': 'F#m',
        'tempo': 87,
        'timeSignature': '4/4',
    },
    {
        'title': 'Hallelujah',
        'artist': 'Leonard Cohen',
        'album': 'Various Positions',
        'duration': 272,
        'genre': 'Folk',
        'difficulty': 'intermediate',
        'originalKey': 'C',
        'tempo': 60,
        'timeSignature': '6/8',
    },
    {
        'title': 'Sweet Child O\' Mine',
        'artist': 'Guns N\' Roses',
        'album': 'Appetite for Destruction',
        'duration': 356,
        'genre': 'Rock',
        'difficulty': 'intermediate',
        'originalKey': 'D',
        'tempo': 125,
        'timeSignature': '4/4',
    },
    {
        'title': 'Smells Like Teen Spirit',
        'artist': 'Nirvana',
        'album': 'Nevermind',
        'duration': 301,
        'genre': 'Grunge',
        'difficulty': 'intermediate',
        'originalKey': 'F',
        'tempo': 116,
        'timeSignature': '4/4',
    },
    # Indian Classical Songs
    {
        'title': 'Raag Yaman',
        'artist': 'Pandit Ravi Shankar',
        'album': 'Classical Ragas',
        'duration': 420,
        'genre': 'Indian Classical',
        'difficulty': 'advanced',
        'originalKey': 'C',
        'tempo': 80,
        'timeSignature': '4/4',
    },
    {
        'title': 'Raag Bhairav',
        'artist': 'Ustad Bismillah Khan',
        'album': 'Morning Ragas',
        'duration': 380,
        'genre': 'Indian Classical',
        'difficulty': 'advanced',
        'originalKey': 'C',
        'tempo': 70,
        'timeSignature': '4/4',
    },
    {
        'title': 'Vande Mataram',
        'artist': 'A.R. Rahman',
        'album': 'Maa Tujhe Salaam',
        'duration': 312,
        'genre': 'Patriotic',
        'difficulty': 'intermediate',
        'originalKey': 'D',
        'tempo': 90,
        'timeSignature': '4/4',
    },
    {
        'title': 'Tum Hi Ho',
        'artist': 'Arijit Singh',
        'album': 'Aashiqui 2',
        'duration': 262,
        'genre': 'Bollywood',
        'difficulty': 'beginner',
        'originalKey': 'C',
        'tempo': 75,
        'timeSignature': '4/4',
    },
    {
        'title': 'Kun Faya Kun',
        'artist': 'A.R. Rahman',
        'album': 'Rockstar',
        'duration': 458,
        'genre': 'Sufi',
        'difficulty': 'intermediate',
        'originalKey': 'D',
        'tempo': 85,
        'timeSignature': '4/4',
    },
]


def seed_songs():
    """Seed initial song library."""
    print("🌱 Seeding song library...")
    
    try:
        # Initialize Firebase
        initialize_firebase()
        
        db = get_firestore_client()
        song_service = SongLibraryService()
        
        # Get Spotify credentials
        spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        seeded_count = 0
        
        for song_data in SEED_SONGS:
            song_id = str(uuid.uuid4())
            
            # Try to enrich with Spotify data
            spotify_data = None
            if spotify_client_id and spotify_client_secret:
                query = f"{song_data['title']} {song_data['artist']}"
                spotify_results = song_service.search_spotify(
                    query=query,
                    client_id=spotify_client_id,
                    client_secret=spotify_client_secret,
                    limit=1
                )
                
                if spotify_results:
                    spotify_data = spotify_results[0]
                    print(f"  ✓ Found on Spotify: {song_data['title']}")
            
            # Create song document
            song_doc = {
                'songId': song_id,
                'title': song_data['title'],
                'artist': song_data['artist'],
                'album': song_data.get('album'),
                'duration': song_data['duration'],
                'genre': song_data.get('genre'),
                'difficulty': song_data.get('difficulty', 'beginner'),
                'originalKey': song_data.get('originalKey', 'C'),
                'tempo': song_data.get('tempo', 120),
                'timeSignature': song_data.get('timeSignature', '4/4'),
                'metadata': {
                    'source': 'library',
                    'spotifyId': spotify_data.get('spotifyId') if spotify_data else None,
                    'albumArt': spotify_data.get('albumArt') if spotify_data else None,
                },
                'audioFiles': {
                    'original': None,
                    'instrumental': None,
                },
                'transcription': {
                    'status': 'pending',
                    'instruments': [],
                },
                'createdBy': 'system',
                'createdAt': datetime.now(timezone.utc),
                'isPublic': True,
                'downloadCount': 0,
                'favoriteCount': 0,
            }
            
            # Add to Firestore
            db.collection('songs').document(song_id).set(song_doc)
            seeded_count += 1
            print(f"  ✓ Seeded: {song_data['title']} by {song_data['artist']}")
        
        print(f"\n✅ Successfully seeded {seeded_count} songs!")
        
    except Exception as e:
        print(f"\n❌ Error seeding songs: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    seed_songs()

