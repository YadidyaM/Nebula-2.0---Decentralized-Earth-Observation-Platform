// Telemetry Types
export interface Position {
  latitude: number;
  longitude: number;
  altitude?: number;
}

export interface Velocity {
  x: number; // m/s
  y: number; // m/s
  z: number; // m/s
}

export interface SensorData {
  temperature?: number; // Celsius
  humidity?: number; // Percentage
  pressure?: number; // hPa
  battery_level?: number; // Percentage
  signal_strength?: number; // 0-1
  cpu_usage?: number; // Percentage
  memory_usage?: number; // Percentage
  disk_usage?: number; // Percentage
}

export interface TelemetryData {
  id?: string;
  agent_id: string;
  timestamp: string; // ISO string
  position: Position;
  velocity?: Velocity;
  sensors: SensorData;
  mission_id?: string;
  data_quality: number; // 0-1
  created_at: string; // ISO string
}

// Telemetry Trends
export interface TelemetryTrend {
  metric: string;
  values: Array<{
    timestamp: string;
    value: number;
  }>;
  unit: string;
  color: string;
}

export interface TelemetryTrendsResponse {
  trends: TelemetryTrend[];
  time_range: {
    start: string;
    end: string;
  };
  resolution: "minute" | "hour" | "day";
}

// Orbital Pass Types
export interface OrbitalPass {
  id: string;
  satellite_name: string;
  pass_start: string; // ISO string
  pass_end: string; // ISO string
  max_elevation: number; // degrees
  duration: number; // minutes
  azimuth_start: number; // degrees
  azimuth_end: number; // degrees
  location: {
    latitude: number;
    longitude: number;
    name: string;
  };
}

export interface OrbitalPassPrediction {
  passes: OrbitalPass[];
  location: {
    latitude: number;
    longitude: number;
    name: string;
  };
  prediction_period: {
    start: string;
    end: string;
  };
}

// Risk Data Types
export enum RiskType {
  FLOOD = "flood",
  DROUGHT = "drought",
  WILDFIRE = "wildfire",
  EARTHQUAKE = "earthquake",
  STORM = "storm",
  HEATWAVE = "heatwave",
  LANDSLIDE = "landslide",
  TSUNAMI = "tsunami",
}

export enum RiskLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface RiskPoint {
  id: string;
  type: RiskType;
  level: RiskLevel;
  latitude: number;
  longitude: number;
  confidence: number; // 0-1
  detected_at: string; // ISO string
  description?: string;
  affected_area_km2?: number;
  estimated_damage?: number; // USD
  source: string; // NASA, NOAA, etc.
}

export interface RiskHeatmapData {
  risks: RiskPoint[];
  time_range: {
    start: string;
    end: string;
  };
  total_risks: number;
  risk_distribution: Record<RiskType, number>;
}

// Satellite Telemetry Panel Types
export interface SatelliteStatus {
  satellite_id: string;
  name: string;
  position: Position;
  velocity: Velocity;
  sensors: SensorData;
  last_update: string;
  status: "operational" | "maintenance" | "offline";
  mission_status?: string;
}

// Telemetry Filter Types
export interface TelemetryFilters {
  agent_id?: string;
  mission_id?: string;
  time_range?: {
    start: string;
    end: string;
  };
  data_quality_min?: number;
  sensor_types?: string[];
}

export interface TelemetryListResponse {
  telemetry: TelemetryData[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}
