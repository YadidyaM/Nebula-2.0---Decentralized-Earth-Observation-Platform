import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Play, 
  Pause, 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Target,
  Zap,
  Settings
} from 'lucide-react';
import { Agent, AgentStatus, AgentType, AgentRarity } from '../../types';
import { useAgents } from '../../hooks';

interface AgentStatusGridProps {
  agents?: Agent[];
  onAgentClick?: (agent: Agent) => void;
  className?: string;
}

const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({
  agents: propAgents,
  onAgentClick,
  className = ''
}) => {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Use agents hook if no agents provided
  const { agents: hookAgents, activateAgent, deactivateAgent, isLoading } = useAgents();
  const agents = propAgents || hookAgents;

  // Get status color
  const getStatusColor = (status: AgentStatus): string => {
    switch (status) {
      case 'idle': return 'text-yellow-400';
      case 'active': return 'text-green-400';
      case 'maintenance': return 'text-blue-400';
      case 'offline': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Get status icon
  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case 'idle': return <Clock className="w-4 h-4" />;
      case 'active': return <Activity className="w-4 h-4" />;
      case 'maintenance': return <Settings className="w-4 h-4" />;
      case 'offline': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  // Get rarity color
  const getRarityColor = (rarity: AgentRarity): string => {
    switch (rarity) {
      case 'common': return 'text-gray-400';
      case 'rare': return 'text-blue-400';
      case 'epic': return 'text-purple-400';
      case 'legendary': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  // Get rarity border color
  const getRarityBorderColor = (rarity: AgentRarity): string => {
    switch (rarity) {
      case 'common': return 'border-gray-500';
      case 'rare': return 'border-blue-500';
      case 'epic': return 'border-purple-500';
      case 'legendary': return 'border-yellow-500';
      default: return 'border-gray-500';
    }
  };

  // Handle agent click
  const handleAgentClick = useCallback((agent: Agent) => {
    setSelectedAgent(agent);
    if (onAgentClick) {
      onAgentClick(agent);
    }
  }, [onAgentClick]);

  // Handle agent activation
  const handleActivateAgent = useCallback(async (agentId: string) => {
    try {
      await activateAgent(agentId);
    } catch (error) {
      console.error('Failed to activate agent:', error);
    }
  }, [activateAgent]);

  // Handle agent deactivation
  const handleDeactivateAgent = useCallback(async (agentId: string) => {
    try {
      await deactivateAgent(agentId);
    } catch (error) {
      console.error('Failed to deactivate agent:', error);
    }
  }, [deactivateAgent]);

  // Format agent type
  const formatAgentType = (type: AgentType): string => {
    return type.replace(/([A-Z])/g, ' $1').trim();
  };

  // Format performance percentage
  const formatPerformance = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-mono text-cyan-400">AGENT STATUS</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-green-400 font-mono text-lg">
              {agents.filter(a => a.status === 'active').length}
            </div>
            <div className="text-gray-400">Active</div>
          </div>
          <div className="text-center">
            <div className="text-yellow-400 font-mono text-lg">
              {agents.filter(a => a.status === 'idle').length}
            </div>
            <div className="text-gray-400">Idle</div>
          </div>
          <div className="text-center">
            <div className="text-blue-400 font-mono text-lg">
              {agents.filter(a => a.status === 'maintenance').length}
            </div>
            <div className="text-gray-400">Maintenance</div>
          </div>
          <div className="text-center">
            <div className="text-red-400 font-mono text-lg">
              {agents.filter(a => a.status === 'offline').length}
            </div>
            <div className="text-gray-400">Offline</div>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="holo-spinner"></div>
          </div>
        ) : agents.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No agents found</div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {agents.map((agent) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  onClick={() => handleAgentClick(agent)}
                  className={`holo-panel p-4 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300 border-2 ${getRarityBorderColor(agent.rarity)}`}
                >
                  {/* Agent Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-sm font-mono text-white mb-1">
                        {agent.name}
                      </h3>
                      <div className="text-xs text-gray-400">
                        {formatAgentType(agent.type)}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <div className={`text-xs font-mono ${getRarityColor(agent.rarity)}`}>
                        {agent.rarity.toUpperCase()}
                      </div>
                      <div className={`flex items-center gap-1 ${getStatusColor(agent.status)}`}>
                        {getStatusIcon(agent.status)}
                      </div>
                    </div>
                  </div>

                  {/* Agent Status */}
                  <div className="flex items-center justify-between mb-3">
                    <div className={`flex items-center gap-2 ${getStatusColor(agent.status)}`}>
                      {getStatusIcon(agent.status)}
                      <span className="text-xs font-mono">
                        {agent.status.toUpperCase()}
                      </span>
                    </div>
                    
                    {agent.current_mission_id && (
                      <div className="flex items-center gap-1 text-xs text-blue-400">
                        <Target className="w-3 h-3" />
                        <span>MISSION</span>
                      </div>
                    )}
                  </div>

                  {/* Performance Metrics */}
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Missions:</span>
                      <span className="text-white font-mono">
                        {agent.performance.missions_completed}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Success Rate:</span>
                      <span className="text-green-400 font-mono">
                        {formatPerformance(agent.performance.success_rate)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Confidence:</span>
                      <span className="text-blue-400 font-mono">
                        {formatPerformance(agent.performance.average_confidence)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Uptime:</span>
                      <span className="text-purple-400 font-mono">
                        {formatPerformance(agent.performance.uptime_percentage)}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    {agent.status === 'idle' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleActivateAgent(agent.id!);
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-xs font-mono rounded bg-green-600/80 hover:bg-green-500/80 text-white border border-green-400/50 transition-all duration-300"
                      >
                        <Play className="w-3 h-3" />
                        ACTIVATE
                      </button>
                    ) : agent.status === 'active' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeactivateAgent(agent.id!);
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-xs font-mono rounded bg-red-600/80 hover:bg-red-500/80 text-white border border-red-400/50 transition-all duration-300"
                      >
                        <Pause className="w-3 h-3" />
                        DEACTIVATE
                      </button>
                    ) : (
                      <button
                        disabled
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-xs font-mono rounded bg-gray-600/80 text-gray-400 border border-gray-500/50 cursor-not-allowed"
                      >
                        <Settings className="w-3 h-3" />
                        {agent.status.toUpperCase()}
                      </button>
                    )}
                  </div>

                  {/* Last Seen */}
                  <div className="mt-2 pt-2 border-t border-gray-700">
                    <div className="text-xs text-gray-500">
                      Last seen: {new Date(agent.last_seen).toLocaleString()}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-cyan-500/30">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Total Agents: {agents.length}</span>
          <span>Active: {agents.filter(a => a.status === 'active').length}</span>
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            <span>System Online</span>
          </div>
        </div>
      </div>

      {/* Agent Details Modal */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="holo-panel rounded-lg p-6 max-w-2xl w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-mono text-cyan-400">
                  {selectedAgent.name}
                </h3>
                <button
                  onClick={() => setSelectedAgent(null)}
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <div className="text-white font-mono">
                      {formatAgentType(selectedAgent.type)}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">Rarity:</span>
                    <div className={`font-mono ${getRarityColor(selectedAgent.rarity)}`}>
                      {selectedAgent.rarity.toUpperCase()}
                    </div>
                  </div>
                </div>
                
                <div>
                  <span className="text-gray-400">Performance:</span>
                  <div className="mt-2 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Missions Completed:</span>
                      <span className="font-mono">{selectedAgent.performance.missions_completed}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Success Rate:</span>
                      <span className="font-mono text-green-400">
                        {formatPerformance(selectedAgent.performance.success_rate)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Average Confidence:</span>
                      <span className="font-mono text-blue-400">
                        {formatPerformance(selectedAgent.performance.average_confidence)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Uptime:</span>
                      <span className="font-mono text-purple-400">
                        {formatPerformance(selectedAgent.performance.uptime_percentage)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AgentStatusGrid;
