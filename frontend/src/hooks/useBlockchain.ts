import { useState, useEffect, useCallback } from "react";
import { BlockchainRecord } from "../types/blockchain";
import { apiClient } from "../services/api";

export const useBlockchain = () => {
  const [records, setRecords] = useState<BlockchainRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getBlockchainRecords();
      if (response.success && response.data) {
        setRecords(response.data);
      } else {
        setError(response.message || "Failed to fetch blockchain records.");
      }
    } catch (err) {
      console.error("Error fetching blockchain records:", err);
      setError(
        "An unexpected error occurred while fetching blockchain records."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecords();
    const interval = setInterval(fetchRecords, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchRecords]);

  return { records, loading, error, fetchRecords };
};
