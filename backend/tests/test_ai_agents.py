"""
Tests for AI agents and Swarms orchestrator
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents.base_agent import BaseAgent, AgentStatus
from app.agents.specialized.forest_guardian import ForestGuardian
from app.agents.specialized.ice_sentinel import IceSentinel
from app.agents.specialized.storm_tracker import StormTracker
from app.agents.specialized.water_watcher import WaterWatcher
from app.agents.specialized.security_sentinel import SecuritySentinel
from app.agents.specialized.disaster_responder import DisasterResponder
from app.agents.orchestrator import OrchestratorAgent
from app.services.ai.swarms_orchestrator import SwarmsOrchestrator
from app.models.mission import Mission, MissionType, MissionStatus, MissionPriority
from app.models.agent import Position

@pytest.mark.ai
class TestBaseAgent:
    """Test cases for base agent functionality."""
    
    @pytest.fixture
    def base_agent(self):
        """Create a base agent instance for testing."""
        return BaseAgent("test_agent", "Test Agent", "test_wallet_key")
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, base_agent):
        """Test agent initialization."""
        assert base_agent.agent_id == "test_agent"
        assert base_agent.name == "Test Agent"
        assert base_agent.wallet_key == "test_wallet_key"
        assert base_agent.status == AgentStatus.OFFLINE
    
    @pytest.mark.asyncio
    async def test_update_status(self, base_agent):
        """Test updating agent status."""
        await base_agent.update_status(AgentStatus.ONLINE)
        assert base_agent.status == AgentStatus.ONLINE
        
        await base_agent.update_status(AgentStatus.MAINTENANCE)
        assert base_agent.status == AgentStatus.MAINTENANCE
    
    @pytest.mark.asyncio
    async def test_update_position(self, base_agent):
        """Test updating agent position."""
        position = Position(lat=40.7128, lng=-74.0060, alt=700)
        await base_agent.update_position(position)
        
        assert base_agent.position.lat == 40.7128
        assert base_agent.position.lng == -74.0060
        assert base_agent.position.alt == 700
    
    @pytest.mark.asyncio
    async def test_abstract_methods(self, base_agent):
        """Test that abstract methods raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await base_agent.execute_mission(MagicMock())

@pytest.mark.ai
class TestForestGuardian:
    """Test cases for Forest Guardian agent."""
    
    @pytest.fixture
    def forest_guardian(self):
        """Create a Forest Guardian agent instance."""
        return ForestGuardian()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, forest_guardian):
        """Test Forest Guardian initialization."""
        assert forest_guardian.agent_id == "agent_forest_guardian"
        assert forest_guardian.name == "Forest Guardian"
        assert "deforestation" in forest_guardian.specialization
        assert "biodiversity" in forest_guardian.specialization
    
    @pytest.mark.asyncio
    async def test_monitoring_regions(self, forest_guardian):
        """Test monitoring regions configuration."""
        assert len(forest_guardian.monitoring_regions) > 0
        
        # Check that regions have required fields
        for region in forest_guardian.monitoring_regions:
            assert "name" in region
            assert "lat" in region
            assert "lng" in region
            assert "radius" in region
    
    @pytest.mark.asyncio
    async def test_data_sources(self, forest_guardian):
        """Test data sources configuration."""
        assert len(forest_guardian.data_sources) > 0
        
        # Check that data sources are properly configured
        for source_name, source_url in forest_guardian.data_sources.items():
            assert isinstance(source_name, str)
            assert isinstance(source_url, str)
            assert source_url.startswith("http")

@pytest.mark.ai
class TestIceSentinel:
    """Test cases for Ice Sentinel agent."""
    
    @pytest.fixture
    def ice_sentinel(self):
        """Create an Ice Sentinel agent instance."""
        return IceSentinel()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, ice_sentinel):
        """Test Ice Sentinel initialization."""
        assert ice_sentinel.agent_id == "agent_ice_sentinel"
        assert ice_sentinel.name == "Ice Sentinel"
        assert "cryosphere" in ice_sentinel.specialization
        assert "glacier_monitoring" in ice_sentinel.specialization
    
    @pytest.mark.asyncio
    async def test_monitoring_regions(self, ice_sentinel):
        """Test polar monitoring regions."""
        polar_regions = ["Arctic", "Antarctica", "Greenland"]
        
        for region_name in polar_regions:
            region = next(
                (r for r in ice_sentinel.monitoring_regions if r["name"] == region_name),
                None
            )
            assert region is not None
            assert region["lat"] is not None
            assert region["lng"] is not None
            assert region["radius"] > 0

@pytest.mark.ai
class TestStormTracker:
    """Test cases for Storm Tracker agent."""
    
    @pytest.fixture
    def storm_tracker(self):
        """Create a Storm Tracker agent instance."""
        return StormTracker()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, storm_tracker):
        """Test Storm Tracker initialization."""
        assert storm_tracker.agent_id == "agent_storm_tracker"
        assert storm_tracker.name == "Storm Tracker"
        assert "weather" in storm_tracker.specialization
        assert "storm_tracking" in storm_tracker.specialization
    
    @pytest.mark.asyncio
    async def test_storm_types(self, storm_tracker):
        """Test storm types configuration."""
        expected_storm_types = ["hurricane", "typhoon", "cyclone", "tornado"]
        
        for storm_type in expected_storm_types:
            assert storm_type in storm_tracker.storm_types
    
    @pytest.mark.asyncio
    async def test_tracking_regions(self, storm_tracker):
        """Test storm tracking regions."""
        ocean_regions = ["Atlantic", "Pacific", "Indian"]
        
        for region_name in ocean_regions:
            region = next(
                (r for r in storm_tracker.tracking_regions if r["name"] == region_name),
                None
            )
            assert region is not None
            assert region["lat"] is not None
            assert region["lng"] is not None
            assert region["radius"] > 0

@pytest.mark.ai
class TestWaterWatcher:
    """Test cases for Water Watcher agent."""
    
    @pytest.fixture
    def water_watcher(self):
        """Create a Water Watcher agent instance."""
        return WaterWatcher()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, water_watcher):
        """Test Water Watcher initialization."""
        assert water_watcher.agent_id == "agent_water_watcher"
        assert water_watcher.name == "Water Watcher"
        assert "water_quality" in water_watcher.specialization
        assert "flood_monitoring" in water_watcher.specialization
    
    @pytest.mark.asyncio
    async def test_monitoring_parameters(self, water_watcher):
        """Test water monitoring parameters."""
        assert len(water_watcher.monitoring_parameters) > 0
        
        # Check that parameters have required fields
        for param in water_watcher.monitoring_parameters:
            assert "name" in param
            assert "unit" in param
            assert "threshold" in param

@pytest.mark.ai
class TestSecuritySentinel:
    """Test cases for Security Sentinel agent."""
    
    @pytest.fixture
    def security_sentinel(self):
        """Create a Security Sentinel agent instance."""
        return SecuritySentinel()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, security_sentinel):
        """Test Security Sentinel initialization."""
        assert security_sentinel.agent_id == "agent_security_sentinel"
        assert security_sentinel.name == "Security Sentinel"
        assert "threat_detection" in security_sentinel.specialization
        assert "system_monitoring" in security_sentinel.specialization
    
    @pytest.mark.asyncio
    async def test_security_threats(self, security_sentinel):
        """Test security threat types."""
        expected_threats = ["intrusion", "malware", "ddos", "data_breach"]
        
        for threat in expected_threats:
            assert threat in security_sentinel.threat_types

@pytest.mark.ai
class TestDisasterResponder:
    """Test cases for Disaster Responder agent."""
    
    @pytest.fixture
    def disaster_responder(self):
        """Create a Disaster Responder agent instance."""
        return DisasterResponder()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, disaster_responder):
        """Test Disaster Responder initialization."""
        assert disaster_responder.agent_id == "agent_disaster_responder"
        assert disaster_responder.name == "Disaster Responder"
        assert "emergency_response" in disaster_responder.specialization
        assert "disaster_coordination" in disaster_responder.specialization
    
    @pytest.mark.asyncio
    async def test_disaster_types(self, disaster_responder):
        """Test disaster types."""
        expected_disasters = ["earthquake", "flood", "wildfire", "hurricane"]
        
        for disaster in expected_disasters:
            assert disaster in disaster_responder.disaster_types

@pytest.mark.ai
class TestSwarmsOrchestrator:
    """Test cases for Swarms AI orchestrator."""
    
    @pytest.fixture
    async def swarms_orchestrator(self):
        """Create a Swarms orchestrator instance."""
        orchestrator = SwarmsOrchestrator()
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, swarms_orchestrator):
        """Test orchestrator initialization."""
        assert swarms_orchestrator is not None
        assert hasattr(swarms_orchestrator, 'agents')
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, swarms_orchestrator):
        """Test agent coordination functionality."""
        # Test that orchestrator can coordinate agents
        assert hasattr(swarms_orchestrator, 'coordinate_agents')
        
        # Test agent assignment
        mission = Mission(
            name="Test Mission",
            description="Test mission description",
            mission_type=MissionType.ENVIRONMENTAL_MONITORING,
            priority=MissionPriority.HIGH,
            target_location={
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 100
            },
            required_capabilities=["optical_imaging"],
            estimated_duration=3600,
            reward_amount=1000
        )
        
        # This should not raise an exception
        await swarms_orchestrator.coordinate_agents(mission)
    
    @pytest.mark.asyncio
    async def test_swarm_status(self, swarms_orchestrator):
        """Test getting swarm status."""
        status = await swarms_orchestrator.get_swarm_status()
        
        assert isinstance(status, dict)
        assert "total_agents" in status
        assert "active_agents" in status
        assert "swarm_health" in status

@pytest.mark.ai
class TestOrchestratorAgent:
    """Test cases for main orchestrator agent."""
    
    @pytest.fixture
    async def orchestrator_agent(self, mock_solana_client, mock_swarms_orchestrator):
        """Create an orchestrator agent instance."""
        orchestrator = OrchestratorAgent(mock_solana_client, mock_swarms_orchestrator)
        await orchestrator.start()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_start(self, orchestrator_agent):
        """Test orchestrator startup."""
        assert orchestrator_agent.is_running is True
    
    @pytest.mark.asyncio
    async def test_mission_processing(self, orchestrator_agent):
        """Test mission processing."""
        mission = Mission(
            name="Test Mission",
            description="Test mission description",
            mission_type=MissionType.ENVIRONMENTAL_MONITORING,
            priority=MissionPriority.HIGH,
            target_location={
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 100
            },
            required_capabilities=["optical_imaging"],
            estimated_duration=3600,
            reward_amount=1000
        )
        
        # Test mission processing
        result = await orchestrator_agent.process_mission(mission)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_stop(self, orchestrator_agent):
        """Test orchestrator shutdown."""
        await orchestrator_agent.stop()
        assert orchestrator_agent.is_running is False

@pytest.mark.ai
class TestAgentIntegration:
    """Integration tests for agent system."""
    
    @pytest.mark.asyncio
    async def test_agent_swarm_coordination(self):
        """Test coordination between multiple agents."""
        # Create multiple agents
        forest_guardian = ForestGuardian()
        ice_sentinel = IceSentinel()
        storm_tracker = StormTracker()
        
        # Initialize agents
        await forest_guardian.initialize()
        await ice_sentinel.initialize()
        await storm_tracker.initialize()
        
        # Verify all agents are online
        assert forest_guardian.status == AgentStatus.ONLINE
        assert ice_sentinel.status == AgentStatus.ONLINE
        assert storm_tracker.status == AgentStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_agent_capability_matching(self):
        """Test agent capability matching for missions."""
        forest_guardian = ForestGuardian()
        ice_sentinel = IceSentinel()
        
        # Test mission requiring forest monitoring capabilities
        forest_mission = Mission(
            name="Forest Monitoring",
            description="Monitor forest health",
            mission_type=MissionType.ENVIRONMENTAL_MONITORING,
            priority=MissionPriority.MEDIUM,
            target_location={"latitude": 0, "longitude": 0, "radius": 100},
            required_capabilities=["deforestation_detection"],
            estimated_duration=1800,
            reward_amount=500
        )
        
        # Forest Guardian should be suitable for this mission
        assert "deforestation_detection" in forest_guardian.capabilities
        
        # Ice Sentinel should not be suitable
        assert "deforestation_detection" not in ice_sentinel.capabilities
    
    @pytest.mark.asyncio
    async def test_agent_performance_tracking(self):
        """Test agent performance tracking."""
        forest_guardian = ForestGuardian()
        
        # Simulate mission execution
        mission = Mission(
            name="Test Mission",
            description="Test mission",
            mission_type=MissionType.ENVIRONMENTAL_MONITORING,
            priority=MissionPriority.LOW,
            target_location={"latitude": 0, "longitude": 0, "radius": 100},
            required_capabilities=["optical_imaging"],
            estimated_duration=600,
            reward_amount=100
        )
        
        # Execute mission
        result = await forest_guardian.execute_mission(mission)
        
        # Verify performance metrics are updated
        assert forest_guardian.performance_metrics is not None
        assert "missions_completed" in forest_guardian.performance_metrics
        assert "success_rate" in forest_guardian.performance_metrics
