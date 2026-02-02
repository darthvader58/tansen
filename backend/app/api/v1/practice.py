"""
Practice feedback API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from ...core.security import get_current_user
from ...models.user import User
from ...services.practice_feedback_service import PracticeFeedbackService
from ...core.firebase import get_firestore_client, get_storage_bucket
import logging
import tempfile
import os
from datetime import datetime

router = APIRouter()
practice_service = PracticeFeedbackService()
logger = logging.getLogger(__name__)

@router.post("/feedback")
async def analyze_practice_performance(
    user_audio: UploadFile = File(...),
    song_id: str = Form(...),
    instrument: str = Form(default="piano"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze user's practice performance against a reference song.
    
    - **user_audio**: Audio file of user's performance
    - **song_id**: ID of the reference song
    - **instrument**: Instrument being practiced (default: piano)
    
    Returns detailed feedback including:
    - Overall score
    - Pitch, tempo, and rhythm accuracy
    - Specific note corrections
    - Personalized improvement suggestions
    """
    try:
        # Get Firestore and Storage clients
        db = get_firestore_client()
        storage_bucket = get_storage_bucket()
        
        # Get reference song from Firestore
        song_ref = db.collection('songs').document(song_id)
        song_doc = song_ref.get()
        
        if not song_doc.exists:
            raise HTTPException(status_code=404, detail="Song not found")
        
        song_data = song_doc.to_dict()
        
        # Check if reference audio exists
        if not song_data.get('audio_url'):
            raise HTTPException(
                status_code=400,
                detail="Reference audio not available for this song"
            )
        
        # Save user audio to temporary file
        user_audio_path = None
        ref_audio_path = None
        
        try:
            # Save uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_user:
                content = await user_audio.read()
                tmp_user.write(content)
                user_audio_path = tmp_user.name
            
            # Download reference audio from Firebase Storage
            ref_audio_blob = storage_bucket.blob(song_data['audio_url'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_ref:
                ref_audio_blob.download_to_filename(tmp_ref.name)
                ref_audio_path = tmp_ref.name
            
            # Analyze performance
            logger.info(f"Analyzing practice performance for user {current_user.uid}, song {song_id}")
            analysis_result = practice_service.analyze_performance(
                user_audio_path=user_audio_path,
                reference_audio_path=ref_audio_path,
                instrument=instrument
            )
            
            # Save practice session to Firestore
            practice_session = {
                'user_id': current_user.uid,
                'song_id': song_id,
                'song_title': song_data.get('title', 'Unknown'),
                'instrument': instrument,
                'timestamp': datetime.utcnow(),
                'overall_score': analysis_result['overall_score'],
                'pitch_accuracy': analysis_result['pitch_accuracy'],
                'tempo_accuracy': analysis_result['tempo_accuracy'],
                'rhythm_accuracy': analysis_result['rhythm_accuracy'],
                'grade': analysis_result['grade']
            }
            
            db.collection('practice_sessions').add(practice_session)
            
            # Update user stats
            user_ref = db.collection('users').document(current_user.uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                practice_stats = user_data.get('practice_stats', {})
                
                # Update total practice time (estimate 5 minutes per session)
                practice_stats['total_minutes'] = practice_stats.get('total_minutes', 0) + 5
                practice_stats['total_sessions'] = practice_stats.get('total_sessions', 0) + 1
                practice_stats['last_practice'] = datetime.utcnow()
                
                # Update instrument stats
                instruments = practice_stats.get('instruments', {})
                instruments[instrument] = instruments.get(instrument, 0) + 1
                practice_stats['instruments'] = instruments
                
                user_ref.update({'practice_stats': practice_stats})
            
            return {
                'success': True,
                'analysis': analysis_result,
                'song': {
                    'id': song_id,
                    'title': song_data.get('title'),
                    'artist': song_data.get('artist')
                }
            }
            
        finally:
            # Clean up temporary files
            if user_audio_path and os.path.exists(user_audio_path):
                os.unlink(user_audio_path)
            if ref_audio_path and os.path.exists(ref_audio_path):
                os.unlink(ref_audio_path)
    
    except Exception as e:
        logger.error(f"Error analyzing practice performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze performance: {str(e)}"
        )


@router.get("/history")
async def get_practice_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's practice session history.
    
    Returns list of recent practice sessions with scores and feedback.
    """
    try:
        db = get_firestore_client()
        sessions_ref = db.collection('practice_sessions')\
            .where('user_id', '==', current_user.uid)\
            .order_by('timestamp', direction='DESCENDING')\
            .limit(limit)
        
        sessions = []
        for doc in sessions_ref.stream():
            session_data = doc.to_dict()
            session_data['id'] = doc.id
            # Convert timestamp to ISO format
            if 'timestamp' in session_data:
                session_data['timestamp'] = session_data['timestamp'].isoformat()
            sessions.append(session_data)
        
        return {
            'success': True,
            'sessions': sessions
        }
    
    except Exception as e:
        logger.error(f"Error fetching practice history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch practice history: {str(e)}"
        )


@router.get("/stats")
async def get_practice_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's practice statistics and progress.
    
    Returns:
    - Total practice time
    - Number of sessions
    - Instruments practiced
    - Average scores
    - Progress over time
    """
    try:
        db = get_firestore_client()
        
        # Get user stats from Firestore
        user_ref = db.collection('users').document(current_user.uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return {
                'success': True,
                'stats': {
                    'total_minutes': 0,
                    'total_sessions': 0,
                    'instruments': {},
                    'average_score': 0,
                    'streak_days': 0
                }
            }
        
        user_data = user_doc.to_dict()
        practice_stats = user_data.get('practice_stats', {})
        
        # Get recent sessions for average score
        sessions_ref = db.collection('practice_sessions')\
            .where('user_id', '==', current_user.uid)\
            .order_by('timestamp', direction='DESCENDING')\
            .limit(10)
        
        total_score = 0
        session_count = 0
        
        for doc in sessions_ref.stream():
            session_data = doc.to_dict()
            total_score += session_data.get('overall_score', 0)
            session_count += 1
        
        average_score = total_score / session_count if session_count > 0 else 0
        
        # Calculate streak (simplified - just check if practiced today)
        last_practice = practice_stats.get('last_practice')
        streak_days = 0
        if last_practice:
            days_since = (datetime.utcnow() - last_practice).days
            if days_since == 0:
                streak_days = practice_stats.get('streak_days', 1)
            elif days_since == 1:
                streak_days = practice_stats.get('streak_days', 0) + 1
        
        return {
            'success': True,
            'stats': {
                'total_minutes': practice_stats.get('total_minutes', 0),
                'total_sessions': practice_stats.get('total_sessions', 0),
                'instruments': practice_stats.get('instruments', {}),
                'average_score': round(average_score, 1),
                'streak_days': streak_days,
                'last_practice': last_practice.isoformat() if last_practice else None
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching practice stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch practice stats: {str(e)}"
        )
