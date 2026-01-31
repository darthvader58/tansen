# Music Learning & AI Transcription App - Requirements

## 1. Overview

A cross-platform (mobile + web) music learning application that uses AI to transcribe audio into musical notation for various instruments. The app combines real-time/uploaded audio transcription with a comprehensive song library, personalized learning features, and user authentication.

## 2. Technology Stack

### Frontend
- **Framework**: Flutter (mobile + web)
- **Platforms**: iOS, Android, Web

### Backend
- **Language**: Python
- **Database**: Firebase (Firestore for data, Firebase Auth for authentication)
- **Storage**: Firebase Storage (for audio files)

### AI/ML APIs (Free Tier)
- **Basic Pitch** (Spotify): Polyphonic pitch detection and note transcription
- **MT3** (Google Magenta): Multi-instrument music transcription
- **Demucs**: Source separation (isolate instruments from mixed audio) + instrumental generation
- **Additional Recommendations**:
  - **Essentia** (Music Information Retrieval): Tempo, key, rhythm analysis
  - **librosa** (Python): Audio feature extraction and analysis
  - **music21** (Python): Music notation processing and conversion to multiple formats
  - **mingus** (Python): Sargam notation conversion support

### Authentication
- **Google OAuth 2.0**: Primary authentication method
- **Firebase Authentication**: Session management

### Additional APIs/Services
- **YouTube Data API v3**: For fetching song metadata and audio (free tier - 10,000 units/day)
- **yt-dlp**: Python library for downloading YouTube audio (open-source, free)
- **MusicBrainz API**: Song metadata and artist information (free, open-source, no rate limits)
- **Spotify Web API**: Song metadata, album art (free tier - 180 requests/minute)

## 3. User Stories

### 3.1 Authentication & User Management

**US-3.1.1**: As a new user, I want to sign up using my Google account so that I can quickly access the app without creating new credentials.

**Acceptance Criteria**:
- User can click "Sign in with Google" button
- OAuth flow redirects to Google authentication
- Upon successful authentication, user profile is created in Firebase
- User is redirected to the app home screen
- User session persists across app restarts

**US-3.1.2**: As a returning user, I want to sign in with my existing Google account so that I can access my personalized content and history.

**Acceptance Criteria**:
- User can sign in with previously used Google account
- User's profile data, preferences, and history are loaded
- Session remains active until user logs out or token expires

**US-3.1.3**: As a user, I want to log out of my account so that my data remains private on shared devices.

**Acceptance Criteria**:
- User can access logout option from profile/settings
- Upon logout, session is cleared and user is redirected to login screen
- Local cache of user data is cleared

### 3.2 Audio Transcription

**US-3.2.1**: As a musician, I want to upload an audio file and have it transcribed to musical notation so that I can learn to play the song.

**Acceptance Criteria**:
- User can upload audio files (MP3, WAV, M4A, OGG formats)
- File size limit: 50MB per upload
- Upload progress indicator is displayed
- Transcription processing begins automatically after upload
- User receives notification when transcription is complete
- Processing time: < 2 minutes for files under 5 minutes
- Rate limit: Maximum 10 transcription requests per user per 24 hours
- Maximum 2 concurrent transcription jobs per user

**US-3.2.2**: As a musician, I want to select which instrument's notation to view so that I can focus on learning my specific instrument.

**Acceptance Criteria**:
- User can select from available instruments: Piano, Guitar, Bass, Drums, Vocals, Violin, Saxophone
- Notation updates to show selected instrument's part
- Multiple instruments can be selected simultaneously for comparison
- Selection preference is saved for future sessions

**US-3.2.3**: As a musician, I want to view transcriptions in different notation formats so that I can learn using my preferred system.

**Acceptance Criteria**:
- User can switch between notation formats:
  - **Sargam Notation**: Sa Re Ga Ma Pa Dha Ni (supports both Hindustani and Carnatic styles)
  - **Western Staff Notation**: Traditional five-line staff with clefs
  - **Alphabetical/Letter Notation**: A B C D E F G (simple note names)
  - **Piano Roll**: Visual grid representation (optional)
- Notation format preference is saved per user
- All formats display the same musical content, just different representation
- Format selector is easily accessible in the notation view
- Sargam notation includes:
  - Octave indicators (lower/middle/upper: mandra, madhya, taar)
  - Style selector for Hindustani vs Carnatic conventions
  - Komal (flat) and Tivra (sharp) note indicators
- Alphabetical notation includes octave numbers (C4, D5, etc.)

**US-3.2.3a**: As a musician, I want to transpose transcriptions to different scales/keys so that I can practice in my preferred key.

**Acceptance Criteria**:
- User can select target scale/key from dropdown (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
- User can select major or minor mode
- Transcription automatically updates to show notes in the new scale
- Scale change applies to all notation formats (Sargam, Western, Alphabetical)
- Original key is displayed alongside transposed key
- Transposition preference is saved per song
- Audio playback pitch shifts to match the new scale (optional for MVP)

**US-3.2.4**: As a user, I want to record audio in real-time and get instant transcription so that I can see my playing/singing as notation immediately.

**Acceptance Criteria**:
- User can start/stop recording from the app
- Real-time transcription displays with < 500ms latency
- Recording duration limit: 10 minutes per session
- User can save recordings for later review
- Microphone permissions are requested and handled gracefully

**US-3.2.5**: As a musician, I want the app to separate different instruments in a mixed audio track so that I can focus on learning one instrument at a time.

**Acceptance Criteria**:
- App uses source separation (Demucs) to isolate instruments
- User can toggle between: vocals, drums, bass, other, full mix
- Separated tracks can be played individually or in combination
- Quality of separation is acceptable for learning purposes

**US-3.2.6**: As a user, I want to generate an instrumental-only version of any song so that I can practice along without the original vocals or specific instruments.

**Acceptance Criteria**:
- User can generate instrumental version from any uploaded or library song
- Demucs source separation removes vocals while keeping instrumental tracks
- User can selectively remove/keep specific instruments (vocals, drums, bass, other)
- Generated instrumental audio can be downloaded as MP3/WAV
- Audio quality: 320kbps MP3 or 16-bit/44.1kHz WAV for best clarity
- Processing time: < 3 minutes for 5-minute song
- Quality is suitable for practice purposes
- Generated files are cached to avoid reprocessing
- User can preview before downloading
- Rate limit applies to instrumental generation (counts toward 10 requests/24h limit)

### 3.3 Song Library

**US-3.3.1**: As a user, I want to browse a library of pre-transcribed songs so that I can quickly start learning popular music.

**Acceptance Criteria**:
- Library contains at least 100 songs at launch
- Songs are organized by: genre, difficulty, popularity, instrument
- Each song displays: title, artist, duration, difficulty level, available instruments
- Search functionality with filters
- Pagination or infinite scroll for browsing

**US-3.3.2**: As a user, I want to search for specific songs by title or artist so that I can quickly find what I want to learn.

**Acceptance Criteria**:
- Search bar is prominently displayed
- Search returns results as user types (debounced)
- Results show song title, artist, album art
- Search includes fuzzy matching for typos
- Recent searches are saved

**US-3.3.3**: As a user, I want to view detailed notation for any song in the library so that I can learn to play it.

**Acceptance Criteria**:
- Notation is displayed in standard music notation format
- User can switch between different instruments' parts
- User can switch between different notation formats (Sargam/Western/Alphabetical)
- User can transpose to different scales/keys
- Notation is scrollable and zoomable
- Playback controls sync with notation display
- Tempo can be adjusted (50% - 150%)

**US-3.3.4**: As a user, I want to download songs for offline access so that I can practice without internet connectivity.

**Acceptance Criteria**:
- User can download any song from library or their transcriptions
- Download includes: audio file, all notation formats, metadata
- Downloaded songs are accessible in "Offline Library" section
- User can switch scales, instruments, and notation formats offline
- Downloaded content is stored locally on device
- User can manage downloads (view size, delete individual songs)
- Download size is displayed before downloading
- Maximum 50 songs can be downloaded (configurable limit)
- Downloads sync across devices via Firebase

**US-3.3.5**: As a user, I want to see song metadata (key, tempo, time signature) so that I can better understand the music structure.

**Acceptance Criteria**:
- Song detail page displays: key, tempo (BPM), time signature, duration
- Metadata is fetched from MusicBrainz/Spotify APIs
- Chord progressions are displayed where available

**US-3.3.6**: As a user, I want to access songs from music streaming services so that I can transcribe any song I'm listening to.

**Acceptance Criteria**:
- User can search for songs via YouTube, Spotify integration
- User can paste YouTube URL to transcribe that specific video
- App fetches audio from YouTube using yt-dlp or similar library
- Spotify integration provides metadata and album art (audio from YouTube)
- Search results show: title, artist, album art, duration, source (YouTube/Spotify)
- User can preview song before transcribing
- Proper attribution to original source is displayed
- Respects copyright and terms of service for each platform

### 3.4 Personalization & Learning

**US-3.4.1**: As a user, I want to save songs to my favorites so that I can easily access them later.

**Acceptance Criteria**:
- User can add/remove songs from favorites with one tap
- Favorites are synced to Firebase
- Favorites list is accessible from user profile
- Favorites persist across devices

**US-3.4.2**: As a learner, I want to track my practice history so that I can see my progress over time.

**Acceptance Criteria**:
- App records: songs practiced, time spent, date
- Practice history is displayed in user profile
- Statistics show: total practice time, songs learned, streak days
- History syncs across devices

**US-3.4.3**: As a user, I want personalized song recommendations based on my skill level and preferences so that I can discover new music to learn.

**Acceptance Criteria**:
- Recommendations consider: user's instrument, difficulty level, practice history
- "Recommended for You" section on home screen
- At least 10 recommendations displayed
- Recommendations update weekly

**US-3.4.4**: As a learner, I want to set my skill level and preferred instruments so that content is tailored to me.

**Acceptance Criteria**:
- User can select skill level: Beginner, Intermediate, Advanced
- User can select primary and secondary instruments
- Preferences are saved to user profile
- Content filtering respects these preferences

### 3.5 Playback & Practice Features

**US-3.5.1**: As a musician, I want to play the original audio alongside the notation so that I can hear how it should sound.

**Acceptance Criteria**:
- Play/pause controls are easily accessible
- Audio playback syncs with notation scrolling
- Current position is highlighted in notation
- Playback continues in background (mobile)

**US-3.5.2**: As a learner, I want to loop specific sections of a song so that I can practice difficult parts repeatedly.

**Acceptance Criteria**:
- User can set loop start and end points
- Loop controls are intuitive (drag markers on timeline)
- Loop can be enabled/disabled with toggle
- Loop points are saved per song

**US-3.5.3**: As a user, I want to adjust playback speed without changing pitch so that I can learn at my own pace.

**Acceptance Criteria**:
- Speed adjustment range: 50% - 150%
- Speed changes don't affect pitch
- Speed setting persists during session
- Speed indicator is clearly visible

## 4. Non-Functional Requirements

### 4.1 Performance
- App launch time: < 3 seconds
- Transcription processing: < 2 minutes for 5-minute audio
- Real-time transcription latency: < 500ms
- Page load time: < 1 second
- API response time: < 2 seconds (95th percentile)

### 4.2 Scalability
- Support 10,000 concurrent users
- Handle 1,000 transcription requests per hour
- Database can store 100,000+ songs
- Storage can handle 1TB+ of audio files

### 4.3 Security
- All API communications use HTTPS
- User authentication tokens expire after 7 days
- Firebase security rules prevent unauthorized data access
- Audio files are stored with user-specific access controls
- No sensitive data stored in local storage

### 4.4 Usability
- Intuitive UI following Material Design guidelines
- Responsive design for all screen sizes
- Accessibility: Screen reader support, high contrast mode
- Offline mode: View downloaded songs without internet (with full notation switching)
- Multi-language support (English initially, expandable)
- Offline downloads: Up to 50 songs with all notation formats and scales

### 4.5 Reliability
- 99.5% uptime
- Graceful error handling with user-friendly messages
- Automatic retry for failed API calls
- Data backup and recovery procedures

### 4.6 Cost Constraints
- All APIs must use free tiers
- Firebase free tier: Spark plan initially
- Optimize API calls to stay within rate limits
- Monitor usage to prevent unexpected costs

## 5. Technical Constraints

### 5.1 API Rate Limits (Free Tiers)
- **YouTube Data API**: 10,000 units/day
- **Spotify Web API**: 180 requests/minute
- **Firebase Free Tier**: 50K reads/day, 20K writes/day, 1GB storage
- **Google OAuth**: No specific limit but subject to abuse detection

### 5.2 Audio Processing
- Maximum audio file size: 50MB
- Supported formats: MP3, WAV, M4A, OGG, FLAC
- Transcription accuracy: > 80% for clear recordings
- Source separation quality: Acceptable for learning purposes
- Instrumental generation: < 3 minutes for 5-minute song (available for all users)
- Instrumental audio quality: 320kbps MP3 or 16-bit/44.1kHz WAV
- Notation format conversion: Support for Sargam (Hindustani & Carnatic), Western Staff, and Alphabetical notations
- Scale transposition: Support for all 12 chromatic keys with major/minor modes
- Offline storage: Support for 50 downloaded songs with full notation data
- Rate limiting: 10 transcription requests per user per 24 hours, max 2 concurrent jobs

### 5.3 Browser/Device Support
- **Mobile**: iOS 12+, Android 8+
- **Web**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Minimum device specs**: 2GB RAM, 100MB free storage

## 6. Future Enhancements (Out of Scope for MVP)

- Social features (share transcriptions, follow friends)
- Collaborative learning (practice with others)
- Video lessons and tutorials
- MIDI export functionality
- Integration with digital audio workstations (DAWs)
- Premium subscription tier with advanced features
- Offline transcription processing
- Custom instrument tuning support
- Sheet music printing
- Integration with music notation software (MuseScore, Finale)
- Tablature notation for guitar/bass
- Chord diagram generation
- Karaoke mode with lyrics sync
- User editing/correction of transcriptions
- Content moderation system for user uploads
- Real-time pitch shifting for audio playback

## 7. Success Metrics

- User acquisition: 1,000 users in first 3 months
- User retention: 40% monthly active users
- Average session duration: 15+ minutes
- Transcription success rate: > 80%
- User satisfaction: 4+ stars average rating
- Daily active users: 20% of total users

## 8. Risks & Mitigation

### 8.1 API Rate Limit Exhaustion
**Risk**: Free tier API limits may be exceeded with user growth
**Mitigation**: 
- Implement caching strategies
- Queue transcription requests
- Monitor usage closely
- Plan migration to paid tiers

### 8.2 Transcription Accuracy
**Risk**: AI models may not accurately transcribe complex music
**Mitigation**:
- Set user expectations about accuracy
- Allow manual corrections
- Use ensemble of multiple models
- Focus on simpler songs initially

### 8.3 Copyright Issues
**Risk**: Song library may contain copyrighted material
**Mitigation**:
- Use only public domain or licensed content
- Implement DMCA takedown process
- Focus on user-generated transcriptions
- Consult legal counsel

### 8.4 Firebase Cost Overruns
**Risk**: Free tier limits may be exceeded
**Mitigation**:
- Optimize database queries
- Implement pagination
- Use Firebase Storage efficiently
- Monitor usage dashboard

## 9. Open Questions

1. ~~Should we support tablature notation in addition to standard notation?~~ **RESOLVED: No, future enhancement**
2. ~~What's the priority order for instrument support?~~ **RESOLVED: All instruments equal priority**
3. ~~Should users be able to edit/correct transcriptions?~~ **RESOLVED: No, but scale transposition is supported**
4. ~~Do we need offline functionality for the MVP?~~ **RESOLVED: Yes, download feature with 50 song limit**
5. ~~Should we integrate with existing music streaming services for audio sources?~~ **RESOLVED: Yes, YouTube and Spotify**
6. ~~What's the content moderation strategy for user-uploaded content?~~ **RESOLVED: None for MVP**
7. Should we support collaborative transcription (multiple users improving accuracy)?
8. ~~For Sargam notation, should we support both Hindustani and Carnatic styles?~~ **RESOLVED: Yes, both styles**
9. ~~Should instrumental audio generation be available for all songs or only premium users?~~ **RESOLVED: All users**
10. ~~What audio quality should we target for generated instrumental versions (bitrate)?~~ **RESOLVED: 320kbps MP3 or 16-bit/44.1kHz WAV**
11. ~~Should we implement rate limiting for transcription requests to manage API costs?~~ **RESOLVED: Yes, 10 requests per 24 hours**
12. ~~What's the maximum number of concurrent transcription jobs per user?~~ **RESOLVED: 2 concurrent jobs**
