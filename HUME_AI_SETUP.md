# Hume AI Setup Guide

This guide will help you set up Hume AI for the AI Practice Coach feature.

## What is Hume AI?

Hume AI provides advanced audio analysis APIs that can detect prosody, emotions, and musical features in audio. We use it to analyze practice performances and provide accurate feedback.

## Setup Steps

### 1. Get Your Hume API Key

1. Go to [https://www.hume.ai/](https://www.hume.ai/)
2. Click "Sign Up" or "Get Started"
3. Create an account (free tier available)
4. Navigate to your dashboard
5. Go to "API Keys" section
6. Create a new API key
7. Copy the API key

### 2. Add API Key to Backend

Open `backend/.env` and update the `HUME_API_KEY`:

```env
HUME_API_KEY=your-actual-hume-api-key-here
```

### 3. Restart Backend

```bash
cd backend
# Stop the current backend process
# Then restart:
/Users/shashwatraj/garudenv/bin/python3.13 -m uvicorn app.main:app --reload
```

## How It Works

### Backend Flow

1. **User records audio** via Flutter app
2. **Audio uploaded** to backend `/api/v1/practice/feedback` endpoint
3. **Hume AI analyzes** both user audio and reference song:
   - Extracts prosody features (pitch, tempo, rhythm)
   - Analyzes emotional expression
   - Calculates consistency metrics
4. **Comparison** between user and reference performances
5. **Feedback generated** with:
   - Overall score (0-100)
   - Pitch accuracy
   - Tempo accuracy
   - Rhythm accuracy
   - Personalized suggestions
   - Letter grade (A+ to D)

### Frontend Flow

1. **Song selection** from available songs
2. **Audio recording** using device microphone
3. **Upload to backend** for analysis
4. **Display results** with:
   - Visual score indicators
   - Detailed metrics
   - Actionable feedback
   - Try again option

## API Endpoints

### Analyze Practice Performance

```http
POST /api/v1/practice/feedback
Content-Type: multipart/form-data

Parameters:
- user_audio: Audio file (WAV format)
- song_id: Reference song ID
- instrument: Instrument type (default: "piano")

Response:
{
  "success": true,
  "analysis": {
    "overall_score": 85.0,
    "pitch_accuracy": 88.0,
    "tempo_accuracy": 82.0,
    "rhythm_accuracy": 85.0,
    "grade": "B+",
    "suggestions": [...],
    "note_feedback": [...],
    "tempo_feedback": {...},
    "rhythm_feedback": {...}
  },
  "song": {
    "id": "song_id",
    "title": "Song Title",
    "artist": "Artist Name"
  }
}
```

### Get Practice History

```http
GET /api/v1/practice/history?limit=20

Response:
{
  "success": true,
  "sessions": [
    {
      "id": "session_id",
      "song_title": "Song Title",
      "instrument": "piano",
      "overall_score": 85,
      "timestamp": "2026-02-02T12:00:00"
    }
  ]
}
```

### Get Practice Stats

```http
GET /api/v1/practice/stats

Response:
{
  "success": true,
  "stats": {
    "total_minutes": 127,
    "total_sessions": 25,
    "instruments": {
      "piano": 15,
      "guitar": 10
    },
    "average_score": 82.5,
    "streak_days": 7
  }
}
```

## Hume AI Features Used

### Prosody Analysis

Hume's prosody model extracts:
- **Pitch contours**: Melody and note accuracy
- **Tempo variations**: Speed and consistency
- **Rhythm patterns**: Timing and beat alignment
- **Energy levels**: Dynamics and expression
- **Emotional expression**: Musical feeling and interpretation

### Comparison Algorithm

Our service compares:
1. **Mean values**: Average pitch, tempo, energy
2. **Standard deviation**: Consistency and stability
3. **Distribution similarity**: Overall pattern matching

### Scoring System

- **Pitch Accuracy (40%)**: Note correctness
- **Tempo Accuracy (30%)**: Speed consistency
- **Rhythm Accuracy (30%)**: Timing precision

## Troubleshooting

### "Hume API error" Message

- Check your API key is correct in `.env`
- Verify you have API credits remaining
- Check Hume AI service status

### "Job timeout" Error

- Audio file may be too long (max 5 minutes recommended)
- Try with shorter audio clips
- Check your internet connection

### "Permission denied" for Microphone

**Web:**
- Browser will prompt for microphone access
- Click "Allow" when prompted
- Check browser settings if blocked

**Mobile:**
- Go to device Settings > Apps > Tansen
- Enable Microphone permission

## Free Tier Limits

Hume AI free tier includes:
- **1,000 API calls/month**
- **Up to 5 minutes per audio file**
- **Standard processing speed**

For production, consider upgrading to a paid plan.

## Best Practices

1. **Audio Quality**: Record in a quiet environment
2. **File Format**: WAV format works best (44.1kHz, 16-bit)
3. **Duration**: Keep recordings under 3 minutes for faster processing
4. **Reference Songs**: Ensure reference audio is high quality

## Support

- **Hume AI Docs**: https://docs.hume.ai/
- **API Reference**: https://docs.hume.ai/reference/
- **Support**: support@hume.ai

## Alternative: Mock Mode (Development)

If you don't have a Hume API key yet, you can use mock data for development:

1. Comment out the Hume service call in `backend/app/api/v1/practice.py`
2. Return mock analysis data
3. This allows frontend development without API costs

Example mock response:
```python
analysis_result = {
    'overall_score': 85.0,
    'pitch_accuracy': 88.0,
    'tempo_accuracy': 82.0,
    'rhythm_accuracy': 85.0,
    'grade': 'B+',
    'suggestions': ['Great job!', 'Keep practicing!'],
    'note_feedback': [],
    'tempo_feedback': {'message': 'Good tempo'},
    'rhythm_feedback': {'message': 'Solid rhythm'}
}
```
