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

class NOAAWeatherClient:
    """NOAA Weather API client for current weather, forecasts, and alerts"""
    
    def __init__(self):
        self.user_agent = settings.noaa_user_agent or "NebulaProtocol/1.0"
        self.base_url = "https://api.weather.gov"
        self.cache_duration = timedelta(minutes=10)
        self.cache: Dict[str, Any] = {}
        
        # Rate limiting: 300 requests/hour per location = ~0.083 requests/second
        self.rate_limiter = TokenBucket(capacity=300, refill_rate=300/3600)
        
        # Location-based rate limiting
        self.location_requests: Dict[str, datetime] = {}
        self.location_rate_limit = timedelta(minutes=1)  # 1 request per minute per location
    
    async def _make_request(self, url: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(retries):
            try:
                # Rate limiting
                if not self.rate_limiter.consume():
                    await asyncio.sleep(1)
                    continue
                
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "application/geo+json"
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    return None
                else:
                    logger.error(f"NOAA API error {response.status_code}: {response.text}")
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
    
    def _validate_coordinates(self, lat: float, lng: float) -> bool:
        """Validate coordinate ranges"""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    async def _get_grid_point(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Get NOAA grid point for coordinates"""
        try:
            if not self._validate_coordinates(lat, lng):
                logger.error(f"Invalid coordinates: {lat}, {lng}")
                return None
            
            cache_key = f"grid_{lat}_{lng}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/points/{lat},{lng}"
            data = await self._make_request(url)
            
            if data:
                self._cache_data(cache_key, data)
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get grid point: {e}")
            return None
    
    @rate_limit(TokenBucket(300, 300/3600))
    async def get_current_weather(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Get current weather conditions for coordinates"""
        try:
            if not self._validate_coordinates(lat, lng):
                logger.error(f"Invalid coordinates: {lat}, {lng}")
                return None
            
            # Check location rate limit
            location_key = f"{lat}_{lng}"
            if location_key in self.location_requests:
                time_since_last = datetime.now() - self.location_requests[location_key]
                if time_since_last < self.location_rate_limit:
                    logger.warning(f"Location rate limit exceeded for {lat}, {lng}")
                    return None
            
            cache_key = f"current_{lat}_{lng}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get grid point
            grid_data = await self._get_grid_point(lat, lng)
            if not grid_data:
                return None
            
            # Get current observations
            observation_url = grid_data.get("properties", {}).get("observationStations")
            if not observation_url:
                logger.warning(f"No observation stations found for {lat}, {lng}")
                return None
            
            # Get latest observation
            stations_data = await self._make_request(observation_url)
            if not stations_data:
                return None
            
            stations = stations_data.get("features", [])
            if not stations:
                logger.warning(f"No weather stations found for {lat}, {lng}")
                return None
            
            # Get observation from closest station
            latest_observation_url = f"{observation_url}/observations/latest"
            observation_data = await self._make_request(latest_observation_url)
            
            if not observation_data:
                return None
            
            # Process observation data
            properties = observation_data.get("properties", {})
            current_weather = {
                "timestamp": properties.get("timestamp"),
                "temperature": {
                    "value": properties.get("temperature", {}).get("value"),
                    "unit": properties.get("temperature", {}).get("unitCode")
                },
                "humidity": {
                    "value": properties.get("relativeHumidity", {}).get("value"),
                    "unit": properties.get("relativeHumidity", {}).get("unitCode")
                },
                "pressure": {
                    "value": properties.get("barometricPressure", {}).get("value"),
                    "unit": properties.get("barometricPressure", {}).get("unitCode")
                },
                "wind": {
                    "speed": properties.get("windSpeed", {}).get("value"),
                    "direction": properties.get("windDirection", {}).get("value"),
                    "unit": properties.get("windSpeed", {}).get("unitCode")
                },
                "visibility": {
                    "value": properties.get("visibility", {}).get("value"),
                    "unit": properties.get("visibility", {}).get("unitCode")
                },
                "cloud_cover": properties.get("cloudLayers", []),
                "weather_condition": properties.get("textDescription"),
                "coordinates": {"lat": lat, "lng": lng},
                "source": "NOAA Weather API",
                "confidence": 0.95,
                "metadata": {
                    "api_version": "v1",
                    "request_time": datetime.now().isoformat(),
                    "cached": False
                }
            }
            
            self._cache_data(cache_key, current_weather)
            self.location_requests[location_key] = datetime.now()
            
            logger.info(f"Retrieved current weather for {lat}, {lng}")
            return current_weather
            
        except Exception as e:
            logger.error(f"Failed to get current weather: {e}")
            return None
    
    @rate_limit(TokenBucket(300, 300/3600))
    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> Optional[Dict[str, Any]]:
        """Get weather forecast for coordinates"""
        try:
            if not self._validate_coordinates(lat, lng):
                logger.error(f"Invalid coordinates: {lat}, {lng}")
                return None
            
            cache_key = f"forecast_{lat}_{lng}_{days}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get grid point
            grid_data = await self._get_grid_point(lat, lng)
            if not grid_data:
                return None
            
            # Get forecast URL
            forecast_url = grid_data.get("properties", {}).get("forecast")
            if not forecast_url:
                logger.warning(f"No forecast available for {lat}, {lng}")
                return None
            
            forecast_data = await self._make_request(forecast_url)
            if not forecast_data:
                return None
            
            # Process forecast data
            periods = forecast_data.get("properties", {}).get("periods", [])
            forecast_periods = []
            
            for period in periods[:days * 2]:  # Limit to requested days (2 periods per day)
                forecast_period = {
                    "number": period.get("number"),
                    "name": period.get("name"),
                    "start_time": period.get("startTime"),
                    "end_time": period.get("endTime"),
                    "is_daytime": period.get("isDaytime"),
                    "temperature": period.get("temperature"),
                    "temperature_unit": period.get("temperatureUnit"),
                    "temperature_trend": period.get("temperatureTrend"),
                    "wind_speed": period.get("windSpeed"),
                    "wind_direction": period.get("windDirection"),
                    "icon": period.get("icon"),
                    "short_forecast": period.get("shortForecast"),
                    "detailed_forecast": period.get("detailedForecast"),
                    "probability_of_precipitation": period.get("probabilityOfPrecipitation", {}).get("value")
                }
                forecast_periods.append(forecast_period)
            
            forecast = {
                "coordinates": {"lat": lat, "lng": lng},
                "forecast_periods": forecast_periods,
                "forecast_generated": forecast_data.get("properties", {}).get("generatedAt"),
                "forecast_valid": forecast_data.get("properties", {}).get("validTimes"),
                "source": "NOAA Weather API",
                "confidence": 0.90,
                "metadata": {
                    "api_version": "v1",
                    "request_time": datetime.now().isoformat(),
                    "cached": False
                }
            }
            
            self._cache_data(cache_key, forecast)
            logger.info(f"Retrieved {days}-day forecast for {lat}, {lng}")
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to get forecast: {e}")
            return None
    
    @rate_limit(TokenBucket(300, 300/3600))
    async def get_alerts(self, lat: float, lng: float, active: bool = True) -> List[Dict[str, Any]]:
        """Get weather alerts for coordinates"""
        try:
            if not self._validate_coordinates(lat, lng):
                logger.error(f"Invalid coordinates: {lat}, {lng}")
                return []
            
            cache_key = f"alerts_{lat}_{lng}_{active}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get alerts URL
            alerts_url = f"{self.base_url}/alerts"
            params = {
                "point": f"{lat},{lng}",
                "active": active
            }
            
            # Build URL with parameters
            url = f"{alerts_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            alerts_data = await self._make_request(url)
            if not alerts_data:
                return []
            
            # Process alerts data
            features = alerts_data.get("features", [])
            alerts = []
            
            for feature in features:
                properties = feature.get("properties", {})
                alert = {
                    "id": properties.get("id"),
                    "area_desc": properties.get("areaDesc"),
                    "geocode": properties.get("geocode"),
                    "affected_zones": properties.get("affectedZones"),
                    "references": properties.get("references"),
                    "sent": properties.get("sent"),
                    "effective": properties.get("effective"),
                    "onset": properties.get("onset"),
                    "expires": properties.get("expires"),
                    "ends": properties.get("ends"),
                    "status": properties.get("status"),
                    "message_type": properties.get("messageType"),
                    "category": properties.get("category"),
                    "severity": properties.get("severity"),
                    "certainty": properties.get("certainty"),
                    "urgency": properties.get("urgency"),
                    "event": properties.get("event"),
                    "sender": properties.get("sender"),
                    "sender_name": properties.get("senderName"),
                    "headline": properties.get("headline"),
                    "description": properties.get("description"),
                    "instruction": properties.get("instruction"),
                    "response": properties.get("response"),
                    "coordinates": {"lat": lat, "lng": lng},
                    "source": "NOAA Weather API",
                    "confidence": 0.95
                }
                alerts.append(alert)
            
            self._cache_data(cache_key, alerts)
            logger.info(f"Retrieved {len(alerts)} weather alerts for {lat}, {lng}")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get weather alerts: {e}")
            return []
    
    @rate_limit(TokenBucket(300, 300/3600))
    async def get_radar_data(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Get radar data for coordinates"""
        try:
            if not self._validate_coordinates(lat, lng):
                logger.error(f"Invalid coordinates: {lat}, {lng}")
                return None
            
            cache_key = f"radar_{lat}_{lng}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get grid point
            grid_data = await self._get_grid_point(lat, lng)
            if not grid_data:
                return None
            
            # Get radar station
            radar_station = grid_data.get("properties", {}).get("radarStation")
            if not radar_station:
                logger.warning(f"No radar station found for {lat}, {lng}")
                return None
            
            # Get radar data URL
            radar_url = f"{self.base_url}/stations/{radar_station}/observations/latest"
            radar_data = await self._make_request(radar_url)
            
            if not radar_data:
                return None
            
            # Process radar data
            properties = radar_data.get("properties", {})
            radar_info = {
                "station_id": radar_station,
                "timestamp": properties.get("timestamp"),
                "coordinates": {"lat": lat, "lng": lng},
                "radar_coverage": {
                    "station_latitude": properties.get("geometry", {}).get("coordinates", [None, None])[1],
                    "station_longitude": properties.get("geometry", {}).get("coordinates", [None, None])[0],
                    "elevation": properties.get("elevation", {}).get("value")
                },
                "precipitation": {
                    "intensity": properties.get("precipitationIntensity", {}).get("value"),
                    "unit": properties.get("precipitationIntensity", {}).get("unitCode")
                },
                "source": "NOAA Weather API",
                "confidence": 0.85,
                "metadata": {
                    "api_version": "v1",
                    "request_time": datetime.now().isoformat(),
                    "cached": False
                }
            }
            
            self._cache_data(cache_key, radar_info)
            logger.info(f"Retrieved radar data for {lat}, {lng}")
            return radar_info
            
        except Exception as e:
            logger.error(f"Failed to get radar data: {e}")
            return None
    
    async def get_weather_batch(self, locations: List[Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Get weather data for multiple locations in batch"""
        try:
            tasks = []
            for location in locations:
                task = self.get_current_weather(location["lat"], location["lng"])
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Organize results by location
            batch_results = {}
            for i, result in enumerate(results):
                location_key = f"{locations[i]['lat']}_{locations[i]['lng']}"
                if isinstance(result, Exception):
                    logger.error(f"Error getting weather for location {i}: {result}")
                    batch_results[location_key] = None
                else:
                    batch_results[location_key] = result
            
            logger.info(f"Retrieved weather data for {len(batch_results)} locations")
            return batch_results
            
        except Exception as e:
            logger.error(f"Failed to get weather batch: {e}")
            return {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "rate_limit_capacity": self.rate_limiter.capacity,
            "rate_limit_tokens": self.rate_limiter.tokens,
            "rate_limit_refill_rate": self.rate_limiter.refill_rate,
            "location_rate_limit_minutes": self.location_rate_limit.total_seconds() / 60,
            "active_locations": len(self.location_requests)
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.location_requests.clear()
        logger.info("NOAA Weather cache cleared")
