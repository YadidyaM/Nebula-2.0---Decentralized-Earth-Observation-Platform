from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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
    results: Optional[dict] = None
    confidence_score: Optional[float] = None
    anomaly_detected: Optional[bool] = None
    blockchain_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None
    arweave_hash: Optional[str] = None

class MissionCreate(BaseModel):
    name: str
    type: MissionType
    priority: Priority
    target_area: TargetArea
    agents: List[str]

class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    results: Optional[dict] = None
    confidence_score: Optional[float] = None
    anomaly_detected: Optional[bool] = None

# Helper function to convert ObjectId to string
def mission_helper(mission) -> dict:
    if mission:
        mission["id"] = str(mission["_id"])
        del mission["_id"]
    return mission

@router.get("/", response_model=List[Mission])
async def get_missions(
    status: Optional[MissionStatus] = None,
    type: Optional[MissionType] = None,
    priority: Optional[Priority] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    skip: int = 0
):
    """Get missions with optional filtering and pagination"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status.value
        if type:
            filter_query["type"] = type.value
        if priority:
            filter_query["priority"] = priority.value
        if start_date:
            filter_query["start_time"] = {"$gte": start_date}
        if end_date:
            filter_query["end_time"] = {"$lte": end_date}
        
        # Execute query with pagination
        cursor = missions_collection.find(filter_query).skip(skip).limit(limit).sort("start_time", -1)
        missions = []
        
        async for mission in cursor:
            missions.append(mission_helper(mission))
        
        return missions
        
    except Exception as e:
        logger.error(f"Error fetching missions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{mission_id}", response_model=Mission)
async def get_mission(mission_id: str):
    """Get a specific mission by ID"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        return mission_helper(mission)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=Mission)
async def create_mission(mission_data: MissionCreate):
    """Create a new mission with agent assignment and blockchain recording"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        # Create mission document
        mission_doc = {
            "name": mission_data.name,
            "type": mission_data.type.value,
            "status": MissionStatus.PENDING.value,
            "priority": mission_data.priority.value,
            "target_area": mission_data.target_area.dict(),
            "start_time": datetime.now(),
            "end_time": None,
            "agents": mission_data.agents,
            "results": None,
            "confidence_score": None,
            "anomaly_detected": None,
            "blockchain_hash": None,
            "ipfs_hash": None,
            "arweave_hash": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert mission
        result = await missions_collection.insert_one(mission_doc)
        mission_doc["_id"] = result.inserted_id
        
        # TODO: Assign agents to mission
        # TODO: Record mission creation on blockchain
        
        logger.info(f"Created mission {result.inserted_id} with name: {mission_data.name}")
        return mission_helper(mission_doc)
        
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{mission_id}", response_model=Mission)
async def update_mission(mission_id: str, update_data: MissionUpdate):
    """Update a mission with status updates and result storage"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        # Build update document
        update_doc = {"updated_at": datetime.now()}
        if update_data.status:
            update_doc["status"] = update_data.status.value
        if update_data.results:
            update_doc["results"] = update_data.results
        if update_data.confidence_score is not None:
            update_doc["confidence_score"] = update_data.confidence_score
        if update_data.anomaly_detected is not None:
            update_doc["anomaly_detected"] = update_data.anomaly_detected
        
        # Update mission
        result = await missions_collection.update_one(
            {"_id": ObjectId(mission_id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Get updated mission
        updated_mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        
        # TODO: Broadcast mission update via WebSocket
        # TODO: Update blockchain record if status changed to completed
        
        logger.info(f"Updated mission {mission_id}")
        return mission_helper(updated_mission)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{mission_id}")
async def delete_mission(mission_id: str):
    """Delete a mission with cleanup"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        # Check if mission exists
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Delete mission
        result = await missions_collection.delete_one({"_id": ObjectId(mission_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # TODO: Clean up associated telemetry data
        # TODO: Update agent assignments
        # TODO: Remove blockchain records if needed
        
        logger.info(f"Deleted mission {mission_id}")
        return {"message": "Mission deleted successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error deleting mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{mission_id}/results")
async def get_mission_results(mission_id: str):
    """Get detailed results for a mission"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        if not mission.get("results"):
            raise HTTPException(status_code=404, detail="Mission results not available")
        
        return mission["results"]
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching mission results {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{mission_id}/agents")
async def get_mission_agents(mission_id: str):
    """Get agents assigned to a mission"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        return {"agents": mission.get("agents", [])}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching mission agents {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{mission_id}/assign")
async def assign_agent_to_mission(mission_id: str, agent_id: str):
    """Assign an agent to a mission"""
    try:
        db = await get_database()
        missions_collection = db.missions
        
        # Check if mission exists
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Add agent to mission if not already assigned
        if agent_id not in mission.get("agents", []):
            await missions_collection.update_one(
                {"_id": ObjectId(mission_id)},
                {"$push": {"agents": agent_id}, "$set": {"updated_at": datetime.now()}}
            )
        
        logger.info(f"Assigned agent {agent_id} to mission {mission_id}")
        return {"message": f"Agent {agent_id} assigned to mission {mission_id}"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error assigning agent to mission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
