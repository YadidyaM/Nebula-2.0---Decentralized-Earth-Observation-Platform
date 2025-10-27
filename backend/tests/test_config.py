#!/usr/bin/env python3
"""
Test configuration for different test environments
"""

import os
import pytest
from typing import Dict, Any

# Test environment configuration
TEST_CONFIG: Dict[str, Any] = {
    "database": {
        "url": os.getenv("TEST_MONGODB_URL", "mongodb://localhost:27017/nebula_test"),
        "name": os.getenv("TEST_DATABASE_NAME", "nebula_test")
    },
    "redis": {
        "url": os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
    },
    "solana": {
        "rpc_url": os.getenv("TEST_SOLANA_RPC_URL", "https://api.devnet.solana.com"),
        "network": "devnet"
    },
    "swarms": {
        "api_key": os.getenv("TEST_SWARMS_API_KEY", "test_key"),
        "base_url": os.getenv("TEST_SWARMS_BASE_URL", "https://api.swarms.ai")
    },
    "external_apis": {
        "nasa": {
            "api_key": os.getenv("TEST_NASA_API_KEY", "test_key"),
            "base_url": "https://api.nasa.gov"
        },
        "noaa": {
            "api_key": os.getenv("TEST_NOAA_API_KEY", "test_key"),
            "base_url": "https://api.weather.gov"
        },
        "usgs": {
            "api_key": os.getenv("TEST_USGS_API_KEY", "test_key"),
            "base_url": "https://earthquake.usgs.gov"
        }
    }
}

# Test markers configuration
TEST_MARKERS = {
    "unit": "Fast unit tests that don't require external dependencies",
    "integration": "Integration tests that require database and external services",
    "api": "API endpoint tests",
    "slow": "Slow running tests that take more than 5 seconds",
    "satellite": "Satellite physics tests",
    "blockchain": "Blockchain integration tests",
    "ai": "AI agent tests",
    "websocket": "WebSocket tests",
    "external": "Tests that require external API calls",
    "database": "Tests that require database access"
}

# Test data fixtures
SAMPLE_MISSION_DATA = {
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

SAMPLE_AGENT_DATA = {
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

SAMPLE_TELEMETRY_DATA = {
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

SAMPLE_BLOCKCHAIN_RECORD = {
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

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "api_response_time": 200,  # milliseconds
    "database_query_time": 100,  # milliseconds
    "websocket_latency": 50,  # milliseconds
    "satellite_position_update": 1,  # seconds
    "memory_usage": 2048,  # MB
    "cpu_usage": 70,  # percentage
}

# Test environment setup
def setup_test_environment():
    """Setup test environment variables."""
    os.environ.update({
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "MONGODB_URL": TEST_CONFIG["database"]["url"],
        "REDIS_URL": TEST_CONFIG["redis"]["url"],
        "SOLANA_RPC_URL": TEST_CONFIG["solana"]["rpc_url"],
        "SOLANA_NETWORK": TEST_CONFIG["solana"]["network"],
        "SWARMS_API_KEY": TEST_CONFIG["swarms"]["api_key"],
        "NASA_API_KEY": TEST_CONFIG["external_apis"]["nasa"]["api_key"],
        "NOAA_API_KEY": TEST_CONFIG["external_apis"]["noaa"]["api_key"],
        "USGS_API_KEY": TEST_CONFIG["external_apis"]["usgs"]["api_key"]
    })

# Test utilities
class TestUtilities:
    """Utility functions for tests."""
    
    @staticmethod
    def create_test_mission(**kwargs):
        """Create a test mission with default values."""
        mission_data = SAMPLE_MISSION_DATA.copy()
        mission_data.update(kwargs)
        return mission_data
    
    @staticmethod
    def create_test_agent(**kwargs):
        """Create a test agent with default values."""
        agent_data = SAMPLE_AGENT_DATA.copy()
        agent_data.update(kwargs)
        return agent_data
    
    @staticmethod
    def create_test_telemetry(**kwargs):
        """Create test telemetry data with default values."""
        telemetry_data = SAMPLE_TELEMETRY_DATA.copy()
        telemetry_data.update(kwargs)
        return telemetry_data
    
    @staticmethod
    def create_test_blockchain_record(**kwargs):
        """Create test blockchain record with default values."""
        record_data = SAMPLE_BLOCKCHAIN_RECORD.copy()
        record_data.update(kwargs)
        return record_data
    
    @staticmethod
    def assert_performance_benchmark(metric_name: str, actual_value: float):
        """Assert that a performance metric meets the benchmark."""
        benchmark = PERFORMANCE_BENCHMARKS.get(metric_name)
        if benchmark is None:
            raise ValueError(f"Unknown performance metric: {metric_name}")
        
        assert actual_value <= benchmark, \
            f"{metric_name} ({actual_value}) exceeds benchmark ({benchmark})"

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker, description in TEST_MARKERS.items():
        config.addinivalue_line("markers", f"{marker}: {description}")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_satellite_physics" in item.nodeid:
            item.add_marker(pytest.mark.satellite)
        elif "test_blockchain" in item.nodeid:
            item.add_marker(pytest.mark.blockchain)
        elif "test_ai_agents" in item.nodeid:
            item.add_marker(pytest.mark.ai)
        elif "test_websocket" in item.nodeid:
            item.add_marker(pytest.mark.websocket)
        elif "test_api_endpoints" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Add slow marker for tests that might be slow
        if any(keyword in item.nodeid.lower() for keyword in ["integration", "external", "performance"]):
            item.add_marker(pytest.mark.slow)

# Test session setup
def pytest_sessionstart(session):
    """Setup test session."""
    setup_test_environment()
    print("🌌 Nebula Protocol Test Session Started")
    print(f"📊 Running {len(session.items)} tests")

def pytest_sessionfinish(session, exitstatus):
    """Cleanup test session."""
    print(f"\n🏁 Test Session Finished with exit status: {exitstatus}")
    if exitstatus == 0:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")

# Test reporting
def pytest_html_report_title(report):
    """Set HTML report title."""
    report.title = "Nebula Protocol Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    """Customize HTML report summary."""
    prefix.extend([
        "<h2>Nebula Protocol Test Results</h2>",
        "<p>Decentralized Environmental Monitoring Network</p>"
    ])
