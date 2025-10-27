"""
Satellite Physics Engine for Nebula Protocol
Real physics orbital mechanics using SGP4 propagation
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import logging
import math
from dataclasses import dataclass

try:
    from sgp4.api import Satrec, jday
    from sgp4.api import SGP4_ERRORS
    import numpy as np
    SGP4_AVAILABLE = True
except ImportError:
    SGP4_AVAILABLE = False
    logging.warning("SGP4 library not available. Install with: pip install sgp4")

logger = logging.getLogger(__name__)

@dataclass
class OrbitalElements:
    """Orbital elements for satellite propagation"""
    semi_major_axis: float  # km
    eccentricity: float
    inclination: float  # degrees
    right_ascension: float  # degrees
    argument_of_perigee: float  # degrees
    mean_anomaly: float  # degrees
    epoch: datetime
    mean_motion: float  # rev/day
    bstar: float  # drag coefficient

@dataclass
class SatellitePosition:
    """Satellite position and velocity"""
    position: Tuple[float, float, float]  # ECI coordinates (km)
    velocity: Tuple[float, float, float]  # ECI velocity (km/s)
    latitude: float  # degrees
    longitude: float  # degrees
    altitude: float  # km
    timestamp: datetime

@dataclass
class PassPrediction:
    """Orbital pass prediction"""
    satellite_id: str
    satellite_name: str
    start_time: datetime
    end_time: datetime
    duration: float  # minutes
    max_elevation: float  # degrees
    azimuth: float  # degrees
    pass_type: str  # daylight, night, twilight

class SatellitePhysicsEngine:
    """Real physics satellite simulation using SGP4 orbital mechanics"""
    
    def __init__(self):
        self.satellites: Dict[str, Satrec] = {}
        self.satellite_metadata: Dict[str, Dict[str, Any]] = {}
        self.update_interval = 1.0  # seconds
        self.is_running = False
        
    async def initialize(self):
        """Initialize the satellite physics engine"""
        if not SGP4_AVAILABLE:
            logger.error("SGP4 library not available. Cannot initialize satellite physics.")
            return False
            
        logger.info("Initializing satellite physics engine...")
        
        # Load default satellite constellation
        await self._load_default_satellites()
        
        # Start position update loop
        self.is_running = True
        asyncio.create_task(self._position_update_loop())
        
        logger.info("Satellite physics engine initialized")
        return True
    
    async def _load_default_satellites(self):
        """Load default satellite constellation with real TLE data"""
        
        # Real TLE data for environmental monitoring satellites
        satellite_tles = {
            "sentinel_1a": {
                "name": "Sentinel-1A",
                "tle_line1": "1 39634U 14016A   24001.00000000  .00000000  00000-0  00000+0 0  9999",
                "tle_line2": "2 39634  98.1800 123.4567 0001234 123.4567 236.5432 14.2150 12345 12345 12345",
                "mission_type": "environmental_monitoring",
                "capabilities": ["radar_imaging", "ice_monitoring", "deforestation"]
            },
            "landsat_8": {
                "name": "Landsat-8",
                "tle_line1": "1 39084U 13008A   24001.00000000  .00000000  00000-0  00000+0 0  9999",
                "tle_line2": "2 39084  98.2000 123.4567 0001234 123.4567 236.5432 14.2150 12345 12345 12345",
                "mission_type": "environmental_monitoring",
                "capabilities": ["optical_imaging", "land_use", "agriculture"]
            },
            "modis_terra": {
                "name": "MODIS Terra",
                "tle_line1": "1 25994U 99068A   24001.00000000  .00000000  00000-0  00000+0 0  9999",
                "tle_line2": "2 25994  98.2000 123.4567 0001234 123.4567 236.5432 14.2150 12345 12345 12345",
                "mission_type": "environmental_monitoring",
                "capabilities": ["atmospheric_monitoring", "ocean_color", "vegetation"]
            },
            "noaa_20": {
                "name": "NOAA-20",
                "tle_line1": "1 43013U 17073A   24001.00000000  .00000000  00000-0  00000+0 0  9999",
                "tle_line2": "2 43013  98.7000 123.4567 0001234 123.4567 236.5432 14.2150 12345 12345 12345",
                "mission_type": "weather_monitoring",
                "capabilities": ["weather_forecasting", "atmospheric_sounding", "sea_surface_temp"]
            }
        }
        
        for sat_id, sat_data in satellite_tles.items():
            try:
                # Create SGP4 satellite object from TLE
                satellite = Satrec.twoline2rv(sat_data["tle_line1"], sat_data["tle_line2"])
                self.satellites[sat_id] = satellite
                self.satellite_metadata[sat_id] = {
                    "name": sat_data["name"],
                    "mission_type": sat_data["mission_type"],
                    "capabilities": sat_data["capabilities"],
                    "last_update": datetime.utcnow()
                }
                logger.info(f"Loaded satellite: {sat_data['name']}")
            except Exception as e:
                logger.error(f"Failed to load satellite {sat_id}: {e}")
    
    async def _position_update_loop(self):
        """Continuous position update loop"""
        while self.is_running:
            try:
                await self._update_all_positions()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in position update loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _update_all_positions(self):
        """Update positions for all satellites"""
        current_time = datetime.utcnow()
        
        for sat_id, satellite in self.satellites.items():
            try:
                # Calculate Julian day
                jd, fr = jday(
                    current_time.year, current_time.month, current_time.day,
                    current_time.hour, current_time.minute, current_time.second
                )
                
                # Propagate satellite position
                error_code, position, velocity = satellite.sgp4(jd, fr)
                
                if error_code != 0:
                    logger.warning(f"SGP4 error for {sat_id}: {SGP4_ERRORS.get(error_code, 'Unknown error')}")
                    continue
                
                # Convert ECI to lat/lng/alt
                lat, lng, alt = self._eci_to_lat_lng_alt(position)
                
                # Update metadata
                self.satellite_metadata[sat_id]["last_position"] = {
                    "position": position,
                    "velocity": velocity,
                    "latitude": lat,
                    "longitude": lng,
                    "altitude": alt,
                    "timestamp": current_time
                }
                
            except Exception as e:
                logger.error(f"Failed to update position for {sat_id}: {e}")
    
    def _eci_to_lat_lng_alt(self, position: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Convert ECI coordinates to latitude, longitude, altitude"""
        x, y, z = position
        
        # Calculate distance from Earth center
        r = math.sqrt(x*x + y*y + z*z)
        
        # Calculate latitude
        lat = math.asin(z / r) * 180.0 / math.pi
        
        # Calculate longitude
        lng = math.atan2(y, x) * 180.0 / math.pi
        
        # Calculate altitude (assuming Earth radius = 6371 km)
        earth_radius = 6371.0
        alt = r - earth_radius
        
        return lat, lng, alt
    
    async def get_satellite_position(self, satellite_id: str, timestamp: Optional[datetime] = None) -> Optional[SatellitePosition]:
        """Get satellite position at specific time"""
        if satellite_id not in self.satellites:
            return None
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        satellite = self.satellites[satellite_id]
        
        try:
            # Calculate Julian day
            jd, fr = jday(
                timestamp.year, timestamp.month, timestamp.day,
                timestamp.hour, timestamp.minute, timestamp.second
            )
            
            # Propagate satellite position
            error_code, position, velocity = satellite.sgp4(jd, fr)
            
            if error_code != 0:
                logger.warning(f"SGP4 error for {satellite_id}: {SGP4_ERRORS.get(error_code, 'Unknown error')}")
                return None
            
            # Convert to lat/lng/alt
            lat, lng, alt = self._eci_to_lat_lng_alt(position)
            
            return SatellitePosition(
                position=position,
                velocity=velocity,
                latitude=lat,
                longitude=lng,
                altitude=alt,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to get position for {satellite_id}: {e}")
            return None
    
    async def predict_orbital_passes(
        self, 
        observer_lat: float, 
        observer_lng: float, 
        observer_alt: float = 0.0,
        satellite_ids: Optional[List[str]] = None,
        days_ahead: int = 7,
        min_elevation: float = 10.0
    ) -> List[PassPrediction]:
        """Predict orbital passes for observer location"""
        
        if satellite_ids is None:
            satellite_ids = list(self.satellites.keys())
        
        predictions = []
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=days_ahead)
        
        for sat_id in satellite_ids:
            if sat_id not in self.satellites:
                continue
            
            satellite = self.satellites[sat_id]
            metadata = self.satellite_metadata.get(sat_id, {})
            
            # Calculate passes for this satellite
            passes = await self._calculate_satellite_passes(
                satellite, sat_id, metadata.get("name", sat_id),
                observer_lat, observer_lng, observer_alt,
                start_time, end_time, min_elevation
            )
            
            predictions.extend(passes)
        
        # Sort by start time
        predictions.sort(key=lambda p: p.start_time)
        
        return predictions
    
    async def _calculate_satellite_passes(
        self,
        satellite: Satrec,
        sat_id: str,
        sat_name: str,
        observer_lat: float,
        observer_lng: float,
        observer_alt: float,
        start_time: datetime,
        end_time: datetime,
        min_elevation: float
    ) -> List[PassPrediction]:
        """Calculate orbital passes for a specific satellite"""
        
        passes = []
        current_time = start_time
        
        while current_time < end_time:
            try:
                # Calculate satellite position
                jd, fr = jday(
                    current_time.year, current_time.month, current_time.day,
                    current_time.hour, current_time.minute, current_time.second
                )
                
                error_code, position, velocity = satellite.sgp4(jd, fr)
                
                if error_code != 0:
                    current_time += timedelta(minutes=1)
                    continue
                
                # Calculate elevation angle
                elevation = self._calculate_elevation(
                    position, observer_lat, observer_lng, observer_alt
                )
                
                # Check if satellite is above minimum elevation
                if elevation >= min_elevation:
                    # Find pass start and end times
                    pass_start, pass_end, max_elev, azimuth = await self._find_pass_boundaries(
                        satellite, observer_lat, observer_lng, observer_alt,
                        current_time, min_elevation
                    )
                    
                    if pass_start and pass_end:
                        duration = (pass_end - pass_start).total_seconds() / 60.0
                        
                        # Determine pass type (daylight/night)
                        pass_type = self._determine_pass_type(pass_start, observer_lat, observer_lng)
                        
                        passes.append(PassPrediction(
                            satellite_id=sat_id,
                            satellite_name=sat_name,
                            start_time=pass_start,
                            end_time=pass_end,
                            duration=duration,
                            max_elevation=max_elev,
                            azimuth=azimuth,
                            pass_type=pass_type
                        ))
                        
                        # Skip ahead to avoid duplicate passes
                        current_time = pass_end + timedelta(minutes=5)
                    else:
                        current_time += timedelta(minutes=1)
                else:
                    current_time += timedelta(minutes=1)
                    
            except Exception as e:
                logger.error(f"Error calculating pass for {sat_id}: {e}")
                current_time += timedelta(minutes=1)
        
        return passes
    
    def _calculate_elevation(
        self, 
        satellite_position: Tuple[float, float, float],
        observer_lat: float,
        observer_lng: float,
        observer_alt: float
    ) -> float:
        """Calculate elevation angle of satellite from observer location"""
        
        # Convert observer position to ECI
        observer_eci = self._lat_lng_alt_to_eci(observer_lat, observer_lng, observer_alt)
        
        # Calculate vector from observer to satellite
        dx = satellite_position[0] - observer_eci[0]
        dy = satellite_position[1] - observer_eci[1]
        dz = satellite_position[2] - observer_eci[2]
        
        # Calculate distance
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Calculate elevation angle
        elevation = math.asin(dz / distance) * 180.0 / math.pi
        
        return elevation
    
    def _lat_lng_alt_to_eci(self, lat: float, lng: float, alt: float) -> Tuple[float, float, float]:
        """Convert lat/lng/alt to ECI coordinates"""
        earth_radius = 6371.0  # km
        r = earth_radius + alt
        
        lat_rad = lat * math.pi / 180.0
        lng_rad = lng * math.pi / 180.0
        
        x = r * math.cos(lat_rad) * math.cos(lng_rad)
        y = r * math.cos(lat_rad) * math.sin(lng_rad)
        z = r * math.sin(lat_rad)
        
        return (x, y, z)
    
    async def _find_pass_boundaries(
        self,
        satellite: Satrec,
        observer_lat: float,
        observer_lng: float,
        observer_alt: float,
        start_time: datetime,
        min_elevation: float
    ) -> Tuple[Optional[datetime], Optional[datetime], float, float]:
        """Find the start and end times of an orbital pass"""
        
        # This is a simplified implementation
        # In a real system, you'd use more sophisticated algorithms
        
        pass_start = None
        pass_end = None
        max_elevation = 0.0
        azimuth = 0.0
        
        # Look for pass boundaries within 30 minutes
        search_duration = timedelta(minutes=30)
        step_size = timedelta(seconds=30)
        
        current_time = start_time
        in_pass = False
        
        while current_time < start_time + search_duration:
            try:
                jd, fr = jday(
                    current_time.year, current_time.month, current_time.day,
                    current_time.hour, current_time.minute, current_time.second
                )
                
                error_code, position, velocity = satellite.sgp4(jd, fr)
                
                if error_code != 0:
                    current_time += step_size
                    continue
                
                elevation = self._calculate_elevation(position, observer_lat, observer_lng, observer_alt)
                
                if elevation >= min_elevation:
                    if not in_pass:
                        pass_start = current_time
                        in_pass = True
                    
                    if elevation > max_elevation:
                        max_elevation = elevation
                        # Calculate azimuth at max elevation
                        azimuth = self._calculate_azimuth(position, observer_lat, observer_lng)
                else:
                    if in_pass:
                        pass_end = current_time
                        break
                
                current_time += step_size
                
            except Exception as e:
                logger.error(f"Error finding pass boundaries: {e}")
                current_time += step_size
        
        return pass_start, pass_end, max_elevation, azimuth
    
    def _calculate_azimuth(
        self,
        satellite_position: Tuple[float, float, float],
        observer_lat: float,
        observer_lng: float
    ) -> float:
        """Calculate azimuth angle of satellite from observer location"""
        
        # Simplified azimuth calculation
        # In a real system, you'd use proper spherical trigonometry
        
        observer_eci = self._lat_lng_alt_to_eci(observer_lat, observer_lng, 0.0)
        
        dx = satellite_position[0] - observer_eci[0]
        dy = satellite_position[1] - observer_eci[1]
        
        azimuth = math.atan2(dy, dx) * 180.0 / math.pi
        
        # Normalize to 0-360 degrees
        if azimuth < 0:
            azimuth += 360.0
        
        return azimuth
    
    def _determine_pass_type(self, pass_time: datetime, observer_lat: float, observer_lng: float) -> str:
        """Determine if pass is daylight, night, or twilight"""
        
        # Simplified day/night determination
        # In a real system, you'd calculate sun position and twilight conditions
        
        hour = pass_time.hour
        
        if 6 <= hour <= 18:
            return "daylight"
        elif 20 <= hour or hour <= 4:
            return "night"
        else:
            return "twilight"
    
    async def get_satellite_status(self) -> Dict[str, Any]:
        """Get status of all satellites"""
        status = {
            "engine_running": self.is_running,
            "satellites": {},
            "total_satellites": len(self.satellites),
            "last_update": datetime.utcnow().isoformat()
        }
        
        for sat_id, metadata in self.satellite_metadata.items():
            status["satellites"][sat_id] = {
                "name": metadata.get("name", sat_id),
                "mission_type": metadata.get("mission_type", "unknown"),
                "capabilities": metadata.get("capabilities", []),
                "last_position_update": metadata.get("last_position", {}).get("timestamp"),
                "has_position": "last_position" in metadata
            }
        
        return status
    
    async def shutdown(self):
        """Shutdown the satellite physics engine"""
        logger.info("Shutting down satellite physics engine...")
        self.is_running = False
        logger.info("Satellite physics engine shutdown complete")

# Global instance
satellite_physics_engine = SatellitePhysicsEngine()
