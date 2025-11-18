# Specialized agent for security monitoring and border surveillance with Gemini AI integration
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

class SecuritySentinel(BaseAgent):
    """Specialized agent for security monitoring and border surveillance"""
    
    def __init__(self, agent_id: str = "agent_security_sentinel", name: str = "Security Sentinel"):
        super().__init__(agent_id, name, "Security1234567890abcdef")
        self.specialization = ["border_surveillance", "security", "threat_assessment", "infrastructure_monitoring"]
        self.data_sources = {
            "satellite_imagery": "https://api.satellite-imagery.com",
            "radar_data": "https://api.radar-monitoring.com",
            "ais_tracking": "https://api.ais-tracking.com",
            "ground_sensors": "https://api.ground-sensors.com"
        }
        self.monitoring_zones = [
            {"name": "Border Zone Alpha", "lat": 35.0, "lng": 139.0, "radius": 50, "priority": "high"},
            {"name": "Critical Infrastructure", "lat": 40.0, "lng": -74.0, "radius": 25, "priority": "critical"},
            {"name": "Maritime Approaches", "lat": 30.0, "lng": -80.0, "radius": 100, "priority": "medium"},
            {"name": "Airspace Corridor", "lat": 25.0, "lng": -80.0, "radius": 75, "priority": "high"}
        ]
        self.threat_types = ["unauthorized_entry", "suspicious_activity", "infrastructure_tampering", "cyber_intrusion"]
        self.active_threats: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the Security Sentinel agent"""
        await self.update_status(AgentStatus.ONLINE)
        await self.update_position(Position(lat=35.0, lng=139.0, alt=500000))
        logger.info("Security Sentinel initialized")
        
        # Start background monitoring
        asyncio.create_task(self._continuous_security_monitoring())
        asyncio.create_task(self._threat_assessment_analysis())
    
    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        """Execute security monitoring mission"""
        try:
            await self.start_mission(mission)
            
            # Determine mission type and execute accordingly
            if mission.type == MissionType.SECURITY:
                results = await self._conduct_security_surveillance(mission)
            elif mission.type == MissionType.DISASTER_MANAGEMENT:
                results = await self._assess_security_threats(mission)
            else:
                results = await self._general_security_analysis(mission)
            
            await self.complete_mission(results)
            return results
            
        except Exception as e:
            logger.error(f"Error executing mission {mission.id}: {e}")
            await self.update_status(AgentStatus.ERROR)
            return {"error": str(e), "mission_id": mission.id}
    
    async def process_environmental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process security data and detect threats"""
        try:
            analysis = {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "security",
                "threats_detected": [],
                "risk_assessment": "low",
                "security_status": "normal",
                "recommendations": []
            }
            
            # Analyze movement patterns
            if "movement_data" in data:
                movement = data["movement_data"]
                suspicious_patterns = await self._analyze_movement_patterns(movement)
                
                for pattern in suspicious_patterns:
                    analysis["threats_detected"].append({
                        "type": "suspicious_movement",
                        "severity": pattern["severity"],
                        "pattern": pattern["type"],
                        "location": pattern["location"],
                        "confidence": pattern["confidence"]
                    })
                    
                    if pattern["severity"] == "high":
                        analysis["risk_assessment"] = "high"
                        analysis["recommendations"].append("deploy_security_team")
            
            # Analyze infrastructure status
            if "infrastructure_status" in data:
                infra_status = data["infrastructure_status"]
                anomalies = await self._analyze_infrastructure_anomalies(infra_status)
                
                for anomaly in anomalies:
                    analysis["threats_detected"].append({
                        "type": "infrastructure_anomaly",
                        "severity": anomaly["severity"],
                        "facility": anomaly["facility"],
                        "anomaly_type": anomaly["type"],
                        "location": anomaly["location"]
                    })
                    
                    if anomaly["severity"] == "critical":
                        analysis["risk_assessment"] = "critical"
                        analysis["security_status"] = "compromised"
                        analysis["recommendations"].append("immediate_response_required")
            
            # Analyze communication patterns
            if "communication_data" in data:
                comm_data = data["communication_data"]
                suspicious_comm = await self._analyze_communication_patterns(comm_data)
                
                for comm in suspicious_comm:
                    analysis["threats_detected"].append({
                        "type": "suspicious_communication",
                        "severity": comm["severity"],
                        "pattern": comm["pattern"],
                        "frequency": comm["frequency"],
                        "encryption_level": comm["encryption"]
                    })
                    
                    if comm["severity"] == "high":
                        analysis["risk_assessment"] = "high"
                        analysis["recommendations"].append("intercept_communications")
            
            # Analyze cyber activity
            if "cyber_activity" in data:
                cyber_data = data["cyber_activity"]
                cyber_threats = await self._analyze_cyber_threats(cyber_data)
                
                for threat in cyber_threats:
                    analysis["threats_detected"].append({
                        "type": "cyber_threat",
                        "severity": threat["severity"],
                        "attack_type": threat["type"],
                        "target": threat["target"],
                        "source": threat["source"]
                    })
                    
                    if threat["severity"] == "critical":
                        analysis["risk_assessment"] = "critical"
                        analysis["security_status"] = "breached"
                        analysis["recommendations"].append("activate_cyber_defense")
            
            # Use Gemini for enhanced threat detection
            if gemini_service.is_available():
                try:
                    gemini_reasoning = await gemini_service.reason_about_mission(
                        {"type": "security", "data": data, "current_analysis": analysis},
                        self.specialization
                    )
                    if gemini_reasoning and "recommendations" in gemini_reasoning:
                        analysis["recommendations"].extend(gemini_reasoning["recommendations"])
                except Exception as e:
                    logger.error(f"Error in Gemini reasoning for Security Sentinel: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing security data: {e}")
            return {"error": str(e), "agent_id": self.agent_id}
    
    async def _conduct_security_surveillance(self, mission: Mission) -> Dict[str, Any]:
        """Conduct security surveillance for a specific mission"""
        try:
            # Collect security data for the target area
            security_data = await self._collect_security_data(mission.target_area)
            
            surveillance_report = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "surveillance_area": mission.target_area,
                "threat_assessment": security_data.get("threat_level", "low"),
                "detected_activities": security_data.get("activities", []),
                "infrastructure_status": security_data.get("infrastructure", {}),
                "movement_patterns": security_data.get("movement", {}),
                "recommendations": [],
                "confidence_score": 0.93
            }
            
            # Generate recommendations based on findings
            if security_data.get("threat_level") == "high":
                surveillance_report["recommendations"].append("increase_patrol_frequency")
                surveillance_report["recommendations"].append("deploy_additional_sensors")
            
            return surveillance_report
            
        except Exception as e:
            logger.error(f"Error conducting security surveillance: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _assess_security_threats(self, mission: Mission) -> Dict[str, Any]:
        """Assess security threats for disaster management"""
        try:
            # Collect threat assessment data
            threat_data = await self._collect_threat_assessment_data(mission.target_area)
            
            threat_assessment = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "threat_level": threat_data.get("overall_threat", "low"),
                "identified_threats": threat_data.get("threats", []),
                "vulnerability_assessment": threat_data.get("vulnerabilities", {}),
                "response_capabilities": threat_data.get("response_capabilities", {}),
                "evacuation_routes": threat_data.get("evacuation_routes", []),
                "emergency_contacts": threat_data.get("emergency_contacts", []),
                "confidence_score": 0.89,
                "recommendations": []
            }
            
            # Generate response recommendations
            if threat_data.get("overall_threat") == "critical":
                threat_assessment["recommendations"].append("activate_emergency_protocols")
                threat_assessment["recommendations"].append("evacuate_high_risk_areas")
            elif threat_data.get("overall_threat") == "high":
                threat_assessment["recommendations"].append("increase_security_presence")
                threat_assessment["recommendations"].append("prepare_evacuation_plans")
            
            return threat_assessment
            
        except Exception as e:
            logger.error(f"Error assessing security threats: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _general_security_analysis(self, mission: Mission) -> Dict[str, Any]:
        """Perform general security analysis"""
        try:
            # Collect general security data
            security_data = await self._collect_general_security_data(mission.target_area)
            
            analysis = {
                "mission_id": mission.id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "security_perimeter": security_data.get("perimeter", {}),
                "access_points": security_data.get("access_points", []),
                "surveillance_coverage": security_data.get("coverage", {}),
                "response_times": security_data.get("response_times", {}),
                "security_protocols": security_data.get("protocols", {}),
                "personnel_status": security_data.get("personnel", {}),
                "confidence_score": 0.87,
                "recommendations": []
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in general security analysis: {e}")
            return {"error": str(e), "mission_id": mission.id}
    
    async def _collect_security_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect security data from various sources"""
        try:
            security_data = {
                "threat_level": "low",
                "activities": [
                    {
                        "type": "normal_traffic",
                        "count": 15,
                        "location": "main_gate",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "infrastructure": {
                    "perimeter_fence": "intact",
                    "security_cameras": "operational",
                    "access_control": "functioning",
                    "alarm_systems": "active"
                },
                "movement": {
                    "authorized_personnel": 8,
                    "vehicles": 3,
                    "suspicious_activity": 0,
                    "unauthorized_access": 0
                },
                "communication": {
                    "radio_traffic": "normal",
                    "encrypted_channels": 2,
                    "suspicious_transmissions": 0
                }
            }
            
            return security_data
            
        except Exception as e:
            logger.error(f"Error collecting security data: {e}")
            return {}
    
    async def _collect_threat_assessment_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data for threat assessment"""
        try:
            threat_data = {
                "overall_threat": "low",
                "threats": [
                    {
                        "type": "potential_intrusion",
                        "severity": "low",
                        "probability": 0.2,
                        "location": "perimeter_north",
                        "mitigation": "increased_patrols"
                    }
                ],
                "vulnerabilities": {
                    "perimeter_security": "adequate",
                    "access_control": "good",
                    "surveillance_coverage": "comprehensive",
                    "response_capability": "excellent"
                },
                "response_capabilities": {
                    "response_time": 5,  # minutes
                    "personnel_available": 12,
                    "equipment_status": "operational",
                    "backup_systems": "ready"
                },
                "evacuation_routes": [
                    {"route": "primary", "capacity": 500, "status": "clear"},
                    {"route": "secondary", "capacity": 300, "status": "clear"}
                ],
                "emergency_contacts": [
                    {"type": "police", "number": "911", "response_time": 10},
                    {"type": "security_team", "number": "internal", "response_time": 2}
                ]
            }
            
            return threat_data
            
        except Exception as e:
            logger.error(f"Error collecting threat assessment data: {e}")
            return {}
    
    async def _collect_general_security_data(self, target_area: Dict[str, Any]) -> Dict[str, Any]:
        """Collect general security data"""
        try:
            security_data = {
                "perimeter": {
                    "total_length": 5000,  # meters
                    "fence_height": 3.0,  # meters
                    "breach_points": 0,
                    "maintenance_status": "good"
                },
                "access_points": [
                    {"type": "main_gate", "status": "operational", "traffic": "normal"},
                    {"type": "emergency_exit", "status": "secured", "traffic": "none"},
                    {"type": "service_entrance", "status": "operational", "traffic": "low"}
                ],
                "coverage": {
                    "camera_coverage": 95,  # percentage
                    "motion_sensors": 100,  # percentage
                    "perimeter_alarms": 100,  # percentage
                    "blind_spots": 2
                },
                "response_times": {
                    "average_response": 3.5,  # minutes
                    "emergency_response": 1.2,  # minutes
                    "backup_response": 8.0  # minutes
                },
                "protocols": {
                    "access_control": "active",
                    "visitor_management": "strict",
                    "emergency_procedures": "updated",
                    "communication_protocols": "secure"
                },
                "personnel": {
                    "on_duty": 8,
                    "available": 12,
                    "training_status": "current",
                    "alert_level": "normal"
                }
            }
            
            return security_data
            
        except Exception as e:
            logger.error(f"Error collecting general security data: {e}")
            return {}
    
    async def _analyze_movement_patterns(self, movement_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze movement patterns for suspicious activity"""
        try:
            suspicious_patterns = []
            
            # Check for unusual movement patterns
            if movement_data.get("speed", 0) > 50:  # km/h in restricted area
                suspicious_patterns.append({
                    "type": "high_speed_movement",
                    "severity": "medium",
                    "location": movement_data.get("location", "unknown"),
                    "confidence": 0.8
                })
            
            # Check for unauthorized access attempts
            if movement_data.get("unauthorized_access_attempts", 0) > 0:
                suspicious_patterns.append({
                    "type": "unauthorized_access",
                    "severity": "high",
                    "location": movement_data.get("location", "unknown"),
                    "confidence": 0.95
                })
            
            # Check for loitering behavior
            if movement_data.get("dwell_time", 0) > 1800:  # 30 minutes
                suspicious_patterns.append({
                    "type": "suspicious_loitering",
                    "severity": "medium",
                    "location": movement_data.get("location", "unknown"),
                    "confidence": 0.7
                })
            
            return suspicious_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing movement patterns: {e}")
            return []
    
    async def _analyze_infrastructure_anomalies(self, infra_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze infrastructure for anomalies"""
        try:
            anomalies = []
            
            # Check for tampering
            if infra_status.get("tampering_detected", False):
                anomalies.append({
                    "type": "infrastructure_tampering",
                    "severity": "critical",
                    "facility": infra_status.get("facility", "unknown"),
                    "location": infra_status.get("location", "unknown")
                })
            
            # Check for system failures
            if infra_status.get("system_failures", 0) > 0:
                anomalies.append({
                    "type": "system_failure",
                    "severity": "high",
                    "facility": infra_status.get("facility", "unknown"),
                    "location": infra_status.get("location", "unknown")
                })
            
            # Check for unauthorized modifications
            if infra_status.get("unauthorized_modifications", False):
                anomalies.append({
                    "type": "unauthorized_modification",
                    "severity": "high",
                    "facility": infra_status.get("facility", "unknown"),
                    "location": infra_status.get("location", "unknown")
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error analyzing infrastructure anomalies: {e}")
            return []
    
    async def _analyze_communication_patterns(self, comm_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze communication patterns for suspicious activity"""
        try:
            suspicious_comm = []
            
            # Check for encrypted communications
            if comm_data.get("encrypted_channels", 0) > comm_data.get("normal_channels", 0) * 2:
                suspicious_comm.append({
                    "type": "excessive_encryption",
                    "severity": "medium",
                    "pattern": "high_encryption_usage",
                    "frequency": comm_data.get("encrypted_channels", 0),
                    "encryption": "high"
                })
            
            # Check for unusual transmission patterns
            if comm_data.get("transmission_frequency", 0) > 100:  # transmissions per hour
                suspicious_comm.append({
                    "type": "high_frequency_transmissions",
                    "severity": "medium",
                    "pattern": "excessive_communication",
                    "frequency": comm_data.get("transmission_frequency", 0),
                    "encryption": "unknown"
                })
            
            return suspicious_comm
            
        except Exception as e:
            logger.error(f"Error analyzing communication patterns: {e}")
            return []
    
    async def _analyze_cyber_threats(self, cyber_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze cyber threats"""
        try:
            cyber_threats = []
            
            # Check for intrusion attempts
            if cyber_data.get("intrusion_attempts", 0) > 0:
                cyber_threats.append({
                    "type": "intrusion_attempt",
                    "severity": "high",
                    "attack_type": "unauthorized_access",
                    "target": cyber_data.get("target_system", "unknown"),
                    "source": cyber_data.get("source_ip", "unknown")
                })
            
            # Check for malware detection
            if cyber_data.get("malware_detected", False):
                cyber_threats.append({
                    "type": "malware_infection",
                    "severity": "critical",
                    "attack_type": "malware",
                    "target": cyber_data.get("infected_system", "unknown"),
                    "source": cyber_data.get("infection_source", "unknown")
                })
            
            # Check for data exfiltration
            if cyber_data.get("data_exfiltration", False):
                cyber_threats.append({
                    "type": "data_breach",
                    "severity": "critical",
                    "attack_type": "data_theft",
                    "target": cyber_data.get("compromised_system", "unknown"),
                    "source": cyber_data.get("attacker_ip", "unknown")
                })
            
            return cyber_threats
            
        except Exception as e:
            logger.error(f"Error analyzing cyber threats: {e}")
            return []
    
    async def _continuous_security_monitoring(self):
        """Background task for continuous security monitoring"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Monitor each security zone periodically
                for zone in self.monitoring_zones:
                    if self.status == AgentStatus.ONLINE:
                        # Collect security data for this zone
                        security_data = await self._collect_security_data(zone)
                        
                        # Process the data
                        analysis = await self.process_environmental_data(security_data)
                        
                        # Log significant findings
                        if analysis.get("risk_assessment") in ["medium", "high", "critical"]:
                            logger.warning(f"Security Sentinel detected {analysis['risk_assessment']} risk in {zone['name']}")
                
                # Wait 15 minutes before next monitoring cycle
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Error in continuous security monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _threat_assessment_analysis(self):
        """Background task for threat assessment analysis"""
        while self.status != AgentStatus.OFFLINE:
            try:
                # Analyze threats in each monitoring zone
                for zone in self.monitoring_zones:
                    if self.status == AgentStatus.ONLINE:
                        # Collect threat assessment data
                        threat_data = await self._collect_threat_assessment_data(zone)
                        
                        # Check for critical threats
                        if threat_data.get("overall_threat") == "critical":
                            logger.critical(f"Security Sentinel detected critical threat in {zone['name']}")
                        elif threat_data.get("overall_threat") == "high":
                            logger.warning(f"Security Sentinel detected high threat in {zone['name']}")
                
                # Wait 1 hour before next analysis cycle
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in threat assessment analysis: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def get_specialized_status(self) -> Dict[str, Any]:
        """Get specialized status information for Security Sentinel"""
        base_status = await self.get_health_status()
        
        specialized_status = {
            **base_status,
            "specialization": self.specialization,
            "monitoring_zones": len(self.monitoring_zones),
            "active_threats": len(self.active_threats),
            "threat_types_monitored": len(self.threat_types),
            "data_sources": list(self.data_sources.keys()),
            "last_monitoring_cycle": datetime.now().isoformat()
        }
        
        return specialized_status
