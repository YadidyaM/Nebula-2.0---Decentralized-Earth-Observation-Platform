# LangGraph workflow node for aggregating and validating mission results using Gemini AI
from typing import Dict, Any
import logging
from app.services.ai.gemini_service import gemini_service
from app.models.mission import Mission, MissionStatus

logger = logging.getLogger(__name__)

async def result_aggregator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Result aggregation node that validates and aggregates results using Gemini AI"""
    try:
        mission: Mission = state.get("mission")
        execution_results = state.get("execution_results", {})
        
        if not mission:
            state["errors"] = state.get("errors", []) + ["No mission provided to aggregator"]
            return state
        
        aggregated_results = {
            "mission_id": mission.id,
            "timestamp": mission.created_at.isoformat(),
            "results": execution_results,
            "validation": None,
            "confidence_score": 0.0,
            "anomalies": []
        }
        
        # Use Gemini to validate and analyze results
        if gemini_service.is_available() and execution_results:
            try:
                validation = await gemini_service.detect_anomalies(
                    execution_results,
                    f"Mission {mission.id} results validation for {mission.type.value} mission"
                )
                
                if validation:
                    aggregated_results["validation"] = validation
                    aggregated_results["confidence_score"] = validation.get("confidence_score", 0.8)
                    aggregated_results["anomalies"] = validation.get("anomalies", [])
                    
                    logger.info(f"Gemini validation completed for mission {mission.id}")
            except Exception as e:
                logger.error(f"Error in Gemini validation: {e}")
                aggregated_results["validation_error"] = str(e)
        
        # Calculate overall confidence score
        if not aggregated_results["confidence_score"]:
            aggregated_results["confidence_score"] = _calculate_confidence_fallback(execution_results)
        
        # Update mission with results
        mission.results = aggregated_results
        mission.confidence_score = aggregated_results["confidence_score"]
        mission.anomaly_detected = len(aggregated_results["anomalies"]) > 0
        
        # Determine mission status
        if state.get("errors"):
            mission.status = MissionStatus.FAILED
        elif aggregated_results["confidence_score"] >= 0.7:
            mission.status = MissionStatus.COMPLETED
        else:
            mission.status = MissionStatus.FAILED
        
        state["execution_results"] = aggregated_results
        state["current_step"] = "complete"
        state["completed"] = True
        
        logger.info(f"Result aggregation completed for mission {mission.id}")
        return state
        
    except Exception as e:
        logger.error(f"Error in result aggregator node: {e}")
        state["errors"] = state.get("errors", []) + [f"Result aggregation error: {str(e)}"]
        mission.status = MissionStatus.FAILED
        return state

def _calculate_confidence_fallback(results: Dict[str, Any]) -> float:
    """Calculate confidence score fallback when Gemini is unavailable"""
    if not results:
        return 0.5
    
    # Simple heuristic: more results = higher confidence
    num_results = len(results)
    if num_results == 0:
        return 0.0
    elif num_results == 1:
        return 0.7
    elif num_results >= 2:
        return 0.85
    
    return 0.75

