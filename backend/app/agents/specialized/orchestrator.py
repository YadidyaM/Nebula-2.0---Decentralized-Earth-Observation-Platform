from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import json

from app.agents.base_agent import BaseAgent, OrchestratorAgent
from app.models.agent import AgentStatus, Position
from app.models.mission import Mission, MissionStatus, MissionType
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator

logger = logging.getLogger(__name__)

class Orchestrator(BaseAgent):
    """Main orchestrator agent that coordinates all other specialized agents"""
    
    def __init__(self, agent_id: str = "agent_orchestrator", name: str = "Orchestrator"):
        super().__init__(agent_id, name, "Orch1234567890abcdef")
        self.specialization = ["coordination", "mission_planning", "agent_management", "resource_allocation"]
        self.managed_agents: Dict[str, BaseAgent] = {}
        self.mission_queue: List[Mission] = []
        self.active_missions: Dict[str, Mission] = {}
        self.swarms_orchestrator: Optional[SwarmsOrchestrator] = None
        self.running = False
        self.performance_metrics = {
            "missions_completed": 0,
            "missions_failed": 0,
            "average_response_time": 0.0,
            "agent_utilization": 0.0
        }
        
    async def initialize(self):
        """Initialize the Orchestrator agent"""
        await self.update_status(AgentStatus.ONLINE)
        await self.update_position(Position(lat=0.0, lng=0.0, alt=400000))
        logger.info("Orchestrator initialized")
        
        # Initialize Swarms orchestrator
        try:
            self.swarms_orchestrator = SwarmsOrchestrator()
            await self.swarms_orchestrator.initialize()
            logger.info("Swarms orchestrator initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Swarms orchestrator: {e}")
        
        # Start background tasks
        asyncio.create_task(self._mission_distributor())
        asyncio.create_task(self._agent_monitor())
        asyncio.create_task(self._performance_analyzer())
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Orchestrator doesn't execute missions directly, it coordinates them"""
        try:
            # Add mission to queue
            await self.assign_mission(mission)
            
            # Wait for mission to be assigned and completed
            max_wait_time = 300  # 5 minutes
            wait_time = 0
            
            while mission.id in self.mission_queue and wait_time < max_wait_time:
                await asyncio.sleep(1)
                wait_time += 1
            
            if mission.id in self.active_missions:
                # Mission is being executed
                return {
                    "mission_id": mission.id,
                    "status": "assigned",
                    "assigned_agent": self.active_missions[mission.id].agents[0] if self.active_missions[mission.id].agents else "unknown",
                    "message": "Mission assigned to specialized agent"
                }
            else:
                return {
                    "mission_id": mission.id,
                    "status": "queued",
                    "message": "Mission added to queue for processing"
                }
                
        except Exception as e:
            logger.error(f"Error coordinating mission {mission.id}: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process environmental data and coordinate responses across agents"""
        try:
            analysis = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "orchestration",
                "global_analysis": True,
                "data_quality": "high",
                "anomalies_detected": [],
                "recommended_actions": [],
                "agent_coordination": {},
                "resource_allocation": {}
            }
            
            # Analyze data for global patterns
            if data.get("risk_level") == "critical":
                analysis["recommended_actions"].append("deploy_emergency_response")
                analysis["agent_coordination"]["disaster_responder"] = "activate"
                analysis["agent_coordination"]["security_sentinel"] = "monitor"
            
            # Check for multi-agent coordination needs
            if data.get("requires_coordination", False):
                analysis["recommended_actions"].append("coordinate_multi_agent_response")
                
                # Determine which agents should be involved
                if "weather" in data.get("data_types", []):
                    analysis["agent_coordination"]["storm_tracker"] = "activate"
                if "water" in data.get("data_types", []):
                    analysis["agent_coordination"]["water_watcher"] = "activate"
                if "ice" in data.get("data_types", []):
                    analysis["agent_coordination"]["ice_sentinel"] = "activate"
                if "forest" in data.get("data_types", []):
                    analysis["agent_coordination"]["forest_guardian"] = "activate"
            
            # Resource allocation recommendations
            if data.get("resource_intensive", False):
                analysis["resource_allocation"]["priority"] = "high"
                analysis["resource_allocation"]["agents_needed"] = 3
                analysis["resource_allocation"]["estimated_duration"] = "extended"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing environmental data: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def register_agent(self, agent: BaseAgent):
        """Register a new agent with the orchestrator"""
        try:
            self.managed_agents[agent.agent_id] = agent
            logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
            
            # Update agent status
            await agent.update_status(AgentStatus.ONLINE)
            
            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": "registered",
                "specialization": agent.specialization
            }
            
        except Exception as e:
            logger.error(f"Error registering agent {agent.agent_id}: {e}")
            return {"error": str(e), "agent_id": agent.agent_id}
    
    async def assign_mission(self, mission: Mission):
        """Assign a mission to the appropriate agent"""
        try:
            self.mission_queue.append(mission)
            logger.info(f"Mission {mission.id} added to queue")
            
            # If we have Swarms orchestrator, use it for complex missions
            if self.swarms_orchestrator and mission.priority.value in ["high", "critical"]:
                await self._coordinate_with_swarms(mission)
            
        except Exception as e:
            logger.error(f"Error assigning mission {mission.id}: {e}")
    
    async def _mission_distributor(self):
        """Background task to distribute missions to agents"""
        while self.running or len(self.mission_queue) > 0:
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
        try:
            best_agent = None
            best_score = 0
            
            for agent_id, agent in self.managed_agents.items():
                if agent.status == AgentStatus.ONLINE and not agent.current_mission:
                    # Calculate suitability score
                    score = await self._calculate_agent_score(agent, mission)
                    if score > best_score:
                        best_score = score
                        best_agent = agent
            
            if best_agent:
                # Assign mission to agent
                await best_agent.start_mission(mission)
                self.active_missions[mission.id] = mission
                
                # Update mission status
                mission.status = MissionStatus.ACTIVE
                
                logger.info(f"Mission {mission.id} assigned to {best_agent.name} (score: {best_score})")
                
                # Monitor mission progress
                asyncio.create_task(self._monitor_mission_progress(mission, best_agent))
            else:
                # No available agents, put mission back in queue
                self.mission_queue.append(mission)
                logger.warning(f"No available agents for mission {mission.id}")
                
        except Exception as e:
            logger.error(f"Error distributing mission {mission.id}: {e}")
            # Put mission back in queue on error
            self.mission_queue.append(mission)
    
    async def _calculate_agent_score(self, agent: BaseAgent, mission: Mission) -> float:
        """Calculate how suitable an agent is for a mission"""
        try:
            score = 0.0
            
            # Base score from success rate
            score += agent.success_rate * 50
            
            # Bonus for specialization match
            mission_type = mission.type.value.lower()
            for specialization in agent.specialization:
                if specialization.lower() in mission_type or mission_type in specialization.lower():
                    score += 30
            
            # Bonus for being online and available
            if agent.status == AgentStatus.ONLINE:
                score += 20
            
            # Bonus for recent performance
            if agent.missions_completed > 0:
                score += min(20, agent.missions_completed * 2)
            
            # Penalty for recent failures
            if agent.success_rate < 0.8:
                score -= 20
            
            return max(0, score)
            
        except Exception as e:
            logger.error(f"Error calculating agent score: {e}")
            return 0.0
    
    async def _monitor_mission_progress(self, mission: Mission, agent: BaseAgent):
        """Monitor the progress of an assigned mission"""
        try:
            start_time = datetime.now()
            max_duration = timedelta(hours=24)  # Maximum mission duration
            
            while mission.id in self.active_missions:
                # Check if mission is completed
                if not agent.current_mission or agent.current_mission.id != mission.id:
                    # Mission completed
                    self.active_missions.pop(mission.id, None)
                    mission.status = MissionStatus.COMPLETED
                    self.performance_metrics["missions_completed"] += 1
                    logger.info(f"Mission {mission.id} completed by {agent.name}")
                    break
                
                # Check for timeout
                if datetime.now() - start_time > max_duration:
                    # Mission timeout
                    self.active_missions.pop(mission.id, None)
                    mission.status = MissionStatus.FAILED
                    self.performance_metrics["missions_failed"] += 1
                    logger.warning(f"Mission {mission.id} timed out")
                    break
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error monitoring mission {mission.id}: {e}")
            self.active_missions.pop(mission.id, None)
            mission.status = MissionStatus.FAILED
            self.performance_metrics["missions_failed"] += 1
    
    async def _agent_monitor(self):
        """Background task to monitor agent health"""
        while self.running:
            try:
                for agent_id, agent in self.managed_agents.items():
                    # Check if agent is responsive
                    if (datetime.now() - agent.last_update).seconds > 300:  # 5 minutes
                        await agent.update_status(AgentStatus.ERROR)
                        logger.warning(f"Agent {agent.name} appears unresponsive")
                    
                    # Check agent health
                    health_status = await agent.get_health_status()
                    if health_status.get("status") == AgentStatus.ERROR:
                        logger.warning(f"Agent {agent.name} is in error state")
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in agent monitor: {e}")
                await asyncio.sleep(30)
    
    async def _performance_analyzer(self):
        """Background task to analyze performance metrics"""
        while self.running:
            try:
                # Calculate agent utilization
                total_agents = len(self.managed_agents)
                active_agents = len([a for a in self.managed_agents.values() if a.current_mission])
                
                if total_agents > 0:
                    self.performance_metrics["agent_utilization"] = active_agents / total_agents
                
                # Calculate average response time
                total_missions = self.performance_metrics["missions_completed"] + self.performance_metrics["missions_failed"]
                if total_missions > 0:
                    success_rate = self.performance_metrics["missions_completed"] / total_missions
                    self.performance_metrics["average_response_time"] = 5.0 * success_rate  # Simulated
                
                logger.info(f"Performance metrics: {self.performance_metrics}")
                
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Error in performance analyzer: {e}")
                await asyncio.sleep(300)
    
    async def _coordinate_with_swarms(self, mission: Mission):
        """Coordinate mission execution with Swarms AI orchestrator"""
        try:
            if not self.swarms_orchestrator:
                return
            
            # Create swarm for complex missions
            agent_configs = []
            for agent_id, agent in self.managed_agents.items():
                if agent.status == AgentStatus.ONLINE:
                    agent_configs.append({
                        "agent_name": agent.name,
                        "system_prompt": f"You are {agent.name}, specialized in {', '.join(agent.specialization)}",
                        "llm": "gpt-4",
                        "max_loops": 3,
                        "temperature": 0.7
                    })
            
            if agent_configs:
                swarm_id = await self.swarms_orchestrator.create_swarm(
                    f"mission_{mission.id}",
                    agent_configs
                )
                
                # Execute mission using swarm
                mission_context = {
                    "mission_type": mission.type.value,
                    "target_area": mission.target_area.dict(),
                    "priority": mission.priority.value,
                    "description": mission.name
                }
                
                result = await self.swarms_orchestrator.execute_mission(
                    swarm_id,
                    mission.name,
                    mission_context
                )
                
                logger.info(f"Swarms coordination result for mission {mission.id}: {result}")
                
        except Exception as e:
            logger.error(f"Error coordinating with Swarms: {e}")
    
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        await self.update_status(AgentStatus.ONLINE)
        logger.info("Orchestrator started")
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        await self.update_status(AgentStatus.OFFLINE)
        logger.info("Orchestrator stopped")
    
    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        try:
            base_status = await self.get_health_status()
            
            # Get agent statuses
            agent_statuses = {}
            for agent_id, agent in self.managed_agents.items():
                agent_statuses[agent_id] = {
                    "name": agent.name,
                    "status": agent.status.value,
                    "current_mission": agent.current_mission.id if agent.current_mission else None,
                    "specialization": agent.specialization,
                    "last_update": agent.last_update.isoformat()
                }
            
            orchestrator_status = {
                **base_status,
                "running": self.running,
                "managed_agents": len(self.managed_agents),
                "mission_queue_size": len(self.mission_queue),
                "active_missions": len(self.active_missions),
                "agent_statuses": agent_statuses,
                "performance_metrics": self.performance_metrics,
                "swarms_available": self.swarms_orchestrator is not None,
                "last_coordination": datetime.now().isoformat()
            }
            
            return orchestrator_status
            
        except Exception as e:
            logger.error(f"Error getting orchestrator status: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def get_mission_statistics(self) -> Dict[str, Any]:
        """Get mission statistics and analytics"""
        try:
            total_missions = self.performance_metrics["missions_completed"] + self.performance_metrics["missions_failed"]
            success_rate = self.performance_metrics["missions_completed"] / total_missions if total_missions > 0 else 0
            
            statistics = {
                "total_missions": total_missions,
                "completed_missions": self.performance_metrics["missions_completed"],
                "failed_missions": self.performance_metrics["missions_failed"],
                "success_rate": success_rate,
                "average_response_time": self.performance_metrics["average_response_time"],
                "agent_utilization": self.performance_metrics["agent_utilization"],
                "queue_size": len(self.mission_queue),
                "active_missions": len(self.active_missions),
                "registered_agents": len(self.managed_agents)
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting mission statistics: {e}")
            return {"error": str(e)}
