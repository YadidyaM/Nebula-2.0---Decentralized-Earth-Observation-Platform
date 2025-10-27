import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import {
  Mission,
  CreateMissionRequest,
  UpdateMissionRequest,
  MissionListResponse,
  MissionFilters,
  Agent,
  UpdateAgentStatusRequest,
  AgentListResponse,
  AgentFilters,
  TelemetryData,
  TelemetryListResponse,
  TelemetryFilters,
  TelemetryTrendsResponse,
  BlockchainRecord,
  CreateTransactionRequest,
  RecordDataHashRequest,
  BlockchainListResponse,
  BlockchainFilters,
  ApiResponse,
  ApiError,
} from "../types";

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem("auth_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request timestamp
        config.metadata = { startTime: Date.now() };

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log response time
        const duration = Date.now() - response.config.metadata?.startTime;
        console.log(
          `API ${response.config.method?.toUpperCase()} ${
            response.config.url
          } - ${duration}ms`
        );

        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Retry logic for network errors
        if (error.code === "NETWORK_ERROR" && !originalRequest._retry) {
          originalRequest._retry = true;
          await this.delay(1000);
          return this.client(originalRequest);
        }

        // Handle different error types
        if (error.response) {
          const apiError: ApiError = {
            code: error.response.data?.code || "UNKNOWN_ERROR",
            message: error.response.data?.message || error.message,
            details: error.response.data?.details,
            timestamp: new Date().toISOString(),
          };
          throw apiError;
        } else if (error.request) {
          const apiError: ApiError = {
            code: "NETWORK_ERROR",
            message: "Network error - please check your connection",
            timestamp: new Date().toISOString(),
          };
          throw apiError;
        } else {
          const apiError: ApiError = {
            code: "CLIENT_ERROR",
            message: error.message,
            timestamp: new Date().toISOString(),
          };
          throw apiError;
        }
      }
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Mission API Methods
  async getMissions(
    filters?: MissionFilters,
    page = 1,
    limit = 20
  ): Promise<MissionListResponse> {
    const params = new URLSearchParams();

    if (filters?.status) {
      filters.status.forEach((status) => params.append("status", status));
    }
    if (filters?.type) {
      filters.type.forEach((type) => params.append("type", type));
    }
    if (filters?.priority) {
      filters.priority.forEach((priority) =>
        params.append("priority", priority)
      );
    }
    if (filters?.date_range) {
      params.append("start_date", filters.date_range.start);
      params.append("end_date", filters.date_range.end);
    }
    if (filters?.location) {
      params.append("lat", filters.location.lat.toString());
      params.append("lng", filters.location.lng.toString());
      params.append("radius", filters.location.radius_km.toString());
    }

    params.append("page", page.toString());
    params.append("limit", limit.toString());

    const response = await this.client.get(`/missions?${params.toString()}`);
    return response.data;
  }

  async getMission(id: string): Promise<Mission> {
    const response = await this.client.get(`/missions/${id}`);
    return response.data;
  }

  async createMission(mission: CreateMissionRequest): Promise<Mission> {
    const response = await this.client.post("/missions", mission);
    return response.data;
  }

  async updateMission(
    id: string,
    updates: UpdateMissionRequest
  ): Promise<Mission> {
    const response = await this.client.put(`/missions/${id}`, updates);
    return response.data;
  }

  async deleteMission(id: string): Promise<void> {
    await this.client.delete(`/missions/${id}`);
  }

  // Agent API Methods
  async getAgents(
    filters?: AgentFilters,
    page = 1,
    limit = 20
  ): Promise<AgentListResponse> {
    const params = new URLSearchParams();

    if (filters?.status) {
      filters.status.forEach((status) => params.append("status", status));
    }
    if (filters?.type) {
      filters.type.forEach((type) => params.append("type", type));
    }
    if (filters?.rarity) {
      filters.rarity.forEach((rarity) => params.append("rarity", rarity));
    }
    if (filters?.staking_status) {
      filters.staking_status.forEach((status) =>
        params.append("staking_status", status)
      );
    }

    params.append("page", page.toString());
    params.append("limit", limit.toString());

    const response = await this.client.get(`/agents?${params.toString()}`);
    return response.data;
  }

  async getAgent(id: string): Promise<Agent> {
    const response = await this.client.get(`/agents/${id}`);
    return response.data;
  }

  async updateAgentStatus(
    id: string,
    updates: UpdateAgentStatusRequest
  ): Promise<Agent> {
    const response = await this.client.put(`/agents/${id}/status`, updates);
    return response.data;
  }

  async activateAgent(id: string): Promise<Agent> {
    return this.updateAgentStatus(id, { status: "active" });
  }

  async deactivateAgent(id: string): Promise<Agent> {
    return this.updateAgentStatus(id, { status: "idle" });
  }

  // Telemetry API Methods
  async getTelemetry(
    filters?: TelemetryFilters,
    page = 1,
    limit = 100
  ): Promise<TelemetryListResponse> {
    const params = new URLSearchParams();

    if (filters?.agent_id) {
      params.append("agent_id", filters.agent_id);
    }
    if (filters?.mission_id) {
      params.append("mission_id", filters.mission_id);
    }
    if (filters?.time_range) {
      params.append("start_time", filters.time_range.start);
      params.append("end_time", filters.time_range.end);
    }
    if (filters?.data_quality_min) {
      params.append("data_quality_min", filters.data_quality_min.toString());
    }
    if (filters?.sensor_types) {
      filters.sensor_types.forEach((type) =>
        params.append("sensor_type", type)
      );
    }

    params.append("page", page.toString());
    params.append("limit", limit.toString());

    const response = await this.client.get(`/telemetry?${params.toString()}`);
    return response.data;
  }

  async getTelemetryTrends(
    timeRange: "1h" | "6h" | "24h" | "7d",
    agentId?: string
  ): Promise<TelemetryTrendsResponse> {
    const params = new URLSearchParams();
    params.append("time_range", timeRange);
    if (agentId) {
      params.append("agent_id", agentId);
    }

    const response = await this.client.get(
      `/telemetry/trends?${params.toString()}`
    );
    return response.data;
  }

  async createTelemetryData(
    telemetry: Omit<TelemetryData, "id" | "created_at">
  ): Promise<TelemetryData> {
    const response = await this.client.post("/telemetry", telemetry);
    return response.data;
  }

  // Blockchain API Methods
  async getBlockchainRecords(
    filters?: BlockchainFilters,
    page = 1,
    limit = 20
  ): Promise<BlockchainListResponse> {
    const params = new URLSearchParams();

    if (filters?.transaction_type) {
      filters.transaction_type.forEach((type) => params.append("type", type));
    }
    if (filters?.status) {
      filters.status.forEach((status) => params.append("status", status));
    }
    if (filters?.solana_address) {
      params.append("solana_address", filters.solana_address);
    }
    if (filters?.date_range) {
      params.append("start_date", filters.date_range.start);
      params.append("end_date", filters.date_range.end);
    }

    params.append("page", page.toString());
    params.append("limit", limit.toString());

    const response = await this.client.get(
      `/blockchain/records?${params.toString()}`
    );
    return response.data;
  }

  async createTransaction(
    transaction: CreateTransactionRequest
  ): Promise<BlockchainRecord> {
    const response = await this.client.post(
      "/blockchain/transactions",
      transaction
    );
    return response.data;
  }

  async recordDataHash(
    request: RecordDataHashRequest
  ): Promise<BlockchainRecord> {
    const response = await this.client.post("/blockchain/record-hash", request);
    return response.data;
  }

  // Risk API Methods
  async getRiskData(timeRange?: string, riskType?: string): Promise<any> {
    const params = new URLSearchParams();
    if (timeRange) params.append("time_range", timeRange);
    if (riskType) params.append("risk_type", riskType);

    const response = await this.client.get(`/risks?${params.toString()}`);
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }

  // Utility Methods
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.client.post(endpoint, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  }

  // Cancel all pending requests
  cancelAllRequests() {
    // This would require implementing request cancellation
    // For now, we'll just log it
    console.log("Cancelling all pending requests");
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
export default apiClient;
