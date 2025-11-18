# LangGraph-based orchestrator implementing state machine for agent workflow coordination
from typing import Dict, List, Optional, Any, TypedDict, Annotated
from datetime import datetime
import asyncio
import logging

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available. Install with: pip install langgraph")

from app.models.mission import Mission, MissionStatus
from app.agents.base_agent import BaseAgent
from app.services.ai.gemini_service import gemini_service
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator

logger = logging.getLogger(__name__)

class MissionState(TypedDict):
    """State representation for LangGraph workflow"""
    mission: Mission
    current_step: str
    selected_agents: List[str]
    mission_plan: Optional[Dict[str, Any]]
    execution_results: Optional[Dict[str, Any]]
    swarm_id: Optional[str]
    errors: List[str]
    completed: bool

class LangGraphOrchestrator:
    """LangGraph-based orchestrator for managing agent workflows with state machines"""
    
    def __init__(self, swarms_orchestrator: Optional[SwarmsOrchestrator] = None):
        self.swarms_orchestrator = swarms_orchestrator
        self.workflow: Optional[StateGraph] = None
        self.managed_agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, MissionState] = {}
        
        if LANGGRAPH_AVAILABLE:
            self._build_workflow()
        else:
            logger.warning("LangGraph not available, orchestrator will use fallback mode")
    
    def _build_workflow(self):
        """Build the LangGraph workflow state machine"""
        if not LANGGRAPH_AVAILABLE:
            return
        
        workflow = StateGraph(MissionState)
        
        # Add nodes
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("agent_selection", self._agent_selection_node)
        workflow.add_node("swarm_formation", self._swarm_formation_node)
        workflow.add_node("execution", self._execution_node)
        workflow.add_node("monitoring", self._monitoring_node)
        workflow.add_node("result_aggregation", self._result_aggregation_node)
        
        # Define edges
        workflow.set_entry_point("planning")
        workflow.add_edge("planning", "agent_selection")
        workflow.add_conditional_edges(
            "agent_selection",
            self._should_form_swarm,
            {
                "swarm": "swarm_formation",
                "direct": "execution"
            }
        )
        workflow.add_edge("swarm_formation", "execution")
        workflow.add_edge("execution", "monitoring")
        workflow.add_conditional_edges(
            "monitoring",
            self._is_complete,
            {
                "complete": "result_aggregation",
                "continue": "execution"
            }
        )
        workflow.add_edge("result_aggregation", END)
        
        self.workflow = workflow.compile()
        logger.info("LangGraph workflow built successfully")
    
    async def _planning_node(self, state: MissionState) -> MissionState:
        """Planning node - uses Gemini to analyze mission and create plan"""
        try:
            mission = state["mission"]
            
            # Use Gemini to analyze mission requirements
            if gemini_service.is_available():
                mission_data = {
                    "type": mission.type.value,
                    "name": mission.name,
                    "priority": mission.priority.value,
                    "target_area": {
                        "lat": mission.target_area.lat,
                        "lng": mission.target_area.lng,
                        "radius": mission.target_area.radius
                    }
                }
                
                plan = await gemini_service.analyze_mission_requirements(
                    mission.name,
                    mission.type.value,
                    mission_data["target_area"]
                )
                
                if plan:
                    state["mission_plan"] = plan
                    logger.info(f"Mission plan created for {mission.id}")
            else:
                # Fallback plan
                state["mission_plan"] = {
                    "resources": ["satellite_imagery", "environmental_data"],
                    "estimated_duration": 3600,
                    "risk_level": "medium"
                }
            
            state["current_step"] = "planning_complete"
            return state
            
        except Exception as e:
            logger.error(f"Error in planning node: {e}")
            state["errors"].append(f"Planning error: {str(e)}")
            return state
    
    async def _agent_selection_node(self, state: MissionState) -> MissionState:
        """Agent selection node - uses Gemini to select optimal agents"""
        try:
            mission = state["mission"]
            mission_plan = state.get("mission_plan", {})
            
            # Use Gemini for intelligent agent selection
            if gemini_service.is_available():
                agent_capabilities = [agent.specialization for agent in self.managed_agents.values()]
                
                reasoning = await gemini_service.reason_about_mission(
                    {
                        "type": mission.type.value,
                        "priority": mission.priority.value,
                        "plan": mission_plan
                    },
                    [cap for caps in agent_capabilities for cap in caps]
                )
                
                # Select agents based on mission type and reasoning
                selected = self._select_agents_for_mission(mission, reasoning)
                state["selected_agents"] = selected
            else:
                # Fallback selection
                state["selected_agents"] = self._select_agents_fallback(mission)
            
            state["current_step"] = "agent_selection_complete"
            return state
            
        except Exception as e:
            logger.error(f"Error in agent selection node: {e}")
            state["errors"].append(f"Agent selection error: {str(e)}")
            return state
    
    def _should_form_swarm(self, state: MissionState) -> str:
        """Determine if we should form a Swarms AI swarm"""
        selected_agents = state.get("selected_agents", [])
        mission = state["mission"]
        
        # Form swarm for high priority missions or multiple agents
        if len(selected_agents) > 1 or mission.priority.value in ["high", "critical"]:
            return "swarm"
        return "direct"
    
    async def _swarm_formation_node(self, state: MissionState) -> MissionState:
        """Swarm formation node - creates Swarms AI swarm if needed"""
        try:
            if not self.swarms_orchestrator:
                state["current_step"] = "swarm_formation_skipped"
                return state
            
            selected_agents = state.get("selected_agents", [])
            mission = state["mission"]
            
            # Create agent configs for Swarms
            agent_configs = []
            for agent_id in selected_agents:
                if agent_id in self.managed_agents:
                    agent = self.managed_agents[agent_id]
                    agent_configs.append({
                        "agent_name": agent.name,
                        "system_prompt": f"You are {agent.name}, specialized in {', '.join(agent.specialization)}",
                        "llm": "gpt-4",
                        "max_loops": 5,
                        "temperature": 0.7
                    })
            
            if agent_configs:
                swarm_id = await self.swarms_orchestrator.create_swarm(
                    f"mission_{mission.id}",
                    agent_configs
                )
                state["swarm_id"] = swarm_id
                logger.info(f"Swarm {swarm_id} created for mission {mission.id}")
            
            state["current_step"] = "swarm_formation_complete"
            return state
            
        except Exception as e:
            logger.error(f"Error in swarm formation node: {e}")
            state["errors"].append(f"Swarm formation error: {str(e)}")
            return state
    
    async def _execution_node(self, state: MissionState) -> MissionState:
        """Execution node - executes mission using selected agents or swarm"""
        try:
            mission = state["mission"]
            swarm_id = state.get("swarm_id")
            selected_agents = state.get("selected_agents", [])
            
            if swarm_id and self.swarms_orchestrator:
                # Execute using Swarms AI
                mission_context = {
                    "mission_type": mission.type.value,
                    "target_area": {
                        "lat": mission.target_area.lat,
                        "lng": mission.target_area.lng,
                        "radius": mission.target_area.radius
                    },
                    "priority": mission.priority.value
                }
                
                result = await self.swarms_orchestrator.execute_mission(
                    swarm_id,
                    mission.name,
                    mission_context
                )
                
                state["execution_results"] = result
            else:
                # Execute using direct agent assignment
                results = {}
                for agent_id in selected_agents:
                    if agent_id in self.managed_agents:
                        agent = self.managed_agents[agent_id]
                        if hasattr(agent, 'execute_mission'):
                            result = await agent.execute_mission(mission)
                            results[agent_id] = result
                
                state["execution_results"] = results
            
            state["current_step"] = "execution_complete"
            return state
            
        except Exception as e:
            logger.error(f"Error in execution node: {e}")
            state["errors"].append(f"Execution error: {str(e)}")
            return state
    
    async def _monitoring_node(self, state: MissionState) -> MissionState:
        """Monitoring node - monitors mission progress"""
        try:
            execution_results = state.get("execution_results", {})
            
            # Check if mission is complete
            if execution_results:
                if isinstance(execution_results, dict):
                    if execution_results.get("status") == "completed":
                        state["completed"] = True
                    elif "error" in execution_results:
                        state["errors"].append(execution_results["error"])
                else:
                    state["completed"] = True
            
            state["current_step"] = "monitoring_complete"
            return state
            
        except Exception as e:
            logger.error(f"Error in monitoring node: {e}")
            state["errors"].append(f"Monitoring error: {str(e)}")
            return state
    
    def _is_complete(self, state: MissionState) -> str:
        """Check if mission is complete"""
        if state.get("completed", False) or state.get("errors"):
            return "complete"
        return "continue"
    
    async def _result_aggregation_node(self, state: MissionState) -> MissionState:
        """Result aggregation node - aggregates and validates results"""
        try:
            execution_results = state.get("execution_results", {})
            mission = state["mission"]
            
            # Use Gemini to validate and analyze results
            if gemini_service.is_available() and execution_results:
                validation = await gemini_service.detect_anomalies(
                    execution_results,
                    f"Mission {mission.id} results validation"
                )
                
                if validation:
                    state["execution_results"]["validation"] = validation
            
            state["current_step"] = "complete"
            state["completed"] = True
            return state
            
        except Exception as e:
            logger.error(f"Error in result aggregation node: {e}")
            state["errors"].append(f"Result aggregation error: {str(e)}")
            return state
    
    def _select_agents_for_mission(self, mission, reasoning: Optional[Dict[str, Any]] = None) -> List[str]:
        """Select agents for mission based on type and reasoning"""
        agent_mapping = {
            "forestry": ["agent_forest_guardian"],
            "cryosphere": ["agent_ice_sentinel"],
            "weather": ["agent_storm_tracker"],
            "urban_infrastructure": ["agent_urban_monitor"],
            "hydrology": ["agent_water_watcher"],
            "security": ["agent_security_sentinel"],
            "land_monitoring": ["agent_land_surveyor"],
            "disaster_management": ["agent_disaster_responder"]
        }
        
        base_agents = agent_mapping.get(mission.type.value, [])
        
        # Add additional agents based on reasoning
        if reasoning and "recommended_agents" in reasoning:
            base_agents.extend(reasoning["recommended_agents"])
        
        # Filter to only available agents
        available_agents = [aid for aid in base_agents if aid in self.managed_agents]
        return available_agents[:3]  # Limit to 3 agents
    
    def _select_agents_fallback(self, mission) -> List[str]:
        """Fallback agent selection"""
        return self._select_agents_for_mission(mission, None)
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute a mission using LangGraph workflow"""
        if not self.workflow:
            logger.warning("LangGraph workflow not available, using fallback")
            return await self._fallback_execution(mission)
        
        try:
            # Initialize state
            initial_state: MissionState = {
                "mission": mission,
                "current_step": "start",
                "selected_agents": [],
                "mission_plan": None,
                "execution_results": None,
                "swarm_id": None,
                "errors": [],
                "completed": False
            }
            
            # Store active workflow
            self.active_workflows[mission.id] = initial_state
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Update mission status
            if final_state.get("completed"):
                mission.status = MissionStatus.COMPLETED
            elif final_state.get("errors"):
                mission.status = MissionStatus.FAILED
            
            mission.results = final_state.get("execution_results")
            
            # Clean up
            self.active_workflows.pop(mission.id, None)
            
            return {
                "mission_id": mission.id,
                "status": "completed" if final_state.get("completed") else "failed",
                "results": final_state.get("execution_results"),
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Error executing mission with LangGraph: {e}")
            return await self._fallback_execution(mission)
    
    async def _fallback_execution(self, mission: Mission) -> Dict[str, Any]:
        """Fallback execution when LangGraph is not available"""
        selected_agents = self._select_agents_fallback(mission)
        
        results = {}
        for agent_id in selected_agents:
            if agent_id in self.managed_agents:
                agent = self.managed_agents[agent_id]
                if hasattr(agent, 'execute_mission'):
                    result = await agent.execute_mission(mission)
                    results[agent_id] = result
        
        return {
            "mission_id": mission.id,
            "status": "completed",
            "results": results,
            "method": "fallback"
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.managed_agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.agent_id} with LangGraph orchestrator")
    
    def get_workflow_status(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active workflow"""
        if mission_id in self.active_workflows:
            state = self.active_workflows[mission_id]
            return {
                "mission_id": mission_id,
                "current_step": state.get("current_step"),
                "selected_agents": state.get("selected_agents", []),
                "swarm_id": state.get("swarm_id"),
                "completed": state.get("completed", False),
                "errors": state.get("errors", [])
            }
        return None

