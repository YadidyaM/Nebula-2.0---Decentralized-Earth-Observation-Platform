// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// Error Types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// WebSocket Message Types
export enum WebSocketMessageType {
  MISSION_UPDATE = "mission_update",
  AGENT_STATUS_UPDATE = "agent_status_update",
  TELEMETRY_UPDATE = "telemetry_update",
  RISK_ALERT = "risk_alert",
  SYSTEM_ALERT = "system_alert",
  BLOCKCHAIN_UPDATE = "blockchain_update",
  CHAT_MESSAGE = "chat_message",
  VOICE_COMMAND = "voice_command",
}

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: any;
  timestamp: string;
  id?: string;
}

// Chat Types
export enum ChatMode {
  MONITOR = "monitor",
  INTERACTIVE = "interactive",
}

export enum MessageType {
  AUTONOMOUS = "autonomous",
  COMMAND = "command",
  RESPONSE = "response",
  ERROR = "error",
  SYSTEM = "system",
}

export interface ChatMessage {
  id: string;
  type: MessageType;
  content: string;
  timestamp: string;
  sender?: string;
  metadata?: Record<string, any>;
}

// Voice Command Types
export interface VoiceCommand {
  id: string;
  text: string;
  confidence: number; // 0-1
  timestamp: string;
  processed: boolean;
  response?: string;
}

// System Alert Types
export enum AlertType {
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  SUCCESS = "success",
}

export interface SystemAlert {
  id: string;
  type: AlertType;
  title: string;
  message: string;
  timestamp: string;
  dismissed: boolean;
  auto_dismiss?: boolean;
  dismiss_after?: number; // seconds
}

// UI State Types
export interface PanelState {
  activePanel: string | null;
  panelsVisible: boolean;
  chatMinimized: boolean;
  chatMode: ChatMode;
}

export interface ThemeSettings {
  colorScheme: "dark" | "light";
  primaryColor: string;
  animationsEnabled: boolean;
  holographicEffects: boolean;
}

// Form Types
export interface MissionFormData {
  name: string;
  type: string;
  priority: string;
  target_area: {
    latitude: number;
    longitude: number;
    radius_km: number;
    description: string;
  };
  assigned_agents: string[];
}

export interface AgentFormData {
  name: string;
  type: string;
  rarity: string;
  position?: {
    latitude: number;
    longitude: number;
    altitude?: number;
  };
}

// Filter Types
export interface FilterState {
  missions: {
    status: string[];
    type: string[];
    priority: string[];
    dateRange?: {
      start: string;
      end: string;
    };
  };
  agents: {
    status: string[];
    type: string[];
    rarity: string[];
  };
  telemetry: {
    timeRange?: {
      start: string;
      end: string;
    };
    dataQualityMin: number;
  };
}

// Settings Types
export interface UserSettings {
  theme: ThemeSettings;
  notifications: {
    missionUpdates: boolean;
    agentAlerts: boolean;
    riskAlerts: boolean;
    soundEnabled: boolean;
  };
  voice: {
    enabled: boolean;
    language: string;
    autoProcess: boolean;
  };
  performance: {
    animationsEnabled: boolean;
    holographicEffects: boolean;
    dataRefreshRate: number; // seconds
  };
}

// Export all types
export * from "./missions";
export * from "./agents";
export * from "./blockchain";
export * from "./telemetry";
