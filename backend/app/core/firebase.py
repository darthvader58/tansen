"""
Firebase initialization and utilities.
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global Firebase instances
_firestore_client = None
_storage_bucket = None


def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    global _firestore_client, _storage_bucket
    
    try:
        # Initialize Firebase app
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': settings.firebase_storage_bucket
        })
        
        # Initialize Firestore
        _firestore_client = firestore.client()
        
        # Initialize Storage
        _storage_bucket = storage.bucket()
        
        logger.info("Firebase initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def get_firestore_client():
    """Get Firestore client instance."""
    if _firestore_client is None:
        raise RuntimeError("Firebase not initialized. Call initialize_firebase() first.")
    return _firestore_client


def get_storage_bucket():
    """Get Firebase Storage bucket instance."""
    if _storage_bucket is None:
        raise RuntimeError("Firebase not initialized. Call initialize_firebase() first.")
    return _storage_bucket


def get_storage_client():
    """Get Firebase Storage bucket instance (alias for get_storage_bucket)."""
    return get_storage_bucket()


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        Decoded token containing user information
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError("Invalid token")


async def get_user_document(user_id: str) -> dict:
    """
    Get user document from Firestore.
    
    Args:
        user_id: Firebase user ID
        
    Returns:
        User document data
    """
    db = get_firestore_client()
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        return user_doc.to_dict()
    return None


async def create_user_document(user_id: str, user_data: dict):
    """
    Create user document in Firestore.
    
    Args:
        user_id: Firebase user ID
        user_data: User data to store
    """
    db = get_firestore_client()
    user_ref = db.collection('users').document(user_id)
    user_ref.set(user_data)


async def update_user_document(user_id: str, updates: dict):
    """
    Update user document in Firestore.
    
    Args:
        user_id: Firebase user ID
        updates: Fields to update
    """
    db = get_firestore_client()
    user_ref = db.collection('users').document(user_id)
    user_ref.update(updates)
