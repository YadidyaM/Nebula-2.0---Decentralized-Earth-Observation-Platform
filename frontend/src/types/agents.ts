// Agent Types
export enum AgentRarity {
  COMMON = "common",
  RARE = "rare",
  EPIC = "epic",
  LEGENDARY = "legendary",
}

export enum AgentStatus {
  IDLE = "idle",
  ACTIVE = "active",
  MAINTENANCE = "maintenance",
  OFFLINE = "offline",
}

export enum AgentType {
  FOREST_GUARDIAN = "Forest Guardian",
  ICE_SENTINEL = "Ice Sentinel",
  STORM_TRACKER = "Storm Tracker",
  URBAN_MONITOR = "Urban Monitor",
  WATER_WATCHER = "Water Watcher",
  SECURITY_SENTINEL = "Security Sentinel",
  LAND_SURVEYOR = "Land Surveyor",
  DISASTER_RESPONDER = "Disaster Responder",
  ORCHESTRATOR = "Orchestrator Agent",
}

export interface AgentPosition {
  latitude: number;
  longitude: number;
  altitude?: number;
}

export interface AgentPerformance {
  missions_completed: number;
  success_rate: number; // 0-1
  average_confidence: number; // 0-1
  uptime_percentage: number; // 0-100
  last_performance_update: string; // ISO string
}

export interface Agent {
  id?: string;
  name: string;
  type: AgentType;
  rarity: AgentRarity;
  status: AgentStatus;
  solana_address: string;
  current_mission_id?: string;
  last_seen: string; // ISO string
  position?: AgentPosition;
  performance: AgentPerformance;
  staking_status?: "staked" | "unstaked";
  nft_mint_address?: string;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

// Agent NFT Types
export interface AgentNFTMetadata {
  name: string;
  description: string;
  image: string;
  rarity: AgentRarity;
  agent_type: AgentType;
  attributes: Array<{
    trait_type: string;
    value: string | number;
  }>;
  performance: AgentPerformance;
  mint_address: string;
  owner_address: string;
  staking_status: "staked" | "unstaked";
  staking_rewards: number;
  purchase_price: number; // in $NEBULA tokens
}

// Agent Update Types
export interface UpdateAgentStatusRequest {
  status: AgentStatus;
  position?: AgentPosition;
  current_mission_id?: string;
}

export interface AgentStakingRequest {
  agent_id: string;
  action: "stake" | "unstake";
  amount?: number; // for partial staking
}

// Agent Filter Types
export interface AgentFilters {
  status?: AgentStatus[];
  type?: AgentType[];
  rarity?: AgentRarity[];
  staking_status?: ("staked" | "unstaked")[];
}

export interface AgentListResponse {
  agents: Agent[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}
