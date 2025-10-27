"""
Test configuration and fixtures for Nebula Protocol backend tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock, MagicMock
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.main import app
from app.db.mongodb import get_database
from app.services.satellite_physics import satellite_physics_engine
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator
from app.services.blockchain.solana_client import SolanaClient

# Test database configuration
TEST_DATABASE_URL = "mongodb://localhost:27017/nebula_test"
TEST_DATABASE_NAME = "nebula_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a test database connection."""
    client = AsyncIOMotorClient(TEST_DATABASE_URL)
    db = client[TEST_DATABASE_NAME]
    
    # Clean up before tests
    await db.drop_collection("missions")
    await db.drop_collection("agents")
    await db.drop_collection("telemetry")
    await db.drop_collection("users")
    await db.drop_collection("blockchain_records")
    
    yield db
    
    # Clean up after tests
    await db.drop_collection("missions")
    await db.drop_collection("agents")
    await db.drop_collection("telemetry")
    await db.drop_collection("users")
    await db.drop_collection("blockchain_records")
    client.close()

@pytest.fixture
def client(test_db) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    def override_get_database():
        return test_db
    
    app.dependency_overrides[get_database] = override_get_database
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def mock_satellite_physics():
    """Mock satellite physics engine for testing."""
    mock_engine = AsyncMock()
    mock_engine.is_running = True
    mock_engine.satellites = {
        "sentinel_1a": MagicMock(),
        "landsat_8": MagicMock(),
        "modis_terra": MagicMock(),
        "noaa_20": MagicMock()
    }
    mock_engine.satellite_metadata = {
        "sentinel_1a": {
            "name": "Sentinel-1A",
            "mission_type": "environmental_monitoring",
            "capabilities": ["radar_imaging", "ice_monitoring"]
        },
        "landsat_8": {
            "name": "Landsat-8",
            "mission_type": "environmental_monitoring",
            "capabilities": ["optical_imaging", "land_use"]
        }
    }
    
    # Mock position data
    mock_position = {
        "satellite_id": "sentinel_1a",
        "satellite_name": "Sentinel-1A",
        "position": {"x": 1000, "y": 2000, "z": 3000},
        "velocity": {"x": 1, "y": 2, "z": 3},
        "latitude": 45.0,
        "longitude": 0.0,
        "altitude": 693.0,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    mock_engine.get_satellite_position.return_value = mock_position
    mock_engine.get_satellite_status.return_value = {
        "engine_running": True,
        "total_satellites": 4,
        "satellites": mock_engine.satellite_metadata,
        "last_update": "2024-01-01T00:00:00Z"
    }
    
    return mock_engine

@pytest.fixture
async def mock_swarms_orchestrator():
    """Mock Swarms AI orchestrator for testing."""
    mock_orchestrator = AsyncMock()
    mock_orchestrator.agents = {
        "forest_guardian": AsyncMock(),
        "ice_sentinel": AsyncMock(),
        "storm_tracker": AsyncMock(),
        "urban_monitor": AsyncMock(),
        "water_watcher": AsyncMock(),
        "security_sentinel": AsyncMock(),
        "land_surveyor": AsyncMock(),
        "disaster_responder": AsyncMock()
    }
    
    return mock_orchestrator

@pytest.fixture
async def mock_solana_client():
    """Mock Solana client for testing."""
    mock_client = AsyncMock()
    mock_client.is_connected = True
    mock_client.get_balance.return_value = 1000000  # 1 SOL in lamports
    mock_client.send_transaction.return_value = "test_transaction_hash"
    
    return mock_client

@pytest.fixture
def sample_mission_data():
    """Sample mission data for testing."""
    return {
        "name": "Test Forest Monitoring Mission",
        "description": "Monitor deforestation in Amazon rainforest",
        "mission_type": "environmental_monitoring",
        "priority": "high",
        "target_location": {
            "latitude": -3.4653,
            "longitude": -62.2159,
            "radius": 100
        },
        "required_capabilities": ["optical_imaging", "deforestation_detection"],
        "estimated_duration": 3600,
        "reward_amount": 1000
    }

@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Forest Guardian",
        "agent_type": "forest_guardian",
        "status": "online",
        "capabilities": ["optical_imaging", "deforestation_detection"],
        "position": {
            "latitude": -3.4653,
            "longitude": -62.2159,
            "altitude": 700
        },
        "performance_metrics": {
            "missions_completed": 10,
            "success_rate": 0.95,
            "average_response_time": 30
        }
    }

@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data for testing."""
    return {
        "agent_id": "test_agent_123",
        "timestamp": "2024-01-01T00:00:00Z",
        "position": {
            "latitude": -3.4653,
            "longitude": -62.2159,
            "altitude": 700
        },
        "environmental_data": {
            "temperature": 25.5,
            "humidity": 80.0,
            "air_quality": "good",
            "vegetation_index": 0.75
        },
        "system_status": {
            "battery_level": 85,
            "signal_strength": 95,
            "cpu_usage": 45,
            "memory_usage": 60
        }
    }

@pytest.fixture
def sample_blockchain_record():
    """Sample blockchain record for testing."""
    return {
        "transaction_hash": "test_hash_123",
        "transaction_type": "mission_completion",
        "agent_id": "test_agent_123",
        "mission_id": "test_mission_456",
        "amount": 1000,
        "status": "confirmed",
        "timestamp": "2024-01-01T00:00:00Z",
        "block_number": 12345,
        "gas_used": 21000
    }

@pytest.fixture
def mock_nasa_api():
    """Mock NASA API responses."""
    return {
        "eonet_events": [
            {
                "id": "test_event_1",
                "title": "Test Wildfire",
                "description": "Test wildfire event",
                "link": "https://example.com",
                "categories": [{"id": 8, "title": "Wildfires"}],
                "geometry": [{
                    "date": "2024-01-01T00:00:00Z",
                    "type": "Point",
                    "coordinates": [-3.4653, -62.2159]
                }]
            }
        ],
        "earth_observatory": {
            "url": "https://example.com/image.jpg",
            "date": "2024-01-01",
            "cloud_score": 0.1
        }
    }

@pytest.fixture
def mock_noaa_api():
    """Mock NOAA API responses."""
    return {
        "current_weather": {
            "temperature": 25.5,
            "humidity": 80,
            "pressure": 1013.25,
            "wind_speed": 5.2,
            "wind_direction": 180,
            "conditions": "Partly Cloudy"
        },
        "forecast": [
            {
                "date": "2024-01-01",
                "high": 28,
                "low": 22,
                "conditions": "Sunny",
                "precipitation": 0
            }
        ]
    }

@pytest.fixture
def mock_usgs_api():
    """Mock USGS API responses."""
    return {
        "earthquakes": [
            {
                "id": "test_eq_1",
                "magnitude": 4.5,
                "place": "Test Location",
                "time": "2024-01-01T00:00:00Z",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-3.4653, -62.2159, 10]
                }
            }
        ],
        "water_data": {
            "site_id": "test_site",
            "site_name": "Test River",
            "parameter": "Streamflow",
            "value": 150.5,
            "unit": "ft3/s",
            "date": "2024-01-01T00:00:00Z"
        }
    }

# Test markers
pytestmark = pytest.mark.asyncio
