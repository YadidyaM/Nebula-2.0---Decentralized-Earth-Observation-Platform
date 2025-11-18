# Constellation manager for coordinating multiple satellites, calculating coverage patterns, and optimizing positioning
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import math
import asyncio

from app.services.satellite_physics import satellite_physics_engine, SatellitePosition
from app.services.orbital_mechanics import orbital_mechanics

logger = logging.getLogger(__name__)

class ConstellationManager:
    """Manages satellite constellations, calculates coverage patterns, and optimizes satellite positioning"""
    
    def __init__(self):
        self.constellations: Dict[str, List[str]] = {}  # constellation_id -> [satellite_ids]
        self.coverage_maps: Dict[str, Dict[str, Any]] = {}
        self.optimization_cache: Dict[str, Any] = {}
    
    async def create_constellation(self, constellation_id: str, satellite_ids: List[str], 
                                   constellation_type: str = "walker") -> Dict[str, Any]:
        """Create a new satellite constellation"""
        try:
            self.constellations[constellation_id] = {
                "satellite_ids": satellite_ids,
                "type": constellation_type,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            logger.info(f"Created constellation {constellation_id} with {len(satellite_ids)} satellites")
            
            return {
                "constellation_id": constellation_id,
                "satellite_count": len(satellite_ids),
                "type": constellation_type,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error creating constellation: {e}")
            return {"error": str(e)}
    
    async def calculate_coverage_pattern(self, constellation_id: str, 
                                        target_lat: float, target_lng: float,
                                        time_horizon_hours: float = 24.0) -> Dict[str, Any]:
        """Calculate coverage pattern for a location from constellation"""
        try:
            if constellation_id not in self.constellations:
                return {"error": "Constellation not found"}
            
            satellite_ids = self.constellations[constellation_id]["satellite_ids"]
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=time_horizon_hours)
            
            coverage_data = {
                "constellation_id": constellation_id,
                "target_location": {"lat": target_lat, "lng": target_lng},
                "time_horizon_hours": time_horizon_hours,
                "coverage_periods": [],
                "total_coverage_time": 0.0,
                "coverage_percentage": 0.0
            }
            
            # Calculate passes for each satellite
            all_passes = []
            for sat_id in satellite_ids:
                passes = await satellite_physics_engine.predict_orbital_passes(
                    target_lat, target_lng, 0.0, [sat_id], 
                    days_ahead=time_horizon_hours/24, min_elevation=10.0
                )
                all_passes.extend(passes)
            
            # Sort passes by start time
            all_passes.sort(key=lambda p: p.start_time)
            
            # Merge overlapping passes
            if all_passes:
                merged_periods = self._merge_coverage_periods(all_passes)
                coverage_data["coverage_periods"] = [
                    {
                        "start": p["start"].isoformat(),
                        "end": p["end"].isoformat(),
                        "duration_minutes": p["duration"]
                    }
                    for p in merged_periods
                ]
                
                total_coverage = sum(p["duration"] for p in merged_periods)
                coverage_data["total_coverage_time"] = total_coverage
                coverage_data["coverage_percentage"] = (total_coverage / (time_horizon_hours * 60)) * 100
            
            self.coverage_maps[constellation_id] = coverage_data
            return coverage_data
            
        except Exception as e:
            logger.error(f"Error calculating coverage pattern: {e}")
            return {"error": str(e)}
    
    def _merge_coverage_periods(self, passes: List[Any]) -> List[Dict[str, Any]]:
        """Merge overlapping coverage periods"""
        if not passes:
            return []
        
        merged = []
        current_start = passes[0].start_time
        current_end = passes[0].end_time
        
        for pass_obj in passes[1:]:
            if pass_obj.start_time <= current_end:
                # Overlapping - extend current period
                current_end = max(current_end, pass_obj.end_time)
            else:
                # Non-overlapping - save current and start new
                merged.append({
                    "start": current_start,
                    "end": current_end,
                    "duration": (current_end - current_start).total_seconds() / 60.0
                })
                current_start = pass_obj.start_time
                current_end = pass_obj.end_time
        
        # Add last period
        merged.append({
            "start": current_start,
            "end": current_end,
            "duration": (current_end - current_start).total_seconds() / 60.0
        })
        
        return merged
    
    async def optimize_satellite_positioning(self, constellation_id: str, 
                                            target_areas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize satellite positioning for maximum coverage of target areas"""
        try:
            if constellation_id not in self.constellations:
                return {"error": "Constellation not found"}
            
            satellite_ids = self.constellations[constellation_id]["satellite_ids"]
            
            # Calculate coverage for each target area
            coverage_results = []
            for area in target_areas:
                coverage = await self.calculate_coverage_pattern(
                    constellation_id,
                    area["lat"],
                    area["lng"],
                    area.get("time_horizon", 24.0)
                )
                coverage_results.append({
                    "area": area,
                    "coverage": coverage.get("coverage_percentage", 0.0)
                })
            
            # Calculate optimization metrics
            avg_coverage = sum(r["coverage"] for r in coverage_results) / len(coverage_results) if coverage_results else 0.0
            min_coverage = min(r["coverage"] for r in coverage_results) if coverage_results else 0.0
            max_coverage = max(r["coverage"] for r in coverage_results) if coverage_results else 0.0
            
            optimization_result = {
                "constellation_id": constellation_id,
                "target_areas": len(target_areas),
                "average_coverage": avg_coverage,
                "minimum_coverage": min_coverage,
                "maximum_coverage": max_coverage,
                "coverage_results": coverage_results,
                "optimization_score": avg_coverage * 0.7 + min_coverage * 0.3,  # Weighted score
                "recommendations": []
            }
            
            # Generate recommendations
            if min_coverage < 50:
                optimization_result["recommendations"].append("add_more_satellites")
            if avg_coverage < 70:
                optimization_result["recommendations"].append("adjust_orbital_parameters")
            
            self.optimization_cache[constellation_id] = optimization_result
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing satellite positioning: {e}")
            return {"error": str(e)}
    
    async def coordinate_multi_satellite_mission(self, mission_id: str, 
                                                 satellite_ids: List[str],
                                                 target_areas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate a mission across multiple satellites in constellation"""
        try:
            coordination_plan = {
                "mission_id": mission_id,
                "satellite_ids": satellite_ids,
                "target_areas": target_areas,
                "assignment": {},
                "timeline": [],
                "coverage_analysis": {}
            }
            
            # Assign satellites to target areas
            for i, area in enumerate(target_areas):
                sat_id = satellite_ids[i % len(satellite_ids)]  # Round-robin assignment
                coordination_plan["assignment"][area["id"]] = sat_id
                
                # Calculate when satellite will be over target
                passes = await satellite_physics_engine.predict_orbital_passes(
                    area["lat"], area["lng"], 0.0, [sat_id],
                    days_ahead=1, min_elevation=30.0
                )
                
                if passes:
                    next_pass = passes[0]
                    coordination_plan["timeline"].append({
                        "satellite_id": sat_id,
                        "area_id": area["id"],
                        "pass_start": next_pass.start_time.isoformat(),
                        "pass_end": next_pass.end_time.isoformat(),
                        "max_elevation": next_pass.max_elevation
                    })
            
            # Calculate overall coverage
            for area in target_areas:
                coverage = await self.calculate_coverage_pattern(
                    "mission_" + mission_id,
                    area["lat"],
                    area["lng"],
                    24.0
                )
                coordination_plan["coverage_analysis"][area["id"]] = coverage
            
            return coordination_plan
            
        except Exception as e:
            logger.error(f"Error coordinating multi-satellite mission: {e}")
            return {"error": str(e)}
    
    async def get_constellation_status(self, constellation_id: str) -> Dict[str, Any]:
        """Get status of a constellation"""
        try:
            if constellation_id not in self.constellations:
                return {"error": "Constellation not found"}
            
            constellation = self.constellations[constellation_id]
            satellite_ids = constellation["satellite_ids"]
            
            # Get status of each satellite
            satellite_statuses = []
            for sat_id in satellite_ids:
                status = await satellite_physics_engine.get_satellite_status()
                if sat_id in status.get("satellites", {}):
                    satellite_statuses.append({
                        "satellite_id": sat_id,
                        "status": status["satellites"][sat_id]
                    })
            
            return {
                "constellation_id": constellation_id,
                "type": constellation["type"],
                "satellite_count": len(satellite_ids),
                "satellite_statuses": satellite_statuses,
                "created_at": constellation["created_at"].isoformat(),
                "status": constellation["status"]
            }
            
        except Exception as e:
            logger.error(f"Error getting constellation status: {e}")
            return {"error": str(e)}

# Global instance
constellation_manager = ConstellationManager()

