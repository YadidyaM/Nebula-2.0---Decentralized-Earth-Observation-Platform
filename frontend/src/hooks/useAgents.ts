import { useState, useEffect, useCallback } from "react";
import { apiClient } from "../services/api";
import { Agent } from "../types/agents";

interface UseAgentsReturn {
  agents: Agent[];
  isLoading: boolean;
  error: string | null;
  fetchAgents: () => Promise<void>;
  getAgent: (id: string) => Promise<Agent | null>;
  activateAgent: (id: string) => Promise<Agent | null>;
  deactivateAgent: (id: string) => Promise<Agent | null>;
}

export const useAgents = (): UseAgentsReturn => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch agents
  const fetchAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getAgents();
      if (response.success && response.data) {
        setAgents(response.data);
      } else {
        setError(response.message || "Failed to fetch agents");
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch agents");
      console.error("Error fetching agents:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Get single agent
  const getAgent = useCallback(async (id: string): Promise<Agent | null> => {
    try {
      const response = await apiClient.getAgent(id);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (err: any) {
      setError(err.message || "Failed to fetch agent");
      console.error("Error fetching agent:", err);
      return null;
    }
  }, []);

  // Activate agent
  const activateAgent = useCallback(
    async (id: string): Promise<Agent | null> => {
      try {
        // Mock implementation - in real app, this would call an API
        const agent = agents.find((a) => a.id === id);
        if (agent) {
          const updatedAgent = { ...agent, status: "active" as const };
          setAgents((prev) =>
            prev.map((a) => (a.id === id ? updatedAgent : a))
          );
          return updatedAgent;
        }
        return null;
      } catch (err: any) {
        setError(err.message || "Failed to activate agent");
        console.error("Error activating agent:", err);
        return null;
      }
    },
    [agents]
  );

  // Deactivate agent
  const deactivateAgent = useCallback(
    async (id: string): Promise<Agent | null> => {
      try {
        // Mock implementation - in real app, this would call an API
        const agent = agents.find((a) => a.id === id);
        if (agent) {
          const updatedAgent = { ...agent, status: "idle" as const };
          setAgents((prev) =>
            prev.map((a) => (a.id === id ? updatedAgent : a))
          );
          return updatedAgent;
        }
        return null;
      } catch (err: any) {
        setError(err.message || "Failed to deactivate agent");
        console.error("Error deactivating agent:", err);
        return null;
      }
    },
    [agents]
  );

  // Auto-refresh agents periodically
  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchAgents]);

  return {
    agents,
    isLoading,
    error,
    fetchAgents,
    getAgent,
    activateAgent,
    deactivateAgent,
  };
};
