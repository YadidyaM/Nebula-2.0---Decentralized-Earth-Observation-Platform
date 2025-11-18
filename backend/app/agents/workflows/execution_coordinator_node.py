# LangGraph workflow node for coordinating parallel agent execution and Swarms AI swarm management
from typing import Dict, Any, List
import logging
import asyncio
from app.models.mission import Mission
from app.agents.base_agent import BaseAgent
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator

logger = logging.getLogger(__name__)

async def execution_coordinator_node(
    state: Dict[str, Any],
    managed_agents: Dict[str, BaseAgent],
    swarms_orchestrator: SwarmsOrchestrator = None
) -> Dict[str, Any]:
    """Execution coordinator node that manages parallel agent execution and Swarms AI coordination"""
    try:
        mission: Mission = state.get("mission")
        selected_agents: List[str] = state.get("selected_agents", [])
        swarm_id: str = state.get("swarm_id")
        
        if not mission:
            state["errors"] = state.get("errors", []) + ["No mission provided to coordinator"]
            return state
        
        execution_results = {}
        
        # Execute using Swarms AI swarm if available
        if swarm_id and swarms_orchestrator:
            try:
                mission_context = {
                    "mission_type": mission.type.value,
                    "target_area": {
                        "lat": mission.target_area.lat,
                        "lng": mission.target_area.lng,
                        "radius": mission.target_area.radius
                    },
                    "priority": mission.priority.value,
                    "description": mission.name
                }
                
                result = await swarms_orchestrator.execute_mission(
                    swarm_id,
                    mission.name,
                    mission_context
                )
                
                execution_results["swarm_execution"] = result
                logger.info(f"Swarms AI execution completed for mission {mission.id}")
            except Exception as e:
                logger.error(f"Error in Swarms execution: {e}")
                state["errors"] = state.get("errors", []) + [f"Swarms execution error: {str(e)}"]
        
        # Also execute with direct agents in parallel
        if selected_agents:
            agent_tasks = []
            for agent_id in selected_agents:
                if agent_id in managed_agents:
                    agent = managed_agents[agent_id]
                    if hasattr(agent, 'execute_mission'):
                        agent_tasks.append(_execute_agent_mission(agent, mission))
            
            if agent_tasks:
                agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
                for i, result in enumerate(agent_results):
                    if not isinstance(result, Exception):
                        execution_results[selected_agents[i]] = result
                    else:
                        logger.error(f"Agent execution error: {result}")
                        state["errors"] = state.get("errors", []) + [f"Agent {selected_agents[i]} error: {str(result)}"]
        
        state["execution_results"] = execution_results
        state["current_step"] = "execution_complete"
        return state
        
    except Exception as e:
        logger.error(f"Error in execution coordinator node: {e}")
        state["errors"] = state.get("errors", []) + [f"Execution coordination error: {str(e)}"]
        return state

async def _execute_agent_mission(agent: BaseAgent, mission: Mission) -> Dict[str, Any]:
    """Execute mission with a single agent"""
    try:
        result = await agent.execute_mission(mission)
        return result
    except Exception as e:
        logger.error(f"Error executing mission with agent {agent.agent_id}: {e}")
        return {"error": str(e), "agent_id": agent.agent_id}

