import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MapPin,
  Clock,
  Calendar,
  Download,
  Navigation,
  Satellite,
  Globe,
  Timer,
} from "lucide-react";
import { apiClient, handleApiError } from "../../lib/api-utils";
import { formatDate, formatDuration, formatCoordinate } from "../../lib/formatters";
import { validateCoordinates } from "../../lib/validators";

interface PassPrediction {
  satellite_id: string;
  satellite_name: string;
  start_time: string;
  end_time: string;
  duration: number;
  max_elevation: number;
  azimuth: number;
  pass_type: "daylight" | "night" | "twilight";
}

interface Location {
  lat: number;
  lng: number;
  name?: string;
}

interface OrbitalPassPredictorProps {
  className?: string;
}

const OrbitalPassPredictor: React.FC<OrbitalPassPredictorProps> = ({
  className = "",
}) => {
  const [location, setLocation] = useState<Location>({ lat: 0, lng: 0 });
  const [locationName, setLocationName] = useState("");
  const [predictions, setPredictions] = useState<PassPrediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSatellites, setSelectedSatellites] = useState<string[]>([]);
  const [availableSatellites, setAvailableSatellites] = useState<
    Array<{ id: string; name: string; type: string }>
  >([]);
  const [daysAhead, setDaysAhead] = useState(7);
  const [nextPass, setNextPass] = useState<PassPrediction | null>(null);
  const [timeToNextPass, setTimeToNextPass] = useState<number>(0);

  // Get user's current location
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser");
      return;
    }

    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setLocation({ lat: latitude, lng: longitude });
        setError(null);
        setLoading(false);
      },
      (err) => {
        setError(`Failed to get location: ${err.message}`);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // 5 minutes
      }
    );
  };

  // Fetch available satellites from satellite physics engine
  const fetchSatellites = async () => {
    try {
      const response = await apiClient.get("/satellites/constellation");
      const satellites = response.data.satellites.map((sat: any) => ({
        id: sat.id,
        name: sat.name,
        type: sat.mission_type
      }));
      setAvailableSatellites(satellites);
    } catch (err) {
      console.error("Failed to fetch satellites:", err);
    }
  };

  // Calculate orbital passes using real satellite physics
  const calculatePasses = async () => {
    if (!location.lat || !location.lng) {
      setError("Please set a location first");
      return;
    }

    const coordValidation = validateCoordinates(location.lat, location.lng);
    if (!coordValidation.isValid) {
      setError(coordValidation.errors.join(", "));
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Use the real satellite physics API endpoint
      const params = new URLSearchParams({
        latitude: location.lat.toString(),
        longitude: location.lng.toString(),
        altitude: "0",
        days_ahead: daysAhead.toString(),
        min_elevation: "10"
      });

      if (selectedSatellites.length > 0) {
        selectedSatellites.forEach(id => {
          params.append('satellite_ids', id);
        });
      }

      const response = await apiClient.get(`/satellites/predictions?${params}`);
      const passes = response.data.sort(
        (a: PassPrediction, b: PassPrediction) =>
          new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      );

      setPredictions(passes);
      setNextPass(passes[0] || null);
    } catch (err) {
      setError(handleApiError(err));
      console.error("Failed to calculate passes:", err);
    } finally {
      setLoading(false);
    }
  };

  // Update countdown timer
  useEffect(() => {
    if (!nextPass) return;

    const updateTimer = () => {
      const now = new Date().getTime();
      const startTime = new Date(nextPass.start_time).getTime();
      const timeDiff = startTime - now;

      if (timeDiff > 0) {
        setTimeToNextPass(timeDiff);
      } else {
        setTimeToNextPass(0);
        // Recalculate passes when current pass starts
        calculatePasses();
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [nextPass]);

  // Initial setup
  useEffect(() => {
    fetchSatellites();
    getCurrentLocation();
  }, []);

  // Format countdown timer
  const formatCountdown = (milliseconds: number): string => {
    if (milliseconds <= 0) return "Now";
    
    const days = Math.floor(milliseconds / (1000 * 60 * 60 * 24));
    const hours = Math.floor((milliseconds % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);

    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
    if (minutes > 0) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  };

  // Export schedule as ICS
  const exportSchedule = () => {
    const icsContent = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Nebula Protocol//Satellite Passes//EN",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      ...predictions.map((pass) => [
        "BEGIN:VEVENT",
        `UID:${pass.satellite_id}-${pass.start_time}@nebula.protocol`,
        `DTSTART:${formatDate(pass.start_time, "yyyyMMddTHHmmss")}Z`,
        `DTEND:${formatDate(pass.end_time, "yyyyMMddTHHmmss")}Z`,
        `SUMMARY:${pass.satellite_name} Pass`,
        `DESCRIPTION:Max Elevation: ${pass.max_elevation.toFixed(1)}°\\nDuration: ${formatDuration(pass.duration)}\\nAzimuth: ${pass.azimuth.toFixed(1)}°`,
        `LOCATION:${formatCoordinate(location.lat, location.lng)}`,
        "END:VEVENT",
      ]).flat(),
      "END:VCALENDAR",
    ].join("\r\n");

    const blob = new Blob([icsContent], { type: "text/calendar" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `satellite-passes-${formatDate(new Date(), "yyyy-MM-dd")}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Get pass type color
  const getPassTypeColor = (type: string) => {
    switch (type) {
      case "daylight":
        return "text-yellow-400 bg-yellow-500/20 border-yellow-500/30";
      case "night":
        return "text-blue-400 bg-blue-500/20 border-blue-500/30";
      case "twilight":
        return "text-purple-400 bg-purple-500/20 border-purple-500/30";
      default:
        return "text-slate-400 bg-slate-500/20 border-slate-500/30";
    }
  };

  return (
    <div className={`relative group ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 rounded-lg p-6 hover:border-cyan-400/50 transition-all">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Satellite className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold text-slate-100">Orbital Pass Predictor</h3>
          </div>
          <button
            onClick={exportSchedule}
            disabled={predictions.length === 0}
            className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-green-400 transition-all disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>

        {/* Location Input */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Latitude
            </label>
            <input
              type="number"
              value={location.lat}
              onChange={(e) =>
                setLocation((prev) => ({ ...prev, lat: parseFloat(e.target.value) }))
              }
              placeholder="0.000000"
              step="0.000001"
              className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 placeholder-slate-400 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Longitude
            </label>
            <input
              type="number"
              value={location.lng}
              onChange={(e) =>
                setLocation((prev) => ({ ...prev, lng: parseFloat(e.target.value) }))
              }
              placeholder="0.000000"
              step="0.000001"
              className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 placeholder-slate-400 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={getCurrentLocation}
              disabled={loading}
              className="w-full px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 border border-cyan-500/30 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <MapPin className="w-4 h-4" />
              {loading ? "Getting..." : "Current Location"}
            </button>
          </div>
        </div>

        {/* Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Days Ahead
            </label>
            <select
              value={daysAhead}
              onChange={(e) => setDaysAhead(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
            >
              <option value={1}>1 Day</option>
              <option value={3}>3 Days</option>
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Satellites
            </label>
            <select
              multiple
              value={selectedSatellites}
              onChange={(e) =>
                setSelectedSatellites(
                  Array.from(e.target.selectedOptions, (option) => option.value)
                )
              }
              className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
              size={3}
            >
              <option value="">All Satellites</option>
              {availableSatellites.map((sat) => (
                <option key={sat.id} value={sat.id}>
                  {sat.name} ({sat.type})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Calculate Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={calculatePasses}
            disabled={loading || !location.lat || !location.lng}
            className="px-6 py-3 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 text-cyan-400 border border-cyan-500/30 rounded-lg transition-all disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Navigation className="w-4 h-4" />
                Calculate Passes
              </>
            )}
          </button>
        </div>

        {/* Next Pass Countdown */}
        {nextPass && (
          <div className="mb-6 p-4 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-lg font-semibold text-slate-100 mb-1">
                  Next Pass: {nextPass.satellite_name}
                </h4>
                <p className="text-slate-400 text-sm">
                  {formatDate(nextPass.start_time, "MMM dd, HH:mm")} -{" "}
                  {formatDate(nextPass.end_time, "HH:mm")}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-cyan-400">
                  {formatCountdown(timeToNextPass)}
                </div>
                <p className="text-slate-400 text-sm">until start</p>
              </div>
            </div>
          </div>
        )}

        {/* Predictions List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <AnimatePresence>
            {predictions.map((pass, index) => (
              <motion.div
                key={`${pass.satellite_id}-${pass.start_time}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg hover:border-cyan-500/30 transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <Satellite className="w-5 h-5 text-cyan-400" />
                    <h4 className="font-semibold text-slate-100">
                      {pass.satellite_name}
                    </h4>
                    <span
                      className={`px-2 py-1 text-xs rounded-full border ${getPassTypeColor(
                        pass.pass_type
                      )}`}
                    >
                      {pass.pass_type}
                    </span>
                  </div>
                  <div className="text-sm text-slate-400">
                    {formatDate(pass.start_time, "MMM dd, HH:mm")}
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-300">
                      {formatDuration(pass.duration)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-300">
                      {pass.max_elevation.toFixed(1)}°
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-300">
                      {pass.azimuth.toFixed(1)}°
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Timer className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-300">
                      {formatDate(pass.end_time, "HH:mm")}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Error State */}
        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && predictions.length === 0 && !error && (
          <div className="text-center py-8">
            <Satellite className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No passes found for the selected criteria</p>
            <p className="text-slate-500 text-sm mt-1">
              Try adjusting the location or time range
            </p>
          </div>
        )}
      </div>
      <div className="absolute inset-0 scan-line" />
    </div>
  );
};

export default OrbitalPassPredictor;
