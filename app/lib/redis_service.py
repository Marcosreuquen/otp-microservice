"""
Redis utilities for enhanced caching, rate limiting, and session management.
"""

from typing import Optional, Dict, Any, List
from redis.asyncio import Redis
from datetime import datetime, timedelta
import json
import hashlib
from uuid import UUID

from app.lib.cache import redis_client
from app.utils.logger import Logger


class RedisService:
    """Enhanced Redis service with additional utilities for the OTP microservice."""
    
    def __init__(self, redis: Redis = None):
        self.redis = redis or redis_client
    
    # ================== RATE LIMITING ==================
    
    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (e.g., 'sms_rate:user_id:app_id')
            limit: Maximum requests allowed
            window: Time window in seconds (default: 60)
            
        Returns:
            tuple: (is_allowed, current_count)
        """
        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, window)
            return current <= limit, current
        except Exception as e:
            Logger.warning(f"Rate limit check failed for {key}: {e}")
            return True, 0  # Fail open
    
    async def get_rate_limit_status(self, key: str) -> Dict[str, Any]:
        """Get current rate limit status."""
        try:
            current = await self.redis.get(key) or 0
            ttl = await self.redis.ttl(key)
            return {
                "current": int(current),
                "remaining_time": ttl if ttl > 0 else 0
            }
        except Exception as e:
            Logger.warning(f"Failed to get rate limit status for {key}: {e}")
            return {"current": 0, "remaining_time": 0}
    
    # ================== OTP MANAGEMENT ==================
    
    async def store_otp(self, user_id: UUID, app_id: UUID, otp: str, ttl: int = 120) -> bool:
        """Store OTP with expiration."""
        key = f"otp:{user_id}:{app_id}"
        try:
            await self.redis.setex(key, ttl, otp)
            return True
        except Exception as e:
            Logger.warning(f"Failed to store OTP for {key}: {e}")
            return False
    
    async def get_and_delete_otp(self, user_id: UUID, app_id: UUID) -> Optional[str]:
        """Get OTP and immediately delete it to prevent reuse."""
        key = f"otp:{user_id}:{app_id}"
        try:
            # Use pipeline for atomic get-and-delete
            pipe = self.redis.pipeline()
            pipe.get(key)
            pipe.delete(key)
            results = await pipe.execute()
            return results[0] if results[0] else None
        except Exception as e:
            Logger.warning(f"Failed to get and delete OTP for {key}: {e}")
            return None
    
    async def check_otp_exists(self, user_id: UUID, app_id: UUID) -> bool:
        """Check if OTP exists without consuming it."""
        key = f"otp:{user_id}:{app_id}"
        try:
            exists = await self.redis.exists(key)
            return bool(exists)
        except Exception as e:
            Logger.warning(f"Failed to check OTP existence for {key}: {e}")
            return False
    
    # ================== SESSION MANAGEMENT ==================
    
    async def store_user_session(self, user_id: UUID, session_data: Dict[str, Any], ttl: int = 3600) -> Optional[str]:
        """Store user session data and return session token."""
        try:
            # Generate session token
            session_token = hashlib.sha256(f"{user_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()
            session_key = f"session:{session_token}"
            
            # Store session data
            session_data.update({
                "user_id": str(user_id),
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            })
            
            await self.redis.setex(session_key, ttl, json.dumps(session_data, default=str))
            return session_token
        except Exception as e:
            Logger.warning(f"Failed to store session for user {user_id}: {e}")
            return None
    
    async def get_user_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session data."""
        session_key = f"session:{session_token}"
        try:
            session_data = await self.redis.get(session_key)
            return json.loads(session_data) if session_data else None
        except Exception as e:
            Logger.warning(f"Failed to get session {session_token}: {e}")
            return None
    
    async def delete_user_session(self, session_token: str) -> bool:
        """Delete user session."""
        session_key = f"session:{session_token}"
        try:
            result = await self.redis.delete(session_key)
            return bool(result)
        except Exception as e:
            Logger.warning(f"Failed to delete session {session_token}: {e}")
            return False
    
    # ================== FAILED ATTEMPTS TRACKING ==================
    
    async def track_failed_attempt(self, identifier: str, attempt_type: str = "login", ttl: int = 900) -> int:
        """
        Track failed attempts (login, OTP verification, etc.).
        
        Args:
            identifier: User identifier (email, user_id, IP, etc.)
            attempt_type: Type of attempt (login, otp_verify, etc.)
            ttl: Time window in seconds (default: 15 minutes)
            
        Returns:
            Current number of failed attempts
        """
        key = f"failed_attempts:{attempt_type}:{identifier}"
        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, ttl)
            return current
        except Exception as e:
            Logger.warning(f"Failed to track attempt for {key}: {e}")
            return 0
    
    async def clear_failed_attempts(self, identifier: str, attempt_type: str = "login") -> bool:
        """Clear failed attempts for successful authentication."""
        key = f"failed_attempts:{attempt_type}:{identifier}"
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            Logger.warning(f"Failed to clear attempts for {key}: {e}")
            return False
    
    async def is_blocked(self, identifier: str, attempt_type: str = "login", max_attempts: int = 5) -> bool:
        """Check if identifier is blocked due to too many failed attempts."""
        key = f"failed_attempts:{attempt_type}:{identifier}"
        try:
            attempts = await self.redis.get(key)
            return int(attempts or 0) >= max_attempts
        except Exception as e:
            Logger.warning(f"Failed to check if blocked for {key}: {e}")
            return False
    
    # ================== CACHING UTILITIES ==================
    
    async def cache_user_data(self, user_id: UUID, data: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache user data to reduce database queries."""
        key = f"user_cache:{user_id}"
        try:
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
            return True
        except Exception as e:
            Logger.warning(f"Failed to cache user data for {user_id}: {e}")
            return False
    
    async def get_cached_user_data(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        key = f"user_cache:{user_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            Logger.warning(f"Failed to get cached user data for {user_id}: {e}")
            return None
    
    async def invalidate_user_cache(self, user_id: UUID) -> bool:
        """Invalidate cached user data."""
        key = f"user_cache:{user_id}"
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            Logger.warning(f"Failed to invalidate user cache for {user_id}: {e}")
            return False
    
    # ================== BASIC UTILITIES ==================
    
    # ================== HEALTH & DIAGNOSTICS ==================
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive Redis health check."""
        try:
            start_time = datetime.utcnow()
            
            # Test basic connectivity
            pong = await self.redis.ping()
            
            # Test read/write operations
            test_key = "health_check_test"
            await self.redis.setex(test_key, 10, "test_value")
            test_value = await self.redis.get(test_key)
            await self.redis.delete(test_key)
            
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds() * 1000
            
            # Get Redis info
            info = await self.redis.info()
            
            return {
                "status": "healthy",
                "ping": bool(pong),
                "read_write": test_value == "test_value",
                "latency_ms": round(latency, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "ping": False,
                "read_write": False
            }


# Global instance
redis_service = RedisService()