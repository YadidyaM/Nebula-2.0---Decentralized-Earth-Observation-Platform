import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Radio, 
  Wifi, 
  WifiOff, 
  Clock, 
  Activity,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { Mission } from '../../types';
import { useWebSocket } from '../../hooks';

interface MissionControlHeaderProps {
  isConnected?: boolean;
  missionCount?: number;
  activeMission?: Mission | null;
  className?: string;
}

const MissionControlHeader: React.FC<MissionControlHeaderProps> = ({
  isConnected = false,
  missionCount = 0,
  activeMission = null,
  className = ''
}) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemHealth, setSystemHealth] = useState<'healthy' | 'warning' | 'critical'>('healthy');
  const [alertsCount, setAlertsCount] = useState(0);

  const { connectionState, reconnectAttempts } = useWebSocket();

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Monitor system health
  useEffect(() => {
    // This would normally check various system metrics
    // For now, we'll simulate based on connection status
    if (!isConnected) {
      setSystemHealth('critical');
    } else if (reconnectAttempts > 0) {
      setSystemHealth('warning');
    } else {
      setSystemHealth('healthy');
    }
  }, [isConnected, reconnectAttempts]);

  // Format time
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Format date
  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Get connection status color
  const getConnectionColor = (): string => {
    if (isConnected) return 'text-green-400';
    if (reconnectAttempts > 0) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Get system health color
  const getSystemHealthColor = (): string => {
    switch (systemHealth) {
      case 'healthy': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Get system health icon
  const getSystemHealthIcon = () => {
    switch (systemHealth) {
      case 'healthy': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      className={`fixed top-0 left-0 right-0 z-40 h-16 bg-black/80 backdrop-blur-sm border-b border-cyan-500/30 ${className}`}
    >
      <div className="flex items-center justify-between h-full px-6">
        {/* Left Section - Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Radio className="w-6 h-6 text-cyan-400" />
            <div className="text-xl font-display font-bold text-cyan-400">
              NEBULA PROTOCOL
            </div>
          </div>
          
          <div className="text-sm text-gray-400 font-mono">
            MISSION CONTROL CENTER
          </div>
        </div>

        {/* Center Section - Active Mission */}
        <div className="flex-1 flex justify-center">
          {activeMission ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-3 px-4 py-2 bg-slate-800/50 rounded-lg border border-cyan-500/30"
            >
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <div className="text-sm">
                <span className="text-gray-400">ACTIVE:</span>
                <span className="text-white ml-2 font-mono">{activeMission.name}</span>
              </div>
              <div className="text-xs text-gray-500">
                {activeMission.type.toUpperCase()}
              </div>
            </motion.div>
          ) : (
            <div className="text-sm text-gray-500 font-mono">
              NO ACTIVE MISSION
            </div>
          )}
        </div>

        {/* Right Section - Status Indicators */}
        <div className="flex items-center gap-6">
          {/* Mission Count */}
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <div className="text-sm">
              <span className="text-gray-400">MISSIONS:</span>
              <span className="text-white ml-1 font-mono">{missionCount}</span>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-400" />
            )}
            <div className="text-sm">
              <span className="text-gray-400">LINK:</span>
              <span className={`ml-1 font-mono ${getConnectionColor()}`}>
                {connectionState.toUpperCase()}
              </span>
            </div>
            {reconnectAttempts > 0 && (
              <div className="text-xs text-yellow-400">
                ({reconnectAttempts})
              </div>
            )}
          </div>

          {/* System Health */}
          <div className="flex items-center gap-2">
            <div className={getSystemHealthColor()}>
              {getSystemHealthIcon()}
            </div>
            <div className="text-sm">
              <span className="text-gray-400">SYS:</span>
              <span className={`ml-1 font-mono ${getSystemHealthColor()}`}>
                {systemHealth.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Alerts */}
          {alertsCount > 0 && (
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
              <div className="text-sm">
                <span className="text-gray-400">ALERTS:</span>
                <span className="text-red-400 ml-1 font-mono">{alertsCount}</span>
              </div>
            </div>
          )}

          {/* Time */}
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <div className="text-sm font-mono">
              <div className="text-white">{formatTime(currentTime)}</div>
              <div className="text-xs text-gray-500">{formatDate(currentTime)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Scan Line Effect */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="scan-lines h-full"></div>
      </div>
    </motion.div>
  );
};

export default MissionControlHeader;
