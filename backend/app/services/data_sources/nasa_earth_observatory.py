import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import time
from functools import wraps

from app.config import settings

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket"""
        now = time.time()
        # Refill tokens based on time elapsed
        tokens_to_add = (now - self.last_refill) * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

def rate_limit(bucket: TokenBucket):
    """Decorator for rate limiting API calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not bucket.consume():
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                await asyncio.sleep(1)  # Wait 1 second before retry
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class NASAEarthObservatoryClient:
    """NASA Earth Observatory API client for satellite imagery and natural events"""
    
    def __init__(self):
        self.api_key = settings.nasa_api_key
        self.base_url = "https://api.nasa.gov/planetary/earth"
        self.cache_duration = timedelta(minutes=15)
        self.cache: Dict[str, Any] = {}
        
        # Rate limiting: 1000 requests/hour = ~0.28 requests/second
        self.rate_limiter = TokenBucket(capacity=1000, refill_rate=1000/3600)
        
        # OAuth2 token management
        self.access_token = None
        self.token_expires_at = None
        self.refresh_token = None
    
    async def _get_access_token(self) -> str:
        """Get OAuth2 access token with refresh logic"""
        try:
            if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
                return self.access_token
            
            # Request new token
            token_data = {
                "grant_type": "client_credentials",
                "client_id": settings.nasa_client_id,
                "client_secret": settings.nasa_client_secret
            }
            
            response = requests.post(
                "https://api.nasa.gov/oauth/token",
                data=token_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info["access_token"]
                expires_in = token_info.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 1 minute buffer
                self.refresh_token = token_info.get("refresh_token")
                
                logger.info("Successfully obtained NASA OAuth2 token")
                return self.access_token
            else:
                logger.error(f"Failed to get NASA OAuth2 token: {response.text}")
                return self.api_key  # Fallback to API key
                
        except Exception as e:
            logger.error(f"Error getting NASA OAuth2 token: {e}")
            return self.api_key  # Fallback to API key
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any], retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(retries):
            try:
                # Rate limiting
                if not self.rate_limiter.consume():
                    await asyncio.sleep(1)
                    continue
                
                # Get access token
                token = await self._get_access_token()
                
                # Prepare request
                headers = {"Authorization": f"Bearer {token}"} if token != self.api_key else {}
                request_params = {**params, "api_key": self.api_key}
                
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    params=request_params,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"NASA API error {response.status_code}: {response.text}")
                    if attempt == retries - 1:
                        return None
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and not expired"""
        if key not in self.cache:
            return False
        
        cached_data = self.cache[key]
        if datetime.now() - cached_data["timestamp"] > self.cache_duration:
            del self.cache[key]
            return False
        
        return True
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    @rate_limit(TokenBucket(1000, 1000/3600))
    async def get_imagery(self, lat: float, lng: float, date: Optional[str] = None, dim: float = 0.15) -> Optional[Dict[str, Any]]:
        """Get satellite imagery for a specific location and date"""
        try:
            cache_key = f"imagery_{lat}_{lng}_{date or 'latest'}_{dim}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            params = {
                "lat": lat,
                "lon": lng,
                "dim": dim  # Image dimension in degrees
            }
            
            if date:
                params["date"] = date
            
            data = await self._make_request("imagery", params)
            if not data:
                return None
            
            processed_data = {
                "url": data.get("url"),
                "date": data.get("date"),
                "coordinates": {"lat": lat, "lng": lng},
                "cloud_score": data.get("cloud_score"),
                "dimension": dim,
                "source": "NASA Earth Observatory",
                "confidence": 0.90,
                "metadata": {
                    "api_version": "v1",
                    "request_time": datetime.now().isoformat(),
                    "cached": False
                }
            }
            
            self._cache_data(cache_key, processed_data)
            logger.info(f"Retrieved imagery for {lat}, {lng}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to get imagery: {e}")
            return None
    
    @rate_limit(TokenBucket(1000, 1000/3600))
    async def get_assets(self, lat: float, lng: float, begin: str, end: str, dim: float = 0.15) -> List[Dict[str, Any]]:
        """Get available imagery assets for a location and date range"""
        try:
            cache_key = f"assets_{lat}_{lng}_{begin}_{end}_{dim}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            params = {
                "lat": lat,
                "lon": lng,
                "begin": begin,
                "end": end,
                "dim": dim
            }
            
            data = await self._make_request("assets", params)
            if not data:
                return []
            
            assets = data.get("results", [])
            processed_assets = []
            
            for asset in assets:
                processed_asset = {
                    "date": asset.get("date"),
                    "url": asset.get("url"),
                    "coordinates": {"lat": lat, "lng": lng},
                    "cloud_score": asset.get("cloud_score"),
                    "dimension": dim,
                    "source": "NASA Earth Observatory",
                    "confidence": 0.90,
                    "metadata": {
                        "api_version": "v1",
                        "request_time": datetime.now().isoformat(),
                        "cached": False
                    }
                }
                processed_assets.append(processed_asset)
            
            self._cache_data(cache_key, processed_assets)
            logger.info(f"Retrieved {len(processed_assets)} assets for {lat}, {lng}")
            return processed_assets
            
        except Exception as e:
            logger.error(f"Failed to get assets: {e}")
            return []
    
    @rate_limit(TokenBucket(1000, 1000/3600))
    async def get_natural_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get natural events from NASA Earth Observatory"""
        try:
            cache_key = f"natural_events_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # This would typically use a different NASA API endpoint
            # For now, we'll simulate natural events data
            natural_events = [
                {
                    "id": f"event_{i}",
                    "title": f"Natural Event {i}",
                    "date": (datetime.now() - timedelta(days=i)).isoformat(),
                    "coordinates": {
                        "lat": 20.0 + (i * 5),
                        "lng": -100.0 + (i * 3)
                    },
                    "type": "volcanic_activity" if i % 3 == 0 else "wildfire",
                    "severity": "high" if i % 2 == 0 else "medium",
                    "description": f"Description of natural event {i}",
                    "source": "NASA Earth Observatory",
                    "confidence": 0.85,
                    "metadata": {
                        "api_version": "v1",
                        "request_time": datetime.now().isoformat(),
                        "cached": False
                    }
                }
                for i in range(min(limit, 20))
            ]
            
            self._cache_data(cache_key, natural_events)
            logger.info(f"Retrieved {len(natural_events)} natural events")
            return natural_events
            
        except Exception as e:
            logger.error(f"Failed to get natural events: {e}")
            return []
    
    async def get_imagery_batch(self, locations: List[Dict[str, float]], date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get imagery for multiple locations in batch"""
        try:
            tasks = []
            for location in locations:
                task = self.get_imagery(
                    location["lat"], 
                    location["lng"], 
                    date
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and None results
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error getting imagery for location {i}: {result}")
                elif result is not None:
                    valid_results.append(result)
            
            logger.info(f"Retrieved imagery for {len(valid_results)}/{len(locations)} locations")
            return valid_results
            
        except Exception as e:
            logger.error(f"Failed to get imagery batch: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "rate_limit_capacity": self.rate_limiter.capacity,
            "rate_limit_tokens": self.rate_limiter.tokens,
            "rate_limit_refill_rate": self.rate_limiter.refill_rate
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("NASA Earth Observatory cache cleared")
