// Blockchain Types
export enum TransactionType {
  MISSION_COMPLETION = "mission_completion",
  NFT_MINT = "nft_mint",
  NFT_STAKE = "nft_stake",
  TOKEN_TRANSFER = "token_transfer",
  DATA_HASH_RECORD = "data_hash_record",
  REWARD_DISTRIBUTION = "reward_distribution",
}

export interface BlockchainRecord {
  id?: string;
  transaction_id: string;
  transaction_type: TransactionType;
  timestamp: string; // ISO string
  solana_address: string;
  related_entity_id?: string; // mission_id, agent_id, etc.
  data_hash?: string; // IPFS/Arweave hash
  status: "pending" | "confirmed" | "failed";
  details?: Record<string, any>;
  block_height?: number;
  signature?: string;
  created_at: string; // ISO string
}

// Solana Wallet Types
export interface WalletInfo {
  publicKey: string;
  connected: boolean;
  balance: number; // SOL balance
  tokenBalance: number; // $NEBULA token balance
  network: "devnet" | "mainnet-beta";
}

// NFT Types
export interface NFTMetadata {
  name: string;
  symbol: string;
  description: string;
  image: string;
  external_url?: string;
  attributes: Array<{
    trait_type: string;
    value: string | number;
  }>;
  properties?: Record<string, any>;
}

export interface NFTCollection {
  name: string;
  symbol: string;
  description: string;
  image: string;
  total_supply: number;
  minted_count: number;
  floor_price: number;
  volume_traded: number;
}

// Staking Types
export interface StakingInfo {
  agent_id: string;
  staked_amount: number;
  staking_period: number; // in days
  reward_rate: number; // APY percentage
  last_reward_claim: string; // ISO string
  total_rewards_earned: number;
  staking_status: "active" | "inactive" | "pending";
}

export interface StakingPool {
  pool_id: string;
  total_staked: number;
  total_rewards: number;
  reward_rate: number; // APY percentage
  participants: number;
  lock_period: number; // in days
}

// Token Economics
export interface TokenEconomics {
  total_supply: number;
  circulating_supply: number;
  staking_rewards: {
    daily_rate: number;
    annual_rate: number;
  };
  mission_rewards: {
    completion_reward: number;
    verification_bonus: number;
  };
  nft_pricing: {
    common: number;
    rare: number;
    epic: number;
    legendary: number;
  };
}

// Transaction Request Types
export interface CreateTransactionRequest {
  type: TransactionType;
  solana_address: string;
  related_entity_id?: string;
  data_hash?: string;
  details?: Record<string, any>;
}

export interface RecordDataHashRequest {
  mission_id: string;
  data_hash: string;
  storage_type: "ipfs" | "arweave";
  solana_address: string;
}

// Blockchain Filter Types
export interface BlockchainFilters {
  transaction_type?: TransactionType[];
  status?: ("pending" | "confirmed" | "failed")[];
  solana_address?: string;
  date_range?: {
    start: string;
    end: string;
  };
}

export interface BlockchainListResponse {
  records: BlockchainRecord[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}
