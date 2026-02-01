#!/usr/bin/env python3
"""Verify Phase 2 implementation."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("Verifying Phase 2 Implementation...")
print("=" * 50)

# Test imports
try:
    from app.services.audio_processor import AudioProcessor
    print("✓ AudioProcessor imported")
except Exception as e:
    print(f"✗ AudioProcessor import failed: {e}")

try:
    from app.services.transcription_service import TranscriptionService
    print("✓ TranscriptionService imported")
except Exception as e:
    print(f"✗ TranscriptionService import failed: {e}")

try:
    from app.celery_app import celery_app
    print("✓ Celery app imported")
except Exception as e:
    print(f"✗ Celery app import failed: {e}")

try:
    from app.tasks.transcription import transcribe_audio_task
    print("✓ Transcription task imported")
except Exception as e:
    print(f"✗ Transcription task import failed: {e}")

try:
    from app.api.v1.transcriptions import router
    print("✓ Transcription API endpoints imported")
except Exception as e:
    print(f"✗ Transcription API import failed: {e}")

print("=" * 50)
print("Phase 2 module verification complete!")
