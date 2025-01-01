from datetime import datetime, timedelta
import json
import os
import pickle
from typing import Dict, Any, Optional
from dash.exceptions import PreventUpdate
from dash import html

class FirebaseCache:
    def __init__(self, cache_dir: str = '.cache', cache_duration: int = 10800):
        """
        Initialize Firebase cache
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration: Cache duration in seconds (default 1 hour)
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(seconds=cache_duration)
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _get_cache_path(self, collection: str) -> str:
        """Get cache file path for collection"""
        return os.path.join(self.cache_dir, f"{collection}_cache.pkl")
        
    def _get_metadata_path(self, collection: str) -> str:
        """Get metadata file path for collection"""
        return os.path.join(self.cache_dir, f"{collection}_metadata.json")
    
    def get_cached_data(self, collection: str) -> Optional[list]:
        """
        Get cached data if valid, otherwise return None
        
        Args:
            collection: Firebase collection name
        """
        cache_path = self._get_cache_path(collection)
        metadata_path = self._get_metadata_path(collection)
        
        # Check if cache exists
        if not (os.path.exists(cache_path) and os.path.exists(metadata_path)):
            return None
            
        # Read metadata
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
            # Check if cache is expired
            cache_time = datetime.fromisoformat(metadata['timestamp'])
            if datetime.now() - cache_time > self.cache_duration:
                return None
                
            # Read cached data
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
            
    def update_cache(self, collection: str, data: list):
        """
        Update cache with new data
        
        Args:
            collection: Firebase collection name
            data: List of documents to cache
        """
        try:
            # Save data
            cache_path = self._get_cache_path(collection)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
                
            # Save metadata
            metadata_path = self._get_metadata_path(collection)
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'count': len(data)
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
                
        except Exception as e:
            print(f"Error updating cache: {e}")
            
    def clear_cache(self, collection: Optional[str] = None):
        """
        Clear cache files
        
        Args:
            collection: Optional collection name. If None, clears all cache
        """
        try:
            if collection:
                # Clear specific collection
                cache_path = self._get_cache_path(collection)
                metadata_path = self._get_metadata_path(collection)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
            else:
                # Clear all cache
                for file in os.listdir(self.cache_dir):
                    os.remove(os.path.join(self.cache_dir, file))
                    
        except Exception as e:
            print(f"Error clearing cache: {e}")
            
    def get_cache_info(self, collection: str) -> Dict[str, Any]:
        """
        Get information about the cache
        
        Args:
            collection: Collection name
        """
        try:
            metadata_path = self._get_metadata_path(collection)
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                cache_time = datetime.fromisoformat(metadata['timestamp'])
                
                return {
                    'exists': True,
                    'age': datetime.now() - cache_time,
                    'expires_in': self.cache_duration - (datetime.now() - cache_time),
                    'count': metadata.get('count', 0)
                }
            return {'exists': False}
            
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {'exists': False, 'error': str(e)}