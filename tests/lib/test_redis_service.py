"""
Tests for the enhanced Redis service functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
import json
from datetime import datetime

from app.lib.redis_service import RedisService, redis_service


class TestRedisService:
    """Test suite for RedisService class."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        mock_redis = MagicMock()
        mock_redis.incr = AsyncMock()
        mock_redis.expire = AsyncMock()
        mock_redis.setex = AsyncMock()
        mock_redis.get = AsyncMock()
        mock_redis.delete = AsyncMock()
        mock_redis.exists = AsyncMock()
        mock_redis.pipeline = MagicMock()
        mock_redis.hset = AsyncMock()
        mock_redis.hgetall = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.info = AsyncMock()
        mock_redis.scan = AsyncMock()
        return mock_redis
    
    @pytest.fixture
    def redis_service_instance(self, mock_redis):
        """Create RedisService instance with mock Redis."""
        return RedisService(redis=mock_redis)
    
    # ================== RATE LIMITING TESTS ==================
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_first_request(self, redis_service_instance, mock_redis):
        """Test rate limit check for first request."""
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True
        
        is_allowed, current = await redis_service_instance.check_rate_limit("test_key", 5)
        
        assert is_allowed is True
        assert current == 1
        mock_redis.incr.assert_called_once_with("test_key")
        mock_redis.expire.assert_called_once_with("test_key", 60)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_within_limit(self, redis_service_instance, mock_redis):
        """Test rate limit check within allowed limit."""
        mock_redis.incr.return_value = 3
        
        is_allowed, current = await redis_service_instance.check_rate_limit("test_key", 5)
        
        assert is_allowed is True
        assert current == 3
        mock_redis.incr.assert_called_once_with("test_key")
        # expire should not be called for existing key
        mock_redis.expire.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, redis_service_instance, mock_redis):
        """Test rate limit check when limit is exceeded."""
        mock_redis.incr.return_value = 6
        
        is_allowed, current = await redis_service_instance.check_rate_limit("test_key", 5)
        
        assert is_allowed is False
        assert current == 6
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_failure(self, redis_service_instance, mock_redis):
        """Test rate limit check when Redis fails."""
        mock_redis.incr.side_effect = Exception("Redis connection failed")
        
        is_allowed, current = await redis_service_instance.check_rate_limit("test_key", 5)
        
        # Should fail open (allow request)
        assert is_allowed is True
        assert current == 0
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_status(self, redis_service_instance, mock_redis):
        """Test getting rate limit status."""
        mock_redis.get.return_value = "3"
        mock_redis.ttl.return_value = 45
        
        status = await redis_service_instance.get_rate_limit_status("test_key")
        
        assert status["current"] == 3
        assert status["remaining_time"] == 45
    
    # ================== OTP MANAGEMENT TESTS ==================
    
    @pytest.mark.asyncio
    async def test_store_otp(self, redis_service_instance, mock_redis):
        """Test storing OTP in Redis."""
        user_id = uuid4()
        app_id = uuid4()
        otp = "123456"
        
        mock_redis.setex.return_value = True
        
        result = await redis_service_instance.store_otp(user_id, app_id, otp, 120)
        
        assert result is True
        mock_redis.setex.assert_called_once_with(f"otp:{user_id}:{app_id}", 120, otp)
    
    @pytest.mark.asyncio
    async def test_get_and_delete_otp(self, redis_service_instance, mock_redis):
        """Test getting and deleting OTP atomically."""
        user_id = uuid4()
        app_id = uuid4()
        expected_otp = "123456"
        
        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.get = MagicMock()
        mock_pipeline.delete = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[expected_otp, 1])
        mock_redis.pipeline.return_value = mock_pipeline
        
        result = await redis_service_instance.get_and_delete_otp(user_id, app_id)
        
        assert result == expected_otp
        mock_pipeline.get.assert_called_once_with(f"otp:{user_id}:{app_id}")
        mock_pipeline.delete.assert_called_once_with(f"otp:{user_id}:{app_id}")
    
    @pytest.mark.asyncio
    async def test_get_and_delete_otp_not_found(self, redis_service_instance, mock_redis):
        """Test getting and deleting OTP when OTP doesn't exist."""
        user_id = uuid4()
        app_id = uuid4()
        
        mock_pipeline = MagicMock()
        mock_pipeline.get = MagicMock()
        mock_pipeline.delete = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[None, 0])
        mock_redis.pipeline.return_value = mock_pipeline
        
        result = await redis_service_instance.get_and_delete_otp(user_id, app_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_check_otp_exists(self, redis_service_instance, mock_redis):
        """Test checking if OTP exists."""
        user_id = uuid4()
        app_id = uuid4()
        
        mock_redis.exists.return_value = 1
        
        result = await redis_service_instance.check_otp_exists(user_id, app_id)
        
        assert result is True
        mock_redis.exists.assert_called_once_with(f"otp:{user_id}:{app_id}")
    
    # ================== SESSION MANAGEMENT TESTS ==================
    
    @pytest.mark.asyncio
    async def test_store_user_session(self, redis_service_instance, mock_redis):
        """Test storing user session."""
        user_id = uuid4()
        session_data = {"role": "user", "permissions": ["read"]}
        
        mock_redis.setex.return_value = True
        
        session_token = await redis_service_instance.store_user_session(user_id, session_data, 3600)
        
        assert session_token is not None
        assert len(session_token) == 64  # SHA256 hex digest length
        mock_redis.setex.assert_called_once()
        
        # Check if session data was properly formatted
        call_args = mock_redis.setex.call_args
        session_key, ttl, stored_data = call_args[0]
        
        assert session_key == f"session:{session_token}"
        assert ttl == 3600
        
        stored_session = json.loads(stored_data)
        assert stored_session["user_id"] == str(user_id)
        assert stored_session["role"] == "user"
        assert stored_session["permissions"] == ["read"]
        assert "created_at" in stored_session
        assert "expires_at" in stored_session
    
    @pytest.mark.asyncio
    async def test_get_user_session(self, redis_service_instance, mock_redis):
        """Test getting user session."""
        session_token = "test_session_token"
        session_data = {
            "user_id": str(uuid4()),
            "role": "user",
            "created_at": datetime.utcnow().isoformat()
        }
        
        mock_redis.get.return_value = json.dumps(session_data)
        
        result = await redis_service_instance.get_user_session(session_token)
        
        assert result == session_data
        mock_redis.get.assert_called_once_with(f"session:{session_token}")
    
    @pytest.mark.asyncio
    async def test_delete_user_session(self, redis_service_instance, mock_redis):
        """Test deleting user session."""
        session_token = "test_session_token"
        
        mock_redis.delete.return_value = 1
        
        result = await redis_service_instance.delete_user_session(session_token)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(f"session:{session_token}")
    
    # ================== FAILED ATTEMPTS TRACKING TESTS ==================
    
    @pytest.mark.asyncio
    async def test_track_failed_attempt(self, redis_service_instance, mock_redis):
        """Test tracking failed attempts."""
        identifier = "user@example.com"
        attempt_type = "login"
        
        mock_redis.incr.return_value = 3
        
        result = await redis_service_instance.track_failed_attempt(identifier, attempt_type)
        
        assert result == 3
        mock_redis.incr.assert_called_once_with(f"failed_attempts:{attempt_type}:{identifier}")
    
    @pytest.mark.asyncio
    async def test_clear_failed_attempts(self, redis_service_instance, mock_redis):
        """Test clearing failed attempts."""
        identifier = "user@example.com"
        attempt_type = "login"
        
        mock_redis.delete.return_value = 1
        
        result = await redis_service_instance.clear_failed_attempts(identifier, attempt_type)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(f"failed_attempts:{attempt_type}:{identifier}")
    
    @pytest.mark.asyncio
    async def test_is_blocked(self, redis_service_instance, mock_redis):
        """Test checking if user is blocked."""
        identifier = "user@example.com"
        
        mock_redis.get.return_value = "6"
        
        result = await redis_service_instance.is_blocked(identifier, max_attempts=5)
        
        assert result is True
        mock_redis.get.assert_called_once_with(f"failed_attempts:login:{identifier}")
    
    @pytest.mark.asyncio
    async def test_is_not_blocked(self, redis_service_instance, mock_redis):
        """Test checking if user is not blocked."""
        identifier = "user@example.com"
        
        mock_redis.get.return_value = "3"
        
        result = await redis_service_instance.is_blocked(identifier, max_attempts=5)
        
        assert result is False
    
    # ================== CACHING UTILITIES TESTS ==================
    
    @pytest.mark.asyncio
    async def test_cache_user_data(self, redis_service_instance, mock_redis):
        """Test caching user data."""
        user_id = uuid4()
        user_data = {"name": "John Doe", "email": "john@example.com"}
        
        mock_redis.setex.return_value = True
        
        result = await redis_service_instance.cache_user_data(user_id, user_data, 300)
        
        assert result is True
        mock_redis.setex.assert_called_once_with(
            f"user_cache:{user_id}", 
            300, 
            json.dumps(user_data, default=str)
        )
    
    @pytest.mark.asyncio
    async def test_get_cached_user_data(self, redis_service_instance, mock_redis):
        """Test getting cached user data."""
        user_id = uuid4()
        user_data = {"name": "John Doe", "email": "john@example.com"}
        
        mock_redis.get.return_value = json.dumps(user_data)
        
        result = await redis_service_instance.get_cached_user_data(user_id)
        
        assert result == user_data
        mock_redis.get.assert_called_once_with(f"user_cache:{user_id}")
    
    @pytest.mark.asyncio
    async def test_invalidate_user_cache(self, redis_service_instance, mock_redis):
        """Test invalidating user cache."""
        user_id = uuid4()
        
        mock_redis.delete.return_value = 1
        
        result = await redis_service_instance.invalidate_user_cache(user_id)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(f"user_cache:{user_id}")
    
    # ================== BASIC UTILITIES TESTS ==================
    
    # ================== HEALTH & DIAGNOSTICS TESTS ==================
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, redis_service_instance, mock_redis):
        """Test health check when Redis is healthy."""
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = "test_value"
        mock_redis.delete.return_value = 1
        mock_redis.info.return_value = {
            "connected_clients": 5,
            "used_memory_human": "2.1M",
            "redis_version": "7.0.0"
        }
        
        result = await redis_service_instance.health_check()
        
        assert result["status"] == "healthy"
        assert result["ping"] is True
        assert result["read_write"] is True
        assert "latency_ms" in result
        assert result["connected_clients"] == 5
        assert result["used_memory_human"] == "2.1M"
        assert result["redis_version"] == "7.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, redis_service_instance, mock_redis):
        """Test health check when Redis is unhealthy."""
        mock_redis.ping.side_effect = Exception("Connection failed")
        
        result = await redis_service_instance.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["ping"] is False
        assert result["read_write"] is False
        assert "error" in result


class TestRedisServiceIntegration:
    """Integration tests for RedisService with actual Redis patterns."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_workflow(self):
        """Test complete rate limiting workflow."""
        mock_redis = MagicMock()
        mock_redis.incr = AsyncMock()
        mock_redis.expire = AsyncMock()
        mock_redis.get = AsyncMock()
        mock_redis.ttl = AsyncMock()
        
        service = RedisService(redis=mock_redis)
        
        # Simulate multiple requests
        mock_redis.incr.side_effect = [1, 2, 3, 4, 5, 6]  # 6 requests
        
        results = []
        for i in range(6):
            is_allowed, current = await service.check_rate_limit("test_user", 5)
            results.append((is_allowed, current))
        
        # First 5 should be allowed, 6th should be denied
        for i in range(5):
            assert results[i][0] is True  # is_allowed
            assert results[i][1] == i + 1  # current count
        
        assert results[5][0] is False  # 6th request denied
        assert results[5][1] == 6
    
    @pytest.mark.asyncio
    async def test_otp_verification_workflow(self):
        """Test OTP storage and verification workflow."""
        mock_redis = MagicMock()
        mock_redis.setex = AsyncMock(return_value=True)
        mock_pipeline = MagicMock()
        mock_pipeline.get = MagicMock()
        mock_pipeline.delete = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=["123456", 1])
        mock_redis.pipeline.return_value = mock_pipeline
        
        service = RedisService(redis=mock_redis)
        user_id = uuid4()
        app_id = uuid4()
        otp = "123456"
        
        # Store OTP
        stored = await service.store_otp(user_id, app_id, otp)
        assert stored is True
        
        # Retrieve and delete OTP
        retrieved_otp = await service.get_and_delete_otp(user_id, app_id)
        assert retrieved_otp == otp
        
        # Verify pipeline was used correctly
        mock_pipeline.get.assert_called_once_with(f"otp:{user_id}:{app_id}")
        mock_pipeline.delete.assert_called_once_with(f"otp:{user_id}:{app_id}")