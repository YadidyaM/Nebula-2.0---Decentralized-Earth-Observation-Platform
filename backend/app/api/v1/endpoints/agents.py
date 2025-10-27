from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

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

class AgentUpdate(BaseModel):
    status: Optional[AgentStatus] = None
    position: Optional[Position] = None
    staked: Optional[bool] = None

# Helper function to convert ObjectId to string
def agent_helper(agent) -> dict:
    if agent:
        agent["id"] = str(agent["_id"])
        del agent["_id"]
    return agent

@router.get("/", response_model=List[Agent])
async def get_agents(
    status: Optional[AgentStatus] = None,
    type: Optional[AgentType] = None,
    rarity: Optional[AgentRarity] = None,
    staked: Optional[bool] = None
):
    """Get all agents with optional filtering"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status.value
        if type:
            filter_query["type"] = type.value
        if rarity:
            filter_query["rarity"] = rarity.value
        if staked is not None:
            filter_query["staked"] = staked
        
        # Execute query
        cursor = agents_collection.find(filter_query)
        agents = []
        
        async for agent in cursor:
            agents.append(agent_helper(agent))
        
        return agents
        
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get a specific agent by ID with detailed performance metrics"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent_helper(agent)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update_data: AgentUpdate):
    """Update an agent"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        # Build update document
        update_doc = {"last_update": datetime.now()}
        if update_data.status:
            update_doc["status"] = update_data.status.value
        if update_data.position:
            update_doc["position"] = update_data.position.dict()
        if update_data.staked is not None:
            update_doc["staked"] = update_data.staked
            if update_data.staked:
                update_doc["staked_at"] = datetime.now()
            else:
                update_doc["staked_at"] = None
        
        # Update agent
        result = await agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get updated agent
        updated_agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        
        # TODO: Broadcast agent status update via WebSocket
        
        logger.info(f"Updated agent {agent_id}")
        return agent_helper(updated_agent)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{agent_id}/status", response_model=Agent)
async def update_agent_status(agent_id: str, status: AgentStatus):
    """Update agent status for activation/deactivation"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        # Update agent status
        result = await agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {"status": status.value, "last_update": datetime.now()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get updated agent
        updated_agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        
        # TODO: Broadcast agent status update via WebSocket
        
        logger.info(f"Updated agent {agent_id} status to {status.value}")
        return agent_helper(updated_agent)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating agent status {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/assign")
async def assign_agent_to_mission(agent_id: str, mission_id: str):
    """Assign an agent to a mission"""
    try:
        db = await get_database()
        agents_collection = db.agents
        missions_collection = db.missions
        
        # Check if agent exists
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if mission exists
        mission = await missions_collection.find_one({"_id": ObjectId(mission_id)})
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Add agent to mission
        await missions_collection.update_one(
            {"_id": ObjectId(mission_id)},
            {"$push": {"agents": agent_id}, "$set": {"updated_at": datetime.now()}}
        )
        
        # Update agent status to busy
        await agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {"status": AgentStatus.BUSY.value, "last_update": datetime.now()}}
        )
        
        logger.info(f"Assigned agent {agent_id} to mission {mission_id}")
        return {"message": f"Agent {agent_id} assigned to mission {mission_id}"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error assigning agent to mission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/stake")
async def stake_agent(agent_id: str):
    """Stake an agent NFT for rewards"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if agent.get("staked", False):
            raise HTTPException(status_code=400, detail="Agent already staked")
        
        # Update agent staking status
        await agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {
                "staked": True,
                "staked_at": datetime.now(),
                "last_update": datetime.now()
            }}
        )
        
        # TODO: Record staking transaction on blockchain
        
        logger.info(f"Staked agent {agent_id}")
        return {"message": f"Agent {agent.get('name', agent_id)} staked successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error staking agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/unstake")
async def unstake_agent(agent_id: str):
    """Unstake an agent NFT"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if not agent.get("staked", False):
            raise HTTPException(status_code=400, detail="Agent not staked")
        
        # Update agent staking status
        await agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {
                "staked": False,
                "staked_at": None,
                "last_update": datetime.now()
            }}
        )
        
        # TODO: Record unstaking transaction on blockchain
        
        logger.info(f"Unstaked agent {agent_id}")
        return {"message": f"Agent {agent.get('name', agent_id)} unstaked successfully"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error unstaking agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}/rewards")
async def get_agent_rewards(agent_id: str):
    """Get agent staking rewards"""
    try:
        db = await get_database()
        agents_collection = db.agents
        
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Calculate rewards based on staking duration and rarity
        rewards_per_hour = {
            AgentRarity.COMMON.value: 1.0,
            AgentRarity.RARE.value: 2.0,
            AgentRarity.EPIC.value: 3.0,
            AgentRarity.LEGENDARY.value: 5.0
        }
        
        if agent.get("staked", False) and agent.get("staked_at"):
            hours_staked = (datetime.now() - agent["staked_at"]).total_seconds() / 3600
            hourly_rate = rewards_per_hour.get(agent.get("rarity", "common"), 1.0)
            total_rewards = hours_staked * hourly_rate
        else:
            total_rewards = 0.0
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.get("name", "Unknown"),
            "rarity": agent.get("rarity", "common"),
            "staked": agent.get("staked", False),
            "staked_at": agent.get("staked_at"),
            "rewards_earned": agent.get("rewards_earned", 0.0),
            "current_staking_rewards": total_rewards,
            "hourly_rate": rewards_per_hour.get(agent.get("rarity", "common"), 1.0)
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching agent rewards {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}/performance")
async def get_agent_performance(agent_id: str):
    """Get detailed performance metrics for an agent"""
    try:
        db = await get_database()
        agents_collection = db.agents
        missions_collection = db.missions
        
        agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get mission statistics
        missions_completed = await missions_collection.count_documents({
            "agents": agent_id,
            "status": "completed"
        })
        
        missions_failed = await missions_collection.count_documents({
            "agents": agent_id,
            "status": "failed"
        })
        
        total_missions = missions_completed + missions_failed
        success_rate = missions_completed / total_missions if total_missions > 0 else 0.0
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.get("name", "Unknown"),
            "missions_completed": missions_completed,
            "missions_failed": missions_failed,
            "total_missions": total_missions,
            "success_rate": success_rate,
            "rewards_earned": agent.get("rewards_earned", 0.0),
            "staked": agent.get("staked", False),
            "last_update": agent.get("last_update")
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching agent performance {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")