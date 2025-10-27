"""
Satellite Physics API Endpoints
Real physics orbital mechanics and satellite tracking
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from app.services.satellite_physics import (
    satellite_physics_engine,
    SatellitePosition,
    PassPrediction,
    OrbitalElements
)

router = APIRouter()

# Pydantic models for API responses
class SatellitePositionResponse(BaseModel):
    satellite_id: str
    satellite_name: str
    position: Dict[str, float] = Field(..., description="ECI position coordinates (km)")
    velocity: Dict[str, float] = Field(..., description="ECI velocity vector (km/s)")
    latitude: float = Field(..., description="Latitude in degrees")
    longitude: float = Field(..., description="Longitude in degrees")
    altitude: float = Field(..., description="Altitude in km")
    timestamp: datetime = Field(..., description="Position timestamp")

class PassPredictionResponse(BaseModel):
    satellite_id: str
    satellite_name: str
    start_time: datetime
    end_time: datetime
    duration: float = Field(..., description="Pass duration in minutes")
    max_elevation: float = Field(..., description="Maximum elevation angle in degrees")
    azimuth: float = Field(..., description="Azimuth angle in degrees")
    pass_type: str = Field(..., description="Pass type: daylight, night, or twilight")

class SatelliteStatusResponse(BaseModel):
    engine_running: bool
    total_satellites: int
    satellites: Dict[str, Dict[str, Any]]
    last_update: str

class OrbitalElementsResponse(BaseModel):
    satellite_id: str
    semi_major_axis: float
    eccentricity: float
    inclination: float
    right_ascension: float
    argument_of_perigee: float
    mean_anomaly: float
    epoch: datetime
    mean_motion: float
    bstar: float

@router.get("/satellites/status", response_model=SatelliteStatusResponse)
async def get_satellite_status():
    """Get status of all satellites in the physics engine"""
    try:
        status = await satellite_physics_engine.get_satellite_status()
        return SatelliteStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get satellite status: {str(e)}")

@router.get("/satellites/{satellite_id}/position", response_model=SatellitePositionResponse)
async def get_satellite_position(
    satellite_id: str,
    timestamp: Optional[datetime] = Query(None, description="Specific timestamp for position calculation")
):
    """Get current or historical position of a satellite"""
    try:
        position = await satellite_physics_engine.get_satellite_position(satellite_id, timestamp)
        
        if not position:
            raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
        
        metadata = satellite_physics_engine.satellite_metadata.get(satellite_id, {})
        
        return SatellitePositionResponse(
            satellite_id=satellite_id,
            satellite_name=metadata.get("name", satellite_id),
            position={
                "x": position.position[0],
                "y": position.position[1],
                "z": position.position[2]
            },
            velocity={
                "x": position.velocity[0],
                "y": position.velocity[1],
                "z": position.velocity[2]
            },
            latitude=position.latitude,
            longitude=position.longitude,
            altitude=position.altitude,
            timestamp=position.timestamp
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get satellite position: {str(e)}")

@router.get("/satellites/positions", response_model=List[SatellitePositionResponse])
async def get_all_satellite_positions(
    timestamp: Optional[datetime] = Query(None, description="Specific timestamp for position calculation")
):
    """Get positions of all satellites"""
    try:
        positions = []
        
        for sat_id in satellite_physics_engine.satellites.keys():
            position = await satellite_physics_engine.get_satellite_position(sat_id, timestamp)
            
            if position:
                metadata = satellite_physics_engine.satellite_metadata.get(sat_id, {})
                
                positions.append(SatellitePositionResponse(
                    satellite_id=sat_id,
                    satellite_name=metadata.get("name", sat_id),
                    position={
                        "x": position.position[0],
                        "y": position.position[1],
                        "z": position.position[2]
                    },
                    velocity={
                        "x": position.velocity[0],
                        "y": position.velocity[1],
                        "z": position.velocity[2]
                    },
                    latitude=position.latitude,
                    longitude=position.longitude,
                    altitude=position.altitude,
                    timestamp=position.timestamp
                ))
        
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get satellite positions: {str(e)}")

@router.get("/satellites/predictions", response_model=List[PassPredictionResponse])
async def predict_orbital_passes(
    latitude: float = Query(..., description="Observer latitude in degrees"),
    longitude: float = Query(..., description="Observer longitude in degrees"),
    altitude: float = Query(0.0, description="Observer altitude in km"),
    satellite_ids: Optional[List[str]] = Query(None, description="Specific satellite IDs to predict"),
    days_ahead: int = Query(7, ge=1, le=30, description="Days ahead to predict (1-30)"),
    min_elevation: float = Query(10.0, ge=0, le=90, description="Minimum elevation angle in degrees")
):
    """Predict orbital passes for observer location"""
    try:
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90 degrees")
        
        if not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180 degrees")
        
        predictions = await satellite_physics_engine.predict_orbital_passes(
            observer_lat=latitude,
            observer_lng=longitude,
            observer_alt=altitude,
            satellite_ids=satellite_ids,
            days_ahead=days_ahead,
            min_elevation=min_elevation
        )
        
        return [
            PassPredictionResponse(
                satellite_id=p.satellite_id,
                satellite_name=p.satellite_name,
                start_time=p.start_time,
                end_time=p.end_time,
                duration=p.duration,
                max_elevation=p.max_elevation,
                azimuth=p.azimuth,
                pass_type=p.pass_type
            )
            for p in predictions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict orbital passes: {str(e)}")

@router.get("/satellites/{satellite_id}/next-pass", response_model=PassPredictionResponse)
async def get_next_satellite_pass(
    satellite_id: str,
    latitude: float = Query(..., description="Observer latitude in degrees"),
    longitude: float = Query(..., description="Observer longitude in degrees"),
    altitude: float = Query(0.0, description="Observer altitude in km"),
    min_elevation: float = Query(10.0, ge=0, le=90, description="Minimum elevation angle in degrees")
):
    """Get the next orbital pass for a specific satellite"""
    try:
        predictions = await satellite_physics_engine.predict_orbital_passes(
            observer_lat=latitude,
            observer_lng=longitude,
            observer_alt=altitude,
            satellite_ids=[satellite_id],
            days_ahead=7,
            min_elevation=min_elevation
        )
        
        if not predictions:
            raise HTTPException(
                status_code=404, 
                detail=f"No passes found for satellite {satellite_id} in the next 7 days"
            )
        
        next_pass = predictions[0]  # First pass is the next one
        
        return PassPredictionResponse(
            satellite_id=next_pass.satellite_id,
            satellite_name=next_pass.satellite_name,
            start_time=next_pass.start_time,
            end_time=next_pass.end_time,
            duration=next_pass.duration,
            max_elevation=next_pass.max_elevation,
            azimuth=next_pass.azimuth,
            pass_type=next_pass.pass_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next satellite pass: {str(e)}")

@router.get("/satellites/{satellite_id}/orbital-elements", response_model=OrbitalElementsResponse)
async def get_satellite_orbital_elements(satellite_id: str):
    """Get orbital elements for a specific satellite"""
    try:
        if satellite_id not in satellite_physics_engine.satellites:
            raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
        
        satellite = satellite_physics_engine.satellites[satellite_id]
        
        # Extract orbital elements from SGP4 satellite object
        orbital_elements = OrbitalElementsResponse(
            satellite_id=satellite_id,
            semi_major_axis=satellite.a,  # Semi-major axis in km
            eccentricity=satellite.ecco,  # Eccentricity
            inclination=satellite.inclo,  # Inclination in degrees
            right_ascension=satellite.nodeo,  # Right ascension in degrees
            argument_of_perigee=satellite.argpo,  # Argument of perigee in degrees
            mean_anomaly=satellite.mo,  # Mean anomaly in degrees
            epoch=datetime.utcnow(),  # Epoch (simplified)
            mean_motion=satellite.no,  # Mean motion in rev/day
            bstar=satellite.bstar  # Drag coefficient
        )
        
        return orbital_elements
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orbital elements: {str(e)}")

@router.post("/satellites/{satellite_id}/track")
async def start_satellite_tracking(satellite_id: str):
    """Start real-time tracking for a specific satellite"""
    try:
        if satellite_id not in satellite_physics_engine.satellites:
            raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
        
        # In a real implementation, this would start a WebSocket connection
        # for real-time position updates
        
        return {
            "message": f"Started tracking satellite {satellite_id}",
            "satellite_id": satellite_id,
            "tracking_active": True,
            "update_interval": satellite_physics_engine.update_interval
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start satellite tracking: {str(e)}")

@router.delete("/satellites/{satellite_id}/track")
async def stop_satellite_tracking(satellite_id: str):
    """Stop real-time tracking for a specific satellite"""
    try:
        if satellite_id not in satellite_physics_engine.satellites:
            raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
        
        # In a real implementation, this would stop WebSocket connections
        
        return {
            "message": f"Stopped tracking satellite {satellite_id}",
            "satellite_id": satellite_id,
            "tracking_active": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop satellite tracking: {str(e)}")

@router.get("/satellites/constellation")
async def get_satellite_constellation():
    """Get information about the satellite constellation"""
    try:
        constellation = {
            "total_satellites": len(satellite_physics_engine.satellites),
            "satellites": []
        }
        
        for sat_id, metadata in satellite_physics_engine.satellite_metadata.items():
            constellation["satellites"].append({
                "id": sat_id,
                "name": metadata.get("name", sat_id),
                "mission_type": metadata.get("mission_type", "unknown"),
                "capabilities": metadata.get("capabilities", []),
                "last_update": metadata.get("last_position", {}).get("timestamp")
            })
        
        return constellation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get constellation info: {str(e)}")
