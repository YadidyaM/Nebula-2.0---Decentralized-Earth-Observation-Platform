# Specialized agent for weather monitoring and storm tracking with Gemini AI integration
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
from app.services.ai.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class StormTracker(BaseAgent):
    """Specialized agent for weather monitoring and storm tracking"""
    
    def __init__(self, agent_id: str = "agent_storm_tracker", name: str = "Storm Tracker"):
        super().__init__(agent_id, name, "Storm1234567890abcdef")
        self.specialization = ["weather", "atmospheric", "climate_patterns", "storm_tracking"]
        self.data_sources = {
            "noaa_weather": "https://api.weather.gov",
            "nasa_goes": "https://goes.gsfc.nasa.gov/api",
            "european_ecmwf": "https://api.ecmwf.int",
            "japan_jma": "https://www.jma.go.jp/api"
        }
        self.storm_types = ["hurricane", "typhoon", "cyclone", "tornado", "thunderstorm", "blizzard"]
        self.tracking_regions = [
            {"name": "Atlantic", "lat": 25.0, "lng": -60.0, "radius": 2000},
            {"name": "Pacific", "lat": 15.0, "lng": -150.0, "radius": 3000},
            {"name": "Indian", "lat": 10.0, "lng": 80.0, "radius": 2000}
        ]
        self.active_storms: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the Storm Tracker agent"""
        await self.update_status(AgentStatus.ONLINE)
        await self.update_position(Position(lat=25.0, lng=-80.0, alt=450000))
        logger.info("Storm Tracker initialized")
        
        # Start background monitoring
        asyncio.create_task(self._continuous_storm_monitoring())
        asyncio.create_task(self._weather_pattern_analysis())
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute weather monitoring mission"""
        try:
            await self.start_mission(mission)
            
            # Determine mission type and execute accordingly
            if mission.type == MissionType.WEATHER:
                results = await self._track_storm_system(mission)
            elif mission.type == MissionType.DISASTER_MANAGEMENT:
                results = await self._assess_storm_threat(mission)
            else:
                results = await self._general_weather_analysis(mission)
            
            await self.complete_mission(results)
            return results
            
        except Exception as e:
            logger.error(f"Error executing mission {mission.id}: {e}")
            await self.update_status(AgentStatus.ERROR)
            return {"error": str(e), "mission_id": mission.id}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather data and detect storm formations"""
        try:
            analysis = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "weather",
                "storms_detected": [],
                "risk_assessment": "low",
                "forecast": {},
                "recommendations": []
            }
            
            # Analyze atmospheric pressure
            if "pressure" in data:
                pressure = data["pressure"].get("current", 1013.25)
                pressure_trend = data["pressure"].get("trend", 0)
                
                if pressure < 1000 and pressure_trend < -2:  # Rapid pressure drop
                    analysis["storms_detected"].append({
                        "type": "low_pressure_system",
                        "severity": "medium",
                        "pressure": pressure,
                        "trend": pressure_trend,
                        "location": data.get("location", "unknown")
                    })
                    analysis["risk_assessment"] = "medium"
            
            # Analyze wind patterns
            if "wind" in data:
                wind_speed = data["wind"].get("speed", 0)
                wind_direction = data["wind"].get("direction", 0)
                
                if wind_speed > 25:  # Strong winds (m/s)
                    analysis["storms_detected"].append({
                        "type": "high_wind_event",
                        "severity": "high" if wind_speed > 40 else "medium",
                        "wind_speed": wind_speed,
                        "direction": wind_direction,
                        "location": data.get("location", "unknown")
                    })
                    analysis["risk_assessment"] = "high" if wind_speed > 40 else "medium"
            
            # Analyze temperature gradients
            if "temperature_gradient" in data:
                gradient = data["temperature_gradient"]
                if gradient > 10:  # Significant temperature difference
                    analysis["storms_detected"].append({
                        "type": "temperature_front",
                        "severity": "medium",
                        "gradient": gradient,
                        "location": data.get("location", "unknown")
                    })
                    analysis["recommendations"].append("monitor_for_severe_weather")
            
            # Analyze humidity and precipitation
            if "humidity" in data and "precipitation" in data:
                humidity = data["humidity"].get("current", 0)
                precipitation = data["precipitation"].get("rate", 0)
                
                if humidity > 90 and precipitation > 10:  # Heavy rain conditions
                    analysis["storms_detected"].append({
                        "type": "heavy_precipitation",
                        "severity": "high" if precipitation > 25 else "medium",
                        "humidity": humidity,
                        "precipitation_rate": precipitation,
                        "location": data.get("location", "unknown")
                    })
                    analysis["risk_assessment"] = "high" if precipitation > 25 else "medium"
            
            # Generate forecast
            analysis["forecast"] = await self._generate_weather_forecast(data)
            
            # Use Gemini for enhanced weather prediction
            if gemini_service.is_available():
                try:
                    gemini_reasoning = await gemini_service.reason_about_mission(
                        {"type": "weather", "data": data, "current_analysis": analysis},
                        self.specialization
                    )
                    if gemini_reasoning and "recommendations" in gemini_reasoning:
                        analysis["recommendations"].extend(gemini_reasoning["recommendations"])
                except Exception as e:
                    logger.error(f"Error in Gemini reasoning for Storm Tracker: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def _track_storm_system(self, mission: Mission) -> Dict[str, Any]:
        """Track a specific storm system"""
        try:
            # Collect weather data for the target area
            weather_data = await self._collect_weather_data(mission.target_area)
            
            # Analyze storm characteristics
            storm_analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "storm_classification": await self._classify_storm(weather_data),
                "current_position": weather_data.get("position", {}),
                "movement_vector": weather_data.get("movement", {}),
                "intensity": weather_data.get("intensity", {}),
                "predicted_path": await self._predict_storm_path(weather_data),
                "confidence_score": 0.89,
                "recommendations": []
            }
            
            # Add storm to active tracking list
            storm_info = {
                "id": f"storm_{mission.id}",
                "mission_id": mission.id,
                "classification": storm_analysis["storm_classification"],
                "position": storm_analysis["current_position"],
                "intensity": storm_analysis["intensity"],
                "last_update": datetime.now()
            }
            self.active_storms.append(storm_info)
            
            return storm_analysis
            
        except Exception as e:
            logger.error(f"Error tracking storm system: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _assess_storm_threat(self, mission: Mission) -> Dict[str, Any]:
        """Assess storm threat for disaster management"""
        try:
            # Collect comprehensive weather data
            threat_data = await self._collect_threat_assessment_data(mission.target_area)
            
            threat_analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "threat_level": "low",
                "storm_type": threat_data.get("storm_type", "unknown"),
                "estimated_arrival": threat_data.get("arrival_time"),
                "impact_zone": threat_data.get("impact_area", {}),
                "potential_damage": threat_data.get("damage_assessment", {}),
                "evacuation_recommendations": [],
                "confidence_score": 0.85,
                "recommendations": []
            }
            
            # Determine threat level
            storm_intensity = threat_data.get("intensity", {}).get("category", 0)
            if storm_intensity >= 3:  # Category 3+ hurricane
                threat_analysis["threat_level"] = "critical"
                threat_analysis["evacuation_recommendations"].append("immediate_evacuation")
            elif storm_intensity >= 1:  # Category 1+ hurricane
                threat_analysis["threat_level"] = "high"
                threat_analysis["evacuation_recommendations"].append("prepare_for_evacuation")
            elif threat_data.get("wind_speed", 0) > 20:  # Strong winds
                threat_analysis["threat_level"] = "medium"
                threat_analysis["recommendations"].append("secure_outdoor_objects")
            
            return threat_analysis
            
        except Exception as e:
            logger.error(f"Error assessing storm threat: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _general_weather_analysis(self, mission: Mission) -> Dict[str, Any]:
        """Perform general weather analysis"""
        try:
            # Collect weather data for the target area
            weather_data = await self._collect_weather_data(mission.target_area)
            
            analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "current_conditions": weather_data.get("current", {}),
                "temperature_trends": weather_data.get("temperature", {}),
                "precipitation_forecast": weather_data.get("precipitation", {}),
                "wind_patterns": weather_data.get("wind", {}),
                "atmospheric_pressure": weather_data.get("pressure", {}),
                "weather_alerts": weather_data.get("alerts", []),
                "confidence_score": 0.87,
                "recommendations": []
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in general weather analysis: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _collect_weather_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect weather data from various sources"""
        try:
            # Simulate data collection from NOAA and other sources
            weather_data = {
                "position": {
                    "lat": target_area.get("lat", 0),
                    "lng": target_area.get("lng", 0),
                    "altitude": 0
                },
                "current": {
                    "temperature": 22.5,  # Celsius
                    "humidity": 65,  # percentage
                    "pressure": 1013.25,  # hPa
                    "visibility": 10  # km
                },
                "wind": {
                    "speed": 15.2,  # m/s
                    "direction": 225,  # degrees
                    "gusts": 22.1  # m/s
                },
                "precipitation": {
                    "rate": 2.5,  # mm/hour
                    "accumulation": 12.3,  # mm
                    "type": "rain"
                },
                "movement": {
                    "speed": 25,  # km/h
                    "direction": 270,  # degrees (west)
                    "acceleration": 0.5  # km/h²
                },
                "intensity": {
                    "category": 1,  # Hurricane category
                    "sustained_winds": 120,  # km/h
                    "pressure": 980  # hPa
                }
            }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
            return {}
    
    async def _collect_threat_assessment_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data for threat assessment"""
        try:
            threat_data = {
                "storm_type": "hurricane",
                "intensity": {
                    "category": 2,
                    "sustained_winds": 155,  # km/h
                    "pressure": 965  # hPa
                },
                "arrival_time": (datetime.now() + timedelta(hours=48)).isoformat(),
                "impact_area": {
                    "radius": 200,  # km
                    "population_at_risk": 500000,
                    "infrastructure_at_risk": ["airports", "ports", "power_grid"]
                },
                "damage_assessment": {
                    "wind_damage": "moderate_to_severe",
                    "flood_risk": "high",
                    "storm_surge": 3.5,  # meters
                    "estimated_losses": 2.5e9  # USD
                },
                "wind_speed": 155,  # km/h
                "precipitation_forecast": {
                    "total": 300,  # mm
                    "peak_rate": 50  # mm/hour
                }
            }
            
            return threat_data
            
        except Exception as e:
            logger.error(f"Error collecting threat assessment data: {e}")
            return {}
    
    async def _classify_storm(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify storm type and characteristics"""
        try:
            wind_speed = weather_data.get("wind", {}).get("speed", 0)
            pressure = weather_data.get("current", {}).get("pressure", 1013.25)
            
            classification = {
                "type": "unknown",
                "category": 0,
                "severity": "low",
                "characteristics": []
            }
            
            # Classify based on wind speed and pressure
            if wind_speed > 74:  # Hurricane force winds (m/s)
                classification["type"] = "hurricane"
                classification["category"] = min(5, int((wind_speed - 74) / 15) + 1)
                classification["severity"] = "high" if classification["category"] >= 3 else "medium"
            elif wind_speed > 32:  # Gale force winds
                classification["type"] = "severe_storm"
                classification["severity"] = "medium"
            elif wind_speed > 17:  # Strong winds
                classification["type"] = "storm"
                classification["severity"] = "low"
            
            # Add pressure characteristics
            if pressure < 980:
                classification["characteristics"].append("very_low_pressure")
            elif pressure < 1000:
                classification["characteristics"].append("low_pressure")
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying storm: {e}")
            return {"type": "unknown", "category": 0, "severity": "low"}
    
    async def _predict_storm_path(self, weather_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict storm path for the next 72 hours"""
        try:
            current_pos = weather_data.get("position", {})
            movement = weather_data.get("movement", {})
            
            predicted_path = []
            current_lat = current_pos.get("lat", 0)
            current_lng = current_pos.get("lng", 0)
            speed = movement.get("speed", 25)  # km/h
            direction = movement.get("direction", 270)  # degrees
            
            # Convert direction to radians
            direction_rad = math.radians(direction)
            
            # Predict position for next 72 hours (every 6 hours)
            for hours in range(0, 73, 6):
                distance = speed * hours  # km
                
                # Calculate new position (simplified)
                lat_offset = (distance * math.cos(direction_rad)) / 111.32  # Approximate km per degree
                lng_offset = (distance * math.sin(direction_rad)) / (111.32 * math.cos(math.radians(current_lat)))
                
                predicted_pos = {
                    "lat": current_lat + lat_offset,
                    "lng": current_lng + lng_offset,
                    "timestamp": (datetime.now() + timedelta(hours=hours)).isoformat(),
                    "confidence": max(0.5, 1.0 - (hours / 72) * 0.3)  # Decreasing confidence over time
                }
                
                predicted_path.append(predicted_pos)
            
            return predicted_path
            
        except Exception as e:
            logger.error(f"Error predicting storm path: {e}")
            return []
    
    async def _generate_weather_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weather forecast based on current data"""
        try:
            forecast = {
                "short_term": {  # Next 24 hours
                    "temperature": {
                        "min": data.get("current", {}).get("temperature", 20) - 5,
                        "max": data.get("current", {}).get("temperature", 20) + 3
                    },
                    "precipitation": {
                        "probability": 60,  # percentage
                        "amount": 15  # mm
                    },
                    "wind": {
                        "speed": data.get("wind", {}).get("speed", 10) + 5,
                        "direction": data.get("wind", {}).get("direction", 180)
                    }
                },
                "medium_term": {  # Next 3 days
                    "temperature_trend": "increasing",
                    "precipitation_trend": "decreasing",
                    "storm_probability": 30
                },
                "long_term": {  # Next week
                    "seasonal_trend": "normal",
                    "climate_anomaly": "none"
                }
            }
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating weather forecast: {e}")
            return {}
    
    async def _continuous_storm_monitoring(self):
        """Background task for continuous storm monitoring"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Update active storm positions
                for storm in self.active_storms:
                    if self.status == AgentStatus.ONLINE:
                        # Simulate storm movement
                        storm["position"]["lat"] += 0.1
                        storm["position"]["lng"] += 0.05
                        storm["last_update"] = datetime.now()
                
                # Remove old storms (older than 7 days)
                cutoff_time = datetime.now() - timedelta(days=7)
                self.active_storms = [s for s in self.active_storms if s["last_update"] > cutoff_time]
                
                # Wait 30 minutes before next update
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Error in continuous storm monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _weather_pattern_analysis(self):
        """Background task for weather pattern analysis"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Analyze weather patterns in each tracking region
                for region in self.tracking_regions:
                    if self.status == AgentStatus.ONLINE:
                        # Collect regional weather data
                        region_data = await self._collect_weather_data(region)
                        
                        # Process the data
                        analysis = await self.process_environmental_data(region_data)
                        
                        # Log significant weather events
                        if analysis.get("risk_assessment") in ["medium", "high"]:
                            logger.warning(f"Storm Tracker detected {analysis['risk_assessment']} weather risk in {region['name']}")
                
                # Wait 2 hours before next analysis cycle
                await asyncio.sleep(7200)
                
            except Exception as e:
                logger.error(f"Error in weather pattern analysis: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def get_specialized_status(self) -> Dict[str, Any]:
        """Get specialized status information for Storm Tracker"""
        base_status = await self.get_health_status()
        
        specialized_status = {
            **base_status,
            "specialization": self.specialization,
            "tracking_regions": len(self.tracking_regions),
            "active_storms": len(self.active_storms),
            "data_sources": list(self.data_sources.keys()),
            "last_monitoring_cycle": datetime.now().isoformat()
        }
        
        return specialized_status
