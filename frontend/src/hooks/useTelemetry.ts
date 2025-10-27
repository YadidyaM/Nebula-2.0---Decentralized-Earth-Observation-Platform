import { useState, useEffect, useCallback } from "react";
import { apiClient } from "../services/api";
import { TelemetryData } from "../types/telemetry";

interface UseTelemetryReturn {
  telemetryData: TelemetryData[];
  isLoading: boolean;
  error: string | null;
  fetchTelemetry: () => Promise<void>;
}

export const useTelemetry = (agentId?: string): UseTelemetryReturn => {
  const [telemetryData, setTelemetryData] = useState<TelemetryData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch telemetry data
  const fetchTelemetry = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTelemetry(agentId);
      if (response.success && response.data) {
        setTelemetryData(response.data);
      } else {
        setError(response.message || "Failed to fetch telemetry data");
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch telemetry data");
      console.error("Error fetching telemetry:", err);
    } finally {
      setIsLoading(false);
    }
  }, [agentId]);

  // Auto-refresh telemetry periodically
  useEffect(() => {
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [fetchTelemetry]);

  return {
    telemetryData,
    isLoading,
    error,
    fetchTelemetry,
  };
};
