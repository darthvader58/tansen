# Music Learning & AI Transcription App - Design Document

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer (Flutter)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Mobile     │  │     Web      │  │   Tablet     │      │
│  │  (iOS/Android)│  │   Browser    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                          │
│              (Python FastAPI/Flask Backend)                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────┐
│   Firebase   │  │  AI/ML Services  │  │  External   │
│   Services   │  │                  │  │    APIs     │
│              │  │  - Basic Pitch   │  │             │
│ - Auth       │  │  - MT3           │  │ - YouTube   │
│ - Firestore  │  │  - Demucs        │  │ - Spotify   │
│ - Storage    │  │  - Essentia      │  │ - MusicBrainz│
└──────────────┘  └──────────────────┘  └─────────────┘
```

### 1.2 Technology Stack Details

**Frontend (Flutter)**
- Framework: Flutter 3.x
- State Management: Provider or Riverpod
- HTTP Client: dio
- Local Storage: sqflite (offline data), shared_preferences (settings)
- Audio Playback: just_audio
- Audio Recording: record
- File Picker: file_picker

**Backend (Python)**
- Framework: FastAPI (async support, automatic API docs)
- Web Server: Uvicorn
- Task Queue: Celery with Redis
- Audio Processing: librosa, soundfile, pydub
- AI/ML Libraries: basic-pitch, demucs, essentia, music21, mingus
- YouTube Download: yt-dlp
- API Clients: spotipy (Spotify), musicbrainzngs (MusicBrainz)

**Database & Storage**
- Primary Database: Firebase Firestore (NoSQL)
- File Storage: Firebase Storage
- Cache: Redis (for rate limiting, session management, job queues)

**Authentication**
- Firebase Authentication with Google OAuth 2.0

**Deployment**
- Backend: Cloud Run, Heroku, or Railway (containerized)
- Frontend: Firebase Hosting (web), App Store/Play Store (mobile)
- Task Workers: Separate container instances for Celery workers

## 2. Data Models

### 2.1 Firestore Collections

#### Users Collection
```json
{
  "userId": "string (Firebase UID)",
  "email": "string",
  "displayName": "string",
  "photoURL": "string",
  "createdAt": "timestamp",
  "lastLoginAt": "timestamp",
  "preferences": {
    "skillLevel": "beginner|intermediate|advanced",
    "primaryInstrument": "string",
    "secondaryInstruments": ["string"],
    "notationFormat": "sargam|western|alphabetical",
    "sargamStyle": "hindustani|carnatic",
    "theme": "light|dark|system"
  },
  "stats": {
    "totalPracticeTime": "number (minutes)",
    "songsLearned": "number",
    "currentStreak": "number (days)",
    "longestStreak": "number (days)"
  },
  "rateLimits": {
    "transcriptionsToday": "number",
    "lastTranscriptionReset": "timestamp",
    "activeJobs": "number"
  }
}
```

#### Songs Collection
```json
{
  "songId": "string (UUID)",
  "title": "string",
  "artist": "string",
  "album": "string",
  "duration": "number (seconds)",
  "genre": "string",
  "difficulty": "beginner|intermediate|advanced",
  "originalKey": "string (e.g., 'C', 'Am')",
  "tempo": "number (BPM)",
  "timeSignature": "string (e.g., '4/4')",
  "metadata": {
    "spotifyId": "string",
    "youtubeId": "string",
    "musicbrainzId": "string",
    "albumArt": "string (URL)",
    "source": "library|user_upload|youtube|spotify"
  },
  "audioFiles": {
    "original": "string (Firebase Storage path)",
    "instrumental": "string (Firebase Storage path)",
    "separated": {
      "vocals": "string",
      "drums": "string",
      "bass": "string",
      "other": "string"
    }
  },
  "transcription": {
    "status": "pending|processing|completed|failed",
    "processedAt": "timestamp",
    "instruments": ["piano", "guitar", "bass", "drums", "vocals", "violin", "saxophone"]
  },
  "createdBy": "string (userId)",
  "createdAt": "timestamp",
  "isPublic": "boolean",
  "downloadCount": "number",
  "favoriteCount": "number"
}
```

#### Transcriptions Collection
```json
{
  "transcriptionId": "string (UUID)",
  "songId": "string (reference to Songs)",
  "userId": "string (reference to Users)",
  "instrument": "string",
  "notationData": {
    "notes": [
      {
        "pitch": "string (e.g., 'C4', 'Sa')",
        "startTime": "number (seconds)",
        "duration": "number (seconds)",
        "velocity": "number (0-127)"
      }
    ],
    "chords": [
      {
        "name": "string (e.g., 'Cmaj7')",
        "startTime": "number",
        "duration": "number"
      }
    ]
  },
  "formats": {
    "sargam": "string (Firebase Storage path - JSON)",
    "western": "string (MusicXML path)",
    "alphabetical": "string (JSON path)",
    "midi": "string (MIDI file path)"
  },
  "createdAt": "timestamp",
  "processingTime": "number (seconds)"
}
```

#### UserFavorites Collection
```json
{
  "favoriteId": "string (userId_songId)",
  "userId": "string",
  "songId": "string",
  "addedAt": "timestamp"
}
```

#### PracticeHistory Collection
```json
{
  "historyId": "string (UUID)",
  "userId": "string",
  "songId": "string",
  "instrument": "string",
  "practiceDate": "timestamp",
  "duration": "number (minutes)",
  "notationFormat": "string",
  "scale": "string",
  "completionPercentage": "number (0-100)"
}
```

#### OfflineDownloads Collection
```json
{
  "downloadId": "string (userId_songId)",
  "userId": "string",
  "songId": "string",
  "downloadedAt": "timestamp",
  "fileSize": "number (bytes)",
  "localPath": "string (device-specific)",
  "includesAudio": "boolean",
  "includesNotations": ["sargam", "western", "alphabetical"]
}
```

### 2.2 Redis Cache Structure

**Rate Limiting Keys**
- `rate_limit:transcription:{userId}` → List of timestamps (last 24h)
- `active_jobs:{userId}` → Set of job IDs

**Session Cache**
- `session:{sessionId}` → User session data (TTL: 7 days)

**Job Queue**
- `celery:transcription_queue` → Pending transcription jobs
- `job_status:{jobId}` → Job progress and status

## 3. API Design

### 3.1 Authentication Endpoints

**POST /api/v1/auth/google**
- Description: Authenticate user with Google OAuth token
- Request Body:
```json
{
  "idToken": "string"
}
```
- Response:
```json
{
  "userId": "string",
  "sessionToken": "string",
  "expiresAt": "timestamp",
  "user": {
    "email": "string",
    "displayName": "string",
    "photoURL": "string"
  }
}
```

**POST /api/v1/auth/logout**
- Description: Invalidate user session
- Headers: `Authorization: Bearer {sessionToken}`
- Response: `204 No Content`

### 3.2 Transcription Endpoints

**POST /api/v1/transcriptions/upload**
- Description: Upload audio file for transcription
- Headers: `Authorization: Bearer {sessionToken}`
- Request: Multipart form data
  - `file`: Audio file (MP3, WAV, M4A, OGG, FLAC)
  - `instruments`: JSON array of instruments to transcribe
- Response:
```json
{
  "jobId": "string",
  "songId": "string",
  "status": "queued",
  "estimatedTime": "number (seconds)",
  "queuePosition": "number"
}
```
- Rate Limit: 10 requests per 24 hours per user
- Errors:
  - `429 Too Many Requests`: Rate limit exceeded
  - `400 Bad Request`: Invalid file format or size
  - `503 Service Unavailable`: Max concurrent jobs reached

**POST /api/v1/transcriptions/youtube**
- Description: Transcribe audio from YouTube URL
- Headers: `Authorization: Bearer {sessionToken}`
- Request Body:
```json
{
  "youtubeUrl": "string",
  "instruments": ["string"]
}
```
- Response: Same as upload endpoint

**GET /api/v1/transcriptions/{jobId}/status**
- Description: Check transcription job status
- Response:
```json
{
  "jobId": "string",
  "status": "queued|processing|completed|failed",
  "progress": "number (0-100)",
  "songId": "string (if completed)",
  "error": "string (if failed)"
}
```

**GET /api/v1/transcriptions/{transcriptionId}**
- Description: Get transcription data
- Query Parameters:
  - `format`: sargam|western|alphabetical
  - `scale`: C|C#|D|...|B
  - `mode`: major|minor
  - `instrument`: piano|guitar|bass|...
- Response:
```json
{
  "transcriptionId": "string",
  "songId": "string",
  "instrument": "string",
  "format": "string",
  "scale": "string",
  "notationData": {
    "notes": [...],
    "chords": [...]
  }
}
```

### 3.3 Song Library Endpoints

**GET /api/v1/songs**
- Description: Browse song library
- Query Parameters:
  - `page`: number (default: 1)
  - `limit`: number (default: 20, max: 100)
  - `genre`: string
  - `difficulty`: beginner|intermediate|advanced
  - `instrument`: string
  - `sortBy`: popularity|title|artist|date
- Response:
```json
{
  "songs": [...],
  "pagination": {
    "page": "number",
    "limit": "number",
    "total": "number",
    "hasNext": "boolean"
  }
}
```

**GET /api/v1/songs/search**
- Description: Search songs by title or artist
- Query Parameters:
  - `q`: string (search query)
  - `source`: library|youtube|spotify (optional)
- Response:
```json
{
  "results": [
    {
      "songId": "string",
      "title": "string",
      "artist": "string",
      "albumArt": "string",
      "duration": "number",
      "source": "string"
    }
  ]
}
```

**GET /api/v1/songs/{songId}**
- Description: Get song details
- Response:
```json
{
  "songId": "string",
  "title": "string",
  "artist": "string",
  "album": "string",
  "duration": "number",
  "genre": "string",
  "difficulty": "string",
  "originalKey": "string",
  "tempo": "number",
  "timeSignature": "string",
  "metadata": {...},
  "availableInstruments": ["string"],
  "isFavorite": "boolean",
  "isDownloaded": "boolean"
}
```

**POST /api/v1/songs/{songId}/instrumental**
- Description: Generate instrumental version
- Headers: `Authorization: Bearer {sessionToken}`
- Request Body:
```json
{
  "removeVocals": "boolean",
  "removeDrums": "boolean",
  "removeBass": "boolean",
  "format": "mp3|wav"
}
```
- Response:
```json
{
  "jobId": "string",
  "status": "queued",
  "estimatedTime": "number"
}
```

**GET /api/v1/songs/{songId}/instrumental/{jobId}**
- Description: Get instrumental generation status and download URL
- Response:
```json
{
  "jobId": "string",
  "status": "completed",
  "downloadUrl": "string (signed URL, expires in 1 hour)",
  "fileSize": "number",
  "format": "string"
}
```

### 3.4 User Endpoints

**GET /api/v1/users/me**
- Description: Get current user profile
- Headers: `Authorization: Bearer {sessionToken}`
- Response: User object (see data model)

**PATCH /api/v1/users/me**
- Description: Update user preferences
- Request Body:
```json
{
  "preferences": {
    "skillLevel": "string",
    "primaryInstrument": "string",
    "notationFormat": "string",
    "sargamStyle": "string"
  }
}
```

**GET /api/v1/users/me/favorites**
- Description: Get user's favorite songs
- Response:
```json
{
  "favorites": [
    {
      "songId": "string",
      "title": "string",
      "artist": "string",
      "addedAt": "timestamp"
    }
  ]
}
```

**POST /api/v1/users/me/favorites/{songId}**
- Description: Add song to favorites

**DELETE /api/v1/users/me/favorites/{songId}**
- Description: Remove song from favorites

**GET /api/v1/users/me/history**
- Description: Get practice history
- Query Parameters:
  - `startDate`: timestamp
  - `endDate`: timestamp
- Response:
```json
{
  "history": [...],
  "stats": {
    "totalPracticeTime": "number",
    "songsLearned": "number",
    "currentStreak": "number"
  }
}
```

**POST /api/v1/users/me/history**
- Description: Record practice session
- Request Body:
```json
{
  "songId": "string",
  "instrument": "string",
  "duration": "number",
  "completionPercentage": "number"
}
```

### 3.5 Download Endpoints

**POST /api/v1/downloads/{songId}**
- Description: Prepare song for offline download
- Request Body:
```json
{
  "includeAudio": "boolean",
  "notationFormats": ["sargam", "western", "alphabetical"],
  "instruments": ["string"]
}
```
- Response:
```json
{
  "downloadId": "string",
  "downloadUrls": {
    "audio": "string (signed URL)",
    "notations": {
      "sargam": "string",
      "western": "string",
      "alphabetical": "string"
    }
  },
  "totalSize": "number (bytes)",
  "expiresAt": "timestamp"
}
```

**GET /api/v1/downloads**
- Description: Get user's downloaded songs
- Response:
```json
{
  "downloads": [
    {
      "songId": "string",
      "title": "string",
      "downloadedAt": "timestamp",
      "fileSize": "number"
    }
  ],
  "totalSize": "number",
  "remainingSlots": "number (out of 50)"
}
```

**DELETE /api/v1/downloads/{songId}**
- Description: Remove song from downloads

### 3.6 Recommendations Endpoint

**GET /api/v1/recommendations**
- Description: Get personalized song recommendations
- Headers: `Authorization: Bearer {sessionToken}`
- Response:
```json
{
  "recommendations": [
    {
      "songId": "string",
      "title": "string",
      "artist": "string",
      "reason": "string (e.g., 'Based on your skill level')",
      "score": "number (0-1)"
    }
  ]
}
```

## 4. AI/ML Processing Pipeline

### 4.1 Transcription Pipeline

**Step 1: Audio Preprocessing**
```python
def preprocess_audio(audio_file_path):
    # Load audio using librosa
    audio, sr = librosa.load(audio_file_path, sr=22050, mono=True)
    
    # Normalize audio
    audio = librosa.util.normalize(audio)
    
    # Extract features
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    key = estimate_key(audio, sr)  # Using Essentia
    
    return audio, sr, tempo, key
```

**Step 2: Multi-Model Transcription**
```python
def transcribe_audio(audio, sr):
    # Use Basic Pitch for polyphonic transcription
    basic_pitch_result = basic_pitch.predict(audio, sr)
    
    # Use MT3 for multi-instrument transcription
    mt3_result = mt3.transcribe(audio, sr)
    
    # Ensemble results for better accuracy
    final_transcription = ensemble_transcriptions(
        basic_pitch_result, 
        mt3_result
    )
    
    return final_transcription
```

**Step 3: Source Separation (if requested)**
```python
def separate_sources(audio_file_path):
    # Use Demucs for source separation
    separator = demucs.pretrained('htdemucs')
    sources = separator.separate_audio_file(audio_file_path)
    
    # Returns: vocals, drums, bass, other
    return {
        'vocals': sources[0],
        'drums': sources[1],
        'bass': sources[2],
        'other': sources[3]
    }
```

**Step 4: Instrument-Specific Transcription**
```python
def transcribe_by_instrument(separated_sources, instrument):
    if instrument == 'vocals':
        source = separated_sources['vocals']
    elif instrument == 'drums':
        source = separated_sources['drums']
    elif instrument == 'bass':
        source = separated_sources['bass']
    else:
        source = separated_sources['other']
    
    # Transcribe specific source
    notes = basic_pitch.predict(source)
    
    return notes
```

**Step 5: Notation Format Conversion**
```python
def convert_to_formats(notes, original_key):
    # Convert to music21 stream
    stream = music21.stream.Stream()
    for note_data in notes:
        note = music21.note.Note(note_data['pitch'])
        note.duration = music21.duration.Duration(note_data['duration'])
        stream.append(note)
    
    # Generate Western notation (MusicXML)
    western = stream.write('musicxml')
    
    # Generate Sargam notation
    sargam_hindustani = convert_to_sargam(notes, style='hindustani')
    sargam_carnatic = convert_to_sargam(notes, style='carnatic')
    
    # Generate Alphabetical notation
    alphabetical = convert_to_alphabetical(notes)
    
    return {
        'western': western,
        'sargam_hindustani': sargam_hindustani,
        'sargam_carnatic': sargam_carnatic,
        'alphabetical': alphabetical
    }
```

### 4.2 Scale Transposition Algorithm

```python
def transpose_notation(notes, from_key, to_key, mode='major'):
    # Calculate semitone difference
    semitone_diff = calculate_semitone_difference(from_key, to_key)
    
    # Transpose each note
    transposed_notes = []
    for note in notes:
        original_pitch = note['pitch']
        transposed_pitch = transpose_pitch(original_pitch, semitone_diff)
        
        transposed_notes.append({
            'pitch': transposed_pitch,
            'startTime': note['startTime'],
            'duration': note['duration'],
            'velocity': note['velocity']
        })
    
    # Update for mode (major/minor)
    if mode == 'minor':
        transposed_notes = apply_minor_scale_adjustments(transposed_notes)
    
    return transposed_notes
```

### 4.3 Sargam Notation Conversion

```python
def convert_to_sargam(notes, style='hindustani', base_key='C'):
    sargam_map = {
        'C': 'Sa', 'C#': 'Re♭', 'D': 'Re', 'D#': 'Ga♭',
        'E': 'Ga', 'F': 'Ma', 'F#': 'Ma♯',
        'G': 'Pa', 'G#': 'Dha♭', 'A': 'Dha', 'A#': 'Ni♭', 'B': 'Ni'
    }
    
    if style == 'carnatic':
        sargam_map = {
            'C': 'S', 'C#': 'R1', 'D': 'R2', 'D#': 'G1',
            'E': 'G2', 'F': 'M1', 'F#': 'M2',
            'G': 'P', 'G#': 'D1', 'A': 'D2', 'A#': 'N1', 'B': 'N2'
        }
    
    sargam_notes = []
    for note in notes:
        pitch_class = note['pitch'][:-1]  # Remove octave
        octave = int(note['pitch'][-1])
        
        sargam_note = sargam_map.get(pitch_class, 'Sa')
        
        # Add octave indicators
        if octave < 4:
            sargam_note = sargam_note.lower()  # Mandra (lower)
        elif octave > 4:
            sargam_note = sargam_note + "'"  # Taar (upper)
        # octave == 4 is Madhya (middle), no modifier
        
        sargam_notes.append({
            'note': sargam_note,
            'startTime': note['startTime'],
            'duration': note['duration']
        })
    
    return sargam_notes
```

### 4.4 Instrumental Generation Pipeline

```python
def generate_instrumental(audio_file_path, remove_vocals=True, 
                         remove_drums=False, remove_bass=False):
    # Separate sources using Demucs
    sources = separate_sources(audio_file_path)
    
    # Mix selected sources
    instrumental = np.zeros_like(sources['vocals'])
    
    if not remove_vocals:
        instrumental += sources['vocals']
    if not remove_drums:
        instrumental += sources['drums']
    if not remove_bass:
        instrumental += sources['bass']
    
    # Always include 'other' (melody instruments)
    instrumental += sources['other']
    
    # Normalize
    instrumental = librosa.util.normalize(instrumental)
    
    return instrumental
```

## 5. Frontend Architecture (Flutter)

### 5.1 App Structure

```
lib/
├── main.dart
├── app.dart
├── core/
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── services/
│       ├── api_service.dart
│       ├── auth_service.dart
│       ├── storage_service.dart
│       └── audio_service.dart
├── models/
│   ├── user.dart
│   ├── song.dart
│   ├── transcription.dart
│   └── notation.dart
├── providers/
│   ├── auth_provider.dart
│   ├── song_provider.dart
│   ├── transcription_provider.dart
│   └── user_provider.dart
├── screens/
│   ├── auth/
│   │   └── login_screen.dart
│   ├── home/
│   │   └── home_screen.dart
│   ├── library/
│   │   ├── library_screen.dart
│   │   └── song_detail_screen.dart
│   ├── transcription/
│   │   ├── upload_screen.dart
│   │   ├── recording_screen.dart
│   │   └── notation_viewer_screen.dart
│   ├── profile/
│   │   ├── profile_screen.dart
│   │   └── settings_screen.dart
│   └── offline/
│       └── offline_library_screen.dart
└── widgets/
    ├── notation/
    │   ├── sargam_notation_widget.dart
    │   ├── western_notation_widget.dart
    │   └── alphabetical_notation_widget.dart
    ├── audio/
    │   ├── audio_player_widget.dart
    │   └── waveform_widget.dart
    └── common/
        ├── loading_indicator.dart
        └── error_widget.dart
```

### 5.2 State Management (Provider Pattern)

**AuthProvider**
```dart
class AuthProvider extends ChangeNotifier {
  User? _user;
  String? _sessionToken;
  
  Future<void> signInWithGoogle() async {
    // Google OAuth flow
    final GoogleSignInAccount? googleUser = await GoogleSignIn().signIn();
    final GoogleSignInAuthentication googleAuth = 
        await googleUser!.authentication;
    
    // Send to backend
    final response = await apiService.post('/auth/google', {
      'idToken': googleAuth.idToken,
    });
    
    _user = User.fromJson(response['user']);
    _sessionToken = response['sessionToken'];
    
    notifyListeners();
  }
  
  Future<void> signOut() async {
    await apiService.post('/auth/logout');
    _user = null;
    _sessionToken = null;
    notifyListeners();
  }
}
```

**TranscriptionProvider**
```dart
class TranscriptionProvider extends ChangeNotifier {
  Map<String, TranscriptionJob> _jobs = {};
  
  Future<String> uploadAudioFile(File audioFile, List<String> instruments) async {
    // Check rate limits
    if (!await _checkRateLimit()) {
      throw RateLimitException('Maximum 10 transcriptions per 24 hours');
    }
    
    // Upload file
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(audioFile.path),
      'instruments': jsonEncode(instruments),
    });
    
    final response = await apiService.post('/transcriptions/upload', formData);
    
    final jobId = response['jobId'];
    _jobs[jobId] = TranscriptionJob.fromJson(response);
    
    // Start polling for status
    _pollJobStatus(jobId);
    
    notifyListeners();
    return jobId;
  }
  
  Future<void> _pollJobStatus(String jobId) async {
    while (_jobs[jobId]?.status != 'completed' && 
           _jobs[jobId]?.status != 'failed') {
      await Future.delayed(Duration(seconds: 5));
      
      final response = await apiService.get('/transcriptions/$jobId/status');
      _jobs[jobId] = TranscriptionJob.fromJson(response);
      
      notifyListeners();
    }
  }
}
```

### 5.3 Offline Storage Strategy

**Local Database Schema (SQLite)**
```sql
CREATE TABLE downloaded_songs (
  song_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  audio_path TEXT,
  downloaded_at INTEGER,
  file_size INTEGER
);

CREATE TABLE downloaded_notations (
  notation_id TEXT PRIMARY KEY,
  song_id TEXT,
  instrument TEXT,
  format TEXT, -- sargam, western, alphabetical
  notation_data TEXT, -- JSON
  FOREIGN KEY (song_id) REFERENCES downloaded_songs(song_id)
);

CREATE TABLE cached_metadata (
  song_id TEXT PRIMARY KEY,
  metadata TEXT, -- JSON
  cached_at INTEGER
);
```

**Offline Sync Service**
```dart
class OfflineSyncService {
  final Database _db;
  
  Future<void> downloadSong(String songId, {
    bool includeAudio = true,
    List<String> notationFormats = const ['sargam', 'western', 'alphabetical'],
    List<String> instruments = const ['piano'],
  }) async {
    // Request download URLs from backend
    final response = await apiService.post('/downloads/$songId', {
      'includeAudio': includeAudio,
      'notationFormats': notationFormats,
      'instruments': instruments,
    });
    
    // Download audio file
    if (includeAudio) {
      final audioPath = await _downloadFile(
        response['downloadUrls']['audio'],
        'audio_$songId.mp3'
      );
      
      await _db.insert('downloaded_songs', {
        'song_id': songId,
        'audio_path': audioPath,
        'downloaded_at': DateTime.now().millisecondsSinceEpoch,
      });
    }
    
    // Download notation files
    for (var format in notationFormats) {
      for (var instrument in instruments) {
        final notationUrl = response['downloadUrls']['notations'][format];
        final notationData = await _downloadJson(notationUrl);
        
        await _db.insert('downloaded_notations', {
          'notation_id': '${songId}_${instrument}_$format',
          'song_id': songId,
          'instrument': instrument,
          'format': format,
          'notation_data': jsonEncode(notationData),
        });
      }
    }
  }
  
  Future<Notation?> getOfflineNotation(
    String songId, 
    String instrument, 
    String format,
    {String? scale}
  ) async {
    final result = await _db.query(
      'downloaded_notations',
      where: 'song_id = ? AND instrument = ? AND format = ?',
      whereArgs: [songId, instrument, format],
    );
    
    if (result.isEmpty) return null;
    
    var notationData = jsonDecode(result.first['notation_data'] as String);
    
    // Apply scale transposition if needed
    if (scale != null) {
      notationData = _transposeNotation(notationData, scale);
    }
    
    return Notation.fromJson(notationData);
  }
}
```

## 6. Security & Privacy

### 6.1 Authentication Flow

1. User clicks "Sign in with Google"
2. Flutter app initiates Google OAuth flow
3. User authenticates with Google
4. App receives Google ID token
5. App sends ID token to backend `/api/v1/auth/google`
6. Backend verifies token with Google
7. Backend creates/updates user in Firestore
8. Backend generates session token (JWT)
9. App stores session token securely (flutter_secure_storage)
10. All subsequent API calls include session token in Authorization header

### 6.2 Firebase Security Rules

**Firestore Rules**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Songs are publicly readable, but only admins can write
    match /songs/{songId} {
      allow read: if true;
      allow write: if request.auth != null && 
                     get(/databases/$(database)/documents/users/$(request.auth.uid)).data.isAdmin == true;
    }
    
    // Transcriptions are private to the user
    match /transcriptions/{transcriptionId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
    }
    
    // Favorites are private to the user
    match /user_favorites/{favoriteId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
    }
    
    // Practice history is private to the user
    match /practice_history/{historyId} {
      allow read, write: if request.auth != null && 
                           resource.data.userId == request.auth.uid;
    }
  }
}
```

**Storage Rules**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Audio files are readable by authenticated users
    match /audio/{songId}/{fileName} {
      allow read: if request.auth != null;
      allow write: if false; // Only backend can write
    }
    
    // User uploads are private
    match /user_uploads/{userId}/{fileName} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Notation files are readable by authenticated users
    match /notations/{songId}/{fileName} {
      allow read: if request.auth != null;
      allow write: if false;
    }
  }
}
```

### 6.3 Rate Limiting Implementation

```python
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit(user_id: str, limit: int = 10, window_hours: int = 24) -> bool:
    key = f"rate_limit:transcription:{user_id}"
    now = datetime.now().timestamp()
    window_start = now - (window_hours * 3600)
    
    # Remove old entries
    redis_client.zremrangebyscore(key, 0, window_start)
    
    # Count requests in window
    request_count = redis_client.zcard(key)
    
    if request_count >= limit:
        return False
    
    # Add current request
    redis_client.zadd(key, {str(now): now})
    redis_client.expire(key, window_hours * 3600)
    
    return True

def check_concurrent_jobs(user_id: str, max_concurrent: int = 2) -> bool:
    key = f"active_jobs:{user_id}"
    active_count = redis_client.scard(key)
    
    return active_count < max_concurrent
```

## 7. Performance Optimization

### 7.1 Caching Strategy

**Backend Caching**
- Song metadata: Cache for 24 hours
- Transcription results: Cache indefinitely (immutable)
- User preferences: Cache for 1 hour
- API responses: Cache with ETags

**Frontend Caching**
- Images (album art): Cache with flutter_cache_manager
- Audio files: Cache recently played songs (max 5)
- Notation data: Cache current session
- API responses: Cache with dio_cache_interceptor

### 7.2 Database Optimization

**Firestore Indexes**
```
Collection: songs
- Composite index: (genre, difficulty, createdAt DESC)
- Composite index: (isPublic, favoriteCount DESC)
- Single field index: title (for search)
- Single field index: artist (for search)

Collection: transcriptions
- Composite index: (userId, createdAt DESC)
- Composite index: (songId, instrument)

Collection: practice_history
- Composite index: (userId, practiceDate DESC)
```

### 7.3 Audio Processing Optimization

```python
# Use multiprocessing for parallel transcription
from multiprocessing import Pool

def transcribe_multiple_instruments(audio_path, instruments):
    with Pool(processes=len(instruments)) as pool:
        results = pool.starmap(
            transcribe_instrument,
            [(audio_path, inst) for inst in instruments]
        )
    return dict(zip(instruments, results))

# Batch processing for notation conversion
def batch_convert_notations(notes_list, formats):
    converted = {}
    for format in formats:
        converted[format] = [
            convert_to_format(notes, format) 
            for notes in notes_list
        ]
    return converted
```

## 8. Error Handling

### 8.1 Backend Error Responses

```python
from fastapi import HTTPException
from enum import Enum

class ErrorCode(Enum):
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    TRANSCRIPTION_FAILED = "TRANSCRIPTION_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"

class APIError(HTTPException):
    def __init__(self, status_code: int, error_code: ErrorCode, message: str):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code.value,
                "message": message
            }
        )
```

### 8.2 Frontend Error Handling

```dart
class ApiException implements Exception {
  final String errorCode;
  final String message;
  final int statusCode;
  
  ApiException(this.errorCode, this.message, this.statusCode);
  
  String getUserFriendlyMessage() {
    switch (errorCode) {
      case 'RATE_LIMIT_EXCEEDED':
        return 'You\'ve reached the daily limit of 10 transcriptions. Please try again tomorrow.';
      case 'INVALID_FILE_FORMAT':
        return 'This file format is not supported. Please use MP3, WAV, M4A, OGG, or FLAC.';
      case 'FILE_TOO_LARGE':
        return 'File is too large. Maximum size is 50MB.';
      case 'TRANSCRIPTION_FAILED':
        return 'We couldn\'t transcribe this audio. Please try a different file.';
      default:
        return 'An error occurred. Please try again.';
    }
  }
}
```

## 9. Testing Strategy

### 9.1 Backend Testing

**Unit Tests**
- Test each AI model integration independently
- Test notation conversion functions
- Test scale transposition logic
- Test rate limiting logic

**Integration Tests**
- Test complete transcription pipeline
- Test API endpoints with mock data
- Test Firebase integration
- Test external API integrations (YouTube, Spotify)

**Performance Tests**
- Load testing with Apache JMeter
- Transcription processing time benchmarks
- Database query performance
- API response time monitoring

### 9.2 Frontend Testing

**Unit Tests**
- Test data models
- Test utility functions
- Test state management logic

**Widget Tests**
- Test notation display widgets
- Test audio player widget
- Test form validation

**Integration Tests**
- Test complete user flows
- Test offline functionality
- Test authentication flow

## 10. Deployment Architecture

### 10.1 Backend Deployment

**Docker Compose Setup**
```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - FIREBASE_CREDENTIALS=/app/firebase-credentials.json
    depends_on:
      - redis
  
  worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 10.2 CI/CD Pipeline

**GitHub Actions Workflow**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Run Flutter tests
        run: |
          cd frontend
          flutter test
  
  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy music-transcription-api \
            --image gcr.io/$PROJECT_ID/api:latest \
            --platform managed \
            --region us-central1
  
  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Flutter web
        run: flutter build web
      
      - name: Deploy to Firebase Hosting
        run: firebase deploy --only hosting
```

## 11. Monitoring & Analytics

### 11.1 Application Monitoring

**Backend Metrics**
- API response times (p50, p95, p99)
- Transcription processing times
- Error rates by endpoint
- Rate limit hits
- Active concurrent jobs

**Frontend Metrics**
- App launch time
- Screen load times
- Crash rate
- API call success rate

### 11.2 Business Metrics

- Daily/Monthly Active Users (DAU/MAU)
- Transcription requests per day
- Average session duration
- User retention rate
- Feature usage (notation formats, instruments)
- Download counts
- Favorite counts

### 11.3 Logging Strategy

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log transcription events
logger.info("Transcription started", extra={
    "user_id": user_id,
    "song_id": song_id,
    "instruments": instruments,
    "file_size": file_size
})
```

## 12. Correctness Properties

### 12.1 Transcription Accuracy Properties

**Property 1.1**: For any audio input with a clear single note, the transcribed pitch must be within ±50 cents of the actual pitch.

**Property 1.2**: The total duration of all transcribed notes must be within ±5% of the original audio duration.

**Property 1.3**: For any transcription, converting between notation formats (Sargam ↔ Western ↔ Alphabetical) and back must preserve the original pitch sequence.

### 12.2 Scale Transposition Properties

**Property 2.1**: Transposing a transcription by N semitones up and then N semitones down must return the original transcription.

**Property 2.2**: For any note in a transcription, transposing by 12 semitones (one octave) must preserve the pitch class while changing only the octave.

**Property 2.3**: The interval relationships between consecutive notes must be preserved after transposition.

### 12.3 Rate Limiting Properties

**Property 3.1**: No user can successfully submit more than 10 transcription requests within any 24-hour window.

**Property 3.2**: No user can have more than 2 transcription jobs in "processing" status simultaneously.

**Property 3.3**: Rate limit counters must reset exactly 24 hours after the first request in the window.

### 12.4 Offline Download Properties

**Property 4.1**: A user cannot download more than 50 songs at any given time.

**Property 4.2**: For any downloaded song, all selected notation formats must be accessible offline without network requests.

**Property 4.3**: Offline scale transposition must produce identical results to online transposition for the same input.

### 12.5 Audio Quality Properties

**Property 5.1**: Generated instrumental audio must have a bitrate of at least 320kbps for MP3 format.

**Property 5.2**: Source separation must preserve the total energy of the original audio (sum of separated sources ≈ original).

**Property 5.3**: Audio playback speed adjustment between 50%-150% must not alter the pitch by more than ±10 cents.

### 12.6 Authentication Properties

**Property 6.1**: Session tokens must expire exactly 7 days after creation.

**Property 6.2**: After logout, any API request with the invalidated session token must return 401 Unauthorized.

**Property 6.3**: A user's Firebase UID must remain constant across all sessions and devices.

### 12.7 Data Consistency Properties

**Property 7.1**: For any song in a user's favorites, there must exist a corresponding entry in the UserFavorites collection.

**Property 7.2**: Practice history entries must have timestamps that are not in the future.

**Property 7.3**: The sum of file sizes for a user's downloads must not exceed the calculated total size in the downloads endpoint response.

## 13. Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-2)
- Set up Firebase project
- Implement authentication (Google OAuth)
- Create basic Flutter app structure
- Set up Python backend with FastAPI
- Implement basic API endpoints

### Phase 2: Transcription Pipeline (Weeks 3-5)
- Integrate Basic Pitch and MT3
- Implement audio preprocessing
- Create transcription job queue with Celery
- Implement rate limiting
- Build upload and transcription UI

### Phase 3: Notation Systems (Weeks 6-7)
- Implement Western notation display
- Implement Sargam notation (Hindustani & Carnatic)
- Implement Alphabetical notation
- Create notation viewer UI
- Implement scale transposition

### Phase 4: Song Library (Week 8)
- Create song database schema
- Implement search and browse functionality
- Integrate YouTube and Spotify APIs
- Build library UI

### Phase 5: Audio Features (Weeks 9-10)
- Integrate Demucs for source separation
- Implement instrumental generation
- Build audio player with sync
- Implement playback controls (speed, loop)

### Phase 6: Personalization (Week 11)
- Implement favorites system
- Create practice history tracking
- Build recommendation algorithm
- Create user profile and settings UI

### Phase 7: Offline Support (Week 12)
- Implement download system
- Create local database
- Build offline sync logic
- Test offline functionality

### Phase 8: Testing & Polish (Weeks 13-14)
- Write comprehensive tests
- Performance optimization
- Bug fixes
- UI/UX improvements

### Phase 9: Deployment (Week 15)
- Set up production environment
- Deploy backend to cloud
- Publish web app
- Submit mobile apps to stores

## 14. Future Considerations

### 14.1 Scalability Improvements
- Migrate to dedicated ML inference servers (TensorFlow Serving)
- Implement CDN for audio files
- Use Cloud Functions for lightweight tasks
- Implement database sharding for large user base

### 14.2 Feature Enhancements
- Real-time collaborative transcription editing
- Video lessons with synchronized notation
- MIDI export and import
- Integration with music notation software
- Social features (sharing, following)
- Premium subscription tier

### 14.3 ML Model Improvements
- Fine-tune models on specific instruments
- Implement custom model training pipeline
- Add rhythm and timing analysis
- Improve chord detection accuracy
- Support for microtonal music

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-31  
**Status**: Ready for Implementation
