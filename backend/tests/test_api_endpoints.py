"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.main import app
from app.models.mission import MissionType, MissionStatus, MissionPriority
from app.models.agent import AgentStatus, AgentType
from app.models.telemetry import TelemetryType
from app.models.blockchain import TransactionType, TransactionStatus

@pytest.mark.api
class TestMissionEndpoints:
    """Test cases for mission API endpoints."""
    
    def test_create_mission(self, client: TestClient, sample_mission_data):
        """Test creating a new mission."""
        response = client.post("/api/v1/missions/", json=sample_mission_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_mission_data["name"]
        assert data["mission_type"] == sample_mission_data["mission_type"]
        assert data["priority"] == sample_mission_data["priority"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_missions(self, client: TestClient, sample_mission_data):
        """Test retrieving missions."""
        # Create a mission first
        client.post("/api/v1/missions/", json=sample_mission_data)
        
        response = client.get("/api/v1/missions/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_mission_by_id(self, client: TestClient, sample_mission_data):
        """Test retrieving a specific mission by ID."""
        # Create a mission first
        create_response = client.post("/api/v1/missions/", json=sample_mission_data)
        mission_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/missions/{mission_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == mission_id
        assert data["name"] == sample_mission_data["name"]
    
    def test_update_mission(self, client: TestClient, sample_mission_data):
        """Test updating a mission."""
        # Create a mission first
        create_response = client.post("/api/v1/missions/", json=sample_mission_data)
        mission_id = create_response.json()["id"]
        
        # Update the mission
        update_data = {"name": "Updated Mission Name", "priority": "low"}
        response = client.put(f"/api/v1/missions/{mission_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Mission Name"
        assert data["priority"] == "low"
    
    def test_delete_mission(self, client: TestClient, sample_mission_data):
        """Test deleting a mission."""
        # Create a mission first
        create_response = client.post("/api/v1/missions/", json=sample_mission_data)
        mission_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/missions/{mission_id}")
        assert response.status_code == 200
        
        # Verify mission is deleted
        get_response = client.get(f"/api/v1/missions/{mission_id}")
        assert get_response.status_code == 404
    
    def test_get_missions_with_filters(self, client: TestClient, sample_mission_data):
        """Test retrieving missions with filters."""
        # Create multiple missions
        client.post("/api/v1/missions/", json=sample_mission_data)
        
        high_priority_data = sample_mission_data.copy()
        high_priority_data["name"] = "High Priority Mission"
        high_priority_data["priority"] = "high"
        client.post("/api/v1/missions/", json=high_priority_data)
        
        # Filter by priority
        response = client.get("/api/v1/missions/?priority=high")
        assert response.status_code == 200
        
        data = response.json()
        assert all(mission["priority"] == "high" for mission in data)
    
    def test_get_missions_with_pagination(self, client: TestClient, sample_mission_data):
        """Test retrieving missions with pagination."""
        # Create multiple missions
        for i in range(5):
            mission_data = sample_mission_data.copy()
            mission_data["name"] = f"Mission {i}"
            client.post("/api/v1/missions/", json=mission_data)
        
        # Test pagination
        response = client.get("/api/v1/missions/?limit=2&skip=0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2

@pytest.mark.api
class TestAgentEndpoints:
    """Test cases for agent API endpoints."""
    
    def test_create_agent(self, client: TestClient, sample_agent_data):
        """Test creating a new agent."""
        response = client.post("/api/v1/agents/", json=sample_agent_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_agent_data["name"]
        assert data["agent_type"] == sample_agent_data["agent_type"]
        assert data["status"] == sample_agent_data["status"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_agents(self, client: TestClient, sample_agent_data):
        """Test retrieving agents."""
        # Create an agent first
        client.post("/api/v1/agents/", json=sample_agent_data)
        
        response = client.get("/api/v1/agents/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_agent_by_id(self, client: TestClient, sample_agent_data):
        """Test retrieving a specific agent by ID."""
        # Create an agent first
        create_response = client.post("/api/v1/agents/", json=sample_agent_data)
        agent_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == sample_agent_data["name"]
    
    def test_update_agent_status(self, client: TestClient, sample_agent_data):
        """Test updating agent status."""
        # Create an agent first
        create_response = client.post("/api/v1/agents/", json=sample_agent_data)
        agent_id = create_response.json()["id"]
        
        # Update agent status
        update_data = {"status": "offline"}
        response = client.put(f"/api/v1/agents/{agent_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "offline"
    
    def test_get_agents_by_type(self, client: TestClient, sample_agent_data):
        """Test retrieving agents by type."""
        # Create an agent first
        client.post("/api/v1/agents/", json=sample_agent_data)
        
        response = client.get(f"/api/v1/agents/?agent_type={sample_agent_data['agent_type']}")
        assert response.status_code == 200
        
        data = response.json()
        assert all(agent["agent_type"] == sample_agent_data["agent_type"] for agent in data)

@pytest.mark.api
class TestTelemetryEndpoints:
    """Test cases for telemetry API endpoints."""
    
    def test_create_telemetry_record(self, client: TestClient, sample_telemetry_data):
        """Test creating a telemetry record."""
        response = client.post("/api/v1/telemetry/", json=sample_telemetry_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["agent_id"] == sample_telemetry_data["agent_id"]
        assert data["timestamp"] == sample_telemetry_data["timestamp"]
        assert "id" in data
    
    def test_get_telemetry_data(self, client: TestClient, sample_telemetry_data):
        """Test retrieving telemetry data."""
        # Create telemetry record first
        client.post("/api/v1/telemetry/", json=sample_telemetry_data)
        
        response = client.get("/api/v1/telemetry/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_telemetry_by_agent(self, client: TestClient, sample_telemetry_data):
        """Test retrieving telemetry data by agent ID."""
        # Create telemetry record first
        client.post("/api/v1/telemetry/", json=sample_telemetry_data)
        
        response = client.get(f"/api/v1/telemetry/?agent_id={sample_telemetry_data['agent_id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert all(record["agent_id"] == sample_telemetry_data["agent_id"] for record in data)
    
    def test_get_telemetry_trends(self, client: TestClient, sample_telemetry_data):
        """Test retrieving telemetry trends."""
        # Create multiple telemetry records
        for i in range(3):
            telemetry_data = sample_telemetry_data.copy()
            telemetry_data["environmental_data"]["temperature"] = 20 + i
            client.post("/api/v1/telemetry/", json=telemetry_data)
        
        response = client.get("/api/v1/telemetry/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
        assert isinstance(data["trends"], list)

@pytest.mark.api
class TestBlockchainEndpoints:
    """Test cases for blockchain API endpoints."""
    
    def test_create_blockchain_record(self, client: TestClient, sample_blockchain_record):
        """Test creating a blockchain record."""
        response = client.post("/api/v1/blockchain/records/", json=sample_blockchain_record)
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_hash"] == sample_blockchain_record["transaction_hash"]
        assert data["transaction_type"] == sample_blockchain_record["transaction_type"]
        assert "id" in data
    
    def test_get_blockchain_records(self, client: TestClient, sample_blockchain_record):
        """Test retrieving blockchain records."""
        # Create a record first
        client.post("/api/v1/blockchain/records/", json=sample_blockchain_record)
        
        response = client.get("/api/v1/blockchain/records/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_wallet_balance(self, client: TestClient):
        """Test getting wallet balance."""
        response = client.get("/api/v1/blockchain/wallet/balance")
        assert response.status_code == 200
        
        data = response.json()
        assert "balance" in data
        assert "wallet_address" in data
    
    def test_get_transactions(self, client: TestClient, sample_blockchain_record):
        """Test getting transaction history."""
        # Create a record first
        client.post("/api/v1/blockchain/records/", json=sample_blockchain_record)
        
        response = client.get("/api/v1/blockchain/transactions/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.api
class TestSatellitePhysicsEndpoints:
    """Test cases for satellite physics API endpoints."""
    
    def test_get_satellite_status(self, client: TestClient):
        """Test getting satellite status."""
        response = client.get("/api/v1/satellites/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "engine_running" in data
        assert "total_satellites" in data
        assert "satellites" in data
    
    def test_get_satellite_position(self, client: TestClient):
        """Test getting satellite position."""
        response = client.get("/api/v1/satellites/sentinel_1a/position")
        assert response.status_code == 200
        
        data = response.json()
        assert "satellite_id" in data
        assert "position" in data
        assert "velocity" in data
        assert "latitude" in data
        assert "longitude" in data
        assert "altitude" in data
    
    def test_get_all_satellite_positions(self, client: TestClient):
        """Test getting all satellite positions."""
        response = client.get("/api/v1/satellites/positions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_predict_orbital_passes(self, client: TestClient):
        """Test predicting orbital passes."""
        params = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "altitude": 0,
            "days_ahead": 1,
            "min_elevation": 10
        }
        
        response = client.get("/api/v1/satellites/predictions", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_satellite_constellation(self, client: TestClient):
        """Test getting satellite constellation info."""
        response = client.get("/api/v1/satellites/constellation")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_satellites" in data
        assert "satellites" in data
        assert isinstance(data["satellites"], list)
    
    def test_get_next_satellite_pass(self, client: TestClient):
        """Test getting next satellite pass."""
        params = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "altitude": 0,
            "min_elevation": 10
        }
        
        response = client.get("/api/v1/satellites/sentinel_1a/next-pass", params=params)
        # This might return 404 if no passes are found, which is acceptable
        assert response.status_code in [200, 404]

@pytest.mark.api
class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["message"] == "Nebula Protocol API"
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "mongodb" in data
        assert "solana" in data
        assert "swarms_ai" in data
        assert "orchestrator" in data
        assert "satellite_physics" in data

@pytest.mark.api
class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_invalid_mission_id(self, client: TestClient):
        """Test handling of invalid mission ID."""
        response = client.get("/api/v1/missions/invalid_id")
        assert response.status_code == 404
    
    def test_invalid_agent_id(self, client: TestClient):
        """Test handling of invalid agent ID."""
        response = client.get("/api/v1/agents/invalid_id")
        assert response.status_code == 404
    
    def test_invalid_satellite_id(self, client: TestClient):
        """Test handling of invalid satellite ID."""
        response = client.get("/api/v1/satellites/invalid_id/position")
        assert response.status_code == 404
    
    def test_invalid_coordinates(self, client: TestClient):
        """Test handling of invalid coordinates."""
        params = {
            "latitude": 999,  # Invalid latitude
            "longitude": -74.0060,
            "altitude": 0,
            "days_ahead": 1,
            "min_elevation": 10
        }
        
        response = client.get("/api/v1/satellites/predictions", params=params)
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client: TestClient):
        """Test handling of missing required fields."""
        incomplete_data = {"name": "Test Mission"}  # Missing required fields
        
        response = client.post("/api/v1/missions/", json=incomplete_data)
        assert response.status_code == 422  # Validation error
