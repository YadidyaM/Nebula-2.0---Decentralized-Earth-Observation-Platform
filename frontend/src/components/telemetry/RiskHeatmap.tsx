import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Map,
  Layers,
  Clock,
  AlertTriangle,
  Maximize2,
  Minimize2,
  TrendingUp,
  TrendingDown,
  Filter,
} from "lucide-react";
import { apiClient, handleApiError } from "../../lib/api-utils";
import { formatDate, formatNumber } from "../../lib/formatters";

interface RiskPoint {
  id: string;
  lat: number;
  lng: number;
  risk_type: "flood" | "drought" | "wildfire" | "earthquake" | "storm";
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  timestamp: string;
  description: string;
  affected_area: number;
  trend: "increasing" | "decreasing" | "stable";
}

interface RiskHeatmapProps {
  className?: string;
}

const RiskHeatmap: React.FC<RiskHeatmapProps> = ({ className = "" }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [riskPoints, setRiskPoints] = useState<RiskPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRiskTypes, setSelectedRiskTypes] = useState<string[]>([
    "flood",
    "drought",
    "wildfire",
    "earthquake",
    "storm",
  ]);
  const [timeRange, setTimeRange] = useState<"1d" | "7d" | "30d">("7d");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState<RiskPoint | null>(null);
  const [heatmapLayer, setHeatmapLayer] = useState<any>(null);

  // Risk type configurations
  const riskTypes = {
    flood: {
      label: "Flood",
      color: "#3b82f6", // blue-500
      icon: "🌊",
      gradient: ["#1e40af", "#3b82f6", "#60a5fa", "#93c5fd"],
    },
    drought: {
      label: "Drought",
      color: "#f59e0b", // amber-500
      icon: "☀️",
      gradient: ["#92400e", "#f59e0b", "#fbbf24", "#fde68a"],
    },
    wildfire: {
      label: "Wildfire",
      color: "#ef4444", // red-500
      icon: "🔥",
      gradient: ["#991b1b", "#ef4444", "#f87171", "#fca5a5"],
    },
    earthquake: {
      label: "Earthquake",
      color: "#8b5cf6", // violet-500
      icon: "🌍",
      gradient: ["#6b21a8", "#8b5cf6", "#a78bfa", "#c4b5fd"],
    },
    storm: {
      label: "Storm",
      color: "#06b6d4", // cyan-500
      icon: "⛈️",
      gradient: ["#0e7490", "#06b6d4", "#22d3ee", "#67e8f9"],
    },
  };

  // Initialize Mapbox map
  useEffect(() => {
    const initializeMap = async () => {
      try {
        // Dynamic import for Mapbox GL JS
        const mapboxgl = await import("mapbox-gl");
        
        mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || "";

        const mapInstance = new mapboxgl.Map({
          container: mapRef.current!,
          style: "mapbox://styles/mapbox/dark-v11",
          center: [0, 0],
          zoom: 2,
          projection: "globe",
        });

        mapInstance.on("load", () => {
          // Add custom styling
          mapInstance.setFog({
            color: "rgb(15, 23, 42)", // slate-900
            "high-color": "rgb(6, 182, 212)", // cyan-500
            "horizon-blend": 0.02,
          });

          setMap(mapInstance);
        });

        // Add click handler for risk points
        mapInstance.on("click", (e) => {
          const features = mapInstance.queryRenderedFeatures(e.point, {
            layers: ["risk-points"],
          });

          if (features.length > 0) {
            const feature = features[0];
            const riskPoint = riskPoints.find((p) => p.id === feature.properties?.id);
            if (riskPoint) {
              setSelectedPoint(riskPoint);
            }
          }
        });

        return () => mapInstance.remove();
      } catch (err) {
        console.error("Failed to initialize map:", err);
        setError("Failed to initialize map. Please check your Mapbox token.");
      }
    };

    initializeMap();
  }, []);

  // Fetch risk data
  const fetchRiskData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        time_range: timeRange,
        risk_types: selectedRiskTypes.join(","),
      });

      const response = await apiClient.get(`/risks?${params}`);
      setRiskPoints(response.data);
    } catch (err) {
      setError(handleApiError(err));
      console.error("Failed to fetch risk data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Update map with risk points
  useEffect(() => {
    if (!map || !riskPoints.length) return;

    // Remove existing layers
    if (map.getLayer("risk-points")) {
      map.removeLayer("risk-points");
    }
    if (map.getSource("risk-points")) {
      map.removeSource("risk-points");
    }

    // Add risk points as GeoJSON
    map.addSource("risk-points", {
      type: "geojson",
      data: {
        type: "FeatureCollection",
        features: riskPoints.map((point) => ({
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [point.lng, point.lat],
          },
          properties: {
            id: point.id,
            risk_type: point.risk_type,
            severity: point.severity,
            confidence: point.confidence,
            description: point.description,
          },
        })),
      },
    });

    // Add circle layer for risk points
    map.addLayer({
      id: "risk-points",
      type: "circle",
      source: "risk-points",
      paint: {
        "circle-radius": [
          "interpolate",
          ["linear"],
          ["get", "confidence"],
          0,
          8,
          1,
          20,
        ],
        "circle-color": [
          "match",
          ["get", "risk_type"],
          "flood",
          riskTypes.flood.color,
          "drought",
          riskTypes.drought.color,
          "wildfire",
          riskTypes.wildfire.color,
          "earthquake",
          riskTypes.earthquake.color,
          "storm",
          riskTypes.storm.color,
          "#6b7280", // gray-500
        ],
        "circle-opacity": 0.8,
        "circle-stroke-width": 2,
        "circle-stroke-color": "#ffffff",
        "circle-stroke-opacity": 0.5,
      },
    });

    // Add pulsing animation for critical risks
    const criticalPoints = riskPoints.filter((p) => p.severity === "critical");
    if (criticalPoints.length > 0) {
      map.addLayer({
        id: "critical-pulse",
        type: "circle",
        source: "risk-points",
        filter: ["==", ["get", "severity"], "critical"],
        paint: {
          "circle-radius": [
            "interpolate",
            ["linear"],
            ["get", "confidence"],
            0,
            12,
            1,
            24,
          ],
          "circle-color": "#ef4444", // red-500
          "circle-opacity": 0.3,
          "circle-stroke-width": 0,
        },
      });

      // Animate critical points
      let radius = 12;
      const animate = () => {
        radius = radius >= 24 ? 12 : radius + 1;
        map.setPaintProperty("critical-pulse", "circle-radius", radius);
        requestAnimationFrame(animate);
      };
      animate();
    }
  }, [map, riskPoints, riskTypes]);

  // Initial data fetch
  useEffect(() => {
    fetchRiskData();
  }, [timeRange, selectedRiskTypes]);

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low":
        return "text-green-400 bg-green-500/20 border-green-500/30";
      case "medium":
        return "text-yellow-400 bg-yellow-500/20 border-yellow-500/30";
      case "high":
        return "text-orange-400 bg-orange-500/20 border-orange-500/30";
      case "critical":
        return "text-red-400 bg-red-500/20 border-red-500/30";
      default:
        return "text-slate-400 bg-slate-500/20 border-slate-500/30";
    }
  };

  // Get trend icon
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "increasing":
        return <TrendingUp className="w-4 h-4 text-red-400" />;
      case "decreasing":
        return <TrendingDown className="w-4 h-4 text-green-400" />;
      default:
        return <div className="w-4 h-4 bg-slate-400 rounded-full" />;
    }
  };

  return (
    <div className={`relative group ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 rounded-lg p-6 hover:border-cyan-400/50 transition-all">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Map className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold text-slate-100">Risk Heatmap</h3>
            <span className="px-2 py-1 bg-slate-700/50 text-slate-400 text-xs rounded-full">
              {riskPoints.length} risks
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-cyan-400 transition-all"
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>
            <button
              onClick={fetchRiskData}
              disabled={loading}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-green-400 transition-all disabled:opacity-50"
            >
              <div className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Risk Type Filter */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Risk Types
            </label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(riskTypes).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => {
                    setSelectedRiskTypes((prev) =>
                      prev.includes(key)
                        ? prev.filter((t) => t !== key)
                        : [...prev, key]
                    );
                  }}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                    selectedRiskTypes.includes(key)
                      ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                      : "bg-slate-700/50 text-slate-400 hover:text-slate-300 hover:bg-slate-600/50"
                  }`}
                >
                  <span>{config.icon}</span>
                  <span>{config.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Time Range */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Time Range
            </label>
            <div className="flex gap-2">
              {(["1d", "7d", "30d"] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    timeRange === range
                      ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                      : "bg-slate-700/50 text-slate-400 hover:text-slate-300 hover:bg-slate-600/50"
                  }`}
                >
                  {range === "1d" ? "24 Hours" : range === "7d" ? "7 Days" : "30 Days"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div
          className={`relative rounded-lg overflow-hidden border border-slate-600/30 ${
            isFullscreen ? "h-screen" : "h-96"
          }`}
        >
          <div
            ref={mapRef}
            className="w-full h-full"
            style={{ minHeight: isFullscreen ? "100vh" : "24rem" }}
          />
          
          {/* Loading Overlay */}
          {loading && (
            <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                <p className="text-slate-300">Loading risk data...</p>
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur-md border border-slate-600/30 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-slate-100 mb-3">Risk Types</h4>
            <div className="space-y-2">
              {Object.entries(riskTypes).map(([key, config]) => (
                <div key={key} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: config.color }}
                  />
                  <span className="text-xs text-slate-300">{config.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Risk Point Details */}
        <AnimatePresence>
          {selectedPoint && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6 p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {riskTypes[selectedPoint.risk_type]?.icon}
                  </span>
                  <div>
                    <h4 className="font-semibold text-slate-100">
                      {riskTypes[selectedPoint.risk_type]?.label} Risk
                    </h4>
                    <p className="text-slate-400 text-sm">
                      {formatDate(selectedPoint.timestamp, "MMM dd, HH:mm")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-1 text-xs rounded-full border ${getSeverityColor(
                      selectedPoint.severity
                    )}`}
                  >
                    {selectedPoint.severity}
                  </span>
                  {getTrendIcon(selectedPoint.trend)}
                </div>
              </div>
              <p className="text-slate-300 text-sm mb-3">{selectedPoint.description}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Confidence:</span>
                  <span className="text-slate-100 ml-1">
                    {formatNumber(selectedPoint.confidence * 100, 1)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Area:</span>
                  <span className="text-slate-100 ml-1">
                    {formatNumber(selectedPoint.affected_area, 0)} km²
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Coordinates:</span>
                  <span className="text-slate-100 ml-1">
                    {formatNumber(selectedPoint.lat, 4)}, {formatNumber(selectedPoint.lng, 4)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Trend:</span>
                  <span className="text-slate-100 ml-1 capitalize">
                    {selectedPoint.trend}
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

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

export default RiskHeatmap;
