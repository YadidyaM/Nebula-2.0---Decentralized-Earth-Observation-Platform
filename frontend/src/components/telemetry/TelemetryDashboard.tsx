import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Thermometer, 
  Droplets, 
  Wind, 
  Gauge, 
  Eye,
  Filter,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { TelemetryData, RiskLevel } from '../../types';
import { useTelemetry } from '../../hooks';

interface TelemetryDashboardProps {
  telemetryData?: TelemetryData[];
  onDataPointClick?: (data: TelemetryData) => void;
  className?: string;
}

const TelemetryDashboard: React.FC<TelemetryDashboardProps> = ({
  telemetryData: propTelemetryData,
  onDataPointClick,
  className = ''
}) => {
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('24h');
  const [showFilters, setShowFilters] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Use telemetry hook if no data provided
  const { telemetryData: hookTelemetryData, isLoading, fetchTelemetry } = useTelemetry(selectedAgent === 'all' ? undefined : selectedAgent);
  const telemetryData = propTelemetryData || hookTelemetryData;

  // Filter data by time range
  const getFilteredData = useCallback(() => {
    const now = new Date();
    const timeRanges = {
      '1h': 60 * 60 * 1000,
      '6h': 6 * 60 * 60 * 1000,
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000
    };

    const cutoffTime = new Date(now.getTime() - timeRanges[timeRange]);
    return telemetryData.filter(data => new Date(data.timestamp) >= cutoffTime);
  }, [telemetryData, timeRange]);

  const filteredData = getFilteredData();

  // Calculate statistics
  const getStatistics = useCallback(() => {
    if (filteredData.length === 0) return null;

    const stats = {
      totalReadings: filteredData.length,
      avgTemperature: 0,
      avgHumidity: 0,
      avgPressure: 0,
      avgWindSpeed: 0,
      avgAirQuality: 0,
      riskLevels: {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0
      }
    };

    let tempSum = 0, humiditySum = 0, pressureSum = 0, windSum = 0, airQualitySum = 0;
    let tempCount = 0, humidityCount = 0, pressureCount = 0, windCount = 0, airQualityCount = 0;

    filteredData.forEach(data => {
      if (data.environmental_metrics) {
        const metrics = data.environmental_metrics;
        
        if (metrics.temperature !== undefined) {
          tempSum += metrics.temperature;
          tempCount++;
        }
        if (metrics.humidity !== undefined) {
          humiditySum += metrics.humidity;
          humidityCount++;
        }
        if (metrics.pressure !== undefined) {
          pressureSum += metrics.pressure;
          pressureCount++;
        }
        if (metrics.wind_speed !== undefined) {
          windSum += metrics.wind_speed;
          windCount++;
        }
        if (metrics.air_quality_index !== undefined) {
          airQualitySum += metrics.air_quality_index;
          airQualityCount++;
        }
      }
    });

    stats.avgTemperature = tempCount > 0 ? tempSum / tempCount : 0;
    stats.avgHumidity = humidityCount > 0 ? humiditySum / humidityCount : 0;
    stats.avgPressure = pressureCount > 0 ? pressureSum / pressureCount : 0;
    stats.avgWindSpeed = windCount > 0 ? windSum / windCount : 0;
    stats.avgAirQuality = airQualityCount > 0 ? airQualitySum / airQualityCount : 0;

    return stats;
  }, [filteredData]);

  const statistics = getStatistics();

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

  // Format value with unit
  const formatValue = (value: number, unit: string): string => {
    return `${value.toFixed(1)} ${unit}`;
  };

  // Handle data point click
  const handleDataPointClick = useCallback((data: TelemetryData) => {
    if (onDataPointClick) {
      onDataPointClick(data);
    }
  }, [onDataPointClick]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    fetchTelemetry();
  }, [fetchTelemetry]);

  // Mock agent options
  const agentOptions = [
    { value: 'all', label: 'All Agents' },
    { value: 'forest_guardian', label: 'Forest Guardian' },
    { value: 'ice_sentinel', label: 'Ice Sentinel' },
    { value: 'storm_tracker', label: 'Storm Tracker' },
    { value: 'water_watcher', label: 'Water Watcher' }
  ];

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-mono text-cyan-400">TELEMETRY DASHBOARD</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex gap-3 mb-4">
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="flex-1 bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
          >
            {agentOptions.map(agent => (
              <option key={agent.value} value={agent.value}>
                {agent.label}
              </option>
            ))}
          </select>
          
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as '1h' | '6h' | '24h' | '7d')}
            className="flex-1 bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-2 rounded text-sm font-mono transition-colors ${
              autoRefresh
                ? 'bg-green-600/80 text-white border border-green-400/50'
                : 'bg-gray-600/80 text-gray-300 border border-gray-500/50'
            }`}
          >
            AUTO
          </button>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="text-blue-400 font-mono text-lg">
                {statistics.totalReadings}
              </div>
              <div className="text-gray-400">Readings</div>
            </div>
            <div className="text-center">
              <div className="text-green-400 font-mono text-lg">
                {formatValue(statistics.avgTemperature, '°C')}
              </div>
              <div className="text-gray-400">Avg Temp</div>
            </div>
            <div className="text-center">
              <div className="text-blue-400 font-mono text-lg">
                {formatValue(statistics.avgHumidity, '%')}
              </div>
              <div className="text-gray-400">Avg Humidity</div>
            </div>
            <div className="text-center">
              <div className="text-purple-400 font-mono text-lg">
                {formatValue(statistics.avgAirQuality, 'AQI')}
              </div>
              <div className="text-gray-400">Avg Air Quality</div>
            </div>
          </div>
        )}
      </div>

      {/* Telemetry Data */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="holo-spinner"></div>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No telemetry data found</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filteredData.map((data) => (
                <motion.div
                  key={data.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  onClick={() => handleDataPointClick(data)}
                  className="holo-panel p-4 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-mono text-white">
                          Agent {data.agent_id}
                        </span>
                        <div className="flex items-center gap-1 text-xs text-gray-400">
                          <Eye className="w-3 h-3" />
                          <span>
                            {data.location.lat.toFixed(4)}, {data.location.lng.toFixed(4)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-xs text-gray-400">
                        {new Date(data.timestamp).toLocaleString()}
                      </div>
                    </div>
                    
                    {data.environmental_metrics && (
                      <div className="text-right">
                        <div className="text-xs text-gray-400">
                          {data.environmental_metrics.temperature !== undefined && (
                            <div className="flex items-center gap-1">
                              <Thermometer className="w-3 h-3" />
                              <span>{formatValue(data.environmental_metrics.temperature, '°C')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Environmental Metrics */}
                  {data.environmental_metrics && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                      {data.environmental_metrics.temperature !== undefined && (
                        <div className="flex items-center gap-2 text-xs">
                          <Thermometer className="w-3 h-3 text-red-400" />
                          <span className="text-gray-400">Temp:</span>
                          <span className="text-white font-mono">
                            {formatValue(data.environmental_metrics.temperature, '°C')}
                          </span>
                        </div>
                      )}
                      
                      {data.environmental_metrics.humidity !== undefined && (
                        <div className="flex items-center gap-2 text-xs">
                          <Droplets className="w-3 h-3 text-blue-400" />
                          <span className="text-gray-400">Humidity:</span>
                          <span className="text-white font-mono">
                            {formatValue(data.environmental_metrics.humidity, '%')}
                          </span>
                        </div>
                      )}
                      
                      {data.environmental_metrics.pressure !== undefined && (
                        <div className="flex items-center gap-2 text-xs">
                          <Gauge className="w-3 h-3 text-purple-400" />
                          <span className="text-gray-400">Pressure:</span>
                          <span className="text-white font-mono">
                            {formatValue(data.environmental_metrics.pressure, 'hPa')}
                          </span>
                        </div>
                      )}
                      
                      {data.environmental_metrics.wind_speed !== undefined && (
                        <div className="flex items-center gap-2 text-xs">
                          <Wind className="w-3 h-3 text-green-400" />
                          <span className="text-gray-400">Wind:</span>
                          <span className="text-white font-mono">
                            {formatValue(data.environmental_metrics.wind_speed, 'm/s')}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Additional Data */}
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                      {data.speed !== undefined && (
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3 text-yellow-400" />
                          <span className="text-gray-400">Speed:</span>
                          <span className="text-white font-mono">
                            {formatValue(data.speed, 'km/h')}
                          </span>
                        </div>
                      )}
                      
                      {data.battery_level !== undefined && (
                        <div className="flex items-center gap-1">
                          <div className={`w-2 h-2 rounded-full ${
                            data.battery_level > 50 ? 'bg-green-400' : 
                            data.battery_level > 20 ? 'bg-yellow-400' : 'bg-red-400'
                          }`} />
                          <span className="text-gray-400">Battery:</span>
                          <span className="text-white font-mono">
                            {data.battery_level}%
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {data.data_payload && (
                      <div className="text-xs text-gray-400">
                        Data: {JSON.stringify(data.data_payload).substring(0, 50)}...
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
          <span>Total Data Points: {telemetryData.length}</span>
          <span>Filtered: {filteredData.length}</span>
          <div className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            <span>Real-time Monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryDashboard;
