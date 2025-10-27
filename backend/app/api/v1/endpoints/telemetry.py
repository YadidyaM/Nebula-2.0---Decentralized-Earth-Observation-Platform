from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
from bson import ObjectId
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class TelemetryType(str, Enum):
    POSITION = "position"
    VELOCITY = "velocity"
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    SIGNAL = "signal"
    SYSTEM_STATUS = "system_status"

class TelemetryData(BaseModel):
    id: str
    agent_id: str
    type: TelemetryType
    timestamp: datetime
    data: dict
    position: Optional[dict] = None
    velocity: Optional[dict] = None
    altitude: Optional[float] = None
    temperature: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = None

class PositionData(BaseModel):
    lat: float
    lng: float
    alt: float

class VelocityData(BaseModel):
    vx: float
    vy: float
    vz: float
    speed: float

class TelemetryCreate(BaseModel):
    agent_id: str
    type: TelemetryType
    data: dict
    position: Optional[dict] = None
    velocity: Optional[dict] = None
    altitude: Optional[float] = None
    temperature: Optional[float] = None
    battery: Optional[float] = None
    signal_strength: Optional[float] = None

# Helper function to convert ObjectId to string
def telemetry_helper(telemetry) -> dict:
    if telemetry:
        telemetry["id"] = str(telemetry["_id"])
        del telemetry["_id"]
    return telemetry

@router.get("/", response_model=List[TelemetryData])
async def get_telemetry(
    agent_id: Optional[str] = None,
    type: Optional[TelemetryType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    skip: int = 0
):
    """Get telemetry data with optional filtering"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Build filter query
        filter_query = {}
        if agent_id:
            filter_query["agent_id"] = agent_id
        if type:
            filter_query["type"] = type.value
        if start_time:
            filter_query["timestamp"] = {"$gte": start_time}
        if end_time:
            if "timestamp" in filter_query:
                filter_query["timestamp"]["$lte"] = end_time
            else:
                filter_query["timestamp"] = {"$lte": end_time}
        
        # Execute query with pagination
        cursor = telemetry_collection.find(filter_query).skip(skip).limit(limit).sort("timestamp", -1)
        telemetry_data = []
        
        async for telemetry in cursor:
            telemetry_data.append(telemetry_helper(telemetry))
        
        return telemetry_data
        
    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=TelemetryData)
async def create_telemetry(telemetry_data: TelemetryCreate):
    """Create new telemetry data for data ingestion from agents"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Create telemetry document
        telemetry_doc = {
            "agent_id": telemetry_data.agent_id,
            "type": telemetry_data.type.value,
            "timestamp": datetime.now(),
            "data": telemetry_data.data,
            "position": telemetry_data.position,
            "velocity": telemetry_data.velocity,
            "altitude": telemetry_data.altitude,
            "temperature": telemetry_data.temperature,
            "battery": telemetry_data.battery,
            "signal_strength": telemetry_data.signal_strength,
            "created_at": datetime.now()
        }
        
        # Insert telemetry data
        result = await telemetry_collection.insert_one(telemetry_doc)
        telemetry_doc["_id"] = result.inserted_id
        
        # TODO: Broadcast telemetry update via WebSocket
        
        logger.info(f"Created telemetry data for agent {telemetry_data.agent_id}")
        return telemetry_helper(telemetry_doc)
        
    except Exception as e:
        logger.error(f"Error creating telemetry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trends")
async def get_telemetry_trends(
    agent_id: Optional[str] = None,
    time_range: str = "1h",  # 1h, 6h, 24h, 7d
    metric: str = "all"  # all, altitude, velocity, temperature, battery
):
    """Get telemetry trends with aggregation"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Calculate time range
        now = datetime.now()
        time_ranges = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7)
        }
        
        start_time = now - time_ranges.get(time_range, timedelta(hours=1))
        
        # Build filter query
        filter_query = {"timestamp": {"$gte": start_time}}
        if agent_id:
            filter_query["agent_id"] = agent_id
        
        # Aggregate data by time intervals
        pipeline = [
            {"$match": filter_query},
            {
                "$group": {
                    "_id": {
                        "hour": {"$hour": "$timestamp"},
                        "minute": {"$minute": "$timestamp"}
                    },
                    "avg_altitude": {"$avg": "$altitude"},
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_battery": {"$avg": "$battery"},
                    "avg_signal": {"$avg": "$signal_strength"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.hour": 1, "_id.minute": 1}}
        ]
        
        trends = []
        async for trend in telemetry_collection.aggregate(pipeline):
            trends.append({
                "timestamp": f"{trend['_id']['hour']:02d}:{trend['_id']['minute']:02d}",
                "altitude": trend.get("avg_altitude"),
                "temperature": trend.get("avg_temperature"),
                "battery": trend.get("avg_battery"),
                "signal_strength": trend.get("avg_signal"),
                "data_points": trend.get("count", 0)
            })
        
        return {
            "time_range": time_range,
            "agent_id": agent_id,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error fetching telemetry trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/latest")
async def get_latest_telemetry(agent_id: Optional[str] = None):
    """Get latest telemetry data for real-time dashboard"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Build filter query
        filter_query = {}
        if agent_id:
            filter_query["agent_id"] = agent_id
        
        # Get latest data for each type
        pipeline = [
            {"$match": filter_query},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": {"agent_id": "$agent_id", "type": "$type"},
                    "latest": {"$first": "$$ROOT"}
                }
            },
            {"$replaceRoot": {"newRoot": "$latest"}},
            {"$sort": {"timestamp": -1}}
        ]
        
        latest_data = []
        async for telemetry in telemetry_collection.aggregate(pipeline):
            latest_data.append(telemetry_helper(telemetry))
        
        return latest_data
        
    except Exception as e:
        logger.error(f"Error fetching latest telemetry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{telemetry_id}", response_model=TelemetryData)
async def get_telemetry_by_id(telemetry_id: str):
    """Get specific telemetry data by ID"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        telemetry = await telemetry_collection.find_one({"_id": ObjectId(telemetry_id)})
        if not telemetry:
            raise HTTPException(status_code=404, detail="Telemetry data not found")
        
        return telemetry_helper(telemetry)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching telemetry {telemetry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agent/{agent_id}/latest", response_model=List[TelemetryData])
async def get_latest_telemetry_by_agent(agent_id: str):
    """Get latest telemetry data for a specific agent"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Get latest data for each type
        pipeline = [
            {"$match": {"agent_id": agent_id}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$type",
                    "latest": {"$first": "$$ROOT"}
                }
            },
            {"$replaceRoot": {"newRoot": "$latest"}},
            {"$sort": {"timestamp": -1}}
        ]
        
        latest_data = []
        async for telemetry in telemetry_collection.aggregate(pipeline):
            latest_data.append(telemetry_helper(telemetry))
        
        if not latest_data:
            raise HTTPException(status_code=404, detail="No telemetry data found for agent")
        
        return latest_data
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching latest telemetry for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agent/{agent_id}/position", response_model=PositionData)
async def get_agent_position(agent_id: str):
    """Get current position of an agent"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Get latest position data
        position_data = await telemetry_collection.find_one(
            {"agent_id": agent_id, "type": TelemetryType.POSITION.value},
            sort=[("timestamp", -1)]
        )
        
        if not position_data or not position_data.get("position"):
            raise HTTPException(status_code=404, detail="Position data not found for agent")
        
        return PositionData(
            lat=position_data["position"]["lat"],
            lng=position_data["position"]["lng"],
            alt=position_data["position"]["alt"]
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching agent position {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get comprehensive status of an agent"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Get latest data for each metric type
        pipeline = [
            {"$match": {"agent_id": agent_id}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$type",
                    "latest": {"$first": "$$ROOT"}
                }
            },
            {"$replaceRoot": {"newRoot": "$latest"}}
        ]
        
        latest_data = {}
        async for telemetry in telemetry_collection.aggregate(pipeline):
            latest_data[telemetry["type"]] = telemetry
        
        if not latest_data:
            raise HTTPException(status_code=404, detail="No telemetry data found for agent")
        
        # Extract key metrics
        position_data = latest_data.get(TelemetryType.POSITION.value)
        velocity_data = latest_data.get(TelemetryType.VELOCITY.value)
        system_data = latest_data.get(TelemetryType.SYSTEM_STATUS.value)
        
        status = {
            "agent_id": agent_id,
            "last_update": max(t["timestamp"] for t in latest_data.values()),
            "position": None,
            "velocity": None,
            "temperature": None,
            "battery": None,
            "signal_strength": None,
            "system_status": None
        }
        
        if position_data:
            status["position"] = position_data.get("position")
        
        if velocity_data:
            status["velocity"] = velocity_data.get("velocity")
        
        if system_data:
            status["temperature"] = system_data.get("temperature")
            status["battery"] = system_data.get("battery")
            status["signal_strength"] = system_data.get("signal_strength")
            status["system_status"] = system_data.get("data", {}).get("status")
        
        return status
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching agent status {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents/positions")
async def get_all_agent_positions():
    """Get current positions of all agents"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Get latest position for each agent
        pipeline = [
            {"$match": {"type": TelemetryType.POSITION.value}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$agent_id",
                    "latest_position": {"$first": "$$ROOT"}
                }
            },
            {"$replaceRoot": {"newRoot": "$latest_position"}}
        ]
        
        positions = {}
        async for telemetry in telemetry_collection.aggregate(pipeline):
            if telemetry.get("position"):
                positions[telemetry["agent_id"]] = {
                    "lat": telemetry["position"]["lat"],
                    "lng": telemetry["position"]["lng"],
                    "alt": telemetry["position"]["alt"]
                }
        
        return positions
        
    except Exception as e:
        logger.error(f"Error fetching all agent positions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents/status")
async def get_all_agent_status():
    """Get status of all agents"""
    try:
        db = await get_database()
        telemetry_collection = db.telemetry
        
        # Get latest data for each agent and type
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": {"agent_id": "$agent_id", "type": "$type"},
                    "latest": {"$first": "$$ROOT"}
                }
            },
            {"$replaceRoot": {"newRoot": "$latest"}},
            {
                "$group": {
                    "_id": "$agent_id",
                    "telemetry_data": {"$push": "$$ROOT"}
                }
            }
        ]
        
        statuses = {}
        async for agent_data in telemetry_collection.aggregate(pipeline):
            agent_id = agent_data["_id"]
            telemetry_list = agent_data["telemetry_data"]
            
            # Build status from telemetry data
            status = {
                "agent_id": agent_id,
                "last_update": max(t["timestamp"] for t in telemetry_list),
                "position": None,
                "velocity": None,
                "temperature": None,
                "battery": None,
                "signal_strength": None,
                "system_status": None
            }
            
            for telemetry in telemetry_list:
                if telemetry["type"] == TelemetryType.POSITION.value:
                    status["position"] = telemetry.get("position")
                elif telemetry["type"] == TelemetryType.VELOCITY.value:
                    status["velocity"] = telemetry.get("velocity")
                elif telemetry["type"] == TelemetryType.SYSTEM_STATUS.value:
                    status["temperature"] = telemetry.get("temperature")
                    status["battery"] = telemetry.get("battery")
                    status["signal_strength"] = telemetry.get("signal_strength")
                    status["system_status"] = telemetry.get("data", {}).get("status")
            
            statuses[agent_id] = status
        
        return statuses
        
    except Exception as e:
        logger.error(f"Error fetching all agent status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")