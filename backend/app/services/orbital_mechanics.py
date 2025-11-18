# Advanced orbital mechanics module providing orbital element conversions, Hohmann transfers, maneuvers, and collision avoidance
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
import math
import numpy as np

try:
    from poliastro.twobody import Orbit
    from poliastro.bodies import Earth
    from poliastro.maneuver import Maneuver
    from poliastro.constants import GM_earth
    from astropy import units as u
    POLIASTRO_AVAILABLE = True
except ImportError:
    POLIASTRO_AVAILABLE = False
    logging.warning("Poliastro not available. Install with: pip install poliastro")

try:
    from sgp4.api import Satrec, jday
    SGP4_AVAILABLE = True
except ImportError:
    SGP4_AVAILABLE = False

logger = logging.getLogger(__name__)

class OrbitalMechanics:
    """Advanced orbital mechanics calculations including maneuvers, transfers, and collision avoidance"""
    
    def __init__(self):
        self.earth_radius = 6371.0  # km
        self.mu_earth = 398600.4418  # km³/s² (standard gravitational parameter)
    
    def keplerian_to_cartesian(self, orbital_elements: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        """Convert Keplerian orbital elements to Cartesian position and velocity"""
        try:
            a = orbital_elements["semi_major_axis"]  # km
            e = orbital_elements["eccentricity"]
            i = math.radians(orbital_elements["inclination"])  # degrees to radians
            raan = math.radians(orbital_elements["right_ascension"])
            argp = math.radians(orbital_elements["argument_of_perigee"])
            nu = math.radians(orbital_elements["mean_anomaly"])  # Using mean anomaly as approximation
            
            # Calculate position and velocity in perifocal frame
            p = a * (1 - e * e)  # Semi-latus rectum
            r = p / (1 + e * math.cos(nu))  # Distance from focus
            
            # Position in perifocal frame
            r_pf = np.array([
                r * math.cos(nu),
                r * math.sin(nu),
                0.0
            ])
            
            # Velocity in perifocal frame
            v_pf = np.array([
                -math.sqrt(self.mu_earth / p) * math.sin(nu),
                math.sqrt(self.mu_earth / p) * (e + math.cos(nu)),
                0.0
            ])
            
            # Rotation matrices
            R_z_raan = np.array([
                [math.cos(raan), -math.sin(raan), 0],
                [math.sin(raan), math.cos(raan), 0],
                [0, 0, 1]
            ])
            
            R_x_i = np.array([
                [1, 0, 0],
                [0, math.cos(i), -math.sin(i)],
                [0, math.sin(i), math.cos(i)]
            ])
            
            R_z_argp = np.array([
                [math.cos(argp), -math.sin(argp), 0],
                [math.sin(argp), math.cos(argp), 0],
                [0, 0, 1]
            ])
            
            # Transform to ECI frame
            R = R_z_raan @ R_x_i @ R_z_argp
            r_eci = R @ r_pf
            v_eci = R @ v_pf
            
            return r_eci, v_eci
            
        except Exception as e:
            logger.error(f"Error converting Keplerian to Cartesian: {e}")
            return np.array([0, 0, 0]), np.array([0, 0, 0])
    
    def cartesian_to_keplerian(self, position: np.ndarray, velocity: np.ndarray) -> Dict[str, float]:
        """Convert Cartesian position and velocity to Keplerian orbital elements"""
        try:
            r = np.linalg.norm(position)
            v = np.linalg.norm(velocity)
            
            # Specific angular momentum
            h_vec = np.cross(position, velocity)
            h = np.linalg.norm(h_vec)
            
            # Eccentricity vector
            e_vec = (1 / self.mu_earth) * ((v * v - self.mu_earth / r) * position - np.dot(position, velocity) * velocity)
            e = np.linalg.norm(e_vec)
            
            # Semi-major axis
            energy = (v * v) / 2 - self.mu_earth / r
            a = -self.mu_earth / (2 * energy)
            
            # Inclination
            i = math.acos(h_vec[2] / h)
            
            # Right ascension of ascending node
            n_vec = np.cross([0, 0, 1], h_vec)
            n = np.linalg.norm(n_vec)
            if n == 0:
                raan = 0
            else:
                raan = math.acos(n_vec[0] / n)
                if n_vec[1] < 0:
                    raan = 2 * math.pi - raan
            
            # Argument of perigee
            if n == 0:
                argp = 0
            else:
                argp = math.acos(np.dot(n_vec, e_vec) / (n * e))
                if e_vec[2] < 0:
                    argp = 2 * math.pi - argp
            
            # True anomaly
            nu = math.acos(np.dot(e_vec, position) / (e * r))
            if np.dot(position, velocity) < 0:
                nu = 2 * math.pi - nu
            
            return {
                "semi_major_axis": a,
                "eccentricity": e,
                "inclination": math.degrees(i),
                "right_ascension": math.degrees(raan),
                "argument_of_perigee": math.degrees(argp),
                "mean_anomaly": math.degrees(nu)  # Simplified - should calculate mean anomaly
            }
            
        except Exception as e:
            logger.error(f"Error converting Cartesian to Keplerian: {e}")
            return {}
    
    def calculate_hohmann_transfer(self, r1: float, r2: float) -> Dict[str, Any]:
        """Calculate Hohmann transfer orbit parameters and delta-V requirements"""
        try:
            # Semi-major axis of transfer orbit
            a_transfer = (r1 + r2) / 2
            
            # Velocity at perigee of transfer orbit
            v1_transfer = math.sqrt(self.mu_earth * (2 / r1 - 1 / a_transfer))
            
            # Velocity at apogee of transfer orbit
            v2_transfer = math.sqrt(self.mu_earth * (2 / r2 - 1 / a_transfer))
            
            # Circular velocities
            v1_circular = math.sqrt(self.mu_earth / r1)
            v2_circular = math.sqrt(self.mu_earth / r2)
            
            # Delta-V requirements
            dv1 = abs(v1_transfer - v1_circular)  # First burn
            dv2 = abs(v2_circular - v2_transfer)  # Second burn
            dv_total = dv1 + dv2
            
            # Transfer time (half period of transfer orbit)
            period = 2 * math.pi * math.sqrt(a_transfer ** 3 / self.mu_earth)
            transfer_time = period / 2
            
            return {
                "semi_major_axis": a_transfer,
                "eccentricity": (r2 - r1) / (r2 + r1),
                "delta_v1": dv1,
                "delta_v2": dv2,
                "delta_v_total": dv_total,
                "transfer_time": transfer_time,
                "period": period
            }
            
        except Exception as e:
            logger.error(f"Error calculating Hohmann transfer: {e}")
            return {}
    
    def calculate_orbital_maneuver(self, current_orbit: Dict[str, float], target_orbit: Dict[str, float]) -> Dict[str, Any]:
        """Calculate orbital maneuver to change from current to target orbit"""
        try:
            if not POLIASTRO_AVAILABLE:
                # Fallback calculation
                return self._calculate_maneuver_fallback(current_orbit, target_orbit)
            
            # Use Poliastro for precise maneuver calculations
            # Create current orbit
            a1 = current_orbit["semi_major_axis"] * u.km
            ecc1 = current_orbit["eccentricity"] * u.one
            inc1 = current_orbit["inclination"] * u.deg
            raan1 = current_orbit["right_ascension"] * u.deg
            argp1 = current_orbit["argument_of_perigee"] * u.deg
            nu1 = current_orbit["mean_anomaly"] * u.deg
            
            orbit1 = Orbit.from_classical(Earth, a1, ecc1, inc1, raan1, argp1, nu1)
            
            # Create target orbit
            a2 = target_orbit["semi_major_axis"] * u.km
            ecc2 = target_orbit["eccentricity"] * u.one
            inc2 = target_orbit["inclination"] * u.deg
            raan2 = target_orbit["right_ascension"] * u.deg
            argp2 = target_orbit["argument_of_perigee"] * u.deg
            nu2 = target_orbit["mean_anomaly"] * u.deg
            
            orbit2 = Orbit.from_classical(Earth, a2, ecc2, inc2, raan2, argp2, nu2)
            
            # Calculate maneuver (simplified - would need proper Lambert solver)
            # For now, use Hohmann transfer if only semi-major axis changes
            if abs(a1.value - a2.value) > 1.0:
                r1 = a1.value
                r2 = a2.value
                hohmann = self.calculate_hohmann_transfer(r1, r2)
                return {
                    "maneuver_type": "hohmann_transfer",
                    "delta_v_total": hohmann["delta_v_total"],
                    "transfer_time": hohmann["transfer_time"],
                    "details": hohmann
                }
            
            return {"maneuver_type": "none", "delta_v_total": 0.0}
            
        except Exception as e:
            logger.error(f"Error calculating orbital maneuver: {e}")
            return {}
    
    def _calculate_maneuver_fallback(self, current_orbit: Dict[str, float], target_orbit: Dict[str, float]) -> Dict[str, Any]:
        """Fallback maneuver calculation when Poliastro is unavailable"""
        # Simple delta-V calculation for circular orbit changes
        r1 = current_orbit.get("semi_major_axis", 7000)
        r2 = target_orbit.get("semi_major_axis", 7000)
        
        if abs(r1 - r2) > 1.0:
            hohmann = self.calculate_hohmann_transfer(r1, r2)
            return {
                "maneuver_type": "hohmann_transfer",
                "delta_v_total": hohmann["delta_v_total"],
                "transfer_time": hohmann["transfer_time"]
            }
        
        return {"maneuver_type": "none", "delta_v_total": 0.0}
    
    def check_collision_risk(self, sat1_pos: np.ndarray, sat1_vel: np.ndarray, sat2_pos: np.ndarray, sat2_vel: np.ndarray, 
                            sat1_radius: float = 0.01, sat2_radius: float = 0.01, time_horizon: float = 24.0) -> Dict[str, Any]:
        """Check collision risk between two satellites over time horizon"""
        try:
            # Calculate relative position and velocity
            r_rel = sat2_pos - sat1_pos
            v_rel = sat2_vel - sat1_vel
            
            # Minimum separation distance
            min_separation = sat1_radius + sat2_radius  # km
            
            # Calculate closest approach
            # Time to closest approach
            if np.linalg.norm(v_rel) > 0:
                t_ca = -np.dot(r_rel, v_rel) / (np.linalg.norm(v_rel) ** 2)
                
                # Closest approach distance
                r_ca = r_rel + v_rel * t_ca
                d_ca = np.linalg.norm(r_ca)
                
                # Check if collision risk exists
                collision_risk = d_ca < min_separation and 0 <= t_ca <= time_horizon * 3600
                
                return {
                    "collision_risk": collision_risk,
                    "closest_approach_distance": d_ca,
                    "time_to_closest_approach": t_ca,
                    "minimum_separation": min_separation,
                    "risk_level": "high" if d_ca < min_separation * 10 else "low"
                }
            else:
                return {
                    "collision_risk": False,
                    "closest_approach_distance": np.linalg.norm(r_rel),
                    "time_to_closest_approach": 0,
                    "minimum_separation": min_separation,
                    "risk_level": "low"
                }
                
        except Exception as e:
            logger.error(f"Error checking collision risk: {e}")
            return {"collision_risk": False, "error": str(e)}
    
    def calculate_station_keeping(self, current_orbit: Dict[str, float], target_orbit: Dict[str, float]) -> Dict[str, Any]:
        """Calculate station-keeping maneuvers to maintain target orbit"""
        try:
            # Calculate required corrections
            corrections = {}
            
            # Semi-major axis correction
            da = target_orbit["semi_major_axis"] - current_orbit["semi_major_axis"]
            if abs(da) > 0.1:  # 100m threshold
                # Circular velocity change
                r = current_orbit["semi_major_axis"]
                dv = (self.mu_earth / (2 * r * r)) * da
                corrections["semi_major_axis"] = {
                    "delta_v": abs(dv),
                    "direction": "prograde" if dv > 0 else "retrograde"
                }
            
            # Inclination correction
            di = math.radians(target_orbit["inclination"] - current_orbit["inclination"])
            if abs(di) > math.radians(0.1):  # 0.1 degree threshold
                v = math.sqrt(self.mu_earth / current_orbit["semi_major_axis"])
                dv = 2 * v * math.sin(abs(di) / 2)
                corrections["inclination"] = {
                    "delta_v": dv,
                    "direction": "normal"
                }
            
            # Eccentricity correction (simplified)
            de = target_orbit["eccentricity"] - current_orbit["eccentricity"]
            if abs(de) > 0.001:
                v = math.sqrt(self.mu_earth / current_orbit["semi_major_axis"])
                dv = v * abs(de)
                corrections["eccentricity"] = {
                    "delta_v": dv,
                    "direction": "tangential"
                }
            
            total_dv = sum(c["delta_v"] for c in corrections.values())
            
            return {
                "corrections_needed": corrections,
                "total_delta_v": total_dv,
                "station_keeping_required": len(corrections) > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating station-keeping: {e}")
            return {}
    
    def tle_to_keplerian(self, tle_line1: str, tle_line2: str) -> Dict[str, float]:
        """Convert TLE (Two-Line Element) to Keplerian orbital elements"""
        try:
            if not SGP4_AVAILABLE:
                return {}
            
            # Parse TLE
            satellite = Satrec.twoline2rv(tle_line1, tle_line2)
            
            # Extract orbital elements from SGP4
            # Note: SGP4 uses mean motion and other parameters
            # This is a simplified conversion
            mean_motion = satellite.no  # rev/day
            eccentricity = satellite.ecco
            inclination = math.degrees(satellite.inclo)
            raan = math.degrees(satellite.nodeo)
            argp = math.degrees(satellite.argpo)
            mean_anomaly = math.degrees(satellite.mo)
            
            # Calculate semi-major axis from mean motion
            # n = sqrt(mu / a^3) => a = (mu / n^2)^(1/3)
            n_rad_per_sec = mean_motion * 2 * math.pi / 86400  # Convert to rad/s
            a = (self.mu_earth / (n_rad_per_sec ** 2)) ** (1/3)
            
            return {
                "semi_major_axis": a,
                "eccentricity": eccentricity,
                "inclination": inclination,
                "right_ascension": raan,
                "argument_of_perigee": argp,
                "mean_anomaly": mean_anomaly
            }
            
        except Exception as e:
            logger.error(f"Error converting TLE to Keplerian: {e}")
            return {}

# Global instance
orbital_mechanics = OrbitalMechanics()

