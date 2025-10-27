import { useState, useEffect, useCallback } from "react";
import { PublicKey } from "@solana/web3.js";
import { solanaClient } from "../services/solana";
import { WalletInfo, StakingInfo, TokenEconomics } from "../types";

interface UseWalletReturn {
  walletInfo: WalletInfo | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  refreshBalance: () => Promise<void>;
  sendTransaction: (to: string, amount: number) => Promise<string>;
  stakeAgent: (agentId: string, amount: number) => Promise<string>;
  unstakeAgent: (agentId: string) => Promise<string>;
  getStakingInfo: (agentId: string) => Promise<StakingInfo | null>;
  getTokenEconomics: () => Promise<TokenEconomics | null>;
}

export const useWallet = (): UseWalletReturn => {
  const [walletInfo, setWalletInfo] = useState<WalletInfo | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Connect wallet
  const connect = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Check if wallet is available (Phantom, Solflare, etc.)
      if (typeof window !== "undefined" && (window as any).solana) {
        const wallet = (window as any).solana;

        // Request connection
        const response = await wallet.connect();
        const publicKey = new PublicKey(response.publicKey.toString());

        // Get wallet info
        const info = await solanaClient.getWalletInfo(publicKey);
        setWalletInfo(info);
        setIsConnected(true);

        // Store connection state
        localStorage.setItem("wallet_connected", "true");
        localStorage.setItem("wallet_public_key", publicKey.toString());

        console.log("Wallet connected:", publicKey.toString());
      } else {
        throw new Error(
          "Solana wallet not found. Please install Phantom or Solflare."
        );
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect wallet");
      console.error("Wallet connection error:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Disconnect wallet
  const disconnect = useCallback(() => {
    try {
      if (typeof window !== "undefined" && (window as any).solana) {
        (window as any).solana.disconnect();
      }

      setWalletInfo(null);
      setIsConnected(false);
      setError(null);

      // Clear stored state
      localStorage.removeItem("wallet_connected");
      localStorage.removeItem("wallet_public_key");

      console.log("Wallet disconnected");
    } catch (err: any) {
      console.error("Wallet disconnection error:", err);
    }
  }, []);

  // Refresh balance
  const refreshBalance = useCallback(async () => {
    if (!walletInfo?.publicKey) return;

    try {
      const publicKey = new PublicKey(walletInfo.publicKey);
      const info = await solanaClient.getWalletInfo(publicKey);
      setWalletInfo(info);
    } catch (err: any) {
      setError(err.message || "Failed to refresh balance");
      console.error("Balance refresh error:", err);
    }
  }, [walletInfo?.publicKey]);

  // Send transaction
  const sendTransaction = useCallback(
    async (to: string, amount: number): Promise<string> => {
      if (!walletInfo?.publicKey) {
        throw new Error("Wallet not connected");
      }

      try {
        const fromPublicKey = new PublicKey(walletInfo.publicKey);
        const toPublicKey = new PublicKey(to);

        const transaction = await solanaClient.createTransferTransaction(
          fromPublicKey,
          toPublicKey,
          amount
        );

        // Sign and send transaction
        const signature = await solanaClient.sendTransaction(transaction, []);

        // Refresh balance after successful transaction
        await refreshBalance();

        return signature;
      } catch (err: any) {
        setError(err.message || "Transaction failed");
        throw err;
      }
    },
    [walletInfo?.publicKey, refreshBalance]
  );

  // Stake agent
  const stakeAgent = useCallback(
    async (agentId: string, amount: number): Promise<string> => {
      if (!walletInfo?.publicKey) {
        throw new Error("Wallet not connected");
      }

      try {
        const publicKey = new PublicKey(walletInfo.publicKey);
        const signature = await solanaClient.stakeAgent(
          agentId,
          amount,
          publicKey
        );

        // Refresh balance after successful staking
        await refreshBalance();

        return signature;
      } catch (err: any) {
        setError(err.message || "Staking failed");
        throw err;
      }
    },
    [walletInfo?.publicKey, refreshBalance]
  );

  // Unstake agent
  const unstakeAgent = useCallback(
    async (agentId: string): Promise<string> => {
      if (!walletInfo?.publicKey) {
        throw new Error("Wallet not connected");
      }

      try {
        const publicKey = new PublicKey(walletInfo.publicKey);
        const signature = await solanaClient.unstakeAgent(agentId, publicKey);

        // Refresh balance after successful unstaking
        await refreshBalance();

        return signature;
      } catch (err: any) {
        setError(err.message || "Unstaking failed");
        throw err;
      }
    },
    [walletInfo?.publicKey, refreshBalance]
  );

  // Get staking info
  const getStakingInfo = useCallback(
    async (agentId: string): Promise<StakingInfo | null> => {
      if (!walletInfo?.publicKey) {
        return null;
      }

      try {
        const publicKey = new PublicKey(walletInfo.publicKey);
        return await solanaClient.getStakingInfo(agentId, publicKey);
      } catch (err: any) {
        console.error("Error getting staking info:", err);
        return null;
      }
    },
    [walletInfo?.publicKey]
  );

  // Get token economics
  const getTokenEconomics =
    useCallback(async (): Promise<TokenEconomics | null> => {
      try {
        return await solanaClient.getTokenEconomics();
      } catch (err: any) {
        console.error("Error getting token economics:", err);
        return null;
      }
    }, []);

  // Auto-connect on mount if previously connected
  useEffect(() => {
    const wasConnected = localStorage.getItem("wallet_connected") === "true";
    const publicKeyStr = localStorage.getItem("wallet_public_key");

    if (wasConnected && publicKeyStr) {
      try {
        const publicKey = new PublicKey(publicKeyStr);
        solanaClient
          .getWalletInfo(publicKey)
          .then((info) => {
            setWalletInfo(info);
            setIsConnected(true);
          })
          .catch(() => {
            // Clear invalid stored state
            localStorage.removeItem("wallet_connected");
            localStorage.removeItem("wallet_public_key");
          });
      } catch {
        // Clear invalid stored state
        localStorage.removeItem("wallet_connected");
        localStorage.removeItem("wallet_public_key");
      }
    }
  }, []);

  // Listen for wallet events
  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).solana) {
      const wallet = (window as any).solana;

      const handleAccountChange = (publicKey: PublicKey | null) => {
        if (publicKey) {
          solanaClient.getWalletInfo(publicKey).then((info) => {
            setWalletInfo(info);
            setIsConnected(true);
          });
        } else {
          disconnect();
        }
      };

      const handleDisconnect = () => {
        disconnect();
      };

      wallet.on("accountChanged", handleAccountChange);
      wallet.on("disconnect", handleDisconnect);

      return () => {
        wallet.off("accountChanged", handleAccountChange);
        wallet.off("disconnect", handleDisconnect);
      };
    }
  }, [disconnect]);

  // Periodic balance refresh
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(refreshBalance, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [isConnected, refreshBalance]);

  return {
    walletInfo,
    isConnected,
    isLoading,
    error,
    connect,
    disconnect,
    refreshBalance,
    sendTransaction,
    stakeAgent,
    unstakeAgent,
    getStakingInfo,
    getTokenEconomics,
  };
};
