import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Satellite,
  MapPin,
  Zap,
  Battery,
  Thermometer,
  Droplets,
  Gauge,
  Wifi,
  RefreshCw,
  Activity,
  Clock,
} from "lucide-react";
import { apiClient, handleApiError } from "../../lib/api-utils";
import { formatDate, formatNumber, formatCoordinate } from "../../lib/formatters";
import { useWebSocket } from "../../contexts/WebSocketContext";

interface TelemetryData {
  satellite_id: string;
  timestamp: string;
  position: {
    lat: number;
    lng: number;
    altitude: number;
  };
  velocity: {
    x: number;
    y: number;
    z: number;
    magnitude: number;
  };
  signal_strength: number;
  battery_level: number;
  temperature: number;
  humidity: number;
  pressure: number;
  status: "online" | "offline" | "error" | "maintenance";
}

interface SatelliteInfo {
  id: string;
  name: string;
  type: string;
  status: string;
  launch_date: string;
  orbit_type: string;
}

interface SatelliteTelemetryPanelProps {
  className?: string;
}

const SatelliteTelemetryPanel: React.FC<SatelliteTelemetryPanelProps> = ({
  className = "",
}) => {
  const [selectedSatellite, setSelectedSatellite] = useState<string>("");
  const [satellites, setSatellites] = useState<SatelliteInfo[]>([]);
  const [telemetryData, setTelemetryData] = useState<TelemetryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoUpdate, setAutoUpdate] = useState(true);

  const { subscribe, isConnected } = useWebSocket();

  // Fetch available satellites
  const fetchSatellites = async () => {
    try {
      const response = await apiClient.get("/agents?type=satellite");
      setSatellites(response.data);
      if (response.data.length > 0 && !selectedSatellite) {
        setSelectedSatellite(response.data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch satellites:", err);
    }
  };

  // Fetch telemetry data for selected satellite
  const fetchTelemetryData = async () => {
    if (!selectedSatellite) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get(`/telemetry/satellite/${selectedSatellite}`);
      setTelemetryData(response.data);
      setLastUpdate(new Date());
    } catch (err) {
      setError(handleApiError(err));
      console.error("Failed to fetch telemetry data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchSatellites();
  }, []);

  useEffect(() => {
    if (selectedSatellite) {
      fetchTelemetryData();
    }
  }, [selectedSatellite]);

  // Auto-update every 5 seconds
  useEffect(() => {
    if (!autoUpdate || !selectedSatellite) return;

    const interval = setInterval(() => {
      if (isConnected) {
        fetchTelemetryData();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [autoUpdate, selectedSatellite, isConnected]);

  // WebSocket subscription for real-time updates
  useEffect(() => {
    if (!isConnected || !selectedSatellite) return;

    const unsubscribe = subscribe("telemetry_update", (message) => {
      if (message.satellite_id === selectedSatellite) {
        setTelemetryData(message.data);
        setLastUpdate(new Date());
      }
    });

    return unsubscribe;
  }, [subscribe, isConnected, selectedSatellite]);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "text-green-400 bg-green-500/20 border-green-500/30";
      case "offline":
        return "text-slate-400 bg-slate-500/20 border-slate-500/30";
      case "error":
        return "text-red-400 bg-red-500/20 border-red-500/30";
      case "maintenance":
        return "text-yellow-400 bg-yellow-500/20 border-yellow-500/30";
      default:
        return "text-slate-400 bg-slate-500/20 border-slate-500/30";
    }
  };

  // Get signal strength color
  const getSignalColor = (strength: number) => {
    if (strength >= -50) return "text-green-400";
    if (strength >= -70) return "text-yellow-400";
    if (strength >= -90) return "text-orange-400";
    return "text-red-400";
  };

  // Get battery color
  const getBatteryColor = (level: number) => {
    if (level >= 80) return "text-green-400";
    if (level >= 50) return "text-yellow-400";
    if (level >= 20) return "text-orange-400";
    return "text-red-400";
  };

  // Calculate velocity vector angle
  const getVelocityAngle = (velocity: { x: number; y: number }) => {
    return Math.atan2(velocity.y, velocity.x) * (180 / Math.PI);
  };

  // Selected satellite info
  const selectedSatelliteInfo = useMemo(
    () => satellites.find((s) => s.id === selectedSatellite),
    [satellites, selectedSatellite]
  );

  return (
    <div className={`relative group ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 rounded-lg p-6 hover:border-cyan-400/50 transition-all">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Satellite className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold text-slate-100">Satellite Telemetry</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAutoUpdate(!autoUpdate)}
              className={`px-3 py-1 rounded-lg text-xs transition-all ${
                autoUpdate
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-slate-700/50 text-slate-400 border border-slate-600/50"
              }`}
            >
              Auto-update
            </button>
            <button
              onClick={fetchTelemetryData}
              disabled={loading}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-cyan-400 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Satellite Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Select Satellite
          </label>
          <select
            value={selectedSatellite}
            onChange={(e) => setSelectedSatellite(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
          >
            <option value="">Select a satellite...</option>
            {satellites.map((satellite) => (
              <option key={satellite.id} value={satellite.id}>
                {satellite.name} ({satellite.type})
              </option>
            ))}
          </select>
        </div>

        {/* Satellite Info */}
        {selectedSatelliteInfo && (
          <div className="mb-6 p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <Satellite className="w-5 h-5 text-cyan-400" />
                <h4 className="font-semibold text-slate-100">
                  {selectedSatelliteInfo.name}
                </h4>
                <span
                  className={`px-2 py-1 text-xs rounded-full border ${getStatusColor(
                    selectedSatelliteInfo.status
                  )}`}
                >
                  {selectedSatelliteInfo.status}
                </span>
              </div>
              <div className="text-sm text-slate-400">
                {selectedSatelliteInfo.orbit_type}
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-slate-400">Type:</span>
                <span className="text-slate-100 ml-1">
                  {selectedSatelliteInfo.type}
                </span>
              </div>
              <div>
                <span className="text-slate-400">Launch:</span>
                <span className="text-slate-100 ml-1">
                  {formatDate(selectedSatelliteInfo.launch_date, "MMM yyyy")}
                </span>
              </div>
              <div>
                <span className="text-slate-400">Last Update:</span>
                <span className="text-slate-100 ml-1">
                  {formatDate(lastUpdate, "HH:mm:ss")}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`} />
                <span className="text-slate-400">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Telemetry Data */}
        {telemetryData ? (
          <div className="space-y-6">
            {/* Position */}
            <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <MapPin className="w-5 h-5 text-cyan-400" />
                <h4 className="font-semibold text-slate-100">Position</h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <span className="text-slate-400 text-sm">Latitude:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.position.lat, 6)}°
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Longitude:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.position.lng, 6)}°
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Altitude:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.position.altitude, 2)} km
                  </div>
                </div>
              </div>
            </div>

            {/* Velocity */}
            <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-green-400" />
                <h4 className="font-semibold text-slate-100">Velocity</h4>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <span className="text-slate-400 text-sm">Magnitude:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.velocity.magnitude, 2)} km/h
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">X Component:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.velocity.x, 2)} km/h
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Y Component:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.velocity.y, 2)} km/h
                  </div>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Z Component:</span>
                  <div className="text-slate-100 font-mono">
                    {formatNumber(telemetryData.velocity.z, 2)} km/h
                  </div>
                </div>
              </div>
              {/* Velocity Vector Visualization */}
              <div className="mt-4 flex items-center justify-center">
                <div className="relative w-32 h-32 border border-slate-600/30 rounded-full">
                  <div
                    className="absolute w-2 h-2 bg-green-400 rounded-full"
                    style={{
                      left: "50%",
                      top: "50%",
                      transform: `translate(-50%, -50%) rotate(${getVelocityAngle(telemetryData.velocity)}deg) translateY(-60px)`,
                    }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-1 h-1 bg-slate-400 rounded-full" />
                  </div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Signal Strength */}
              <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Wifi className="w-5 h-5 text-blue-400" />
                  <h4 className="font-semibold text-slate-100">Signal Strength</h4>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          telemetryData.signal_strength >= -50
                            ? "bg-green-400"
                            : telemetryData.signal_strength >= -70
                            ? "bg-yellow-400"
                            : telemetryData.signal_strength >= -90
                            ? "bg-orange-400"
                            : "bg-red-400"
                        }`}
                        style={{
                          width: `${Math.max(0, Math.min(100, ((telemetryData.signal_strength + 120) / 120) * 100))}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span
                    className={`font-mono text-sm ${getSignalColor(
                      telemetryData.signal_strength
                    )}`}
                  >
                    {formatNumber(telemetryData.signal_strength, 1)} dBm
                  </span>
                </div>
              </div>

              {/* Battery Level */}
              <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Battery className="w-5 h-5 text-yellow-400" />
                  <h4 className="font-semibold text-slate-100">Battery Level</h4>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          telemetryData.battery_level >= 80
                            ? "bg-green-400"
                            : telemetryData.battery_level >= 50
                            ? "bg-yellow-400"
                            : telemetryData.battery_level >= 20
                            ? "bg-orange-400"
                            : "bg-red-400"
                        }`}
                        style={{ width: `${telemetryData.battery_level}%` }}
                      />
                    </div>
                  </div>
                  <span
                    className={`font-mono text-sm ${getBatteryColor(
                      telemetryData.battery_level
                    )}`}
                  >
                    {formatNumber(telemetryData.battery_level, 1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Environmental Data */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Thermometer className="w-5 h-5 text-orange-400" />
                  <h4 className="font-semibold text-slate-100">Temperature</h4>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {formatNumber(telemetryData.temperature, 1)}°C
                </div>
              </div>

              <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Droplets className="w-5 h-5 text-blue-400" />
                  <h4 className="font-semibold text-slate-100">Humidity</h4>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {formatNumber(telemetryData.humidity, 1)}%
                </div>
              </div>

              <div className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Gauge className="w-5 h-5 text-purple-400" />
                  <h4 className="font-semibold text-slate-100">Pressure</h4>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {formatNumber(telemetryData.pressure, 2)} hPa
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Satellite className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">
              {selectedSatellite ? "No telemetry data available" : "Select a satellite to view telemetry"}
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
      </div>
      <div className="absolute inset-0 scan-line" />
    </div>
  );
};

export default SatelliteTelemetryPanel;
