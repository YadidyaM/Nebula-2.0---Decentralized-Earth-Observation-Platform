from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import requests
import json
import math

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentStatus, Position
from app.models.mission import Mission, MissionStatus, MissionType

logger = logging.getLogger(__name__)

class DisasterResponder(BaseAgent):
    """Specialized agent for emergency response and disaster assessment"""
    
    def __init__(self, agent_id: str = "agent_disaster_responder", name: str = "Disaster Responder"):
        super().__init__(agent_id, name, "Disaster1234567890abcdef")
        self.specialization = ["emergency_response", "disaster_assessment", "crisis_management", "resource_coordination"]
        self.data_sources = {
            "emergency_services": "https://api.emergency-services.gov",
            "disaster_monitoring": "https://api.disaster-monitoring.org",
            "resource_management": "https://api.resource-management.gov",
            "communication_networks": "https://api.communication-networks.org"
        }
        self.disaster_types = ["earthquake", "flood", "wildfire", "hurricane", "tornado", "tsunami", "volcanic_eruption"]
        self.response_capabilities = {
            "search_rescue": True,
            "medical_emergency": True,
            "evacuation_coordination": True,
            "resource_distribution": True,
            "communication_restoration": True,
            "infrastructure_assessment": True
        }
        self.active_disasters: List[Dict[str, Any]] = []
        self.response_teams: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the Disaster Responder agent"""
        await self.update_status(AgentStatus.ONLINE)
        await self.update_position(Position(lat=28.0, lng=-82.0, alt=450000))
        logger.info("Disaster Responder initialized")
        
        # Start background monitoring
        asyncio.create_task(self._continuous_disaster_monitoring())
        asyncio.create_task(self._emergency_response_coordination())
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute disaster response mission"""
        try:
            await self.start_mission(mission)
            
            # Determine mission type and execute accordingly
            if mission.type == MissionType.DISASTER_MANAGEMENT:
                results = await self._coordinate_disaster_response(mission)
            elif mission.type == MissionType.SECURITY:
                results = await self._assess_emergency_situation(mission)
            else:
                results = await self._general_disaster_assessment(mission)
            
            await self.complete_mission(results)
            return results
            
        except Exception as e:
            logger.error(f"Error executing mission {mission.id}: {e}")
            await self.update_status(AgentStatus.ERROR)
            return {"error": str(e), "mission_id": mission.id}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process disaster data and coordinate emergency response"""
        try:
            analysis = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "disaster_response",
                "disasters_detected": [],
                "emergency_level": "none",
                "response_status": "standby",
                "resource_requirements": [],
                "recommendations": []
            }
            
            # Analyze earthquake data
            if "earthquake" in data:
                earthquake = data["earthquake"]
                magnitude = earthquake.get("magnitude", 0)
                
                if magnitude >= 7.0:
                    analysis["disasters_detected"].append({
                        "type": "major_earthquake",
                        "severity": "critical",
                        "magnitude": magnitude,
                        "location": earthquake.get("location", "unknown"),
                        "estimated_damage": "severe"
                    })
                    analysis["emergency_level"] = "critical"
                    analysis["response_status"] = "active"
                    analysis["resource_requirements"].append("search_rescue_teams")
                    analysis["resource_requirements"].append("medical_supplies")
                    analysis["recommendations"].append("activate_emergency_protocols")
                
                elif magnitude >= 5.0:
                    analysis["disasters_detected"].append({
                        "type": "moderate_earthquake",
                        "severity": "high",
                        "magnitude": magnitude,
                        "location": earthquake.get("location", "unknown"),
                        "estimated_damage": "moderate"
                    })
                    analysis["emergency_level"] = "high"
                    analysis["response_status"] = "preparing"
                    analysis["recommendations"].append("prepare_emergency_response")
            
            # Analyze flood data
            if "flood" in data:
                flood = data["flood"]
                water_level = flood.get("water_level", 0)
                flood_threshold = flood.get("flood_threshold", 0)
                
                if water_level > flood_threshold:
                    analysis["disasters_detected"].append({
                        "type": "flooding",
                        "severity": "high",
                        "water_level": water_level,
                        "flood_threshold": flood_threshold,
                        "location": flood.get("location", "unknown"),
                        "affected_area": flood.get("affected_area", 0)
                    })
                    analysis["emergency_level"] = "high"
                    analysis["response_status"] = "active"
                    analysis["resource_requirements"].append("evacuation_teams")
                    analysis["resource_requirements"].append("rescue_boats")
                    analysis["recommendations"].append("evacuate_flooded_areas")
            
            # Analyze wildfire data
            if "wildfire" in data:
                wildfire = data["wildfire"]
                fire_size = wildfire.get("size", 0)  # acres
                fire_intensity = wildfire.get("intensity", "low")
                
                if fire_size > 1000 or fire_intensity == "extreme":
                    analysis["disasters_detected"].append({
                        "type": "major_wildfire",
                        "severity": "critical",
                        "size": fire_size,
                        "intensity": fire_intensity,
                        "location": wildfire.get("location", "unknown"),
                        "containment": wildfire.get("containment", 0)
                    })
                    analysis["emergency_level"] = "critical"
                    analysis["response_status"] = "active"
                    analysis["resource_requirements"].append("firefighting_aircraft")
                    analysis["resource_requirements"].append("evacuation_teams")
                    analysis["recommendations"].append("evacuate_threatened_areas")
            
            # Analyze hurricane data
            if "hurricane" in data:
                hurricane = data["hurricane"]
                category = hurricane.get("category", 0)
                wind_speed = hurricane.get("wind_speed", 0)
                
                if category >= 3:
                    analysis["disasters_detected"].append({
                        "type": "major_hurricane",
                        "severity": "critical",
                        "category": category,
                        "wind_speed": wind_speed,
                        "location": hurricane.get("location", "unknown"),
                        "storm_surge": hurricane.get("storm_surge", 0)
                    })
                    analysis["emergency_level"] = "critical"
                    analysis["response_status"] = "active"
                    analysis["resource_requirements"].append("evacuation_coordination")
                    analysis["resource_requirements"].append("emergency_shelters")
                    analysis["recommendations"].append("mandatory_evacuation")
            
            # Analyze tornado data
            if "tornado" in data:
                tornado = data["tornado"]
                ef_scale = tornado.get("ef_scale", 0)
                
                if ef_scale >= 3:
                    analysis["disasters_detected"].append({
                        "type": "major_tornado",
                        "severity": "critical",
                        "ef_scale": ef_scale,
                        "path_length": tornado.get("path_length", 0),
                        "location": tornado.get("location", "unknown"),
                        "width": tornado.get("width", 0)
                    })
                    analysis["emergency_level"] = "critical"
                    analysis["response_status"] = "active"
                    analysis["resource_requirements"].append("search_rescue_teams")
                    analysis["resource_requirements"].append("medical_emergency_teams")
                    analysis["recommendations"].append("immediate_response_required")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing disaster data: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def _coordinate_disaster_response(self, mission: Mission) -> Dict[str, Any]:
        """Coordinate disaster response for a specific mission"""
        try:
            # Collect disaster assessment data
            disaster_data = await self._collect_disaster_data(mission.target_area)
            
            response_coordination = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "disaster_type": disaster_data.get("type", "unknown"),
                "severity": disaster_data.get("severity", "low"),
                "affected_area": disaster_data.get("affected_area", {}),
                "casualties": disaster_data.get("casualties", {}),
                "infrastructure_damage": disaster_data.get("infrastructure", {}),
                "response_teams_deployed": disaster_data.get("response_teams", []),
                "resource_allocation": disaster_data.get("resources", {}),
                "evacuation_status": disaster_data.get("evacuation", {}),
                "communication_status": disaster_data.get("communication", {}),
                "confidence_score": 0.94,
                "recommendations": []
            }
            
            # Generate response recommendations
            if disaster_data.get("severity") == "critical":
                response_coordination["recommendations"].append("deploy_all_available_resources")
                response_coordination["recommendations"].append("coordinate_with_federal_agencies")
            elif disaster_data.get("severity") == "high":
                response_coordination["recommendations"].append("mobilize_regional_resources")
                response_coordination["recommendations"].append("prepare_evacuation_plans")
            
            return response_coordination
            
        except Exception as e:
            logger.error(f"Error coordinating disaster response: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _assess_emergency_situation(self, mission: Mission) -> Dict[str, Any]:
        """Assess emergency situation for security missions"""
        try:
            # Collect emergency assessment data
            emergency_data = await self._collect_emergency_assessment_data(mission.target_area)
            
            emergency_assessment = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "emergency_type": emergency_data.get("type", "unknown"),
                "threat_level": emergency_data.get("threat_level", "low"),
                "affected_population": emergency_data.get("population", {}),
                "infrastructure_status": emergency_data.get("infrastructure", {}),
                "evacuation_capability": emergency_data.get("evacuation", {}),
                "medical_capacity": emergency_data.get("medical", {}),
                "communication_systems": emergency_data.get("communication", {}),
                "response_time_estimate": emergency_data.get("response_time", 0),
                "confidence_score": 0.91,
                "recommendations": []
            }
            
            # Generate emergency response recommendations
            if emergency_data.get("threat_level") == "critical":
                emergency_assessment["recommendations"].append("immediate_evacuation_required")
                emergency_assessment["recommendations"].append("deploy_emergency_medical_teams")
            elif emergency_data.get("threat_level") == "high":
                emergency_assessment["recommendations"].append("prepare_evacuation_procedures")
                emergency_assessment["recommendations"].append("mobilize_emergency_resources")
            
            return emergency_assessment
            
        except Exception as e:
            logger.error(f"Error assessing emergency situation: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _general_disaster_assessment(self, mission: Mission) -> Dict[str, Any]:
        """Perform general disaster assessment"""
        try:
            # Collect general disaster data
            disaster_data = await self._collect_general_disaster_data(mission.target_area)
            
            assessment = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "disaster_history": disaster_data.get("history", []),
                "vulnerability_assessment": disaster_data.get("vulnerabilities", {}),
                "preparedness_level": disaster_data.get("preparedness", {}),
                "response_capabilities": disaster_data.get("capabilities", {}),
                "resource_inventory": disaster_data.get("resources", {}),
                "communication_networks": disaster_data.get("networks", {}),
                "evacuation_routes": disaster_data.get("routes", []),
                "emergency_shelters": disaster_data.get("shelters", []),
                "confidence_score": 0.88,
                "recommendations": []
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in general disaster assessment: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _collect_disaster_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect disaster data from various sources"""
        try:
            disaster_data = {
                "type": "earthquake",
                "severity": "high",
                "affected_area": {
                    "radius": 50,  # km
                    "population": 100000,
                    "infrastructure_at_risk": ["hospitals", "schools", "power_grid"]
                },
                "casualties": {
                    "injured": 150,
                    "missing": 25,
                    "deceased": 5,
                    "evacuated": 5000
                },
                "infrastructure": {
                    "damaged_buildings": 200,
                    "destroyed_buildings": 15,
                    "damaged_roads": 25,
                    "power_outages": 10000
                },
                "response_teams": [
                    {"type": "search_rescue", "count": 5, "status": "deployed"},
                    {"type": "medical", "count": 3, "status": "deployed"},
                    {"type": "evacuation", "count": 2, "status": "deployed"}
                ],
                "resources": {
                    "medical_supplies": "adequate",
                    "food_water": "sufficient",
                    "shelter_capacity": "limited",
                    "transportation": "available"
                },
                "evacuation": {
                    "status": "in_progress",
                    "evacuated": 5000,
                    "remaining": 95000,
                    "shelters_available": 8
                },
                "communication": {
                    "cellular": "partial",
                    "radio": "operational",
                    "internet": "limited",
                    "emergency_channels": "active"
                }
            }
            
            return disaster_data
            
        except Exception as e:
            logger.error(f"Error collecting disaster data: {e}")
            return {}
    
    async def _collect_emergency_assessment_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data for emergency assessment"""
        try:
            emergency_data = {
                "type": "security_breach",
                "threat_level": "high",
                "population": {
                    "total": 50000,
                    "at_risk": 10000,
                    "evacuated": 2000,
                    "remaining": 8000
                },
                "infrastructure": {
                    "critical_facilities": "compromised",
                    "transportation": "limited",
                    "utilities": "operational",
                    "communications": "degraded"
                },
                "evacuation": {
                    "capacity": 15000,
                    "routes_available": 3,
                    "transportation": "limited",
                    "shelters": 5
                },
                "medical": {
                    "hospitals": "operational",
                    "ambulances": 8,
                    "medical_staff": "adequate",
                    "supplies": "sufficient"
                },
                "communication": {
                    "emergency_channels": "active",
                    "public_announcements": "operational",
                    "coordination_networks": "functional"
                },
                "response_time": 15  # minutes
            }
            
            return emergency_data
            
        except Exception as e:
            logger.error(f"Error collecting emergency assessment data: {e}")
            return {}
    
    async def _collect_general_disaster_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect general disaster data"""
        try:
            disaster_data = {
                "history": [
                    {"type": "earthquake", "year": 2020, "magnitude": 6.2, "damage": "moderate"},
                    {"type": "flood", "year": 2019, "severity": "high", "affected": 25000},
                    {"type": "wildfire", "year": 2018, "size": 5000, "containment": "complete"}
                ],
                "vulnerabilities": {
                    "seismic": "high",
                    "flood": "medium",
                    "wildfire": "low",
                    "hurricane": "medium"
                },
                "preparedness": {
                    "evacuation_plans": "updated",
                    "emergency_supplies": "adequate",
                    "training": "current",
                    "drills": "regular"
                },
                "capabilities": {
                    "search_rescue": "excellent",
                    "medical_emergency": "good",
                    "evacuation": "good",
                    "communication": "excellent"
                },
                "resources": {
                    "personnel": 150,
                    "equipment": "modern",
                    "vehicles": 25,
                    "supplies": "sufficient"
                },
                "networks": {
                    "emergency_services": "integrated",
                    "communication": "redundant",
                    "coordination": "efficient",
                    "backup_systems": "operational"
                },
                "routes": [
                    {"route": "primary", "capacity": 10000, "status": "clear"},
                    {"route": "secondary", "capacity": 5000, "status": "clear"},
                    {"route": "emergency", "capacity": 2000, "status": "clear"}
                ],
                "shelters": [
                    {"name": "Community Center", "capacity": 500, "status": "ready"},
                    {"name": "School Gym", "capacity": 300, "status": "ready"},
                    {"name": "Church Hall", "capacity": 200, "status": "ready"}
                ]
            }
            
            return disaster_data
            
        except Exception as e:
            logger.error(f"Error collecting general disaster data: {e}")
            return {}
    
    async def _continuous_disaster_monitoring(self):
        """Background task for continuous disaster monitoring"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Monitor for disaster events
                if self.status == AgentStatus.ONLINE:
                    # Simulate disaster monitoring
                    disaster_events = await self._check_for_disaster_events()
                    
                    for event in disaster_events:
                        if event.get("severity") == "critical":
                            logger.critical(f"Disaster Responder detected critical disaster: {event['type']}")
                            # Add to active disasters
                            self.active_disasters.append({
                                "id": f"disaster_{len(self.active_disasters) + 1}",
                                "type": event["type"],
                                "severity": event["severity"],
                                "location": event["location"],
                                "timestamp": datetime.now(),
                                "status": "active"
                            })
                        elif event.get("severity") == "high":
                            logger.warning(f"Disaster Responder detected high severity disaster: {event['type']}")
                
                # Wait 30 minutes before next monitoring cycle
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Error in continuous disaster monitoring: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _emergency_response_coordination(self):
        """Background task for emergency response coordination"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Coordinate response for active disasters
                for disaster in self.active_disasters:
                    if disaster["status"] == "active" and self.status == AgentStatus.ONLINE:
                        # Update disaster status
                        disaster["last_update"] = datetime.now()
                        
                        # Check if disaster is resolved
                        if (datetime.now() - disaster["timestamp"]).days > 7:
                            disaster["status"] = "resolved"
                            logger.info(f"Disaster {disaster['id']} marked as resolved")
                
                # Remove resolved disasters
                self.active_disasters = [d for d in self.active_disasters if d["status"] != "resolved"]
                
                # Wait 1 hour before next coordination cycle
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in emergency response coordination: {e}")
                await asyncio.sleep(1200)  # Wait 20 minutes on error
    
    async def _check_for_disaster_events(self) -> List[Dict[str, Any]]:
        """Check for new disaster events"""
        try:
            # Simulate disaster event detection
            events = []
            
            # Randomly generate disaster events for simulation
            import random
            if random.random() < 0.1:  # 10% chance of disaster event
                disaster_types = ["earthquake", "flood", "wildfire", "hurricane"]
                event_type = random.choice(disaster_types)
                severity = random.choice(["low", "medium", "high", "critical"])
                
                events.append({
                    "type": event_type,
                    "severity": severity,
                    "location": f"Area_{random.randint(1, 100)}",
                    "timestamp": datetime.now().isoformat()
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Error checking for disaster events: {e}")
            return []
    
    async def get_specialized_status(self) -> Dict[str, Any]:
        """Get specialized status information for Disaster Responder"""
        base_status = await self.get_health_status()
        
        specialized_status = {
            **base_status,
            "specialization": self.specialization,
            "disaster_types_monitored": len(self.disaster_types),
            "active_disasters": len(self.active_disasters),
            "response_capabilities": self.response_capabilities,
            "data_sources": list(self.data_sources.keys()),
            "last_monitoring_cycle": datetime.now().isoformat()
        }
        
        return specialized_status
