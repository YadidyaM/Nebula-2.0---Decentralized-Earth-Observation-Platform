#Agent_Factor_monitor
from app.agents.base_agent import BaseAgent
from app.agents.specialized.forest_guardian import ForestGuardianAgent
from app.agents.specialized.ice_sentinel import IceSentinelAgent
from app.agents.specialized.storm_tracker import StormTrackerAgent
from app.agents.specialized.urban_monitor import UrbanMonitorAgent, WaterWatcherAgent, SecuritySentinelAgent
from app.agents.specialized.land_surveyor import LandSurveyorAgent, DisasterResponderAgent
from app.models.agent import AgentType
from typing import Dict, List, Type
import logging

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory class for creating specialized agents"""
    
    _agent_classes: Dict[AgentType, Type[BaseAgent]] = {
        AgentType.FOREST_GUARDIAN: ForestGuardianAgent,
        AgentType.ICE_SENTINEL: IceSentinelAgent,
        AgentType.STORM_TRACKER: StormTrackerAgent,
        AgentType.URBAN_MONITOR: UrbanMonitorAgent,
        AgentType.WATER_WATCHER: WaterWatcherAgent,
        AgentType.SECURITY_SENTINEL: SecuritySentinelAgent,
        AgentType.LAND_SURVEYOR: LandSurveyorAgent,
        AgentType.DISASTER_RESPONDER: DisasterResponderAgent,
    }
    
    @classmethod
    def create_agent(cls, agent_type: AgentType, wallet_address: str) -> BaseAgent:
        """Create a specialized agent instance"""
        if agent_type not in cls._agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_classes[agent_type]
        agent = agent_class(wallet_address)
        
        logger.info(f"Created {agent_type} agent with wallet {wallet_address}")
        return agent
    
    @classmethod
    def get_available_agent_types(cls) -> List[AgentType]:
        """Get list of available agent types"""
        return list(cls._agent_classes.keys())
    
    @classmethod
    def register_agent_type(cls, agent_type: AgentType, agent_class: Type[BaseAgent]):
        """Register a new agent type"""
        cls._agent_classes[agent_type] = agent_class
        logger.info(f"Registered new agent type: {agent_type}")
    
    @classmethod
    def create_all_agents(cls, wallet_addresses: Dict[AgentType, str]) -> Dict[AgentType, BaseAgent]:
        """Create all available agents with their wallet addresses"""
        agents = {}
        
        for agent_type, wallet_address in wallet_addresses.items():
            try:
                agent = cls.create_agent(agent_type, wallet_address)
                agents[agent_type] = agent
            except Exception as e:
                logger.error(f"Failed to create {agent_type} agent: {e}")
        
        logger.info(f"Created {len(agents)} agents")
        return agents
