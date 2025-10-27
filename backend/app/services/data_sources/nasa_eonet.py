import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.config import settings

logger = logging.getLogger(__name__)

class NASAEONETClient:
    """NASA EONET API client for disaster events"""
    
    def __init__(self):
        self.api_key = settings.nasa_api_key
        self.base_url = "https://eonet.gsfc.nasa.gov/api/v3"
        self.cache_duration = timedelta(hours=1)
        self.cache: Dict[str, Any] = {}
    
    async def get_active_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get active disaster events from NASA EONET"""
        try:
            cache_key = f"active_events_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            response = requests.get(
                f"{self.base_url}/events",
                params={"limit": limit, "days": 30},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                
                # Process and normalize events
                processed_events = []
                for event in events:
                    processed_event = {
                        "id": event.get("id"),
                        "title": event.get("title"),
                        "description": event.get("description"),
                        "category": event.get("categories", [{}])[0].get("title", "Unknown"),
                        "severity": self._determine_severity(event),
                        "coordinates": self._extract_coordinates(event),
                        "date": event.get("geometry", [{}])[0].get("date"),
                        "source": "NASA EONET",
                        "confidence": 0.95
                    }
                    processed_events.append(processed_event)
                
                self._cache_data(cache_key, processed_events)
                logger.info(f"Retrieved {len(processed_events)} active events from NASA EONET")
                return processed_events
            else:
                logger.error(f"NASA EONET API error: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get NASA EONET events: {e}")
            return []
    
    async def get_event_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific event"""
        try:
            cache_key = f"event_details_{event_id}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            response = requests.get(
                f"{self.base_url}/events/{event_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                event = response.json()
                
                # Process detailed event data
                processed_event = {
                    "id": event.get("id"),
                    "title": event.get("title"),
                    "description": event.get("description"),
                    "category": event.get("categories", [{}])[0].get("title", "Unknown"),
                    "severity": self._determine_severity(event),
                    "coordinates": self._extract_coordinates(event),
                    "geometry": event.get("geometry", []),
                    "sources": event.get("sources", []),
                    "date": event.get("geometry", [{}])[0].get("date"),
                    "source": "NASA EONET",
                    "confidence": 0.95
                }
                
                self._cache_data(cache_key, processed_event)
                logger.info(f"Retrieved details for event {event_id}")
                return processed_event
            else:
                logger.error(f"NASA EONET API error: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get event details: {e}")
            return None
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get available event categories"""
        try:
            cache_key = "categories"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            response = requests.get(
                f"{self.base_url}/categories",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get("categories", [])
                
                self._cache_data(cache_key, categories)
                logger.info(f"Retrieved {len(categories)} categories from NASA EONET")
                return categories
            else:
                logger.error(f"NASA EONET API error: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def _determine_severity(self, event: Dict[str, Any]) -> str:
        """Determine event severity based on available data"""
        # Simple heuristic based on event properties
        if event.get("title", "").lower() in ["major", "severe", "extreme", "catastrophic"]:
            return "high"
        elif event.get("title", "").lower() in ["moderate", "significant"]:
            return "medium"
        else:
            return "low"
    
    def _extract_coordinates(self, event: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract coordinates from event geometry"""
        geometry = event.get("geometry", [])
        if geometry and len(geometry) > 0:
            coords = geometry[0].get("coordinates", [])
            if coords and len(coords) >= 2:
                return {
                    "lng": coords[0],
                    "lat": coords[1]
                }
        return None
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and not expired"""
        if key in self.cache:
            cached_time = self.cache[key]["timestamp"]
            return datetime.now() - cached_time < self.cache_duration
        return False
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }

class NASAEarthObservatoryClient:
    """NASA Earth Observatory API client for satellite imagery"""
    
    def __init__(self):
        self.api_key = settings.nasa_api_key
        self.base_url = "https://api.nasa.gov/planetary/earth"
        self.cache_duration = timedelta(hours=6)
        self.cache: Dict[str, Any] = {}
    
    async def get_imagery(self, lat: float, lng: float, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get satellite imagery for a specific location and date"""
        try:
            cache_key = f"imagery_{lat}_{lng}_{date or 'latest'}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            params = {
                "lat": lat,
                "lon": lng,
                "api_key": self.api_key
            }
            
            if date:
                params["date"] = date
            
            response = requests.get(
                f"{self.base_url}/imagery",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {
                    "url": data.get("url"),
                    "date": data.get("date"),
                    "coordinates": {"lat": lat, "lng": lng},
                    "cloud_score": data.get("cloud_score"),
                    "source": "NASA Earth Observatory",
                    "confidence": 0.90
                }
                
                self._cache_data(cache_key, processed_data)
                logger.info(f"Retrieved imagery for {lat}, {lng}")
                return processed_data
            else:
                logger.error(f"NASA Earth Observatory API error: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get imagery: {e}")
            return None
    
    async def get_assets(self, lat: float, lng: float, begin: str, end: str) -> List[Dict[str, Any]]:
        """Get available imagery assets for a location and date range"""
        try:
            cache_key = f"assets_{lat}_{lng}_{begin}_{end}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            params = {
                "lat": lat,
                "lon": lng,
                "begin": begin,
                "end": end,
                "api_key": self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/assets",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get("results", [])
                
                processed_assets = []
                for asset in assets:
                    processed_asset = {
                        "date": asset.get("date"),
                        "url": asset.get("url"),
                        "coordinates": {"lat": lat, "lng": lng},
                        "source": "NASA Earth Observatory",
                        "confidence": 0.90
                    }
                    processed_assets.append(processed_asset)
                
                self._cache_data(cache_key, processed_assets)
                logger.info(f"Retrieved {len(processed_assets)} assets for {lat}, {lng}")
                return processed_assets
            else:
                logger.error(f"NASA Earth Observatory API error: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get assets: {e}")
            return []
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and not expired"""
        if key in self.cache:
            cached_time = self.cache[key]["timestamp"]
            return datetime.now() - cached_time < self.cache_duration
        return False
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
