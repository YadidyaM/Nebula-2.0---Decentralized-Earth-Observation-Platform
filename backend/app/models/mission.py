from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MissionType(str, Enum):
    FORESTRY = "forestry"
    CRYOSPHERE = "cryosphere"
    DISASTER_MANAGEMENT = "disaster_management"
    SECURITY = "security"
    WEATHER = "weather"
    HYDROLOGY = "hydrology"
    URBAN_INFRASTRUCTURE = "urban_infrastructure"
    LAND_MONITORING = "land_monitoring"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MissionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class TargetArea(BaseModel):
    lat: float
    lng: float
    radius: float  # in kilometers

class Mission(BaseModel):
    id: str
    name: str
    type: MissionType
    status: MissionStatus
    priority: Priority
    target_area: TargetArea
    start_time: datetime
    end_time: Optional[datetime] = None
    agents: List[str]
    results: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    anomaly_detected: Optional[bool] = None
    blockchain_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None
    arweave_hash: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class MissionCreate(BaseModel):
    name: str
    type: MissionType
    priority: Priority
    target_area: TargetArea
    agents: List[str]

class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    results: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    anomaly_detected: Optional[bool] = None
    blockchain_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None
    arweave_hash: Optional[str] = None
