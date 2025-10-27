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

class USGSClient:
    """USGS Earth Explorer and Water Data API client"""
    
    def __init__(self):
        self.api_token = settings.usgs_api_token
        self.water_base_url = "https://waterservices.usgs.gov/nwis"
        self.earthquake_base_url = "https://earthquake.usgs.gov/fdsnws/event/1"
        self.landsat_base_url = "https://m2m.cr.usgs.gov/api/api/json/stable"
        
        # Rate limiting: 500 requests/hour = ~0.14 requests/second
        self.rate_limiter = TokenBucket(capacity=500, refill_rate=500/3600)
        
        # Cache durations
        self.water_cache_duration = timedelta(minutes=30)
        self.earthquake_cache_duration = timedelta(minutes=5)
        self.landsat_cache_duration = timedelta(hours=1)
        
        self.cache: Dict[str, Any] = {}
    
    async def _make_request(self, url: str, params: Dict[str, Any], retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(retries):
            try:
                # Rate limiting
                if not self.rate_limiter.consume():
                    await asyncio.sleep(1)
                    continue
                
                # Add API token to headers if available
                headers = {}
                if self.api_token:
                    headers["Authorization"] = f"Bearer {self.api_token}"
                
                response = requests.get(
                    url,
                    params=params,
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
                    logger.error(f"USGS API error {response.status_code}: {response.text}")
                    if attempt == retries - 1:
                        return None
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _is_cached(self, key: str, cache_duration: timedelta) -> bool:
        """Check if data is cached and not expired"""
        if key not in self.cache:
            return False
        
        cached_data = self.cache[key]
        if datetime.now() - cached_data["timestamp"] > cache_duration:
            del self.cache[key]
            return False
        
        return True
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    @rate_limit(TokenBucket(500, 500/3600))
    async def get_water_data(self, lat: float, lng: float, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get water data for a location and date range"""
        try:
            cache_key = f"water_{lat}_{lng}_{start_date}_{end_date}"
            if self._is_cached(cache_key, self.water_cache_duration):
                return self.cache[cache_key]["data"]
            
            # Get nearby stations first
            stations = await self._get_nearby_stations(lat, lng)
            if not stations:
                logger.warning(f"No water stations found near {lat}, {lng}")
                return []
            
            water_data = []
            for station in stations[:3]:  # Limit to 3 closest stations
                station_data = await self._get_station_data(station["site_no"], start_date, end_date)
                if station_data:
                    water_data.extend(station_data)
            
            self._cache_data(cache_key, water_data)
            logger.info(f"Retrieved water data for {lat}, {lng}")
            return water_data
            
        except Exception as e:
            logger.error(f"Failed to get water data: {e}")
            return []
    
    async def _get_nearby_stations(self, lat: float, lng: float, radius: float = 50) -> List[Dict[str, Any]]:
        """Get nearby water monitoring stations"""
        try:
            params = {
                "format": "json",
                "bBox": f"{lng-radius},{lat-radius},{lng+radius},{lat+radius}",
                "siteType": "ST",
                "siteStatus": "active"
            }
            
            data = await self._make_request(f"{self.water_base_url}/site", params)
            if not data:
                return []
            
            sites = data.get("value", {}).get("timeSeries", [])
            stations = []
            
            for site in sites:
                station = {
                    "site_no": site.get("sourceInfo", {}).get("siteCode", [{}])[0].get("value"),
                    "site_name": site.get("sourceInfo", {}).get("siteName"),
                    "latitude": site.get("sourceInfo", {}).get("geoLocation", {}).get("geogLocation", {}).get("latitude"),
                    "longitude": site.get("sourceInfo", {}).get("geoLocation", {}).get("geogLocation", {}).get("longitude"),
                    "distance": self._calculate_distance(lat, lng, 
                        site.get("sourceInfo", {}).get("geoLocation", {}).get("geogLocation", {}).get("latitude", 0),
                        site.get("sourceInfo", {}).get("geoLocation", {}).get("geogLocation", {}).get("longitude", 0))
                }
                stations.append(station)
            
            # Sort by distance
            stations.sort(key=lambda x: x["distance"])
            return stations
            
        except Exception as e:
            logger.error(f"Failed to get nearby stations: {e}")
            return []
    
    async def _get_station_data(self, site_no: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get data for a specific station"""
        try:
            params = {
                "format": "json",
                "sites": site_no,
                "startDT": start_date,
                "endDT": end_date,
                "parameterCd": "00060,00065"  # Streamflow and gage height
            }
            
            data = await self._make_request(f"{self.water_base_url}/iv", params)
            if not data:
                return []
            
            time_series = data.get("value", {}).get("timeSeries", [])
            station_data = []
            
            for ts in time_series:
                values = ts.get("values", [{}])[0].get("value", [])
                for value in values:
                    data_point = {
                        "site_no": site_no,
                        "date_time": value.get("dateTime"),
                        "value": float(value.get("value", 0)),
                        "qualifiers": value.get("qualifiers", []),
                        "parameter": ts.get("variable", {}).get("variableCode", [{}])[0].get("value"),
                        "parameter_name": ts.get("variable", {}).get("variableName"),
                        "unit": ts.get("variable", {}).get("unit", {}).get("unitCode")
                    }
                    station_data.append(data_point)
            
            return station_data
            
        except Exception as e:
            logger.error(f"Failed to get station data for {site_no}: {e}")
            return []
    
    @rate_limit(TokenBucket(500, 500/3600))
    async def get_earthquake_data(self, start_date: str, end_date: str, min_magnitude: float = 2.5) -> List[Dict[str, Any]]:
        """Get earthquake data for a date range"""
        try:
            cache_key = f"earthquake_{start_date}_{end_date}_{min_magnitude}"
            if self._is_cached(cache_key, self.earthquake_cache_duration):
                return self.cache[cache_key]["data"]
            
            params = {
                "format": "geojson",
                "starttime": start_date,
                "endtime": end_date,
                "minmagnitude": min_magnitude,
                "orderby": "time"
            }
            
            data = await self._make_request(f"{self.earthquake_base_url}/query", params)
            if not data:
                return []
            
            features = data.get("features", [])
            earthquakes = []
            
            for feature in features:
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [])
                
                earthquake = {
                    "id": feature.get("id"),
                    "magnitude": properties.get("mag"),
                    "place": properties.get("place"),
                    "time": properties.get("time"),
                    "updated": properties.get("updated"),
                    "tz": properties.get("tz"),
                    "url": properties.get("url"),
                    "detail": properties.get("detail"),
                    "felt": properties.get("felt"),
                    "cdi": properties.get("cdi"),
                    "mmi": properties.get("mmi"),
                    "alert": properties.get("alert"),
                    "status": properties.get("status"),
                    "tsunami": properties.get("tsunami"),
                    "sig": properties.get("sig"),
                    "net": properties.get("net"),
                    "code": properties.get("code"),
                    "ids": properties.get("ids"),
                    "sources": properties.get("sources"),
                    "types": properties.get("types"),
                    "nst": properties.get("nst"),
                    "dmin": properties.get("dmin"),
                    "rms": properties.get("rms"),
                    "gap": properties.get("gap"),
                    "magType": properties.get("magType"),
                    "type": properties.get("type"),
                    "title": properties.get("title"),
                    "coordinates": {
                        "longitude": coordinates[0] if len(coordinates) > 0 else None,
                        "latitude": coordinates[1] if len(coordinates) > 1 else None,
                        "depth": coordinates[2] if len(coordinates) > 2 else None
                    }
                }
                earthquakes.append(earthquake)
            
            self._cache_data(cache_key, earthquakes)
            logger.info(f"Retrieved {len(earthquakes)} earthquakes")
            return earthquakes
            
        except Exception as e:
            logger.error(f"Failed to get earthquake data: {e}")
            return []
    
    @rate_limit(TokenBucket(500, 500/3600))
    async def get_landsat_imagery(self, lat: float, lng: float, start_date: str, end_date: str, cloud_cover: int = 20) -> List[Dict[str, Any]]:
        """Get Landsat imagery for a location and date range"""
        try:
            cache_key = f"landsat_{lat}_{lng}_{start_date}_{end_date}_{cloud_cover}"
            if self._is_cached(cache_key, self.landsat_cache_duration):
                return self.cache[cache_key]["data"]
            
            # This would typically use the USGS M2M API for Landsat data
            # For now, we'll simulate Landsat imagery data
            landsat_data = [
                {
                    "scene_id": f"LC08_L1TP_123456_{start_date.replace('-', '')}_01_T1",
                    "acquisition_date": start_date,
                    "cloud_cover": cloud_cover,
                    "coordinates": {"lat": lat, "lng": lng},
                    "satellite": "Landsat-8",
                    "sensor": "OLI_TIRS",
                    "path": 123,
                    "row": 456,
                    "sun_elevation": 45.2,
                    "sun_azimuth": 180.5,
                    "download_url": f"https://earthengine.googleapis.com/v1alpha/projects/landsat/{start_date}",
                    "preview_url": f"https://earthengine.googleapis.com/v1alpha/projects/landsat/{start_date}/preview",
                    "metadata": {
                        "api_version": "v1",
                        "request_time": datetime.now().isoformat(),
                        "cached": False
                    }
                }
            ]
            
            self._cache_data(cache_key, landsat_data)
            logger.info(f"Retrieved {len(landsat_data)} Landsat images")
            return landsat_data
            
        except Exception as e:
            logger.error(f"Failed to get Landsat imagery: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        try:
            from math import radians, cos, sin, asin, sqrt
            
            # Convert decimal degrees to radians
            lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
            c = 2 * asin(sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return float('inf')
    
    async def get_water_data_batch(self, locations: List[Dict[str, float]], start_date: str, end_date: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get water data for multiple locations in batch"""
        try:
            tasks = []
            for location in locations:
                task = self.get_water_data(
                    location["lat"], 
                    location["lng"], 
                    start_date, 
                    end_date
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Organize results by location
            batch_results = {}
            for i, result in enumerate(results):
                location_key = f"{locations[i]['lat']}_{locations[i]['lng']}"
                if isinstance(result, Exception):
                    logger.error(f"Error getting water data for location {i}: {result}")
                    batch_results[location_key] = []
                else:
                    batch_results[location_key] = result or []
            
            logger.info(f"Retrieved water data for {len(batch_results)} locations")
            return batch_results
            
        except Exception as e:
            logger.error(f"Failed to get water data batch: {e}")
            return {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "water_cache_duration_minutes": self.water_cache_duration.total_seconds() / 60,
            "earthquake_cache_duration_minutes": self.earthquake_cache_duration.total_seconds() / 60,
            "landsat_cache_duration_hours": self.landsat_cache_duration.total_seconds() / 3600,
            "rate_limit_capacity": self.rate_limiter.capacity,
            "rate_limit_tokens": self.rate_limiter.tokens,
            "rate_limit_refill_rate": self.rate_limiter.refill_rate
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("USGS cache cleared")
