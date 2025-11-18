# LangGraph workflow node for mission planning using Gemini AI for intelligent mission analysis
from typing import Dict, Any
import logging
from app.services.ai.gemini_service import gemini_service
from app.models.mission import Mission

logger = logging.getLogger(__name__)

async def mission_planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mission planning node that uses Gemini to analyze requirements and create optimal plans"""
    try:
        mission: Mission = state.get("mission")
        
        if not mission:
            state["errors"] = state.get("errors", []) + ["No mission provided to planner"]
            return state
        
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
                logger.info(f"Gemini-generated mission plan created for {mission.id}")
            else:
                # Fallback plan
                state["mission_plan"] = _create_fallback_plan(mission)
        else:
            state["mission_plan"] = _create_fallback_plan(mission)
        
        state["current_step"] = "planning_complete"
        return state
        
    except Exception as e:
        logger.error(f"Error in mission planner node: {e}")
        state["errors"] = state.get("errors", []) + [f"Planning error: {str(e)}"]
        return state

def _create_fallback_plan(mission: Mission) -> Dict[str, Any]:
    """Create a fallback mission plan when Gemini is unavailable"""
    return {
        "resources": ["satellite_imagery", "environmental_data", "weather_data"],
        "estimated_duration": 3600,  # 1 hour
        "risk_level": "medium",
        "required_agents": 1,
        "data_sources": ["NASA", "NOAA", "USGS"]
    }

