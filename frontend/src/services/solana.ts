import {
  Connection,
  PublicKey,
  Transaction,
  Keypair,
  SystemProgram,
  LAMPORTS_PER_SOL,
  sendAndConfirmTransaction,
  TransactionInstruction,
} from "@solana/web3.js";
import { WalletInfo, NFTMetadata, StakingInfo, TokenEconomics } from "../types";

class SolanaClient {
  private connection: Connection | null = null;
  private network: "devnet" | "mainnet-beta" = "devnet";
  private rpcUrl: string;

  constructor() {
    this.rpcUrl =
      import.meta.env.VITE_SOLANA_RPC_URL || "https://api.devnet.solana.com";
    this.network =
      (import.meta.env.VITE_SOLANA_NETWORK as "devnet" | "mainnet-beta") ||
      "devnet";
    this.initializeConnection();
  }

  private initializeConnection() {
    try {
      this.connection = new Connection(this.rpcUrl, "confirmed");
      console.log(`Connected to Solana ${this.network} at ${this.rpcUrl}`);
    } catch (error) {
      console.error("Failed to initialize Solana connection:", error);
    }
  }

  // Connection Management
  async connect(): Promise<boolean> {
    if (!this.connection) {
      this.initializeConnection();
    }

    try {
      const version = await this.connection!.getVersion();
      console.log("Solana RPC version:", version);
      return true;
    } catch (error) {
      console.error("Failed to connect to Solana:", error);
      return false;
    }
  }

  getConnection(): Connection | null {
    return this.connection;
  }

  getNetwork(): string {
    return this.network;
  }

  // Wallet Operations
  async getBalance(publicKey: PublicKey): Promise<number> {
    if (!this.connection) {
      throw new Error("Solana connection not initialized");
    }

    try {
      const balance = await this.connection.getBalance(publicKey);
      return balance / LAMPORTS_PER_SOL;
    } catch (error) {
      console.error("Error getting balance:", error);
      throw error;
    }
  }

  async getTokenBalance(
    publicKey: PublicKey,
    mintAddress: string
  ): Promise<number> {
    if (!this.connection) {
      throw new Error("Solana connection not initialized");
    }

    try {
      // This would require SPL Token program integration
      // For now, return a mock value
      console.log(
        `Getting token balance for ${publicKey.toString()} - mint: ${mintAddress}`
      );
      return 1000; // Mock token balance
    } catch (error) {
      console.error("Error getting token balance:", error);
      throw error;
    }
  }

  async getWalletInfo(publicKey: PublicKey): Promise<WalletInfo> {
    const [solBalance, tokenBalance] = await Promise.all([
      this.getBalance(publicKey),
      this.getTokenBalance(publicKey, "NEBULA_TOKEN_MINT"), // Replace with actual mint
    ]);

    return {
      publicKey: publicKey.toString(),
      connected: true,
      balance: solBalance,
      tokenBalance,
      network: this.network,
    };
  }

  // Transaction Operations
  async sendTransaction(
    transaction: Transaction,
    signers: Keypair[]
  ): Promise<string> {
    if (!this.connection) {
      throw new Error("Solana connection not initialized");
    }

    try {
      const signature = await sendAndConfirmTransaction(
        this.connection,
        transaction,
        signers,
        {
          commitment: "confirmed",
          preflightCommitment: "confirmed",
        }
      );

      console.log("Transaction confirmed:", signature);
      return signature;
    } catch (error) {
      console.error("Transaction failed:", error);
      throw error;
    }
  }

  async createTransferTransaction(
    from: PublicKey,
    to: PublicKey,
    amount: number
  ): Promise<Transaction> {
    const transaction = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: from,
        toPubkey: to,
        lamports: amount * LAMPORTS_PER_SOL,
      })
    );

    return transaction;
  }

  // Mission Recording
  async recordMissionOnBlockchain(
    missionId: string,
    dataHash: string,
    agentPublicKey: PublicKey
  ): Promise<string> {
    if (!this.connection) {
      throw new Error("Solana connection not initialized");
    }

    try {
      // This would interact with a custom Solana program
      // For now, create a simple transfer transaction as a placeholder
      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: agentPublicKey,
          toPubkey: new PublicKey("11111111111111111111111111111111"), // System program
          lamports: 1, // Minimal amount
        })
      );

      // In a real implementation, you would:
      // 1. Create a custom instruction to store the mission data hash
      // 2. Use the mission registry program
      // 3. Include the data hash in the instruction data

      console.log(
        `Recording mission ${missionId} with hash ${dataHash} on blockchain`
      );

      // For now, return a mock transaction signature
      return `mock_tx_${Date.now()}`;
    } catch (error) {
      console.error("Error recording mission on blockchain:", error);
      throw error;
    }
  }

  // NFT Operations
  async getNFTMetadata(mintAddress: string): Promise<NFTMetadata | null> {
    try {
      // This would use Metaplex or similar to fetch NFT metadata
      // For now, return mock data
      return {
        name: "Agent NFT",
        symbol: "AGENT",
        description: "Nebula Protocol Agent NFT",
        image: "https://via.placeholder.com/300x300",
        attributes: [
          { trait_type: "Rarity", value: "Rare" },
          { trait_type: "Type", value: "Forest Guardian" },
        ],
      };
    } catch (error) {
      console.error("Error fetching NFT metadata:", error);
      return null;
    }
  }

  async mintNFT(
    recipient: PublicKey,
    metadata: NFTMetadata,
    signer: Keypair
  ): Promise<string> {
    try {
      // This would use Metaplex to mint an NFT
      // For now, return a mock transaction signature
      console.log(`Minting NFT for ${recipient.toString()}`);
      return `mock_nft_mint_${Date.now()}`;
    } catch (error) {
      console.error("Error minting NFT:", error);
      throw error;
    }
  }

  // Staking Operations
  async stakeAgent(
    agentId: string,
    amount: number,
    stakerPublicKey: PublicKey
  ): Promise<string> {
    try {
      // This would interact with a staking program
      console.log(`Staking agent ${agentId} with amount ${amount}`);
      return `mock_stake_${Date.now()}`;
    } catch (error) {
      console.error("Error staking agent:", error);
      throw error;
    }
  }

  async unstakeAgent(
    agentId: string,
    stakerPublicKey: PublicKey
  ): Promise<string> {
    try {
      // This would interact with a staking program
      console.log(`Unstaking agent ${agentId}`);
      return `mock_unstake_${Date.now()}`;
    } catch (error) {
      console.error("Error unstaking agent:", error);
      throw error;
    }
  }

  async getStakingInfo(
    agentId: string,
    stakerPublicKey: PublicKey
  ): Promise<StakingInfo | null> {
    try {
      // This would query the staking program
      return {
        agent_id: agentId,
        staked_amount: 1000,
        staking_period: 30,
        reward_rate: 10,
        last_reward_claim: new Date().toISOString(),
        total_rewards_earned: 100,
        staking_status: "active",
      };
    } catch (error) {
      console.error("Error getting staking info:", error);
      return null;
    }
  }

  // Token Economics
  async getTokenEconomics(): Promise<TokenEconomics> {
    try {
      // This would fetch real token economics data
      return {
        total_supply: 1000000000,
        circulating_supply: 500000000,
        staking_rewards: {
          daily_rate: 0.1,
          annual_rate: 36.5,
        },
        mission_rewards: {
          completion_reward: 100,
          verification_bonus: 50,
        },
        nft_pricing: {
          common: 1000,
          rare: 5000,
          epic: 25000,
          legendary: 100000,
        },
      };
    } catch (error) {
      console.error("Error getting token economics:", error);
      throw error;
    }
  }

  // Utility Methods
  isValidAddress(address: string): boolean {
    try {
      new PublicKey(address);
      return true;
    } catch {
      return false;
    }
  }

  async getRecentBlockhash(): Promise<string> {
    if (!this.connection) {
      throw new Error("Solana connection not initialized");
    }

    try {
      const { blockhash } = await this.connection.getRecentBlockhash();
      return blockhash;
    } catch (error) {
      console.error("Error getting recent blockhash:", error);
      throw error;
    }
  }

  // Error Handling
  private handleError(error: any): never {
    console.error("Solana client error:", error);
    throw new Error(`Solana operation failed: ${error.message}`);
  }
}

// Create singleton instance
export const solanaClient = new SolanaClient();
export default solanaClient;
