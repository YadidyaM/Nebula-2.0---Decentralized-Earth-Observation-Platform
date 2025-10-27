import React, { useState, useEffect, useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  ComposedChart,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Download, 
  RefreshCw, 
  TrendingUp, 
  Activity,
  Thermometer,
  Battery,
  Zap
} from "lucide-react";
import { apiClient, handleApiError } from "../../lib/api-utils";
import { formatDate, formatNumber, formatDuration } from "../../lib/formatters";
import { useWebSocket } from "../../contexts/WebSocketContext";

interface TelemetryData {
  timestamp: string;
  altitude: number;
  velocity: number;
  temperature: number;
  battery: number;
  signal_strength: number;
}

interface TelemetryTrendsChartProps {
  agentId?: string;
  className?: string;
}

const TelemetryTrendsChart: React.FC<TelemetryTrendsChartProps> = ({
  agentId,
  className = "",
}) => {
  const [data, setData] = useState<TelemetryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<"1h" | "6h" | "24h" | "7d">("24h");
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    "altitude",
    "velocity",
    "temperature",
    "battery",
  ]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { subscribe, isConnected } = useWebSocket();

  // Metric configurations
  const metrics = useMemo(
    () => ({
      altitude: {
        label: "Altitude",
        unit: "km",
        color: "#06b6d4", // cyan-500
        icon: TrendingUp,
        min: 0,
        max: 1000,
      },
      velocity: {
        label: "Velocity",
        unit: "km/h",
        color: "#10b981", // emerald-500
        icon: Zap,
        min: 0,
        max: 50000,
      },
      temperature: {
        label: "Temperature",
        unit: "°C",
        color: "#f59e0b", // amber-500
        icon: Thermometer,
        min: -100,
        max: 100,
      },
      battery: {
        label: "Battery",
        unit: "%",
        color: "#eab308", // yellow-500
        icon: Battery,
        min: 0,
        max: 100,
      },
      signal_strength: {
        label: "Signal",
        unit: "dBm",
        color: "#8b5cf6", // violet-500
        icon: Activity,
        min: -120,
        max: 0,
      },
    }),
    []
  );

  // Fetch telemetry data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        range: timeRange,
        ...(agentId && { agent_id: agentId }),
      });

      const response = await apiClient.get(`/telemetry/trends?${params}`);
      setData(response.data);
      setLastUpdate(new Date());
    } catch (err) {
      setError(handleApiError(err));
      console.error("Failed to fetch telemetry trends:", err);
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [timeRange, agentId]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      if (isConnected) {
        fetchData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh, isConnected]);

  // WebSocket subscription for real-time updates
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribe = subscribe("telemetry_update", (message) => {
      if (agentId && message.agent_id === agentId) {
        setData((prev) => {
          const newData = [...prev, message.data];
          // Keep only last 100 data points
          return newData.slice(-100);
        });
        setLastUpdate(new Date());
      }
    });

    return unsubscribe;
  }, [subscribe, isConnected, agentId]);

  // Export data as CSV
  const exportData = () => {
    const csvContent = [
      ["Timestamp", ...selectedMetrics.map((m) => metrics[m].label)].join(","),
      ...data.map((row) =>
        [
          formatDate(row.timestamp, "yyyy-MM-dd HH:mm:ss"),
          ...selectedMetrics.map((metric) => row[metric as keyof TelemetryData]),
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `telemetry-trends-${timeRange}-${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="backdrop-blur-md bg-slate-900/90 border border-cyan-500/30 rounded-lg p-3 shadow-xl">
          <p className="text-cyan-400 font-mono text-sm mb-2">
            {formatDate(label, "MMM dd, HH:mm:ss")}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 mb-1">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-slate-300 text-sm">
                {entry.dataKey}: {formatNumber(entry.value, 2)} {metrics[entry.dataKey]?.unit}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  // Loading skeleton
  if (loading && data.length === 0) {
    return (
      <div className={`relative group ${className}`}>
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
        <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 rounded-lg p-6 hover:border-cyan-400/50 transition-all">
          <div className="animate-pulse">
            <div className="h-6 bg-slate-700/50 rounded mb-4 w-1/3"></div>
            <div className="h-64 bg-slate-700/30 rounded mb-4"></div>
            <div className="flex gap-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-8 bg-slate-700/40 rounded w-16"></div>
              ))}
            </div>
          </div>
        </div>
        <div className="absolute inset-0 scan-line" />
      </div>
    );
  }

  return (
    <div className={`relative group ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 rounded-lg p-6 hover:border-cyan-400/50 transition-all">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold text-slate-100">Telemetry Trends</h3>
            {agentId && (
              <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">
                Agent {agentId.slice(0, 8)}...
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1 rounded-lg text-xs transition-all ${
                autoRefresh
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-slate-700/50 text-slate-400 border border-slate-600/50"
              }`}
            >
              Auto-refresh
            </button>
            <button
              onClick={fetchData}
              disabled={loading}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-cyan-400 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={exportData}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-green-400 transition-all"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2 mb-6">
          {(["1h", "6h", "24h", "7d"] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                timeRange === range
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                  : "bg-slate-700/50 text-slate-400 hover:text-slate-300 hover:bg-slate-600/50"
              }`}
            >
              {range}
            </button>
          ))}
        </div>

        {/* Metric Selector */}
        <div className="flex flex-wrap gap-2 mb-6">
          {Object.entries(metrics).map(([key, config]) => {
            const Icon = config.icon;
            const isSelected = selectedMetrics.includes(key);
            return (
              <button
                key={key}
                onClick={() => {
                  setSelectedMetrics((prev) =>
                    isSelected
                      ? prev.filter((m) => m !== key)
                      : [...prev, key]
                  );
                }}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                  isSelected
                    ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                    : "bg-slate-700/50 text-slate-400 hover:text-slate-300 hover:bg-slate-600/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{config.label}</span>
              </button>
            );
          })}
        </div>

        {/* Chart */}
        <div className="h-80 mb-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${timeRange}-${selectedMetrics.join(",")}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="timestamp"
                    stroke="#9ca3af"
                    fontSize={12}
                    tickFormatter={(value) => formatDate(value, "HH:mm")}
                  />
                  <YAxis stroke="#9ca3af" fontSize={12} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  
                  {selectedMetrics.map((metric) => {
                    const config = metrics[metric];
                    return (
                      <Line
                        key={metric}
                        type="monotone"
                        dataKey={metric}
                        stroke={config.color}
                        strokeWidth={2}
                        dot={false}
                        name={config.label}
                        connectNulls={false}
                      />
                    );
                  })}
                </ComposedChart>
              </ResponsiveContainer>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Status Bar */}
        <div className="flex items-center justify-between text-sm text-slate-400">
          <div className="flex items-center gap-4">
            <span>Last update: {formatDate(lastUpdate, "HH:mm:ss")}</span>
            <span>Data points: {data.length}</span>
            <span className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`} />
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
          {error && (
            <span className="text-red-400 text-xs bg-red-500/10 px-2 py-1 rounded">
              {error}
            </span>
          )}
        </div>
      </div>
      <div className="absolute inset-0 scan-line" />
    </div>
  );
};

export default TelemetryTrendsChart;
