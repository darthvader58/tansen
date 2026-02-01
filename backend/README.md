# Music Transcription API - Backend

Python FastAPI backend for AI-powered music transcription and learning platform.

## 🏗️ Architecture

- **Framework**: FastAPI (async Python web framework)
- **Database**: Firebase Firestore (NoSQL)
- **Storage**: Firebase Storage
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **AI/ML**: Basic Pitch, MT3, Demucs, Essentia, music21

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── logging.py          # Logging configuration
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── firebase.py         # Firebase initialization
│   │   ├── redis_client.py     # Redis client
│   │   ├── security.py         # JWT & authentication
│   │   └── rate_limiter.py     # Rate limiting logic
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py             # User models
│   │   └── auth.py             # Auth models
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py         # ✅ Authentication endpoints
│   │       ├── transcriptions.py  # 🚧 TODO
│   │       ├── songs.py        # 🚧 TODO
│   │       ├── users.py        # 🚧 TODO
│   │       └── downloads.py    # 🚧 TODO
│   ├── services/               # 🚧 TODO: Business logic
│   ├── tasks/                  # 🚧 TODO: Celery tasks
│   └── utils/                  # 🚧 TODO: Utility functions
├── tests/                      # 🚧 TODO: Test suite
├── requirements.txt            # ✅ Python dependencies
├── Dockerfile                  # ✅ Docker configuration
├── docker-compose.yml          # ✅ Docker Compose setup
├── .env.example                # ✅ Environment variables template
└── README.md                   # This file
```

## ✅ Completed Components

### Core Infrastructure
- [x] FastAPI application setup
- [x] Configuration management with Pydantic Settings
- [x] Logging configuration (JSON format support)
- [x] Custom exception handling
- [x] Firebase Admin SDK integration
- [x] Redis client setup
- [x] JWT authentication & authorization
- [x] Rate limiting system (10 requests/24h, max 2 concurrent jobs)

### Authentication
- [x] Google OAuth integration
- [x] Firebase token verification
- [x] JWT session token generation
- [x] User creation and management
- [x] Login/logout endpoints

### Data Models
- [x] User models (User, UserPreferences, UserStats)
- [x] Authentication models
- [x] Enums for skill levels, notation formats, themes

### DevOps
- [x] Docker configuration
- [x] Docker Compose with Redis
- [x] Environment variable management
- [x] Requirements.txt with all dependencies

## 🚧 TODO: Remaining Backend Tasks

### Phase 2: Transcription Pipeline
- [ ] Audio upload endpoint
- [ ] File validation (format, size)
- [ ] Firebase Storage integration
- [ ] Celery task queue setup
- [ ] Basic Pitch integration
- [ ] MT3 integration
- [ ] Audio preprocessing (librosa)
- [ ] Transcription job management
- [ ] Job status tracking

### Phase 3: Notation Systems
- [ ] Notation format conversion
- [ ] Sargam notation (Hindustani & Carnatic)
- [ ] Western notation (MusicXML)
- [ ] Alphabetical notation
- [ ] Scale transposition algorithm
- [ ] Notation retrieval endpoints

### Phase 4: Song Library
- [ ] Song management endpoints
- [ ] Search functionality
- [ ] Spotify API integration
- [ ] MusicBrainz API integration
- [ ] YouTube Data API integration
- [ ] yt-dlp integration

### Phase 5: Audio Features
- [ ] Demucs source separation
- [ ] Instrumental generation
- [ ] Audio quality optimization (320kbps MP3)

### Phase 6: Personalization
- [ ] Favorites system
- [ ] Practice history tracking
- [ ] Recommendation algorithm
- [ ] User preferences endpoints

### Phase 7: Offline Support
- [ ] Download preparation
- [ ] Signed URL generation
- [ ] Download management

### Phase 8: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Property-based tests
- [ ] Load testing

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Firebase project with credentials
- Redis (via Docker)

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Add Firebase credentials:**
- Download `firebase-credentials.json` from Firebase Console
- Place it in the `backend/` directory

### Running with Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:
- API server on `http://localhost:8000`
- Redis on `localhost:6379`
- Celery worker
- Flower (Celery monitoring) on `http://localhost:5555`

### Running Locally

1. **Start Redis:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

2. **Start API server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Start Celery worker (in another terminal):**
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔑 Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase credentials JSON
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate a secure random string)
- `REDIS_HOST`: Redis host (default: localhost)
- `YOUTUBE_API_KEY`: YouTube Data API key
- `SPOTIFY_CLIENT_ID`: Spotify API client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify API client secret

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/google` - Authenticate with Google OAuth
- `POST /api/v1/auth/logout` - Logout current user

### Transcriptions (TODO)
- `POST /api/v1/transcriptions/upload` - Upload audio for transcription
- `POST /api/v1/transcriptions/youtube` - Transcribe from YouTube URL
- `GET /api/v1/transcriptions/{jobId}/status` - Get job status
- `GET /api/v1/transcriptions/{transcriptionId}` - Get transcription data

### Songs (TODO)
- `GET /api/v1/songs` - Browse song library
- `GET /api/v1/songs/search` - Search songs
- `GET /api/v1/songs/{songId}` - Get song details
- `POST /api/v1/songs/{songId}/instrumental` - Generate instrumental

### Users (TODO)
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update user preferences
- `GET /api/v1/users/me/favorites` - Get favorites
- `POST /api/v1/users/me/favorites/{songId}` - Add to favorites
- `DELETE /api/v1/users/me/favorites/{songId}` - Remove from favorites
- `GET /api/v1/users/me/history` - Get practice history
- `POST /api/v1/users/me/history` - Record practice session

### Downloads (TODO)
- `POST /api/v1/downloads/{songId}` - Prepare download
- `GET /api/v1/downloads` - Get user downloads
- `DELETE /api/v1/downloads/{songId}` - Remove download

## 🔒 Security

- JWT tokens expire after 7 days
- Rate limiting: 10 transcriptions per 24 hours per user
- Max 2 concurrent transcription jobs per user
- Firebase Security Rules enforce data access control
- All API communications use HTTPS in production

## 📊 Monitoring

- **Flower**: Celery task monitoring at http://localhost:5555
- **Logs**: JSON-formatted logs for easy parsing
- **Health Check**: `/health` endpoint for uptime monitoring

## 🤝 Contributing

This is part of a larger music transcription app project. See the main project README for contribution guidelines.

## 📄 License

[Your License Here]

## 🔗 Related Documentation

- [Requirements Document](../.kiro/specs/music-transcription-app/requirements.md)
- [Design Document](../.kiro/specs/music-transcription-app/design.md)
- [Tasks Document](../.kiro/specs/music-transcription-app/tasks.md)

---

**Status**: 🚧 In Development - Core infrastructure complete, transcription pipeline in progress
**Version**: 1.0.0-alpha
**Last Updated**: 2026-01-31
