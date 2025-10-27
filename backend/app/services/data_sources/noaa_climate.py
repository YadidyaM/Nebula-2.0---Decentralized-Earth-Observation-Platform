import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.config import settings

logger = logging.getLogger(__name__)

class NOAAClimateClient:
    """NOAA Climate API client for weather and climate data"""
    
    def __init__(self):
        self.api_token = settings.noaa_api_token
        self.base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2"
        self.headers = {"token": self.api_token} if self.api_token else {}
        self.cache_duration = timedelta(hours=2)
        self.cache: Dict[str, Any] = {}
    
    async def get_weather_data(self, lat: float, lng: float, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get weather data for a location and date range"""
        try:
            cache_key = f"weather_{lat}_{lng}_{start_date}_{end_date}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Get station data first
            stations = await self._get_nearby_stations(lat, lng)
            if not stations:
                logger.warning(f"No weather stations found near {lat}, {lng}")
                return []
            
            weather_data = []
            for station in stations[:3]:  # Limit to 3 closest stations
                station_data = await self._get_station_data(station["id"], start_date, end_date)
                if station_data:
                    weather_data.extend(station_data)
            
            self._cache_data(cache_key, weather_data)
            logger.info(f"Retrieved weather data for {lat}, {lng}")
            return weather_data
            
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return []
    
    async def get_climate_normals(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Get climate normals for a location"""
        try:
            cache_key = f"climate_normals_{lat}_{lng}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # This would require specific NOAA API calls
            # For now, return mock data
            normals = {
                "location": {"lat": lat, "lng": lng},
                "temperature": {
                    "january": {"avg": -5.0, "min": -15.0, "max": 5.0},
                    "july": {"avg": 25.0, "min": 15.0, "max": 35.0},
                    "annual": {"avg": 10.0, "min": -10.0, "max": 30.0}
                },
                "precipitation": {
                    "annual": 800.0,  # mm
                    "seasonal": {"spring": 200, "summer": 250, "fall": 200, "winter": 150}
                },
                "source": "NOAA Climate",
                "confidence": 0.90
            }
            
            self._cache_data(cache_key, normals)
            return normals
            
        except Exception as e:
            logger.error(f"Failed to get climate normals: {e}")
            return None
    
    async def _get_nearby_stations(self, lat: float, lng: float) -> List[Dict[str, Any]]:
        """Get nearby weather stations"""
        try:
            # Mock station data for now
            stations = [
                {"id": "USW00094728", "name": "New York Central Park", "distance": 5.2},
                {"id": "USW00094789", "name": "Newark Airport", "distance": 12.8},
                {"id": "USW00094745", "name": "LaGuardia Airport", "distance": 8.5}
            ]
            return stations
            
        except Exception as e:
            logger.error(f"Failed to get nearby stations: {e}")
            return []
    
    async def _get_station_data(self, station_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get data from a specific weather station"""
        try:
            # Mock weather data
            weather_data = [
                {
                    "station_id": station_id,
                    "date": start_date,
                    "temperature": {"max": 25.0, "min": 15.0, "avg": 20.0},
                    "precipitation": 5.2,
                    "humidity": 65.0,
                    "wind_speed": 12.5,
                    "pressure": 1013.2,
                    "source": "NOAA Weather"
                }
            ]
            return weather_data
            
        except Exception as e:
            logger.error(f"Failed to get station data: {e}")
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

class USGSClient:
    """USGS API client for earthquake and geological data"""
    
    def __init__(self):
        self.api_key = settings.usgs_api_key
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1"
        self.cache_duration = timedelta(minutes=30)
        self.cache: Dict[str, Any] = {}
    
    async def get_earthquakes(self, start_time: str, end_time: str, min_magnitude: float = 4.0) -> List[Dict[str, Any]]:
        """Get earthquake data from USGS"""
        try:
            cache_key = f"earthquakes_{start_time}_{end_time}_{min_magnitude}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            params = {
                "format": "geojson",
                "starttime": start_time,
                "endtime": end_time,
                "minmagnitude": min_magnitude,
                "orderby": "time"
            }
            
            response = requests.get(
                f"{self.base_url}/query",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
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
                        "coordinates": {
                            "lng": coordinates[0] if len(coordinates) > 0 else None,
                            "lat": coordinates[1] if len(coordinates) > 1 else None,
                            "depth": coordinates[2] if len(coordinates) > 2 else None
                        },
                        "tsunami": properties.get("tsunami", 0),
                        "alert": properties.get("alert"),
                        "source": "USGS Earthquake",
                        "confidence": 0.95
                    }
                    earthquakes.append(earthquake)
                
                self._cache_data(cache_key, earthquakes)
                logger.info(f"Retrieved {len(earthquakes)} earthquakes from USGS")
                return earthquakes
            else:
                logger.error(f"USGS API error: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get earthquakes: {e}")
            return []
    
    async def get_earthquake_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific earthquake"""
        try:
            cache_key = f"earthquake_details_{event_id}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            response = requests.get(
                f"{self.base_url}/query",
                params={"eventid": event_id, "format": "geojson"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                
                if features:
                    feature = features[0]
                    properties = feature.get("properties", {})
                    geometry = feature.get("geometry", {})
                    coordinates = geometry.get("coordinates", [])
                    
                    earthquake = {
                        "id": feature.get("id"),
                        "magnitude": properties.get("mag"),
                        "place": properties.get("place"),
                        "time": properties.get("time"),
                        "coordinates": {
                            "lng": coordinates[0] if len(coordinates) > 0 else None,
                            "lat": coordinates[1] if len(coordinates) > 1 else None,
                            "depth": coordinates[2] if len(coordinates) > 2 else None
                        },
                        "tsunami": properties.get("tsunami", 0),
                        "alert": properties.get("alert"),
                        "felt": properties.get("felt"),
                        "cdi": properties.get("cdi"),
                        "mmi": properties.get("mmi"),
                        "source": "USGS Earthquake",
                        "confidence": 0.95
                    }
                    
                    self._cache_data(cache_key, earthquake)
                    return earthquake
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get earthquake details: {e}")
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
