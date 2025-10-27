// Mission Types
export enum MissionType {
  FORESTRY = "forestry",
  CRYOSPHERE = "cryosphere",
  DISASTER_MANAGEMENT = "disaster_management",
  SECURITY = "security",
  WEATHER = "weather",
  HYDROLOGY = "hydrology",
  URBAN_INFRASTRUCTURE = "urban_infrastructure",
  LAND_MONITORING = "land_monitoring",
}

export enum MissionStatus {
  PENDING = "pending",
  ACTIVE = "active",
  COMPLETED = "completed",
  FAILED = "failed",
  VERIFIED = "verified",
}

export enum Priority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface TargetArea {
  latitude: number;
  longitude: number;
  radius_km?: number;
  description?: string;
}

export interface MissionResults {
  data_hash: string; // IPFS/Arweave hash
  confidence_score: number; // 0-100
  anomaly_detected: boolean;
  report_url?: string;
  analysis_summary?: string;
  risk_level?: "low" | "medium" | "high" | "critical";
}

export interface Mission {
  id?: string;
  name: string;
  type: MissionType;
  status: MissionStatus;
  priority: Priority;
  target_area: TargetArea;
  assigned_agents: string[]; // List of agent IDs
  start_time: string; // ISO string
  end_time?: string; // ISO string
  results?: MissionResults;
  blockchain_tx_id?: string;
  verified: boolean;
  verified_at?: string; // ISO string
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Mission Creation/Update Types
export interface CreateMissionRequest {
  name: string;
  type: MissionType;
  priority: Priority;
  target_area: TargetArea;
  assigned_agents?: string[];
}

export interface UpdateMissionRequest {
  name?: string;
  status?: MissionStatus;
  priority?: Priority;
  assigned_agents?: string[];
  results?: MissionResults;
}

// Mission Filter Types
export interface MissionFilters {
  status?: MissionStatus[];
  type?: MissionType[];
  priority?: Priority[];
  date_range?: {
    start: string;
    end: string;
  };
  location?: {
    lat: number;
    lng: number;
    radius_km: number;
  };
}

export interface MissionListResponse {
  missions: Mission[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}
