import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  MapPin, 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Target,
  Activity,
  Database,
  ExternalLink
} from 'lucide-react';
import { Mission, MissionStatus, Priority } from '../../types';

interface MissionViewerProps {
  mission: Mission | null;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const MissionViewer: React.FC<MissionViewerProps> = ({
  mission,
  isOpen,
  onClose,
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(false);

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
      case 'pending': return <Clock className="w-5 h-5" />;
      case 'active': return <Activity className="w-5 h-5" />;
      case 'completed': return <CheckCircle className="w-5 h-5" />;
      case 'failed': return <XCircle className="w-5 h-5" />;
      case 'verified': return <CheckCircle className="w-5 h-5" />;
      default: return <AlertCircle className="w-5 h-5" />;
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
  const formatMissionType = (type: string): string => {
    return type.replace('_', ' ').toUpperCase();
  };

  // Format date
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format coordinates
  const formatCoordinates = (lat: number, lng: number): string => {
    return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
  };

  // Handle close
  const handleClose = () => {
    onClose();
  };

  // Handle key press
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyPress);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [isOpen]);

  if (!mission) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center ${className}`}
          onClick={handleClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="holo-panel rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto custom-scrollbar"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Target className="w-6 h-6 text-cyan-400" />
                <h2 className="text-2xl font-mono text-cyan-400">
                  {mission.name}
                </h2>
              </div>
              <button
                onClick={handleClose}
                className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mission Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column - Basic Info */}
              <div className="space-y-4">
                <div className="holo-panel p-4 rounded">
                  <h3 className="text-lg font-mono text-white mb-3">Mission Details</h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white font-mono">
                        {formatMissionType(mission.type)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Priority:</span>
                      <span className={`font-mono ${getPriorityColor(mission.priority)}`}>
                        {mission.priority.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Status:</span>
                      <div className={`flex items-center gap-2 ${getStatusColor(mission.status)}`}>
                        {getStatusIcon(mission.status)}
                        <span className="font-mono">
                          {mission.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Created:</span>
                      <span className="text-white font-mono text-sm">
                        {formatDate(mission.created_at)}
                      </span>
                    </div>
                    
                    {mission.updated_at && (
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Updated:</span>
                        <span className="text-white font-mono text-sm">
                          {formatDate(mission.updated_at)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Target Area */}
                <div className="holo-panel p-4 rounded">
                  <h3 className="text-lg font-mono text-white mb-3">Target Area</h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-400" />
                      <span className="text-white font-mono">
                        {formatCoordinates(mission.target_area.latitude, mission.target_area.longitude)}
                      </span>
                    </div>
                    
                    {mission.target_area.radius_km && (
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Radius:</span>
                        <span className="text-white font-mono">
                          {mission.target_area.radius_km} km
                        </span>
                      </div>
                    )}
                    
                    {mission.target_area.description && (
                      <div>
                        <span className="text-gray-400">Description:</span>
                        <p className="text-white text-sm mt-1">
                          {mission.target_area.description}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column - Agents & Results */}
              <div className="space-y-4">
                {/* Assigned Agents */}
                <div className="holo-panel p-4 rounded">
                  <h3 className="text-lg font-mono text-white mb-3">Assigned Agents</h3>
                  
                  {mission.assigned_agents.length > 0 ? (
                    <div className="space-y-2">
                      {mission.assigned_agents.map((agentId, index) => (
                        <div key={agentId} className="flex items-center gap-2">
                          <Users className="w-4 h-4 text-purple-400" />
                          <span className="text-white font-mono text-sm">
                            Agent {index + 1}: {agentId}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-400 text-sm">No agents assigned</div>
                  )}
                </div>

                {/* Mission Results */}
                {mission.results && (
                  <div className="holo-panel p-4 rounded">
                    <h3 className="text-lg font-mono text-white mb-3">Mission Results</h3>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Confidence:</span>
                        <span className="text-green-400 font-mono">
                          {(mission.results.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Anomaly Detected:</span>
                        <span className={mission.results.anomaly_detected ? 'text-red-400' : 'text-green-400'}>
                          {mission.results.anomaly_detected ? 'YES' : 'NO'}
                        </span>
                      </div>
                      
                      {mission.results.risk_level && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Risk Level:</span>
                          <span className="text-orange-400 font-mono">
                            {mission.results.risk_level.toUpperCase()}
                          </span>
                        </div>
                      )}
                      
                      {mission.results.data_hash && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Data Hash:</span>
                          <div className="flex items-center gap-2">
                            <Database className="w-4 h-4 text-cyan-400" />
                            <span className="text-cyan-400 font-mono text-xs">
                              {mission.results.data_hash.substring(0, 16)}...
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {mission.results.analysis_summary && (
                        <div>
                          <span className="text-gray-400">Analysis:</span>
                          <p className="text-white text-sm mt-1">
                            {mission.results.analysis_summary}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Blockchain Info */}
                {mission.blockchain_tx_id && (
                  <div className="holo-panel p-4 rounded">
                    <h3 className="text-lg font-mono text-white mb-3">Blockchain Record</h3>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Transaction ID:</span>
                        <div className="flex items-center gap-2">
                          <Database className="w-4 h-4 text-green-400" />
                          <span className="text-green-400 font-mono text-xs">
                            {mission.blockchain_tx_id.substring(0, 16)}...
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Verified:</span>
                        <span className={mission.verified ? 'text-green-400' : 'text-yellow-400'}>
                          {mission.verified ? 'YES' : 'PENDING'}
                        </span>
                      </div>
                      
                      {mission.verified_at && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Verified At:</span>
                          <span className="text-white font-mono text-sm">
                            {formatDate(mission.verified_at)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-cyan-500/30">
              {mission.results?.report_url && (
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                  <ExternalLink className="w-4 h-4" />
                  View Report
                </button>
              )}
              
              <button
                onClick={handleClose}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default MissionViewer;
