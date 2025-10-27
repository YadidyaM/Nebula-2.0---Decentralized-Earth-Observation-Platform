from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TelemetryType(str, Enum):
    POSITION = "position"
    VELOCITY = "velocity"
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    SIGNAL = "signal"
    SYSTEM_STATUS = "system_status"
    MISSION_DATA = "mission_data"
    ENVIRONMENTAL_DATA = "environmental_data"

class TelemetryData(BaseModel):
    id: str
    agent_id: str
    type: TelemetryType
    timestamp: datetime
    data: Dict[str, Any]
    position: Optional[Dict[str, float]] = None
    velocity: Optional[Dict[str, float]] = None
    altitude: Optional[float] = None
    temperature: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = None
    mission_id: Optional[str] = None
    quality_score: float = 1.0
    processed: bool = False

class PositionData(BaseModel):
    lat: float
    lng: float
    alt: float
    accuracy: Optional[float] = None
    timestamp: datetime

class VelocityData(BaseModel):
    vx: float
    vy: float
    vz: float
    speed: float
    direction: Optional[float] = None
    timestamp: datetime

class EnvironmentalData(BaseModel):
    agent_id: str
    timestamp: datetime
    location: Dict[str, float]
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation: Optional[float] = None
    air_quality: Optional[Dict[str, float]] = None
    satellite_data: Optional[Dict[str, Any]] = None
    anomaly_detected: bool = False
    risk_level: Optional[str] = None
