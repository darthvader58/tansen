"""
Rate limiting utilities using Redis.
"""
from datetime import datetime, timedelta
from typing import Tuple
import logging

from app.core.redis_client import get_redis_client
from app.config import settings
from app.core.exceptions import RateLimitError, ValidationError, ErrorCode

logger = logging.getLogger(__name__)


async def check_transcription_rate_limit(user_id: str) -> Tuple[bool, int]:
    """
    Check if user has exceeded transcription rate limit.
    
    Args:
        user_id: User ID
        
    Returns:
        Tuple of (is_allowed, remaining_requests)
        
    Raises:
        RateLimitError: If rate limit exceeded
    """
    redis_client = get_redis_client()
    key = f"rate_limit:transcription:{user_id}"
    
    now = datetime.now().timestamp()
    window_start = now - (24 * 3600)  # 24 hours ago
    
    # Remove old entries
    await redis_client.zremrangebyscore(key, 0, window_start)
    
    # Count requests in window
    request_count = await redis_client.zcard(key)
    
    limit = settings.rate_limit_transcriptions_per_day
    remaining = max(0, limit - request_count)
    
    if request_count >= limit:
        raise RateLimitError(
            f"Maximum {limit} transcription requests per 24 hours exceeded. "
            f"Please try again later."
        )
    
    return True, remaining


async def increment_transcription_count(user_id: str):
    """
    Increment transcription request count for user.
    
    Args:
        user_id: User ID
    """
    redis_client = get_redis_client()
    key = f"rate_limit:transcription:{user_id}"
    
    now = datetime.now().timestamp()
    
    # Add current request
    await redis_client.zadd(key, {str(now): now})
    
    # Set expiration to 24 hours
    await redis_client.expire(key, 24 * 3600)


async def check_concurrent_jobs(user_id: str) -> Tuple[bool, int]:
    """
    Check if user has reached maximum concurrent jobs.
    
    Args:
        user_id: User ID
        
    Returns:
        Tuple of (is_allowed, active_jobs_count)
        
    Raises:
        ValidationError: If max concurrent jobs reached
    """
    redis_client = get_redis_client()
    key = f"active_jobs:{user_id}"
    
    # Get active jobs count
    active_count = await redis_client.scard(key)
    
    max_concurrent = settings.rate_limit_max_concurrent_jobs
    
    if active_count >= max_concurrent:
        raise ValidationError(
            f"Maximum {max_concurrent} concurrent transcription jobs reached. "
            f"Please wait for current jobs to complete.",
            error_code=ErrorCode.MAX_CONCURRENT_JOBS
        )
    
    return True, active_count


async def add_active_job(user_id: str, job_id: str):
    """
    Add job to user's active jobs set.
    
    Args:
        user_id: User ID
        job_id: Job ID
    """
    redis_client = get_redis_client()
    key = f"active_jobs:{user_id}"
    
    await redis_client.sadd(key, job_id)
    # Set expiration to 2 hours (max job duration)
    await redis_client.expire(key, 2 * 3600)


async def remove_active_job(user_id: str, job_id: str):
    """
    Remove job from user's active jobs set.
    
    Args:
        user_id: User ID
        job_id: Job ID
    """
    redis_client = get_redis_client()
    key = f"active_jobs:{user_id}"
    
    await redis_client.srem(key, job_id)


async def get_rate_limit_info(user_id: str) -> dict:
    """
    Get rate limit information for user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with rate limit info
    """
    redis_client = get_redis_client()
    
    # Transcription rate limit
    trans_key = f"rate_limit:transcription:{user_id}"
    now = datetime.now().timestamp()
    window_start = now - (24 * 3600)
    
    await redis_client.zremrangebyscore(trans_key, 0, window_start)
    trans_count = await redis_client.zcard(trans_key)
    trans_remaining = max(0, settings.rate_limit_transcriptions_per_day - trans_count)
    
    # Active jobs
    jobs_key = f"active_jobs:{user_id}"
    active_jobs = await redis_client.scard(jobs_key)
    
    return {
        "transcriptions_used": trans_count,
        "transcriptions_remaining": trans_remaining,
        "transcriptions_limit": settings.rate_limit_transcriptions_per_day,
        "active_jobs": active_jobs,
        "max_concurrent_jobs": settings.rate_limit_max_concurrent_jobs,
    }
