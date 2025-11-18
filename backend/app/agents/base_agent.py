# Base agent class providing foundation for all specialized AI agents with Gemini AI integration
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

from app.models.agent import Agent, AgentStatus, Position
from app.models.mission import Mission, MissionStatus
from app.services.blockchain.solana_client import SolanaClient
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator
from app.services.ai.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, name: str, wallet_address: str):
        self.agent_id = agent_id
        self.name = name
        self.wallet_address = wallet_address
        self.status = AgentStatus.OFFLINE
        self.position = Position(lat=0.0, lng=0.0, alt=400000)
        self.current_mission: Optional[Mission] = None
        self.missions_completed = 0
        self.success_rate = 0.0
        self.last_update = datetime.now()
        self.specialization: List[str] = []
        
    @abstractmethod
    async def initialize(self):
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute a mission and return results"""
        pass
    
    @abstractmethod
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process environmental data and detect anomalies using Gemini AI for intelligent reasoning"""
        # Base implementation with Gemini AI support
        if gemini_service.is_available():
            try:
                analysis = await gemini_service.detect_anomalies(
                    data,
                    f"Environmental data analysis for {self.name}"
                )
                return analysis or {"agent_id": self.agent_id, "analysis": "completed"}
            except Exception as e:
                logger.error(f"Error in Gemini analysis for {self.name}: {e}")
        return {"agent_id": self.agent_id, "analysis": "completed"}
    
    async def update_status(self, status: AgentStatus):
        """Update agent status"""
        self.status = status
        self.last_update = datetime.now()
        logger.info(f"Agent {self.name} status updated to {status}")
    
    async def update_position(self, position: Position):
        """Update agent position"""
        self.position = position
        self.last_update = datetime.now()
        logger.info(f"Agent {self.name} position updated to {position}")
    
    async def start_mission(self, mission: Mission):
        """Start a new mission"""
        self.current_mission = mission
        await self.update_status(AgentStatus.BUSY)
        logger.info(f"Agent {self.name} started mission {mission.id}")
    
    async def complete_mission(self, results: Dict[str, Any]):
        """Complete current mission"""
        if self.current_mission:
            self.missions_completed += 1
            self.current_mission = None
            await self.update_status(AgentStatus.ONLINE)
            logger.info(f"Agent {self.name} completed mission with results: {results}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "position": self.position,
            "missions_completed": self.missions_completed,
            "success_rate": self.success_rate,
            "last_update": self.last_update,
            "current_mission": self.current_mission.id if self.current_mission else None
        }

class OrchestratorAgent(BaseAgent):
    """Main orchestrator agent that coordinates all other agents"""
    
    def __init__(self, solana_client: SolanaClient, swarms_orchestrator: SwarmsOrchestrator):
        super().__init__("agent_orchestrator", "Orchestrator Agent", "Orch1234567890abcdef")
        self.solana_client = solana_client
        self.swarms_orchestrator = swarms_orchestrator
        self.managed_agents: Dict[str, BaseAgent] = {}
        self.mission_queue: List[Mission] = []
        self.running = False
        
    async def initialize(self):
        """Initialize the orchestrator"""
        await self.update_status(AgentStatus.ONLINE)
        logger.info("Orchestrator Agent initialized")
    
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        await self.update_status(AgentStatus.ONLINE)
        # Start background tasks
        asyncio.create_task(self._mission_distributor())
        asyncio.create_task(self._agent_monitor())
        logger.info("Orchestrator Agent started")
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        await self.update_status(AgentStatus.OFFLINE)
        logger.info("Orchestrator Agent stopped")
    
    async def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.managed_agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    async def assign_mission(self, mission: Mission):
        """Assign a mission to the appropriate agent"""
        self.mission_queue.append(mission)
        logger.info(f"Mission {mission.id} added to queue")
    
    async def _mission_distributor(self):
        """Background task to distribute missions to agents"""
        while self.running:
            try:
                if self.mission_queue:
                    mission = self.mission_queue.pop(0)
                    await self._distribute_mission(mission)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in mission distributor: {e}")
                await asyncio.sleep(5)
    
    async def _distribute_mission(self, mission: Mission):
        """Distribute a mission to the best available agent"""
        best_agent = None
        best_score = 0
        
        for agent_id, agent in self.managed_agents.items():
            if agent.status == AgentStatus.ONLINE and not agent.current_mission:
                # Calculate suitability score based on specialization
                score = self._calculate_agent_score(agent, mission)
                if score > best_score:
                    best_score = score
                    best_agent = agent
        
        if best_agent:
            await best_agent.start_mission(mission)
            logger.info(f"Mission {mission.id} assigned to {best_agent.name}")
        else:
            # No available agents, put mission back in queue
            self.mission_queue.append(mission)
            logger.warning(f"No available agents for mission {mission.id}")
    
    def _calculate_agent_score(self, agent: BaseAgent, mission: Mission) -> float:
        """Calculate how suitable an agent is for a mission"""
        score = 0.0
        
        # Base score from success rate
        score += agent.success_rate * 50
        
        # Bonus for specialization match
        for specialization in agent.specialization:
            if specialization in mission.type.value:
                score += 20
        
        # Bonus for being online and available
        if agent.status == AgentStatus.ONLINE:
            score += 10
        
        return score
    
    async def _agent_monitor(self):
        """Background task to monitor agent health"""
        while self.running:
            try:
                for agent_id, agent in self.managed_agents.items():
                    health_status = await agent.get_health_status()
                    # Check if agent is responsive
                    if (datetime.now() - agent.last_update).seconds > 300:  # 5 minutes
                        await agent.update_status(AgentStatus.ERROR)
                        logger.warning(f"Agent {agent.name} appears unresponsive")
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in agent monitor: {e}")
                await asyncio.sleep(30)
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Orchestrator doesn't execute missions directly"""
        return {"error": "Orchestrator does not execute missions directly"}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process environmental data and coordinate responses"""
        # Analyze data for global patterns
        analysis = {
            "global_analysis": True,
            "data_quality": "high",
            "anomalies_detected": [],
            "recommended_actions": []
        }
        
        # Check for critical events that require immediate response
        if data.get("risk_level") == "critical":
            analysis["recommended_actions"].append("deploy_emergency_response")
        
        return analysis
