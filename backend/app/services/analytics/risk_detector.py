import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskType(str, Enum):
    FLOOD = "flood"
    DROUGHT = "drought"
    WILDFIRE = "wildfire"
    EARTHQUAKE = "earthquake"
    STORM = "storm"
    HEATWAVE = "heatwave"
    LANDSLIDE = "landslide"
    TSUNAMI = "tsunami"

@dataclass
class RiskAlert:
    id: str
    risk_type: RiskType
    risk_level: RiskLevel
    location: Dict[str, float]  # lat, lng
    confidence: float
    detected_at: datetime
    description: str
    affected_area: float  # km²
    population_at_risk: Optional[int] = None
    estimated_damage: Optional[float] = None
    recommended_actions: List[str] = None
    data_sources: List[str] = None

class RiskDetector:
    """Advanced risk detection system for environmental threats"""
    
    def __init__(self):
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.risk_thresholds = self._initialize_thresholds()
        self.detection_history: List[RiskAlert] = []
    
    def _initialize_thresholds(self) -> Dict[RiskType, Dict[str, float]]:
        """Initialize risk detection thresholds"""
        return {
            RiskType.FLOOD: {
                "precipitation_threshold": 50.0,  # mm/h
                "water_level_threshold": 3.0,     # meters
                "soil_moisture_threshold": 80.0,  # %
                "confidence_threshold": 0.75
            },
            RiskType.DROUGHT: {
                "precipitation_threshold": 5.0,   # mm/month
                "soil_moisture_threshold": 20.0, # %
                "temperature_threshold": 35.0,    # °C
                "confidence_threshold": 0.80
            },
            RiskType.WILDFIRE: {
                "temperature_threshold": 30.0,    # °C
                "humidity_threshold": 30.0,       # %
                "wind_speed_threshold": 15.0,     # m/s
                "vegetation_dryness_threshold": 0.3,
                "confidence_threshold": 0.85
            },
            RiskType.EARTHQUAKE: {
                "magnitude_threshold": 4.0,       # Richter scale
                "depth_threshold": 50.0,          # km
                "confidence_threshold": 0.90
            },
            RiskType.STORM: {
                "wind_speed_threshold": 25.0,     # m/s
                "pressure_threshold": 1000.0,     # hPa
                "precipitation_threshold": 20.0,  # mm/h
                "confidence_threshold": 0.80
            },
            RiskType.HEATWAVE: {
                "temperature_threshold": 35.0,    # °C
                "duration_threshold": 3,          # days
                "humidity_threshold": 60.0,       # %
                "confidence_threshold": 0.75
            }
        }
    
    async def analyze_environmental_data(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Analyze environmental data for risk detection"""
        try:
            alerts = []
            
            # Analyze each risk type
            for risk_type in RiskType:
                risk_alerts = await self._detect_risk_type(risk_type, data)
                alerts.extend(risk_alerts)
            
            # Update active alerts
            for alert in alerts:
                self.active_alerts[alert.id] = alert
                self.detection_history.append(alert)
            
            # Clean up old alerts
            await self._cleanup_old_alerts()
            
            logger.info(f"Risk analysis completed: {len(alerts)} alerts detected")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to analyze environmental data: {e}")
            return []
    
    async def _detect_risk_type(self, risk_type: RiskType, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect specific risk type"""
        alerts = []
        
        if risk_type == RiskType.FLOOD:
            alerts.extend(await self._detect_flood_risk(data))
        elif risk_type == RiskType.DROUGHT:
            alerts.extend(await self._detect_drought_risk(data))
        elif risk_type == RiskType.WILDFIRE:
            alerts.extend(await self._detect_wildfire_risk(data))
        elif risk_type == RiskType.EARTHQUAKE:
            alerts.extend(await self._detect_earthquake_risk(data))
        elif risk_type == RiskType.STORM:
            alerts.extend(await self._detect_storm_risk(data))
        elif risk_type == RiskType.HEATWAVE:
            alerts.extend(await self._detect_heatwave_risk(data))
        
        return alerts
    
    async def _detect_flood_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect flood risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.FLOOD]
        
        precipitation = data.get("precipitation", 0)
        water_level = data.get("water_level", 0)
        soil_moisture = data.get("soil_moisture", 0)
        
        risk_score = 0.0
        risk_factors = []
        
        if precipitation > thresholds["precipitation_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"High precipitation: {precipitation}mm/h")
        
        if water_level > thresholds["water_level_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"High water level: {water_level}m")
        
        if soil_moisture > thresholds["soil_moisture_threshold"]:
            risk_score += 0.2
            risk_factors.append(f"Saturated soil: {soil_moisture}%")
        
        if risk_score >= thresholds["confidence_threshold"]:
            risk_level = self._determine_risk_level(risk_score)
            
            alert = RiskAlert(
                id=f"flood_{int(datetime.now().timestamp())}",
                risk_type=RiskType.FLOOD,
                risk_level=risk_level,
                location=data.get("location", {"lat": 0, "lng": 0}),
                confidence=risk_score,
                detected_at=datetime.now(),
                description=f"Flood risk detected: {', '.join(risk_factors)}",
                affected_area=self._estimate_flood_area(data),
                population_at_risk=self._estimate_population_at_risk(data, RiskType.FLOOD),
                recommended_actions=self._get_flood_recommendations(risk_level),
                data_sources=["NOAA", "USGS", "Sentinel Hub"]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _detect_drought_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect drought risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.DROUGHT]
        
        precipitation = data.get("precipitation", 0)
        soil_moisture = data.get("soil_moisture", 0)
        temperature = data.get("temperature", 0)
        
        risk_score = 0.0
        risk_factors = []
        
        if precipitation < thresholds["precipitation_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"Low precipitation: {precipitation}mm/month")
        
        if soil_moisture < thresholds["soil_moisture_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"Low soil moisture: {soil_moisture}%")
        
        if temperature > thresholds["temperature_threshold"]:
            risk_score += 0.2
            risk_factors.append(f"High temperature: {temperature}°C")
        
        if risk_score >= thresholds["confidence_threshold"]:
            risk_level = self._determine_risk_level(risk_score)
            
            alert = RiskAlert(
                id=f"drought_{int(datetime.now().timestamp())}",
                risk_type=RiskType.DROUGHT,
                risk_level=risk_level,
                location=data.get("location", {"lat": 0, "lng": 0}),
                confidence=risk_score,
                detected_at=datetime.now(),
                description=f"Drought risk detected: {', '.join(risk_factors)}",
                affected_area=self._estimate_drought_area(data),
                population_at_risk=self._estimate_population_at_risk(data, RiskType.DROUGHT),
                recommended_actions=self._get_drought_recommendations(risk_level),
                data_sources=["NOAA", "NASA", "ESA Copernicus"]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _detect_wildfire_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect wildfire risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.WILDFIRE]
        
        temperature = data.get("temperature", 0)
        humidity = data.get("humidity", 0)
        wind_speed = data.get("wind_speed", 0)
        vegetation_dryness = data.get("vegetation_dryness", 0)
        
        risk_score = 0.0
        risk_factors = []
        
        if temperature > thresholds["temperature_threshold"]:
            risk_score += 0.3
            risk_factors.append(f"High temperature: {temperature}°C")
        
        if humidity < thresholds["humidity_threshold"]:
            risk_score += 0.3
            risk_factors.append(f"Low humidity: {humidity}%")
        
        if wind_speed > thresholds["wind_speed_threshold"]:
            risk_score += 0.2
            risk_factors.append(f"High wind speed: {wind_speed}m/s")
        
        if vegetation_dryness > thresholds["vegetation_dryness_threshold"]:
            risk_score += 0.2
            risk_factors.append(f"Dry vegetation: {vegetation_dryness}")
        
        if risk_score >= thresholds["confidence_threshold"]:
            risk_level = self._determine_risk_level(risk_score)
            
            alert = RiskAlert(
                id=f"wildfire_{int(datetime.now().timestamp())}",
                risk_type=RiskType.WILDFIRE,
                risk_level=risk_level,
                location=data.get("location", {"lat": 0, "lng": 0}),
                confidence=risk_score,
                detected_at=datetime.now(),
                description=f"Wildfire risk detected: {', '.join(risk_factors)}",
                affected_area=self._estimate_wildfire_area(data),
                population_at_risk=self._estimate_population_at_risk(data, RiskType.WILDFIRE),
                recommended_actions=self._get_wildfire_recommendations(risk_level),
                data_sources=["NOAA", "NASA EONET", "Sentinel Hub"]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _detect_earthquake_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect earthquake risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.EARTHQUAKE]
        
        magnitude = data.get("magnitude", 0)
        depth = data.get("depth", 0)
        
        if magnitude >= thresholds["magnitude_threshold"]:
            risk_score = min(magnitude / 7.0, 1.0)  # Normalize to 0-1
            
            if risk_score >= thresholds["confidence_threshold"]:
                risk_level = self._determine_risk_level(risk_score)
                
                alert = RiskAlert(
                    id=f"earthquake_{int(datetime.now().timestamp())}",
                    risk_type=RiskType.EARTHQUAKE,
                    risk_level=risk_level,
                    location=data.get("location", {"lat": 0, "lng": 0}),
                    confidence=risk_score,
                    detected_at=datetime.now(),
                    description=f"Earthquake detected: Magnitude {magnitude}, Depth {depth}km",
                    affected_area=self._estimate_earthquake_area(magnitude),
                    population_at_risk=self._estimate_population_at_risk(data, RiskType.EARTHQUAKE),
                    recommended_actions=self._get_earthquake_recommendations(risk_level),
                    data_sources=["USGS", "NASA EONET"]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_storm_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect storm risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.STORM]
        
        wind_speed = data.get("wind_speed", 0)
        pressure = data.get("pressure", 1013)
        precipitation = data.get("precipitation", 0)
        
        risk_score = 0.0
        risk_factors = []
        
        if wind_speed > thresholds["wind_speed_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"High wind speed: {wind_speed}m/s")
        
        if pressure < thresholds["pressure_threshold"]:
            risk_score += 0.3
            risk_factors.append(f"Low pressure: {pressure}hPa")
        
        if precipitation > thresholds["precipitation_threshold"]:
            risk_score += 0.3
            risk_factors.append(f"Heavy precipitation: {precipitation}mm/h")
        
        if risk_score >= thresholds["confidence_threshold"]:
            risk_level = self._determine_risk_level(risk_score)
            
            alert = RiskAlert(
                id=f"storm_{int(datetime.now().timestamp())}",
                risk_type=RiskType.STORM,
                risk_level=risk_level,
                location=data.get("location", {"lat": 0, "lng": 0}),
                confidence=risk_score,
                detected_at=datetime.now(),
                description=f"Storm risk detected: {', '.join(risk_factors)}",
                affected_area=self._estimate_storm_area(data),
                population_at_risk=self._estimate_population_at_risk(data, RiskType.STORM),
                recommended_actions=self._get_storm_recommendations(risk_level),
                data_sources=["NOAA", "NASA"]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _detect_heatwave_risk(self, data: Dict[str, Any]) -> List[RiskAlert]:
        """Detect heatwave risk"""
        alerts = []
        thresholds = self.risk_thresholds[RiskType.HEATWAVE]
        
        temperature = data.get("temperature", 0)
        duration = data.get("heatwave_duration", 0)
        humidity = data.get("humidity", 0)
        
        risk_score = 0.0
        risk_factors = []
        
        if temperature > thresholds["temperature_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"High temperature: {temperature}°C")
        
        if duration >= thresholds["duration_threshold"]:
            risk_score += 0.4
            risk_factors.append(f"Extended duration: {duration} days")
        
        if humidity > thresholds["humidity_threshold"]:
            risk_score += 0.2
            risk_factors.append(f"High humidity: {humidity}%")
        
        if risk_score >= thresholds["confidence_threshold"]:
            risk_level = self._determine_risk_level(risk_score)
            
            alert = RiskAlert(
                id=f"heatwave_{int(datetime.now().timestamp())}",
                risk_type=RiskType.HEATWAVE,
                risk_level=risk_level,
                location=data.get("location", {"lat": 0, "lng": 0}),
                confidence=risk_score,
                detected_at=datetime.now(),
                description=f"Heatwave risk detected: {', '.join(risk_factors)}",
                affected_area=self._estimate_heatwave_area(data),
                population_at_risk=self._estimate_population_at_risk(data, RiskType.HEATWAVE),
                recommended_actions=self._get_heatwave_recommendations(risk_level),
                data_sources=["NOAA", "NASA"]
            )
            alerts.append(alert)
        
        return alerts
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.7:
            return RiskLevel.HIGH
        elif risk_score >= 0.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _estimate_flood_area(self, data: Dict[str, Any]) -> float:
        """Estimate flood affected area"""
        water_level = data.get("water_level", 0)
        return min(water_level * 100, 1000)  # km²
    
    def _estimate_drought_area(self, data: Dict[str, Any]) -> float:
        """Estimate drought affected area"""
        soil_moisture = data.get("soil_moisture", 50)
        return max((50 - soil_moisture) * 20, 100)  # km²
    
    def _estimate_wildfire_area(self, data: Dict[str, Any]) -> float:
        """Estimate wildfire risk area"""
        wind_speed = data.get("wind_speed", 0)
        return min(wind_speed * 10, 500)  # km²
    
    def _estimate_earthquake_area(self, magnitude: float) -> float:
        """Estimate earthquake affected area"""
        return min(magnitude * 50, 2000)  # km²
    
    def _estimate_storm_area(self, data: Dict[str, Any]) -> float:
        """Estimate storm affected area"""
        wind_speed = data.get("wind_speed", 0)
        return min(wind_speed * 15, 1000)  # km²
    
    def _estimate_heatwave_area(self, data: Dict[str, Any]) -> float:
        """Estimate heatwave affected area"""
        temperature = data.get("temperature", 25)
        return min((temperature - 25) * 100, 2000)  # km²
    
    def _estimate_population_at_risk(self, data: Dict[str, Any], risk_type: RiskType) -> int:
        """Estimate population at risk"""
        # Mock calculation based on area and population density
        area = self._estimate_flood_area(data) if risk_type == RiskType.FLOOD else 100
        population_density = 100  # people per km²
        return int(area * population_density)
    
    def _get_flood_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get flood risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Monitor water levels", "Check drainage systems"],
            RiskLevel.MEDIUM: ["Prepare sandbags", "Evacuate low-lying areas"],
            RiskLevel.HIGH: ["Evacuate immediately", "Activate emergency services"],
            RiskLevel.CRITICAL: ["Mass evacuation", "Emergency response deployment"]
        }
        return recommendations.get(risk_level, [])
    
    def _get_drought_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get drought risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Monitor water usage", "Implement water conservation"],
            RiskLevel.MEDIUM: ["Water restrictions", "Irrigation management"],
            RiskLevel.HIGH: ["Emergency water supply", "Crop protection measures"],
            RiskLevel.CRITICAL: ["Water rationing", "Emergency relief deployment"]
        }
        return recommendations.get(risk_level, [])
    
    def _get_wildfire_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get wildfire risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Clear vegetation", "Monitor fire conditions"],
            RiskLevel.MEDIUM: ["Fire prevention measures", "Evacuation preparation"],
            RiskLevel.HIGH: ["Evacuate high-risk areas", "Deploy firefighting resources"],
            RiskLevel.CRITICAL: ["Mass evacuation", "Emergency fire response"]
        }
        return recommendations.get(risk_level, [])
    
    def _get_earthquake_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get earthquake risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Check building safety", "Prepare emergency kit"],
            RiskLevel.MEDIUM: ["Secure heavy objects", "Evacuate unsafe buildings"],
            RiskLevel.HIGH: ["Evacuate immediately", "Activate emergency services"],
            RiskLevel.CRITICAL: ["Mass evacuation", "Emergency response deployment"]
        }
        return recommendations.get(risk_level, [])
    
    def _get_storm_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get storm risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Monitor weather updates", "Secure outdoor objects"],
            RiskLevel.MEDIUM: ["Seek shelter", "Avoid outdoor activities"],
            RiskLevel.HIGH: ["Evacuate if necessary", "Activate emergency services"],
            RiskLevel.CRITICAL: ["Mass evacuation", "Emergency response deployment"]
        }
        return recommendations.get(risk_level, [])
    
    def _get_heatwave_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get heatwave risk recommendations"""
        recommendations = {
            RiskLevel.LOW: ["Stay hydrated", "Avoid outdoor activities"],
            RiskLevel.MEDIUM: ["Use cooling centers", "Check on vulnerable people"],
            RiskLevel.HIGH: ["Emergency cooling", "Heat illness prevention"],
            RiskLevel.CRITICAL: ["Mass cooling centers", "Emergency medical response"]
        }
        return recommendations.get(risk_level, [])
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        expired_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.detected_at < cutoff_time
        ]
        
        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]
        
        if expired_alerts:
            logger.info(f"Cleaned up {len(expired_alerts)} expired alerts")
    
    async def get_active_alerts(self) -> List[RiskAlert]:
        """Get all active risk alerts"""
        return list(self.active_alerts.values())
    
    async def get_alerts_by_type(self, risk_type: RiskType) -> List[RiskAlert]:
        """Get alerts by risk type"""
        return [alert for alert in self.active_alerts.values() if alert.risk_type == risk_type]
    
    async def get_alerts_by_level(self, risk_level: RiskLevel) -> List[RiskAlert]:
        """Get alerts by risk level"""
        return [alert for alert in self.active_alerts.values() if alert.risk_level == risk_level]
