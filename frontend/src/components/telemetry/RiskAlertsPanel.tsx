import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  Filter, 
  RefreshCw, 
  MapPin, 
  Clock, 
  Eye,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  Bell,
  BellOff
} from 'lucide-react';
import { RiskAlert, RiskLevel, RiskType } from '../../types';

interface RiskAlertsPanelProps {
  alerts?: RiskAlert[];
  onAlertClick?: (alert: RiskAlert) => void;
  className?: string;
}

const RiskAlertsPanel: React.FC<RiskAlertsPanelProps> = ({
  alerts: propAlerts,
  onAlertClick,
  className = ''
}) => {
  const [filterLevel, setFilterLevel] = useState<RiskLevel | 'all'>('all');
  const [filterType, setFilterType] = useState<RiskType | 'all'>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState<Set<string>>(new Set());

  // Mock alerts data for demonstration
  const mockAlerts: RiskAlert[] = [
    {
      id: '1',
      type: 'wildfire',
      level: 'high',
      location: {
        lat: 34.0522,
        lng: -118.2437,
        radius: 50
      },
      description: 'Large wildfire detected near Los Angeles with rapid spread potential',
      timestamp: new Date().toISOString(),
      source_mission_id: 'mission-001',
      affected_area_sq_km: 1250,
      confidence_score: 0.89
    },
    {
      id: '2',
      type: 'flood',
      level: 'critical',
      location: {
        lat: 29.7604,
        lng: -95.3698,
        radius: 100
      },
      description: 'Severe flooding in Houston area with multiple evacuation zones',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      source_mission_id: 'mission-002',
      affected_area_sq_km: 2500,
      confidence_score: 0.95
    },
    {
      id: '3',
      type: 'deforestation',
      level: 'medium',
      location: {
        lat: -3.465,
        lng: -62.215,
        radius: 75
      },
      description: 'Deforestation activity detected in Amazon rainforest region',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      source_mission_id: 'mission-003',
      affected_area_sq_km: 800,
      confidence_score: 0.72
    },
    {
      id: '4',
      type: 'storm',
      level: 'high',
      location: {
        lat: 25.7617,
        lng: -80.1918,
        radius: 150
      },
      description: 'Tropical storm approaching Miami with hurricane-force winds',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      source_mission_id: 'mission-004',
      affected_area_sq_km: 3000,
      confidence_score: 0.91
    }
  ];

  const alerts = propAlerts || mockAlerts;

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    const matchesLevel = filterLevel === 'all' || alert.level === filterLevel;
    const matchesType = filterType === 'all' || alert.type === filterType;
    return matchesLevel && matchesType;
  });

  // Get risk level color
  const getRiskLevelColor = (level: RiskLevel): string => {
    switch (level) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-orange-400';
      case 'critical': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Get risk level background color
  const getRiskLevelBackgroundColor = (level: RiskLevel): string => {
    switch (level) {
      case 'low': return 'bg-green-500/20';
      case 'medium': return 'bg-yellow-500/20';
      case 'high': return 'bg-orange-500/20';
      case 'critical': return 'bg-red-500/20';
      default: return 'bg-gray-500/20';
    }
  };

  // Get risk type color
  const getRiskTypeColor = (type: RiskType): string => {
    switch (type) {
      case 'wildfire': return 'text-red-400';
      case 'flood': return 'text-blue-400';
      case 'drought': return 'text-yellow-400';
      case 'deforestation': return 'text-green-400';
      case 'storm': return 'text-purple-400';
      case 'pollution': return 'text-gray-400';
      case 'security': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  // Get risk type icon
  const getRiskTypeIcon = (type: RiskType) => {
    switch (type) {
      case 'wildfire': return <TrendingUp className="w-4 h-4" />;
      case 'flood': return <TrendingDown className="w-4 h-4" />;
      case 'drought': return <Sun className="w-4 h-4" />;
      case 'deforestation': return <TreePine className="w-4 h-4" />;
      case 'storm': return <Wind className="w-4 h-4" />;
      case 'pollution': return <AlertTriangle className="w-4 h-4" />;
      case 'security': return <Shield className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  // Format risk type
  const formatRiskType = (type: RiskType): string => {
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

  // Handle alert click
  const handleAlertClick = useCallback((alert: RiskAlert) => {
    if (onAlertClick) {
      onAlertClick(alert);
    }
  }, [onAlertClick]);

  // Handle acknowledge alert
  const handleAcknowledgeAlert = useCallback((alertId: string) => {
    setAcknowledgedAlerts(prev => new Set([...prev, alertId]));
  }, []);

  // Get risk type options
  const riskTypes: { value: RiskType | 'all'; label: string }[] = [
    { value: 'all', label: 'All Types' },
    { value: 'wildfire', label: 'Wildfire' },
    { value: 'flood', label: 'Flood' },
    { value: 'drought', label: 'Drought' },
    { value: 'deforestation', label: 'Deforestation' },
    { value: 'storm', label: 'Storm' },
    { value: 'pollution', label: 'Pollution' },
    { value: 'security', label: 'Security' }
  ];

  // Get risk level options
  const riskLevels: { value: RiskLevel | 'all'; label: string }[] = [
    { value: 'all', label: 'All Levels' },
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h2 className="text-lg font-mono text-cyan-400">RISK ALERTS</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-2 rounded transition-colors ${
                autoRefresh
                  ? 'text-green-400 hover:text-green-300'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {autoRefresh ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4"
            >
              <div className="grid grid-cols-2 gap-2">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as RiskType | 'all')}
                  className="bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  {riskTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                
                <select
                  value={filterLevel}
                  onChange={(e) => setFilterLevel(e.target.value as RiskLevel | 'all')}
                  className="bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  {riskLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-red-400 font-mono text-lg">
              {alerts.filter(a => a.level === 'critical').length}
            </div>
            <div className="text-gray-400">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-orange-400 font-mono text-lg">
              {alerts.filter(a => a.level === 'high').length}
            </div>
            <div className="text-gray-400">High</div>
          </div>
          <div className="text-center">
            <div className="text-yellow-400 font-mono text-lg">
              {alerts.filter(a => a.level === 'medium').length}
            </div>
            <div className="text-gray-400">Medium</div>
          </div>
          <div className="text-center">
            <div className="text-green-400 font-mono text-lg">
              {alerts.filter(a => a.level === 'low').length}
            </div>
            <div className="text-gray-400">Low</div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {filteredAlerts.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No alerts found</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filteredAlerts.map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  onClick={() => handleAlertClick(alert)}
                  className={`holo-panel p-4 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300 border-2 ${
                    acknowledgedAlerts.has(alert.id) ? 'border-gray-500 opacity-60' : 'border-red-500/50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`flex items-center gap-1 ${getRiskTypeColor(alert.type)}`}>
                          {getRiskTypeIcon(alert.type)}
                          <span className="text-sm font-mono">
                            {formatRiskType(alert.type)}
                          </span>
                        </div>
                        
                        <div className={`px-2 py-1 rounded text-xs font-mono ${getRiskLevelBackgroundColor(alert.level)} ${getRiskLevelColor(alert.level)}`}>
                          {alert.level.toUpperCase()}
                        </div>
                      </div>
                      
                      <div className="text-sm text-white mb-2">
                        {alert.description}
                      </div>
                      
                      <div className="text-xs text-gray-400">
                        {formatDate(alert.timestamp)}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-xs text-gray-400">
                        Confidence: {(alert.confidence_score * 100).toFixed(1)}%
                      </div>
                      {alert.affected_area_sq_km && (
                        <div className="text-xs text-white font-mono">
                          {alert.affected_area_sq_km} km²
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs">
                      <MapPin className="w-3 h-3 text-blue-400" />
                      <span className="text-gray-400">Location:</span>
                      <span className="text-white font-mono">
                        {formatCoordinates(alert.location.lat, alert.location.lng)}
                      </span>
                      {alert.location.radius && (
                        <span className="text-gray-400">
                          (Radius: {alert.location.radius} km)
                        </span>
                      )}
                    </div>
                    
                    {alert.source_mission_id && (
                      <div className="flex items-center gap-2 text-xs">
                        <Eye className="w-3 h-3 text-purple-400" />
                        <span className="text-gray-400">Source Mission:</span>
                        <span className="text-white font-mono">
                          {alert.source_mission_id}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-end gap-2 mt-3 pt-3 border-t border-gray-700">
                    {!acknowledgedAlerts.has(alert.id) && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAcknowledgeAlert(alert.id);
                        }}
                        className="flex items-center gap-1 px-3 py-1 text-xs font-mono rounded bg-green-600/80 hover:bg-green-500/80 text-white border border-green-400/50 transition-all duration-300"
                      >
                        <CheckCircle className="w-3 h-3" />
                        ACKNOWLEDGE
                      </button>
                    )}
                    
                    {acknowledgedAlerts.has(alert.id) && (
                      <div className="flex items-center gap-1 text-xs text-green-400">
                        <CheckCircle className="w-3 h-3" />
                        <span className="font-mono">ACKNOWLEDGED</span>
                      </div>
                    )}
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
          <span>Total Alerts: {alerts.length}</span>
          <span>Filtered: {filteredAlerts.length}</span>
          <div className="flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Real-time Monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAlertsPanel;
