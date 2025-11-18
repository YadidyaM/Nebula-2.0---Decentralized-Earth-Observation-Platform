# LangGraph workflow node for intelligent agent selection using Gemini AI reasoning
from typing import Dict, Any, List
import logging
from app.services.ai.gemini_service import gemini_service
from app.models.mission import Mission
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

async def agent_selector_node(state: Dict[str, Any], managed_agents: Dict[str, BaseAgent]) -> Dict[str, Any]:
    """Agent selection node that uses Gemini to intelligently select optimal agents for mission"""
    try:
        mission: Mission = state.get("mission")
        mission_plan = state.get("mission_plan", {})
        
        if not mission:
            state["errors"] = state.get("errors", []) + ["No mission provided to selector"]
            return state
        
        # Use Gemini for intelligent agent selection
        if gemini_service.is_available():
            # Collect agent capabilities
            agent_capabilities = []
            for agent_id, agent in managed_agents.items():
                agent_capabilities.append({
                    "id": agent_id,
                    "name": agent.name,
                    "specializations": agent.specialization,
                    "success_rate": agent.success_rate
                })
            
            # Get reasoning from Gemini
            reasoning = await gemini_service.reason_about_mission(
                {
                    "type": mission.type.value,
                    "priority": mission.priority.value,
                    "plan": mission_plan
                },
                [cap for agent in agent_capabilities for cap in agent["specializations"]]
            )
            
            # Select agents based on reasoning
            selected = _select_agents_intelligent(mission, agent_capabilities, reasoning)
            state["selected_agents"] = selected
            logger.info(f"Gemini-selected agents for {mission.id}: {selected}")
        else:
            # Fallback selection
            state["selected_agents"] = _select_agents_fallback(mission, managed_agents)
        
        state["current_step"] = "agent_selection_complete"
        return state
        
    except Exception as e:
        logger.error(f"Error in agent selector node: {e}")
        state["errors"] = state.get("errors", []) + [f"Agent selection error: {str(e)}"]
        return state

def _select_agents_intelligent(
    mission: Mission,
    agent_capabilities: List[Dict[str, Any]],
    reasoning: Dict[str, Any]
) -> List[str]:
    """Select agents using Gemini reasoning"""
    agent_mapping = {
        "forestry": "agent_forest_guardian",
        "cryosphere": "agent_ice_sentinel",
        "weather": "agent_storm_tracker",
        "urban_infrastructure": "agent_urban_monitor",
        "hydrology": "agent_water_watcher",
        "security": "agent_security_sentinel",
        "land_monitoring": "agent_land_surveyor",
        "disaster_management": "agent_disaster_responder"
    }
    
    selected = []
    
    # Primary agent based on mission type
    primary_agent = agent_mapping.get(mission.type.value)
    if primary_agent:
        selected.append(primary_agent)
    
    # Add agents based on Gemini reasoning
    if reasoning and "recommended_agents" in reasoning:
        for rec_agent in reasoning["recommended_agents"]:
            if rec_agent not in selected:
                selected.append(rec_agent)
    
    # Limit to 3 agents max
    return selected[:3]

def _select_agents_fallback(mission: Mission, managed_agents: Dict[str, BaseAgent]) -> List[str]:
    """Fallback agent selection when Gemini is unavailable"""
    agent_mapping = {
        "forestry": "agent_forest_guardian",
        "cryosphere": "agent_ice_sentinel",
        "weather": "agent_storm_tracker",
        "urban_infrastructure": "agent_urban_monitor",
        "hydrology": "agent_water_watcher",
        "security": "agent_security_sentinel",
        "land_monitoring": "agent_land_surveyor",
        "disaster_management": "agent_disaster_responder"
    }
    
    primary_agent = agent_mapping.get(mission.type.value)
    if primary_agent and primary_agent in managed_agents:
        return [primary_agent]
    
    return []

