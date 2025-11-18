# Gemini-powered mission planner for analyzing requirements, generating optimal plans, and predicting outcomes
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.services.ai.gemini_service import gemini_service
from app.models.mission import Mission, MissionType, Priority
from app.agents.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

class MissionPlanner:
    """Gemini-powered mission planner for intelligent mission planning and resource allocation"""
    
    def __init__(self):
        self.agent_factory = AgentFactory()
    
    async def analyze_mission_requirements(self, mission_description: str, mission_type: MissionType, 
                                          target_area: Dict[str, Any], priority: Priority) -> Dict[str, Any]:
        """Analyze mission requirements using Gemini AI"""
        try:
            if gemini_service.is_available():
                analysis = await gemini_service.analyze_mission_requirements(
                    mission_description,
                    mission_type.value,
                    target_area
                )
                return analysis or {}
            
            # Fallback analysis
            return self._fallback_analysis(mission_type, target_area, priority)
            
        except Exception as e:
            logger.error(f"Error analyzing mission requirements: {e}")
            return {}
    
    async def generate_mission_plan(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal mission plan using Gemini AI"""
        try:
            mission_type = mission_data.get("type")
            target_area = mission_data.get("target_area", {})
            priority = mission_data.get("priority", "medium")
            
            # Use Gemini to generate mission plan
            if gemini_service.is_available():
                plan_prompt = f"""
                Generate a comprehensive mission plan for:
                - Mission Type: {mission_type}
                - Target Area: {target_area}
                - Priority: {priority}
                
                Provide:
                1. Required resources (satellites, agents, data sources)
                2. Optimal agent selection
                3. Mission timeline and phases
                4. Risk assessment
                5. Success criteria
                6. Resource allocation
                
                Return as structured JSON.
                """
                
                plan_response = await gemini_service.generate_text(plan_prompt, model_type="pro", temperature=0.3)
                
                if plan_response:
                    # Try to parse JSON from response
                    import json
                    try:
                        json_match = plan_response.find("{")
                        if json_match != -1:
                            json_str = plan_response[json_match:]
                            json_end = json_str.rfind("}")
                            if json_end != -1:
                                return json.loads(json_str[:json_end+1])
                    except Exception as e:
                        logger.debug(f"Could not parse JSON from Gemini response: {e}")
            
            # Fallback plan generation
            return self._generate_fallback_plan(mission_data)
            
        except Exception as e:
            logger.error(f"Error generating mission plan: {e}")
            return {}
    
    async def predict_mission_outcome(self, mission_plan: Dict[str, Any], 
                                     historical_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict mission outcomes and risks using Gemini AI"""
        try:
            if gemini_service.is_available():
                prediction_prompt = f"""
                Predict the outcome of this mission plan:
                {mission_prompt}
                
                Historical data: {historical_data or "None"}
                
                Provide:
                1. Success probability
                2. Expected duration
                3. Potential risks
                4. Mitigation strategies
                5. Resource requirements
                
                Return as JSON.
                """
                
                prediction = await gemini_service.generate_text(prediction_prompt, model_type="pro", temperature=0.2)
                
                if prediction:
                    import json
                    try:
                        json_match = prediction.find("{")
                        if json_match != -1:
                            json_str = prediction[json_match:]
                            json_end = json_str.rfind("}")
                            if json_end != -1:
                                return json.loads(json_str[:json_end+1])
                    except Exception as e:
                        logger.debug(f"Could not parse prediction JSON: {e}")
            
            # Fallback prediction
            return {
                "success_probability": 0.85,
                "expected_duration_hours": 2.0,
                "risks": ["data_quality", "weather_conditions"],
                "mitigation_strategies": ["backup_data_sources", "extended_timeline"]
            }
            
        except Exception as e:
            logger.error(f"Error predicting mission outcome: {e}")
            return {}
    
    def _fallback_analysis(self, mission_type: MissionType, target_area: Dict[str, Any], priority: Priority) -> Dict[str, Any]:
        """Fallback mission requirement analysis"""
        return {
            "required_resources": ["satellite_imagery", "environmental_data"],
            "optimal_agents": [mission_type.value],
            "estimated_duration": 3600,
            "risk_level": priority.value
        }
    
    def _generate_fallback_plan(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback mission plan"""
        return {
            "phases": [
                {"name": "planning", "duration": 300},
                {"name": "execution", "duration": 1800},
                {"name": "analysis", "duration": 600}
            ],
            "resources": ["satellite_access", "agent_coordination"],
            "success_criteria": {"data_quality": 0.8, "coverage": 0.9}
        }

# Global instance
mission_planner = MissionPlanner()

