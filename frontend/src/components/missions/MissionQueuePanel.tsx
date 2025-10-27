import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Zap, 
  Target, 
  Clock, 
  MapPin, 
  Users, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Filter,
  Search
} from 'lucide-react';
import { Mission, MissionType, MissionStatus, Priority } from '../../types';
import { useMissions } from '../../hooks';

interface MissionQueuePanelProps {
  missions?: Mission[];
  onMissionSelect?: (mission: Mission) => void;
  className?: string;
}

const MissionQueuePanel: React.FC<MissionQueuePanelProps> = ({
  missions: propMissions,
  onMissionSelect,
  className = ''
}) => {
  const [autoQueueEnabled, setAutoQueueEnabled] = useState(false);
  const [filterStatus, setFilterStatus] = useState<MissionStatus | 'all'>('all');
  const [filterType, setFilterType] = useState<MissionType | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Use missions hook if no missions provided
  const { missions: hookMissions, createMission, isLoading } = useMissions();
  const missions = propMissions || hookMissions;

  // Filter missions
  const filteredMissions = missions.filter(mission => {
    const matchesStatus = filterStatus === 'all' || mission.status === filterStatus;
    const matchesType = filterType === 'all' || mission.type === filterType;
    const matchesSearch = searchQuery === '' || 
      mission.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mission.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesStatus && matchesType && matchesSearch;
  });

  // Get status color
  const getStatusColor = (status: MissionStatus): string => {
    switch (status) {
      case 'pending': return 'text-yellow-400';
      case 'active': return 'text-green-400';
      case 'completed': return 'text-blue-400';
      case 'failed': return 'text-red-400';
      case 'verified': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  // Get status icon
  const getStatusIcon = (status: MissionStatus) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'active': return <Play className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      case 'verified': return <CheckCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  // Get priority color
  const getPriorityColor = (priority: Priority): string => {
    switch (priority) {
      case 'low': return 'text-gray-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-orange-400';
      case 'critical': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Format mission type
  const formatMissionType = (type: MissionType): string => {
    return type.replace('_', ' ').toUpperCase();
  };

  // Handle new mission creation
  const handleNewMission = useCallback(async () => {
    const newMission = {
      name: `Mission ${Date.now()}`,
      type: 'forestry' as MissionType,
      priority: 'medium' as Priority,
      target_area: {
        latitude: 0,
        longitude: 0,
        radius_km: 10,
        description: 'Manual mission target'
      }
    };

    try {
      await createMission(newMission);
    } catch (error) {
      console.error('Failed to create mission:', error);
    }
  }, [createMission]);

  // Handle mission click
  const handleMissionClick = useCallback((mission: Mission) => {
    if (onMissionSelect) {
      onMissionSelect(mission);
    }
  }, [onMissionSelect]);

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-mono text-cyan-400">MISSION QUEUE</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={handleNewMission}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            New Mission
          </button>
          
          <button
            onClick={() => setAutoQueueEnabled(!autoQueueEnabled)}
            className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              autoQueueEnabled
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
            }`}
          >
            <Zap className="w-4 h-4" />
            Auto Queue
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search missions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800/80 text-white pl-10 pr-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono placeholder-gray-400"
          />
        </div>

        {/* Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 space-y-2"
            >
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as MissionStatus | 'all')}
                  className="flex-1 bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="verified">Verified</option>
                </select>
                
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as MissionType | 'all')}
                  className="flex-1 bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  <option value="all">All Types</option>
                  <option value="forestry">Forestry</option>
                  <option value="cryosphere">Cryosphere</option>
                  <option value="disaster_management">Disaster Management</option>
                  <option value="security">Security</option>
                  <option value="weather">Weather</option>
                  <option value="hydrology">Hydrology</option>
                  <option value="urban_infrastructure">Urban Infrastructure</option>
                  <option value="land_monitoring">Land Monitoring</option>
                </select>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mission List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="holo-spinner"></div>
          </div>
        ) : filteredMissions.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No missions found</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filteredMissions.map((mission) => (
                <motion.div
                  key={mission.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  onClick={() => handleMissionClick(mission)}
                  className="holo-panel p-4 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-sm font-mono text-white mb-1">
                        {mission.name}
                      </h3>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-gray-400">
                          {formatMissionType(mission.type)}
                        </span>
                        <span className={`${getPriorityColor(mission.priority)}`}>
                          {mission.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    
                    <div className={`flex items-center gap-1 ${getStatusColor(mission.status)}`}>
                      {getStatusIcon(mission.status)}
                      <span className="text-xs font-mono">
                        {mission.status.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      <span>
                        {mission.target_area.latitude.toFixed(2)}, {mission.target_area.longitude.toFixed(2)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      <span>{mission.assigned_agents.length} agents</span>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>
                        {new Date(mission.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {mission.results && (
                    <div className="mt-2 pt-2 border-t border-gray-700">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">Confidence:</span>
                        <span className="text-green-400">
                          {(mission.results.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      {mission.results.anomaly_detected && (
                        <div className="text-xs text-red-400 mt-1">
                          ⚠️ Anomaly Detected
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-cyan-500/30">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Total: {missions.length}</span>
          <span>Filtered: {filteredMissions.length}</span>
          {autoQueueEnabled && (
            <span className="text-green-400 animate-pulse">AUTO QUEUE ACTIVE</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MissionQueuePanel;
