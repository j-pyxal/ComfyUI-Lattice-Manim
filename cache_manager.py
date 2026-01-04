"""
Caching system for expensive operations.
Caches transcriptions, code generation, and other computed results.
"""

import os
import hashlib
import json
import pickle
from typing import Optional, Any, Dict
from pathlib import Path

try:
    from .logger_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for expensive operations"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_seconds: int = 86400):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files (default: ~/.comfyui_lattice_manim_cache)
            ttl_seconds: Time-to-live for cache entries in seconds (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".comfyui_lattice_manim_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        
        logger.debug(f"Cache manager initialized with directory: {self.cache_dir}")
    
    def _get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = pickle.dumps(data)
        
        return hashlib.sha256(data_bytes).hexdigest()
    
    def _get_cache_path(self, key: str, suffix: str = ".cache") -> Path:
        """Get cache file path for a key"""
        return self.cache_dir / f"{key}{suffix}"
    
    def get(self, key_data: Any) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key_data: Data to generate cache key from
        
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            import time
            file_age = time.time() - cache_path.stat().st_mtime
            if file_age > self.ttl_seconds:
                logger.debug(f"Cache entry expired: {cache_key}")
                cache_path.unlink()
                return None
            
            # Load cached data
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            logger.debug(f"Cache hit: {cache_key}")
            return cached_data['value']
        except Exception as e:
            logger.warning(f"Failed to load cache entry {cache_key}: {e}")
            # Remove corrupted cache file
            try:
                cache_path.unlink()
            except:
                pass
            return None
    
    def set(self, key_data: Any, value: Any) -> None:
        """
        Set cached value.
        
        Args:
            key_data: Data to generate cache key from
            value: Value to cache
        """
        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'value': value,
                'timestamp': __import__('time').time()
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            
            logger.debug(f"Cached value: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache value {cache_key}: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info(f"Cleared cache directory: {self.cache_dir}")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'entry_count': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

