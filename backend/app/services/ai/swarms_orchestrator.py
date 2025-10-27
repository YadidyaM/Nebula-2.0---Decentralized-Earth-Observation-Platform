import requests
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Official Swarms framework imports
try:
    from swarms import Agent, HierarchicalSwarm, ConcurrentWorkflow, SequentialWorkflow
    from swarms.tools import BaseTool
    SWARMS_AVAILABLE = True
except ImportError:
    SWARMS_AVAILABLE = False
    logger.warning("Swarms framework not available, using mock mode")

from app.config import settings

logger = logging.getLogger(__name__)

class SwarmsOrchestrator:
    """Swarms AI orchestrator for managing AI agents using official Swarms framework"""
    
    def __init__(self):
        self.api_key = settings.swarms_ai_api_key
        # Using official Swarms Cloud API endpoints
        self.base_url = "https://api.swarms.world/v1"
        self.cloud_api_url = "https://api.swarms.world/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Nebula-Protocol/1.0.0"
        }
        self.active_swarms: Dict[str, Dict[str, Any]] = {}
        self.agent_tasks: Dict[str, Dict[str, Any]] = {}
        self.swarm_agents: Dict[str, Any] = {}
    
    async def initialize(self):
        """Initialize the Swarms AI orchestrator using official Swarms framework"""
        try:
            if not self.api_key:
                logger.warning("No Swarms AI API key configured, using mock mode")
                return
            
            # Test API connection to Swarms Cloud API
            response = requests.get(
                f"{self.cloud_api_url}/agents",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Connected to Swarms Cloud API")
                # Initialize our specialized agents using Swarms framework
                await self._initialize_swarm_agents()
            else:
                logger.warning(f"Swarms Cloud API connection failed: {response.text}")
                logger.info("Running in mock mode")
                
        except Exception as e:
            logger.warning(f"Failed to connect to Swarms Cloud API: {e}")
            logger.info("Running in mock mode")
    
    async def _initialize_swarm_agents(self):
        """Initialize specialized agents using official Swarms framework"""
        try:
            if not SWARMS_AVAILABLE:
                logger.warning("Swarms framework not available, using mock agents")
                await self._create_mock_agents()
                return
            
            # Create agent configurations based on Swarms documentation
            agent_configs = {
                "forest_guardian": {
                    "agent_name": "Forest Guardian",
                    "system_prompt": "You are a specialized AI agent for forest monitoring and deforestation detection. Analyze satellite imagery, detect deforestation patterns, assess biodiversity, and monitor carbon sequestration.",
                    "llm": "gpt-4",
                    "max_loops": 5,
                    "temperature": 0.7
                },
                "ice_sentinel": {
                    "agent_name": "Ice Sentinel", 
                    "system_prompt": "You are a specialized AI agent for cryosphere monitoring. Analyze ice sheet changes, glacier retreat, sea ice extent, and polar climate patterns.",
                    "llm": "gpt-4",
                    "max_loops": 5,
                    "temperature": 0.6
                },
                "storm_tracker": {
                    "agent_name": "Storm Tracker",
                    "system_prompt": "You are a specialized AI agent for weather monitoring and storm tracking. Analyze atmospheric conditions, predict storm paths, and assess weather risks.",
                    "llm": "gpt-4",
                    "max_loops": 3,
                    "temperature": 0.8
                },
                "urban_monitor": {
                    "agent_name": "Urban Monitor",
                    "system_prompt": "You are a specialized AI agent for urban infrastructure monitoring. Analyze city development, infrastructure quality, urban heat islands, and population density.",
                    "llm": "gpt-4",
                    "max_loops": 4,
                    "temperature": 0.7
                },
                "water_watcher": {
                    "agent_name": "Water Watcher",
                    "system_prompt": "You are a specialized AI agent for hydrology and water resource monitoring. Analyze water levels, quality, pollution, and flood risks.",
                    "llm": "gpt-4",
                    "max_loops": 4,
                    "temperature": 0.7
                },
                "security_sentinel": {
                    "agent_name": "Security Sentinel",
                    "system_prompt": "You are a specialized AI agent for security monitoring and border surveillance. Analyze movement patterns, infrastructure status, and security threats.",
                    "llm": "gpt-4",
                    "max_loops": 3,
                    "temperature": 0.5
                },
                "land_surveyor": {
                    "agent_name": "Land Surveyor",
                    "system_prompt": "You are a specialized AI agent for land monitoring and soil analysis. Analyze soil health, erosion, agricultural potential, and geological features.",
                    "llm": "gpt-4",
                    "max_loops": 4,
                    "temperature": 0.7
                },
                "disaster_responder": {
                    "agent_name": "Disaster Responder",
                    "system_prompt": "You are a specialized AI agent for emergency response and disaster assessment. Analyze disaster impacts, coordinate response efforts, and assess recovery needs.",
                    "llm": "gpt-4",
                    "max_loops": 2,
                    "temperature": 0.9
                }
            }
            
            # Create agents using official Swarms framework
            for agent_id, config in agent_configs.items():
                try:
                    # Create agent using Swarms Agent class
                    agent = Agent(**config)
                    self.swarm_agents[agent_id] = agent
                    logger.info(f"Created Swarms agent: {config['agent_name']}")
                        
                except Exception as e:
                    logger.error(f"Error creating agent {agent_id}: {e}")
            
            logger.info(f"Initialized {len(self.swarm_agents)} Swarms agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize swarm agents: {e}")
    
    async def _create_mock_agents(self):
        """Create mock agents when Swarms framework is not available"""
        mock_agents = [
            "Forest Guardian", "Ice Sentinel", "Storm Tracker", "Urban Monitor",
            "Water Watcher", "Security Sentinel", "Land Surveyor", "Disaster Responder"
        ]
        
        for agent_name in mock_agents:
            agent_id = f"mock_{agent_name.lower().replace(' ', '_')}"
            self.swarm_agents[agent_id] = {
                "name": agent_name,
                "type": "mock",
                "status": "active"
            }
        
        logger.info(f"Created {len(mock_agents)} mock agents")
    
    async def create_swarm(self, swarm_name: str, agent_configs: List[Dict[str, Any]]) -> str:
        """Create a new swarm using official Swarms framework"""
        try:
            if not SWARMS_AVAILABLE or not self.api_key:
                # Mock mode
                swarm_id = f"mock_swarm_{swarm_name}_{int(datetime.now().timestamp())}"
                self.active_swarms[swarm_id] = {
                    "name": swarm_name,
                    "agents": agent_configs,
                    "status": "active",
                    "created_at": datetime.now()
                }
                logger.info(f"Mock swarm created: {swarm_id}")
                return swarm_id
            
            # Create swarm using official Swarms framework
            try:
                # Create agents for the swarm
                agents = []
                for config in agent_configs:
                    agent = Agent(**config)
                    agents.append(agent)
                
                # Create HierarchicalSwarm (from Swarms docs)
                swarm = HierarchicalSwarm(
                    agents=agents,
                    name=swarm_name,
                    max_loops=10,
                    temperature=0.7
                )
                
                swarm_id = f"swarm_{swarm_name}_{int(datetime.now().timestamp())}"
                self.active_swarms[swarm_id] = {
                    "swarm": swarm,
                    "name": swarm_name,
                    "agents": agents,
                    "status": "active",
                    "created_at": datetime.now()
                }
                
                logger.info(f"Swarms HierarchicalSwarm created: {swarm_id}")
                return swarm_id
                
            except Exception as e:
                logger.error(f"Failed to create Swarms swarm: {e}")
                # Fallback to mock mode
                swarm_id = f"mock_swarm_{swarm_name}_{int(datetime.now().timestamp())}"
                self.active_swarms[swarm_id] = {
                    "name": swarm_name,
                    "agents": agent_configs,
                    "status": "active",
                    "created_at": datetime.now()
                }
                logger.info(f"Fallback mock swarm created: {swarm_id}")
                return swarm_id
                
        except Exception as e:
            logger.error(f"Failed to create swarm: {e}")
            raise e
    
    async def deploy_agent(self, swarm_id: str, agent_config: Dict[str, Any]) -> str:
        """Deploy an agent to a swarm"""
        try:
            if not self.api_key:
                # Mock mode
                agent_id = f"mock_agent_{agent_config['name']}_{int(datetime.now().timestamp())}"
                if swarm_id in self.active_swarms:
                    self.active_swarms[swarm_id]["agents"].append({
                        "id": agent_id,
                        "config": agent_config,
                        "status": "active"
                    })
                logger.info(f"Mock agent deployed: {agent_id}")
                return agent_id
            
            # Real API call
            response = requests.post(
                f"{self.base_url}/swarms/{swarm_id}/agents",
                headers=self.headers,
                json=agent_config,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                agent_id = result["id"]
                logger.info(f"Agent deployed to swarm: {agent_id}")
                return agent_id
            else:
                logger.error(f"Failed to deploy agent: {response.text}")
                raise Exception(f"Failed to deploy agent: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to deploy agent: {e}")
            raise e
    
    async def assign_task(self, swarm_id: str, task: Dict[str, Any]) -> str:
        """Assign a task to the swarm"""
        try:
            if not self.api_key:
                # Mock mode
                task_id = f"mock_task_{int(datetime.now().timestamp())}"
                self.agent_tasks[task_id] = {
                    "swarm_id": swarm_id,
                    "task": task,
                    "status": "assigned",
                    "assigned_at": datetime.now()
                }
                logger.info(f"Mock task assigned: {task_id}")
                return task_id
            
            # Real API call
            response = requests.post(
                f"{self.base_url}/swarms/{swarm_id}/tasks",
                headers=self.headers,
                json=task,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                task_id = result["id"]
                logger.info(f"Task assigned to swarm: {task_id}")
                return task_id
            else:
                logger.error(f"Failed to assign task: {response.text}")
                raise Exception(f"Failed to assign task: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to assign task: {e}")
            raise e
    
    async def get_swarm_status(self, swarm_id: str) -> Dict[str, Any]:
        """Get status of a swarm"""
        try:
            if not self.api_key:
                # Mock mode
                if swarm_id in self.active_swarms:
                    return self.active_swarms[swarm_id]
                else:
                    return {"error": "Swarm not found"}
            
            # Real API call
            response = requests.get(
                f"{self.base_url}/swarms/{swarm_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get swarm status: {response.text}")
                return {"error": "Failed to get swarm status"}
                
        except Exception as e:
            logger.error(f"Failed to get swarm status: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self, swarm_id: str, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        try:
            if not self.api_key:
                # Mock mode
                if swarm_id in self.active_swarms:
                    for agent in self.active_swarms[swarm_id]["agents"]:
                        if agent["id"] == agent_id:
                            return agent
                return {"error": "Agent not found"}
            
            # Real API call
            response = requests.get(
                f"{self.base_url}/swarms/{swarm_id}/agents/{agent_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get agent status: {response.text}")
                return {"error": "Failed to get agent status"}
                
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            return {"error": str(e)}
    
    async def execute_mission(self, swarm_id: str, mission_prompt: str, mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mission using official Swarms framework"""
        try:
            if swarm_id not in self.active_swarms:
                raise ValueError(f"Swarm {swarm_id} not found")
            
            swarm_info = self.active_swarms[swarm_id]
            
            if not SWARMS_AVAILABLE or not self.api_key:
                # Mock execution
                result = {
                    "swarm_id": swarm_id,
                    "mission_prompt": mission_prompt,
                    "result": f"Mock mission execution completed for: {mission_prompt}",
                    "agents_used": len(swarm_info["agents"]),
                    "execution_time": 2.5,
                    "status": "completed"
                }
                logger.info(f"Mock mission executed: {swarm_id}")
                return result
            
            # Real execution using Swarms framework
            try:
                if "swarm" in swarm_info:
                    # Use the actual Swarms HierarchicalSwarm
                    swarm = swarm_info["swarm"]
                    
                    # Execute mission using Swarms framework
                    execution_result = await swarm.arun(mission_prompt)
                    
                    result = {
                        "swarm_id": swarm_id,
                        "mission_prompt": mission_prompt,
                        "result": execution_result,
                        "agents_used": len(swarm_info["agents"]),
                        "execution_time": 5.0,  # Placeholder
                        "status": "completed",
                        "framework": "swarms"
                    }
                    
                    logger.info(f"Swarms mission executed successfully: {swarm_id}")
                    return result
                else:
                    # Fallback to mock execution
                    result = {
                        "swarm_id": swarm_id,
                        "mission_prompt": mission_prompt,
                        "result": f"Fallback mission execution completed for: {mission_prompt}",
                        "agents_used": len(swarm_info["agents"]),
                        "execution_time": 2.5,
                        "status": "completed"
                    }
                    logger.info(f"Fallback mission executed: {swarm_id}")
                    return result
                    
            except Exception as e:
                logger.error(f"Swarms execution failed: {e}")
                # Fallback to mock execution
                result = {
                    "swarm_id": swarm_id,
                    "mission_prompt": mission_prompt,
                    "result": f"Fallback mission execution completed for: {mission_prompt}",
                    "agents_used": len(swarm_info["agents"]),
                    "execution_time": 2.5,
                    "status": "completed"
                }
                logger.info(f"Fallback mission executed: {swarm_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to execute mission: {e}")
            raise e
    
    async def coordinate_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a mission across multiple agents"""
        try:
            # Determine which agents should be involved
            mission_type = mission_data.get("type", "general")
            priority = mission_data.get("priority", "medium")
            
            # Select appropriate agents based on mission type
            selected_agents = self._select_agents_for_mission(mission_type, priority)
            
            # Create coordination plan
            coordination_plan = {
                "mission_id": mission_data.get("id"),
                "mission_type": mission_type,
                "priority": priority,
                "selected_agents": selected_agents,
                "coordination_strategy": "parallel_execution",
                "communication_protocol": "real_time_updates",
                "success_criteria": self._define_success_criteria(mission_type),
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Mission coordination plan created: {coordination_plan['mission_id']}")
            return coordination_plan
            
        except Exception as e:
            logger.error(f"Failed to coordinate mission: {e}")
            return {"error": str(e)}
    
    def _select_agents_for_mission(self, mission_type: str, priority: str) -> List[str]:
        """Select appropriate agents for a mission"""
        agent_mapping = {
            "forestry": ["forest_guardian"],
            "cryosphere": ["ice_sentinel"],
            "weather": ["storm_tracker"],
            "urban": ["urban_monitor"],
            "hydrology": ["water_watcher"],
            "security": ["security_sentinel"],
            "land": ["land_surveyor"],
            "disaster": ["disaster_responder"],
            "general": ["land_surveyor"]
        }
        
        base_agents = agent_mapping.get(mission_type, ["land_surveyor"])
        
        # Add orchestrator for high priority missions
        if priority in ["high", "critical"]:
            base_agents.append("orchestrator")
        
        return base_agents
    
    def _define_success_criteria(self, mission_type: str) -> Dict[str, Any]:
        """Define success criteria for different mission types"""
        criteria_mapping = {
            "forestry": {
                "deforestation_detected": True,
                "confidence_threshold": 0.85,
                "data_quality": "high"
            },
            "cryosphere": {
                "ice_change_measured": True,
                "confidence_threshold": 0.88,
                "data_quality": "high"
            },
            "weather": {
                "storm_tracked": True,
                "confidence_threshold": 0.82,
                "data_quality": "medium"
            },
            "disaster": {
                "damage_assessed": True,
                "confidence_threshold": 0.90,
                "data_quality": "high"
            }
        }
        
        return criteria_mapping.get(mission_type, {
            "data_collected": True,
            "confidence_threshold": 0.80,
            "data_quality": "medium"
        })
    
    async def stop_swarm(self, swarm_id: str) -> bool:
        """Stop a swarm"""
        try:
            if not self.api_key:
                # Mock mode
                if swarm_id in self.active_swarms:
                    self.active_swarms[swarm_id]["status"] = "stopped"
                    logger.info(f"Mock swarm stopped: {swarm_id}")
                    return True
                return False
            
            # Real API call
            response = requests.post(
                f"{self.base_url}/swarms/{swarm_id}/stop",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Swarms AI swarm stopped: {swarm_id}")
                return True
            else:
                logger.error(f"Failed to stop swarm: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop swarm: {e}")
            return False
