# Specialized agent for cryosphere monitoring and ice sheet analysis with Gemini AI integration
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
import requests
import json

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentStatus, Position
from app.models.mission import Mission, MissionStatus, MissionType
from app.services.ai.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class IceSentinel(BaseAgent):
    """Specialized agent for cryosphere monitoring and ice sheet analysis"""
    
    def __init__(self, agent_id: str = "agent_ice_sentinel", name: str = "Ice Sentinel"):
        super().__init__(agent_id, name, "Ice1234567890abcdef")
        self.specialization = ["cryosphere", "glacier_monitoring", "sea_ice", "ice_thickness"]
        self.data_sources = {
            "nasa_icesat2": "https://icesat-2.gsfc.nasa.gov/api",
            "esa_cryosat": "https://cryosat.esa.int/api",
            "noaa_sea_ice": "https://nsidc.org/api"
        }
        self.monitoring_regions = [
            {"name": "Arctic", "lat": 78.0, "lng": 15.0, "radius": 1000},
            {"name": "Antarctica", "lat": -82.0, "lng": 0.0, "radius": 2000},
            {"name": "Greenland", "lat": 71.0, "lng": -42.0, "radius": 500}
        ]
        
    async def initialize(self):
        """Initialize the Ice Sentinel agent"""
        await self.update_status(AgentStatus.ONLINE)
        await self.update_position(Position(lat=78.0, lng=15.0, alt=600000))
        logger.info("Ice Sentinel initialized")
        
        # Start background monitoring
        asyncio.create_task(self._continuous_monitoring())
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute cryosphere monitoring mission"""
        try:
            await self.start_mission(mission)
            
            # Determine mission type and execute accordingly
            if mission.type == MissionType.CRYOSPHERE:
                results = await self._monitor_ice_sheets(mission)
            else:
                results = await self._general_cryosphere_analysis(mission)
            
            await self.complete_mission(results)
            return results
            
        except Exception as e:
            logger.error(f"Error executing mission {mission.id}: {e}")
            await self.update_status(AgentStatus.ERROR)
            return {"error": str(e), "mission_id": mission.id}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process cryosphere environmental data and detect anomalies with Gemini AI reasoning"""
        try:
            analysis = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "cryosphere",
                "anomalies_detected": [],
                "risk_assessment": "low",
                "recommendations": []
            }
            
            # Analyze ice thickness changes
            if "ice_thickness" in data:
                thickness_change = data["ice_thickness"].get("change_rate", 0)
                if thickness_change < -0.1:  # Significant thinning
                    analysis["anomalies_detected"].append({
                        "type": "ice_thinning",
                        "severity": "high",
                        "location": data.get("location", "unknown"),
                        "change_rate": thickness_change
                    })
                    analysis["risk_assessment"] = "high"
                    analysis["recommendations"].append("immediate_monitoring_required")
            
            # Analyze sea ice extent
            if "sea_ice_extent" in data:
                extent = data["sea_ice_extent"].get("current", 0)
                historical_avg = data["sea_ice_extent"].get("historical_average", 0)
                if extent < historical_avg * 0.8:  # 20% below average
                    analysis["anomalies_detected"].append({
                        "type": "sea_ice_loss",
                        "severity": "medium",
                        "current_extent": extent,
                        "historical_average": historical_avg
                    })
                    analysis["risk_assessment"] = "medium"
            
            # Analyze glacier retreat
            if "glacier_position" in data:
                retreat_rate = data["glacier_position"].get("retreat_rate", 0)
                if retreat_rate > 50:  # meters per year
                    analysis["anomalies_detected"].append({
                        "type": "glacier_retreat",
                        "severity": "high",
                        "retreat_rate": retreat_rate,
                        "location": data.get("location", "unknown")
                    })
                    analysis["risk_assessment"] = "high"
                    analysis["recommendations"].append("deploy_emergency_monitoring")
            
            # Use Gemini for enhanced climate pattern reasoning
            if gemini_service.is_available():
                try:
                    gemini_reasoning = await gemini_service.reason_about_mission(
                        {"type": "cryosphere", "data": data, "current_analysis": analysis},
                        self.specialization
                    )
                    if gemini_reasoning and "recommendations" in gemini_reasoning:
                        analysis["recommendations"].extend(gemini_reasoning["recommendations"])
                except Exception as e:
                    logger.error(f"Error in Gemini reasoning for Ice Sentinel: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing environmental data: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def _monitor_ice_sheets(self, mission: Mission) -> Dict[str, Any]:
        """Monitor ice sheet changes for a specific mission"""
        try:
            # Simulate data collection from multiple sources
            ice_data = await self._collect_ice_data(mission.target_area)
            
            # Analyze ice sheet changes
            analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "ice_thickness": ice_data.get("thickness", {}),
                "ice_velocity": ice_data.get("velocity", {}),
                "surface_elevation": ice_data.get("elevation", {}),
                "anomalies_detected": [],
                "confidence_score": 0.92,
                "recommendations": []
            }
            
            # Detect ice sheet anomalies
            if ice_data.get("thickness", {}).get("change_rate", 0) < -0.05:
                analysis["anomalies_detected"].append({
                    "type": "ice_sheet_thinning",
                    "severity": "high",
                    "change_rate": ice_data["thickness"]["change_rate"]
                })
                analysis["recommendations"].append("increase_monitoring_frequency")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error monitoring ice sheets: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _general_cryosphere_analysis(self, mission: Mission) -> Dict[str, Any]:
        """Perform general cryosphere analysis"""
        try:
            # Collect comprehensive cryosphere data
            cryosphere_data = await self._collect_cryosphere_data(mission.target_area)
            
            analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "sea_ice_extent": cryosphere_data.get("sea_ice", {}),
                "glacier_status": cryosphere_data.get("glaciers", {}),
                "permafrost_conditions": cryosphere_data.get("permafrost", {}),
                "temperature_trends": cryosphere_data.get("temperature", {}),
                "anomalies_detected": [],
                "confidence_score": 0.88,
                "recommendations": []
            }
            
            # Analyze temperature trends
            temp_trend = cryosphere_data.get("temperature", {}).get("trend", 0)
            if temp_trend > 2.0:  # Significant warming
                analysis["anomalies_detected"].append({
                    "type": "rapid_warming",
                    "severity": "high",
                    "temperature_trend": temp_trend
                })
                analysis["recommendations"].append("urgent_climate_action_required")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in general cryosphere analysis: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _collect_ice_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect ice data from various sources"""
        try:
            # Simulate data collection from NASA ICESat-2
            ice_data = {
                "thickness": {
                    "current": 2.5,  # meters
                    "change_rate": -0.02,  # meters per year
                    "confidence": 0.95
                },
                "velocity": {
                    "speed": 150,  # meters per year
                    "direction": "southwest",
                    "confidence": 0.88
                },
                "elevation": {
                    "current": 2500,  # meters above sea level
                    "change_rate": -0.5,  # meters per year
                    "confidence": 0.92
                }
            }
            
            return ice_data
            
        except Exception as e:
            logger.error(f"Error collecting ice data: {e}")
            return {}
    
    async def _collect_cryosphere_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect comprehensive cryosphere data"""
        try:
            cryosphere_data = {
                "sea_ice": {
                    "extent": 15.2,  # million km²
                    "concentration": 85,  # percentage
                    "thickness": 1.8,  # meters
                    "trend": -0.3  # million km² per decade
                },
                "glaciers": {
                    "total_area": 200000,  # km²
                    "retreat_rate": 25,  # meters per year
                    "mass_balance": -0.8,  # meters water equivalent per year
                    "status": "retreating"
                },
                "permafrost": {
                    "active_layer_depth": 1.2,  # meters
                    "temperature": -2.5,  # degrees Celsius
                    "thaw_rate": 0.1,  # meters per year
                    "status": "thawing"
                },
                "temperature": {
                    "current": -15.2,  # degrees Celsius
                    "trend": 1.8,  # degrees Celsius per decade
                    "anomaly": 2.1,  # degrees above historical average
                    "confidence": 0.94
                }
            }
            
            return cryosphere_data
            
        except Exception as e:
            logger.error(f"Error collecting cryosphere data: {e}")
            return {}
    
    async def _continuous_monitoring(self):
        """Background task for continuous cryosphere monitoring"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Monitor each region periodically
                for region in self.monitoring_regions:
                    if self.status == AgentStatus.ONLINE:
                        # Collect data for this region
                        region_data = await self._collect_cryosphere_data(region)
                        
                        # Process the data
                        analysis = await self.process_environmental_data(region_data)
                        
                        # Log significant findings
                        if analysis.get("risk_assessment") in ["medium", "high"]:
                            logger.warning(f"Ice Sentinel detected {analysis['risk_assessment']} risk in {region['name']}")
                
                # Wait 1 hour before next monitoring cycle
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def get_specialized_status(self) -> Dict[str, Any]:
        """Get specialized status information for Ice Sentinel"""
        base_status = await self.get_health_status()
        
        specialized_status = {
            **base_status,
            "specialization": self.specialization,
            "monitoring_regions": len(self.monitoring_regions),
            "data_sources": list(self.data_sources.keys()),
            "last_monitoring_cycle": datetime.now().isoformat()
        }
        
        return specialized_status
