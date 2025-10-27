from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    FOREST_GUARDIAN = "forest_guardian"
    ICE_SENTINEL = "ice_sentinel"
    STORM_TRACKER = "storm_tracker"
    URBAN_MONITOR = "urban_monitor"
    WATER_WATCHER = "water_watcher"
    SECURITY_SENTINEL = "security_sentinel"
    LAND_SURVEYOR = "land_surveyor"
    DISASTER_RESPONDER = "disaster_responder"

class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

class AgentRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class Position(BaseModel):
    lat: float
    lng: float
    alt: float  # altitude in meters

class Agent(BaseModel):
    id: str
    name: str
    type: AgentType
    status: AgentStatus
    rarity: AgentRarity
    position: Position
    wallet_address: str
    nft_mint: Optional[str] = None
    staked: bool = False
    staked_at: Optional[datetime] = None
    rewards_earned: float = 0.0
    missions_completed: int = 0
    success_rate: float = 0.0
    last_update: datetime
    specialization: List[str] = []
    health_score: float = 100.0
    battery_level: float = 100.0
    signal_strength: float = 100.0
    temperature: float = 22.0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class AgentUpdate(BaseModel):
    status: Optional[AgentStatus] = None
    position: Optional[Position] = None
    staked: Optional[bool] = None
    health_score: Optional[float] = None
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None
    temperature: Optional[float] = None

class AgentTelemetry(BaseModel):
    agent_id: str
    timestamp: datetime
    position: Position
    velocity: Optional[Dict[str, float]] = None
    health_score: float
    battery_level: float
    signal_strength: float
    temperature: float
    mission_id: Optional[str] = None
    status: AgentStatus
    data: Dict[str, Any] = {}
