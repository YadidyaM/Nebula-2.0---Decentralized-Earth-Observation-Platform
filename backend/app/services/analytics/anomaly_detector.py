import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AnomalyType(str, Enum):
    TEMPERATURE = "temperature"
    PRECIPITATION = "precipitation"
    VEGETATION = "vegetation"
    WATER_LEVEL = "water_level"
    AIR_QUALITY = "air_quality"
    SEISMIC = "seismic"
    ATMOSPHERIC = "atmospheric"

class AnomalySeverity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class AnomalyDetection:
    id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    location: Dict[str, float]  # lat, lng
    confidence: float
    detected_at: datetime
    description: str
    baseline_value: float
    current_value: float
    deviation_percentage: float
    data_sources: List[str]
    recommended_investigation: List[str]

class AnomalyDetector:
    """Advanced anomaly detection system for environmental data"""
    
    def __init__(self):
        self.baseline_data: Dict[str, Dict[str, float]] = {}
        self.anomaly_history: List[AnomalyDetection] = []
        self.detection_thresholds = self._initialize_thresholds()
        self.statistical_windows = {
            "short": timedelta(hours=24),
            "medium": timedelta(days=7),
            "long": timedelta(days=30)
        }
    
    def _initialize_thresholds(self) -> Dict[AnomalyType, Dict[str, float]]:
        """Initialize anomaly detection thresholds"""
        return {
            AnomalyType.TEMPERATURE: {
                "z_score_threshold": 2.5,
                "deviation_threshold": 15.0,  # %
                "confidence_threshold": 0.80
            },
            AnomalyType.PRECIPITATION: {
                "z_score_threshold": 2.0,
                "deviation_threshold": 50.0,  # %
                "confidence_threshold": 0.75
            },
            AnomalyType.VEGETATION: {
                "z_score_threshold": 2.0,
                "deviation_threshold": 20.0,  # %
                "confidence_threshold": 0.85
            },
            AnomalyType.WATER_LEVEL: {
                "z_score_threshold": 2.5,
                "deviation_threshold": 25.0,  # %
                "confidence_threshold": 0.90
            },
            AnomalyType.AIR_QUALITY: {
                "z_score_threshold": 2.0,
                "deviation_threshold": 30.0,  # %
                "confidence_threshold": 0.80
            },
            AnomalyType.SEISMIC: {
                "z_score_threshold": 3.0,
                "deviation_threshold": 100.0,  # %
                "confidence_threshold": 0.95
            },
            AnomalyType.ATMOSPHERIC: {
                "z_score_threshold": 2.0,
                "deviation_threshold": 20.0,  # %
                "confidence_threshold": 0.85
            }
        }
    
    async def detect_anomalies(self, data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect anomalies in environmental data"""
        try:
            anomalies = []
            
            # Update baseline data
            await self._update_baseline_data(data)
            
            # Detect anomalies for each data type
            for anomaly_type in AnomalyType:
                detected_anomalies = await self._detect_anomaly_type(anomaly_type, data)
                anomalies.extend(detected_anomalies)
            
            # Add to history
            self.anomaly_history.extend(anomalies)
            
            # Clean up old history
            await self._cleanup_history()
            
            logger.info(f"Anomaly detection completed: {len(anomalies)} anomalies found")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    async def _detect_anomaly_type(self, anomaly_type: AnomalyType, data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect anomalies for a specific type"""
        anomalies = []
        thresholds = self.detection_thresholds[anomaly_type]
        
        # Get current value
        current_value = self._extract_value(data, anomaly_type)
        if current_value is None:
            return anomalies
        
        # Get baseline data
        location_key = f"{data.get('location', {}).get('lat', 0)}_{data.get('location', {}).get('lng', 0)}"
        baseline_key = f"{location_key}_{anomaly_type.value}"
        
        if baseline_key not in self.baseline_data:
            # Initialize baseline
            self.baseline_data[baseline_key] = {
                "mean": current_value,
                "std": current_value * 0.1,  # Initial estimate
                "count": 1,
                "last_updated": datetime.now()
            }
            return anomalies
        
        baseline = self.baseline_data[baseline_key]
        
        # Calculate statistical measures
        z_score = abs(current_value - baseline["mean"]) / max(baseline["std"], 0.001)
        deviation_percentage = abs(current_value - baseline["mean"]) / max(baseline["mean"], 0.001) * 100
        
        # Check if anomaly is detected
        is_anomaly = (
            z_score >= thresholds["z_score_threshold"] or
            deviation_percentage >= thresholds["deviation_threshold"]
        )
        
        if is_anomaly:
            confidence = min(z_score / thresholds["z_score_threshold"], 1.0)
            
            if confidence >= thresholds["confidence_threshold"]:
                severity = self._determine_severity(z_score, deviation_percentage)
                
                anomaly = AnomalyDetection(
                    id=f"{anomaly_type.value}_{int(datetime.now().timestamp())}",
                    anomaly_type=anomaly_type,
                    severity=severity,
                    location=data.get("location", {"lat": 0, "lng": 0}),
                    confidence=confidence,
                    detected_at=datetime.now(),
                    description=self._generate_anomaly_description(anomaly_type, current_value, baseline["mean"], deviation_percentage),
                    baseline_value=baseline["mean"],
                    current_value=current_value,
                    deviation_percentage=deviation_percentage,
                    data_sources=self._get_data_sources(anomaly_type),
                    recommended_investigation=self._get_investigation_recommendations(anomaly_type, severity)
                )
                anomalies.append(anomaly)
        
        # Update baseline with new data
        await self._update_baseline_statistics(baseline_key, current_value)
        
        return anomalies
    
    def _extract_value(self, data: Dict[str, Any], anomaly_type: AnomalyType) -> Optional[float]:
        """Extract relevant value from data based on anomaly type"""
        value_mapping = {
            AnomalyType.TEMPERATURE: data.get("temperature"),
            AnomalyType.PRECIPITATION: data.get("precipitation"),
            AnomalyType.VEGETATION: data.get("vegetation_index"),
            AnomalyType.WATER_LEVEL: data.get("water_level"),
            AnomalyType.AIR_QUALITY: data.get("air_quality_index"),
            AnomalyType.SEISMIC: data.get("seismic_activity"),
            AnomalyType.ATMOSPHERIC: data.get("atmospheric_pressure")
        }
        
        return value_mapping.get(anomaly_type)
    
    def _determine_severity(self, z_score: float, deviation_percentage: float) -> AnomalySeverity:
        """Determine anomaly severity"""
        if z_score >= 4.0 or deviation_percentage >= 100:
            return AnomalySeverity.CRITICAL
        elif z_score >= 3.0 or deviation_percentage >= 50:
            return AnomalySeverity.MAJOR
        elif z_score >= 2.5 or deviation_percentage >= 25:
            return AnomalySeverity.MODERATE
        else:
            return AnomalySeverity.MINOR
    
    def _generate_anomaly_description(self, anomaly_type: AnomalyType, current_value: float, 
                                    baseline_value: float, deviation_percentage: float) -> str:
        """Generate human-readable anomaly description"""
        direction = "above" if current_value > baseline_value else "below"
        
        descriptions = {
            AnomalyType.TEMPERATURE: f"Temperature {direction} normal: {current_value:.1f}°C vs {baseline_value:.1f}°C ({deviation_percentage:.1f}% deviation)",
            AnomalyType.PRECIPITATION: f"Precipitation {direction} normal: {current_value:.1f}mm vs {baseline_value:.1f}mm ({deviation_percentage:.1f}% deviation)",
            AnomalyType.VEGETATION: f"Vegetation index {direction} normal: {current_value:.3f} vs {baseline_value:.3f} ({deviation_percentage:.1f}% deviation)",
            AnomalyType.WATER_LEVEL: f"Water level {direction} normal: {current_value:.1f}m vs {baseline_value:.1f}m ({deviation_percentage:.1f}% deviation)",
            AnomalyType.AIR_QUALITY: f"Air quality {direction} normal: {current_value:.1f} vs {baseline_value:.1f} ({deviation_percentage:.1f}% deviation)",
            AnomalyType.SEISMIC: f"Seismic activity {direction} normal: {current_value:.3f} vs {baseline_value:.3f} ({deviation_percentage:.1f}% deviation)",
            AnomalyType.ATMOSPHERIC: f"Atmospheric pressure {direction} normal: {current_value:.1f}hPa vs {baseline_value:.1f}hPa ({deviation_percentage:.1f}% deviation)"
        }
        
        return descriptions.get(anomaly_type, f"Anomaly detected: {deviation_percentage:.1f}% deviation")
    
    def _get_data_sources(self, anomaly_type: AnomalyType) -> List[str]:
        """Get relevant data sources for anomaly type"""
        source_mapping = {
            AnomalyType.TEMPERATURE: ["NOAA", "NASA", "ESA Copernicus"],
            AnomalyType.PRECIPITATION: ["NOAA", "NASA", "USGS"],
            AnomalyType.VEGETATION: ["NASA", "ESA Copernicus", "Sentinel Hub"],
            AnomalyType.WATER_LEVEL: ["USGS", "NOAA", "ESA Copernicus"],
            AnomalyType.AIR_QUALITY: ["NOAA", "ESA Copernicus", "NASA"],
            AnomalyType.SEISMIC: ["USGS", "NASA EONET"],
            AnomalyType.ATMOSPHERIC: ["NOAA", "NASA", "ESA Copernicus"]
        }
        
        return source_mapping.get(anomaly_type, ["Multiple sources"])
    
    def _get_investigation_recommendations(self, anomaly_type: AnomalyType, severity: AnomalySeverity) -> List[str]:
        """Get investigation recommendations based on anomaly type and severity"""
        recommendations = {
            AnomalyType.TEMPERATURE: {
                AnomalySeverity.MINOR: ["Monitor temperature trends", "Check sensor calibration"],
                AnomalySeverity.MODERATE: ["Investigate heat sources", "Check climate patterns"],
                AnomalySeverity.MAJOR: ["Deploy additional sensors", "Analyze regional patterns"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Multi-agency coordination"]
            },
            AnomalyType.PRECIPITATION: {
                AnomalySeverity.MINOR: ["Monitor precipitation patterns", "Check drainage systems"],
                AnomalySeverity.MODERATE: ["Analyze weather systems", "Check flood risk"],
                AnomalySeverity.MAJOR: ["Deploy flood monitoring", "Activate emergency protocols"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Evacuation planning"]
            },
            AnomalyType.VEGETATION: {
                AnomalySeverity.MINOR: ["Monitor vegetation health", "Check seasonal patterns"],
                AnomalySeverity.MODERATE: ["Analyze land use changes", "Check environmental factors"],
                AnomalySeverity.MAJOR: ["Deploy ground surveys", "Investigate causes"],
                AnomalySeverity.CRITICAL: ["Emergency assessment", "Conservation measures"]
            },
            AnomalyType.WATER_LEVEL: {
                AnomalySeverity.MINOR: ["Monitor water levels", "Check dam operations"],
                AnomalySeverity.MODERATE: ["Analyze water sources", "Check infrastructure"],
                AnomalySeverity.MAJOR: ["Deploy additional monitoring", "Activate flood protocols"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Evacuation planning"]
            },
            AnomalyType.AIR_QUALITY: {
                AnomalySeverity.MINOR: ["Monitor air quality", "Check pollution sources"],
                AnomalySeverity.MODERATE: ["Analyze pollution patterns", "Check industrial activity"],
                AnomalySeverity.MAJOR: ["Deploy air quality stations", "Investigate sources"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Public health alerts"]
            },
            AnomalyType.SEISMIC: {
                AnomalySeverity.MINOR: ["Monitor seismic activity", "Check sensor networks"],
                AnomalySeverity.MODERATE: ["Analyze seismic patterns", "Check geological factors"],
                AnomalySeverity.MAJOR: ["Deploy additional sensors", "Activate monitoring"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Evacuation planning"]
            },
            AnomalyType.ATMOSPHERIC: {
                AnomalySeverity.MINOR: ["Monitor atmospheric pressure", "Check weather patterns"],
                AnomalySeverity.MODERATE: ["Analyze pressure systems", "Check storm development"],
                AnomalySeverity.MAJOR: ["Deploy weather stations", "Activate storm monitoring"],
                AnomalySeverity.CRITICAL: ["Emergency response", "Storm preparation"]
            }
        }
        
        return recommendations.get(anomaly_type, {}).get(severity, ["Investigate anomaly"])
    
    async def _update_baseline_data(self, data: Dict[str, Any]):
        """Update baseline data with new measurements"""
        location_key = f"{data.get('location', {}).get('lat', 0)}_{data.get('location', {}).get('lng', 0)}"
        
        for anomaly_type in AnomalyType:
            value = self._extract_value(data, anomaly_type)
            if value is not None:
                baseline_key = f"{location_key}_{anomaly_type.value}"
                await self._update_baseline_statistics(baseline_key, value)
    
    async def _update_baseline_statistics(self, baseline_key: str, new_value: float):
        """Update baseline statistics using exponential moving average"""
        if baseline_key not in self.baseline_data:
            self.baseline_data[baseline_key] = {
                "mean": new_value,
                "std": new_value * 0.1,
                "count": 1,
                "last_updated": datetime.now()
            }
            return
        
        baseline = self.baseline_data[baseline_key]
        
        # Exponential moving average for mean
        alpha = 0.1  # Smoothing factor
        baseline["mean"] = alpha * new_value + (1 - alpha) * baseline["mean"]
        
        # Update standard deviation using variance
        variance = alpha * (new_value - baseline["mean"]) ** 2 + (1 - alpha) * baseline["std"] ** 2
        baseline["std"] = np.sqrt(variance)
        
        baseline["count"] += 1
        baseline["last_updated"] = datetime.now()
    
    async def _cleanup_history(self):
        """Clean up old anomaly history"""
        cutoff_time = datetime.now() - timedelta(days=30)
        self.anomaly_history = [
            anomaly for anomaly in self.anomaly_history
            if anomaly.detected_at > cutoff_time
        ]
    
    async def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        total_anomalies = len(self.anomaly_history)
        
        if total_anomalies == 0:
            return {
                "total_anomalies": 0,
                "anomalies_by_type": {},
                "anomalies_by_severity": {},
                "detection_rate": 0.0
            }
        
        # Count by type
        anomalies_by_type = {}
        for anomaly_type in AnomalyType:
            count = len([a for a in self.anomaly_history if a.anomaly_type == anomaly_type])
            anomalies_by_type[anomaly_type.value] = count
        
        # Count by severity
        anomalies_by_severity = {}
        for severity in AnomalySeverity:
            count = len([a for a in self.anomaly_history if a.severity == severity])
            anomalies_by_severity[severity.value] = count
        
        # Calculate detection rate (anomalies per day)
        if self.anomaly_history:
            time_span = (max(a.detected_at for a in self.anomaly_history) - 
                        min(a.detected_at for a in self.anomaly_history)).days
            detection_rate = total_anomalies / max(time_span, 1)
        else:
            detection_rate = 0.0
        
        return {
            "total_anomalies": total_anomalies,
            "anomalies_by_type": anomalies_by_type,
            "anomalies_by_severity": anomalies_by_severity,
            "detection_rate": detection_rate,
            "baseline_locations": len(self.baseline_data)
        }
    
    async def get_recent_anomalies(self, hours: int = 24) -> List[AnomalyDetection]:
        """Get anomalies detected in the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            anomaly for anomaly in self.anomaly_history
            if anomaly.detected_at > cutoff_time
        ]
    
    async def get_anomalies_by_location(self, lat: float, lng: float, radius: float = 10.0) -> List[AnomalyDetection]:
        """Get anomalies within a radius of a location"""
        def distance(lat1, lng1, lat2, lng2):
            # Simple distance calculation (not accurate for large distances)
            return ((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) ** 0.5
        
        return [
            anomaly for anomaly in self.anomaly_history
            if distance(
                anomaly.location["lat"], anomaly.location["lng"],
                lat, lng
            ) <= radius
        ]
