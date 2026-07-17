"""Response caching for improved performance."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """File-based cache for LLM and tool responses."""

    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24, max_size_mb: int = 100):
        """
        Initialize response cache.
        
        Args:
            cache_dir: Cache directory path (default: ~/.cli_agent/cache)
            ttl_hours: Time-to-live for cached responses in hours
            max_size_mb: Maximum cache size in megabytes
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".cli_agent" / "cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        
        logger.info(f"Response cache initialized: {self.cache_dir} (TTL: {ttl_hours}h, Max: {max_size_mb}MB)")

    def _generate_key(self, operation: str, **kwargs) -> str:
        """
        Generate a unique cache key from operation and parameters.
        
        Args:
            operation: Operation name (e.g., tool name, LLM request)
            **kwargs: Operation parameters
            
        Returns:
            Cache key hash
        """
        # Create a deterministic string from operation and sorted kwargs
        key_data = {
            "operation": operation,
            "params": dict(sorted(kwargs.items()))
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"{operation}_{key_hash}"

    def get(self, operation: str, **kwargs) -> Optional[Any]:
        """
        Get cached response if available and not expired.
        
        Args:
            operation: Operation name
            **kwargs: Operation parameters
            
        Returns:
            Cached response or None
        """
        cache_key = self._generate_key(operation, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired: {cache_key}")
                cache_file.unlink()  # Delete expired cache
                return None
            
            logger.debug(f"Cache hit: {cache_key}")
            return cache_data['response']
        
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def set(self, operation: str, response: Any, **kwargs) -> bool:
        """
        Cache a response.
        
        Args:
            operation: Operation name
            response: Response to cache
            **kwargs: Operation parameters
            
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_key(operation, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                'operation': operation,
                'timestamp': datetime.now().isoformat(),
                'params': kwargs,
                'response': response,
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"Cache set: {cache_key}")
            return True
        
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

    def invalidate(self, operation: str, **kwargs) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            operation: Operation name
            **kwargs: Operation parameters
            
        Returns:
            True if entry was invalidated
        """
        cache_key = self._generate_key(operation, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Cache invalidated: {cache_key}")
            return True
        
        return False

    def clear(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear cache entries.
        
        Args:
            older_than_hours: Only clear entries older than this (None = clear all)
            
        Returns:
            Number of entries cleared
        """
        cleared = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            if older_than_hours:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    age = datetime.now() - cached_time
                    
                    if age < timedelta(hours=older_than_hours):
                        continue
                except Exception:
                    pass
            
            cache_file.unlink()
            cleared += 1
        
        logger.info(f"Cleared {cleared} cache entries")
        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_entries': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.max_size / (1024 * 1024),
            'ttl_hours': self.ttl.total_seconds() / 3600,
            'cache_dir': str(self.cache_dir),
        }

    def cleanup(self) -> int:
        """
        Remove expired entries and enforce size limit.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        
        # Remove expired entries
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    removed += 1
            except Exception:
                # Delete corrupted cache files
                cache_file.unlink()
                removed += 1
        
        # Enforce size limit
        cache_files = sorted(
            self.cache_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime
        )
        
        total_size = sum(f.stat().st_size for f in cache_files)
        while total_size > self.max_size and cache_files:
            oldest_file = cache_files.pop(0)
            total_size -= oldest_file.stat().st_size
            oldest_file.unlink()
            removed += 1
        
        if removed > 0:
            logger.info(f"Cache cleanup: removed {removed} entries")
        
        return removed


# Convenience functions
_cache_instance: Optional[ResponseCache] = None


def get_cache(**kwargs) -> ResponseCache:
    """Get or create cache instance (singleton)."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ResponseCache(**kwargs)
    return _cache_instance


def cache_response(operation: str, **cache_kwargs):
    """
    Decorator for caching function responses.
    
    Args:
        operation: Operation name for cache key
        **cache_kwargs: Additional cache configuration
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Try to get from cache
            cached = cache.get(operation, **kwargs)
            if cached is not None:
                logger.debug(f"Returning cached response for {operation}")
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(operation, result, **kwargs)
            
            return result
        return wrapper
    return decorator
