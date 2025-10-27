"""
Tests for satellite physics engine
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.services.satellite_physics import (
    SatellitePhysicsEngine,
    SatellitePosition,
    PassPrediction,
    OrbitalElements
)

@pytest.mark.satellite
class TestSatellitePhysicsEngine:
    """Test cases for satellite physics engine."""
    
    @pytest.fixture
    async def physics_engine(self):
        """Create a satellite physics engine instance for testing."""
        engine = SatellitePhysicsEngine()
        # Mock the SGP4 library for testing
        with patch('app.services.satellite_physics.SGP4_AVAILABLE', True):
            with patch('app.services.satellite_physics.Satrec') as mock_satrec:
                with patch('app.services.satellite_physics.jday') as mock_jday:
                    # Setup mock satellite
                    mock_satellite = MagicMock()
                    mock_satellite.sgp4.return_value = (0, [1000, 2000, 3000], [1, 2, 3])
                    mock_satrec.twoline2rv.return_value = mock_satellite
                    
                    # Setup mock Julian day calculation
                    mock_jday.return_value = (2450000.0, 0.5)
                    
                    await engine.initialize()
                    yield engine
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, physics_engine):
        """Test satellite physics engine initialization."""
        assert physics_engine.is_running is True
        assert len(physics_engine.satellites) > 0
        assert len(physics_engine.satellite_metadata) > 0
    
    @pytest.mark.asyncio
    async def test_get_satellite_position(self, physics_engine):
        """Test getting satellite position."""
        position = await physics_engine.get_satellite_position("sentinel_1a")
        
        assert position is not None
        assert isinstance(position, SatellitePosition)
        assert position.latitude is not None
        assert position.longitude is not None
        assert position.altitude is not None
        assert position.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_get_satellite_position_with_timestamp(self, physics_engine):
        """Test getting satellite position at specific timestamp."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        position = await physics_engine.get_satellite_position("sentinel_1a", timestamp)
        
        assert position is not None
        assert position.timestamp == timestamp
    
    @pytest.mark.asyncio
    async def test_predict_orbital_passes(self, physics_engine):
        """Test orbital pass prediction."""
        predictions = await physics_engine.predict_orbital_passes(
            observer_lat=40.7128,
            observer_lng=-74.0060,
            observer_alt=0.0,
            days_ahead=1,
            min_elevation=10.0
        )
        
        assert isinstance(predictions, list)
        # In a real test, we would verify the prediction logic
    
    @pytest.mark.asyncio
    async def test_get_satellite_status(self, physics_engine):
        """Test getting satellite status."""
        status = await physics_engine.get_satellite_status()
        
        assert isinstance(status, dict)
        assert "engine_running" in status
        assert "total_satellites" in status
        assert "satellites" in status
        assert "last_update" in status
        assert status["engine_running"] is True
    
    @pytest.mark.asyncio
    async def test_eci_to_lat_lng_alt_conversion(self, physics_engine):
        """Test ECI to lat/lng/alt coordinate conversion."""
        # Test with known ECI coordinates
        position = (6371.0, 0.0, 0.0)  # On equator, 0 longitude
        lat, lng, alt = physics_engine._eci_to_lat_lng_alt(position)
        
        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert isinstance(alt, float)
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180
    
    @pytest.mark.asyncio
    async def test_lat_lng_alt_to_eci_conversion(self, physics_engine):
        """Test lat/lng/alt to ECI coordinate conversion."""
        # Test with known coordinates
        lat, lng, alt = 0.0, 0.0, 0.0  # On equator, sea level
        eci = physics_engine._lat_lng_alt_to_eci(lat, lng, alt)
        
        assert isinstance(eci, tuple)
        assert len(eci) == 3
        assert all(isinstance(coord, float) for coord in eci)
    
    @pytest.mark.asyncio
    async def test_elevation_calculation(self, physics_engine):
        """Test elevation angle calculation."""
        satellite_position = (7000, 0, 0)  # 7000 km from Earth center
        observer_lat, observer_lng, observer_alt = 0.0, 0.0, 0.0
        
        elevation = physics_engine._calculate_elevation(
            satellite_position, observer_lat, observer_lng, observer_alt
        )
        
        assert isinstance(elevation, float)
        assert -90 <= elevation <= 90
    
    @pytest.mark.asyncio
    async def test_azimuth_calculation(self, physics_engine):
        """Test azimuth angle calculation."""
        satellite_position = (7000, 0, 0)
        observer_lat, observer_lng = 0.0, 0.0
        
        azimuth = physics_engine._calculate_azimuth(
            satellite_position, observer_lat, observer_lng
        )
        
        assert isinstance(azimuth, float)
        assert 0 <= azimuth <= 360
    
    @pytest.mark.asyncio
    async def test_pass_type_determination(self, physics_engine):
        """Test pass type determination (daylight/night/twilight)."""
        # Test daylight pass
        daylight_time = datetime(2024, 1, 1, 12, 0, 0)  # Noon
        pass_type = physics_engine._determine_pass_type(daylight_time, 0.0, 0.0)
        assert pass_type in ["daylight", "night", "twilight"]
        
        # Test night pass
        night_time = datetime(2024, 1, 1, 2, 0, 0)  # 2 AM
        pass_type = physics_engine._determine_pass_type(night_time, 0.0, 0.0)
        assert pass_type in ["daylight", "night", "twilight"]
    
    @pytest.mark.asyncio
    async def test_engine_shutdown(self, physics_engine):
        """Test satellite physics engine shutdown."""
        await physics_engine.shutdown()
        assert physics_engine.is_running is False
    
    @pytest.mark.asyncio
    async def test_invalid_satellite_id(self, physics_engine):
        """Test handling of invalid satellite ID."""
        position = await physics_engine.get_satellite_position("invalid_satellite")
        assert position is None
    
    @pytest.mark.asyncio
    async def test_sgp4_error_handling(self, physics_engine):
        """Test SGP4 error handling."""
        # Mock SGP4 error
        with patch.object(physics_engine.satellites['sentinel_1a'], 'sgp4') as mock_sgp4:
            mock_sgp4.return_value = (1, None, None)  # Error code 1
            
            position = await physics_engine.get_satellite_position("sentinel_1a")
            # Should handle error gracefully
            assert position is None

@pytest.mark.satellite
class TestSatellitePosition:
    """Test cases for SatellitePosition dataclass."""
    
    def test_satellite_position_creation(self):
        """Test creating a SatellitePosition instance."""
        position = SatellitePosition(
            position=(1000, 2000, 3000),
            velocity=(1, 2, 3),
            latitude=45.0,
            longitude=0.0,
            altitude=700.0,
            timestamp=datetime.now()
        )
        
        assert position.position == (1000, 2000, 3000)
        assert position.velocity == (1, 2, 3)
        assert position.latitude == 45.0
        assert position.longitude == 0.0
        assert position.altitude == 700.0
        assert isinstance(position.timestamp, datetime)

@pytest.mark.satellite
class TestPassPrediction:
    """Test cases for PassPrediction dataclass."""
    
    def test_pass_prediction_creation(self):
        """Test creating a PassPrediction instance."""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)
        
        prediction = PassPrediction(
            satellite_id="sentinel_1a",
            satellite_name="Sentinel-1A",
            start_time=start_time,
            end_time=end_time,
            duration=10.0,
            max_elevation=45.0,
            azimuth=180.0,
            pass_type="daylight"
        )
        
        assert prediction.satellite_id == "sentinel_1a"
        assert prediction.satellite_name == "Sentinel-1A"
        assert prediction.start_time == start_time
        assert prediction.end_time == end_time
        assert prediction.duration == 10.0
        assert prediction.max_elevation == 45.0
        assert prediction.azimuth == 180.0
        assert prediction.pass_type == "daylight"

@pytest.mark.satellite
class TestOrbitalElements:
    """Test cases for OrbitalElements dataclass."""
    
    def test_orbital_elements_creation(self):
        """Test creating an OrbitalElements instance."""
        elements = OrbitalElements(
            semi_major_axis=7000.0,
            eccentricity=0.001,
            inclination=98.2,
            right_ascension=123.45,
            argument_of_perigee=67.89,
            mean_anomaly=234.56,
            epoch=datetime.now(),
            mean_motion=14.2,
            bstar=0.00001
        )
        
        assert elements.semi_major_axis == 7000.0
        assert elements.eccentricity == 0.001
        assert elements.inclination == 98.2
        assert elements.right_ascension == 123.45
        assert elements.argument_of_perigee == 67.89
        assert elements.mean_anomaly == 234.56
        assert isinstance(elements.epoch, datetime)
        assert elements.mean_motion == 14.2
        assert elements.bstar == 0.00001
