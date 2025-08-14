"""
Caching utilities for Portfolio Backend API.
"""
import json
import hashlib
import asyncio
from typing import Any, Optional, Dict, Union, Callable
from functools import wraps
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("portfolio.cache")

# Optional Redis support - graceful fallback to memory cache
redis = None
try:
    import redis.asyncio as redis
    logger.info("Redis asyncio support available")
except ImportError:
    try:
        import redis as redis_sync
        logger.info("Using sync Redis with async wrapper")
        
        # Create a simple async wrapper for sync redis
        class AsyncRedisWrapper:
            def __init__(self, sync_client):
                self.client = sync_client
            
            async def ping(self):
                return self.client.ping()
            
            async def get(self, key):
                return self.client.get(key)
            
            async def setex(self, key, ttl, value):
                return self.client.setex(key, ttl, value)
            
            async def delete(self, *keys):
                return self.client.delete(*keys)
            
            async def keys(self, pattern):
                return self.client.keys(pattern)
            
            @classmethod
            def from_url(cls, url, **kwargs):
                sync_client = redis_sync.from_url(url, **kwargs)
                return cls(sync_client)
        
        redis = AsyncRedisWrapper
    except ImportError:
        logger.warning("Redis not available, using memory cache only")
        redis = None


class CacheManager:
    """Centralized cache management using Redis or in-memory fallback."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self.connected_to_redis = False
    
    async def connect(self, redis_url: Optional[str] = None):
        """Connect to Redis cache."""
        if not redis_url:
            redis_url = getattr(settings, 'redis_url', None)
        
        if redis_url:
            try:
                if hasattr(redis, 'from_url'):
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    # Test connection
                    await self.redis_client.ping()
                    self.connected_to_redis = True
                    logger.info("Connected to Redis cache")
                else:
                    # Fallback for older redis versions
                    logger.info("Redis async not available, using memory cache")
                    self.connected_to_redis = False
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {str(e)}. Using memory cache fallback.")
                self.redis_client = None
                self.connected_to_redis = False
        else:
            logger.info("No Redis URL provided, using memory cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_client and self.connected_to_redis:
                value = await self.redis_client.get(key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
            else:
                # Memory cache fallback
                cache_entry = self.memory_cache.get(key)
                if cache_entry and cache_entry['expires_at'] > datetime.now():
                    self.cache_stats['hits'] += 1
                    return cache_entry['value']
                elif cache_entry:
                    # Expired entry, remove it
                    del self.memory_cache[key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (Time To Live) in seconds."""
        try:
            if self.redis_client and self.connected_to_redis:
                serialized_value = json.dumps(value, default=str)
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                # Memory cache fallback
                expires_at = datetime.now() + timedelta(seconds=ttl)
                self.memory_cache[key] = {
                    'value': value,
                    'expires_at': expires_at
                }
                # Clean expired entries periodically
                await self._clean_expired_memory_cache()
            
            self.cache_stats['sets'] += 1
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
    
    async def delete(self, key: str):
        """Delete key from cache."""
        try:
            if self.redis_client and self.connected_to_redis:
                await self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            
            self.cache_stats['deletes'] += 1
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching a pattern."""
        try:
            if self.redis_client and self.connected_to_redis:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # Memory cache pattern matching
                keys_to_delete = [key for key in self.memory_cache.keys() 
                                if self._matches_pattern(key, pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            
            logger.info(f"Cleared cache pattern: {pattern}")
            
        except Exception as e:
            logger.error(f"Cache pattern clear error for {pattern}: {str(e)}")
    
    async def _clean_expired_memory_cache(self):
        """Clean expired entries from memory cache."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry['expires_at'] <= now
        ]
        for key in expired_keys:
            del self.memory_cache[key]
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for memory cache."""
        if pattern.endswith('*'):
            return key.startswith(pattern[:-1])
        return key == pattern
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'backend': 'redis' if self.connected_to_redis else 'memory',
            'connected': self.connected_to_redis,
            'stats': self.cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache) if not self.connected_to_redis else None
        }


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    # Create hash of the combined key for consistent length
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            key_suffix = cache_key(*args, **kwargs)
            full_key = f"{key_prefix}:{func_name}:{key_suffix}" if key_prefix else f"{func_name}:{key_suffix}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(full_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func_name}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func_name}, executing function")
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.set(full_key, result, ttl)
            
            return result
        return wrapper
    return decorator


class ContentCache:
    """Specialized cache for content operations."""
    
    @staticmethod
    async def invalidate_content_cache(content_type: str, content_id: Optional[int] = None):
        """Invalidate cache for specific content type."""
        patterns = [
            f"content:{content_type}:*",
            f"list:{content_type}:*"
        ]
        
        if content_id:
            patterns.append(f"content:{content_type}:{content_id}:*")
        
        for pattern in patterns:
            await cache_manager.clear_pattern(pattern)
        
        logger.info(f"Invalidated cache for {content_type}" + (f" ID {content_id}" if content_id else ""))
    
    @staticmethod
    async def cache_content_list(content_type: str, language: str, content: Any, ttl: int = 600):
        """Cache content list with language-specific key."""
        key = f"list:{content_type}:lang:{language}"
        await cache_manager.set(key, content, ttl)
    
    @staticmethod
    async def get_cached_content_list(content_type: str, language: str) -> Optional[Any]:
        """Get cached content list for specific language."""
        key = f"list:{content_type}:lang:{language}"
        return await cache_manager.get(key)
    
    @staticmethod
    async def cache_single_content(content_type: str, content_id: int, language: str, content: Any, ttl: int = 300):
        """Cache single content item with language-specific key."""
        key = f"content:{content_type}:{content_id}:lang:{language}"
        await cache_manager.set(key, content, ttl)
    
    @staticmethod
    async def get_cached_single_content(content_type: str, content_id: int, language: str) -> Optional[Any]:
        """Get cached single content item for specific language."""
        key = f"content:{content_type}:{content_id}:lang:{language}"
        return await cache_manager.get(key)


# Utility functions
async def warm_cache():
    """Warm up cache with frequently accessed data."""
    try:
        from app.database import SessionLocal
        from app.services.content import (
            about_service, skill_service, project_service,
            experience_service, education_service, contact_service
        )
        
        db = SessionLocal()
        
        # Warm up content caches
        languages = ['en', 'es']
        
        for lang in languages:
            # Cache skills
            skills = skill_service.get_skills(db)
            await ContentCache.cache_content_list("skills", lang, skills, ttl=1800)  # 30 minutes
            
            # Cache projects
            projects = project_service.get_projects(db)
            await ContentCache.cache_content_list("projects", lang, projects, ttl=1800)
            
            # Cache experiences
            experiences = experience_service.get_experiences(db)
            await ContentCache.cache_content_list("experience", lang, experiences, ttl=1800)
            
            # Cache education
            education = education_service.get_education_records(db)
            await ContentCache.cache_content_list("education", lang, education, ttl=1800)
            
            # Cache about
            about = about_service.get_about(db)
            if about:
                await ContentCache.cache_single_content("about", about.id, lang, about, ttl=3600)  # 1 hour
            
            # Cache contact
            contact = contact_service.get_contact(db)
            if contact:
                await ContentCache.cache_single_content("contact", contact.id, lang, contact, ttl=3600)
        
        db.close()
        logger.info("Cache warmed up successfully")
        
    except Exception as e:
        logger.error(f"Error warming cache: {str(e)}")


content_cache = ContentCache()