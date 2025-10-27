import { useState, useEffect, useCallback } from "react";
import { apiClient } from "../services/api";
import {
  Mission,
  CreateMissionPayload,
  UpdateMissionPayload,
} from "../types/missions";

interface UseMissionsReturn {
  missions: Mission[];
  isLoading: boolean;
  error: string | null;
  fetchMissions: () => Promise<void>;
  createMission: (mission: CreateMissionPayload) => Promise<Mission | null>;
  updateMission: (mission: Mission) => Promise<Mission | null>;
  deleteMission: (id: string) => Promise<boolean>;
}

export const useMissions = (): UseMissionsReturn => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch missions
  const fetchMissions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getMissions();
      if (response.success && response.data) {
        setMissions(response.data);
      } else {
        setError(response.message || "Failed to fetch missions");
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch missions");
      console.error("Error fetching missions:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create mission
  const createMission = useCallback(
    async (mission: CreateMissionPayload): Promise<Mission | null> => {
      try {
        const response = await apiClient.createMission(mission);
        if (response.success && response.data) {
          setMissions((prev) => [response.data!, ...prev]);
          return response.data;
        }
        setError(response.message || "Failed to create mission");
        return null;
      } catch (err: any) {
        setError(err.message || "Failed to create mission");
        console.error("Error creating mission:", err);
        return null;
      }
    },
    []
  );

  // Update mission
  const updateMission = useCallback(
    async (mission: Mission): Promise<Mission | null> => {
      try {
        const payload: UpdateMissionPayload = {
          status: mission.status,
          data_collected: mission.data_collected,
          blockchain_tx: mission.blockchain_tx_id,
        };
        const response = await apiClient.updateMission(mission.id, payload);
        if (response.success && response.data) {
          setMissions((prev) =>
            prev.map((m) => (m.id === mission.id ? response.data! : m))
          );
          return response.data;
        }
        setError(response.message || "Failed to update mission");
        return null;
      } catch (err: any) {
        setError(err.message || "Failed to update mission");
        console.error("Error updating mission:", err);
        return null;
      }
    },
    []
  );

  // Delete mission
  const deleteMission = useCallback(async (id: string): Promise<boolean> => {
    try {
      const response = await apiClient.deleteMission(id);
      if (response.success) {
        setMissions((prev) => prev.filter((m) => m.id !== id));
        return true;
      }
      setError(response.message || "Failed to delete mission");
      return false;
    } catch (err: any) {
      setError(err.message || "Failed to delete mission");
      console.error("Error deleting mission:", err);
      return false;
    }
  }, []);

  // Auto-refresh missions periodically
  useEffect(() => {
    fetchMissions();
    const interval = setInterval(fetchMissions, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchMissions]);

  return {
    missions,
    isLoading,
    error,
    fetchMissions,
    createMission,
    updateMission,
    deleteMission,
  };
};
