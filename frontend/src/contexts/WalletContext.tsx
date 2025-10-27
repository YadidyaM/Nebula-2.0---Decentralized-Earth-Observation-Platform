import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { 
  ConnectionProvider, 
  WalletProvider, 
  useWallet as useSolanaWallet,
  useConnection
} from '@solana/wallet-adapter-react'
import { 
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  TorusWalletAdapter,
  LedgerWalletAdapter,
  SlopeWalletAdapter
} from '@solana/wallet-adapter-wallets'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { 
  Connection, 
  PublicKey, 
  Transaction, 
  VersionedTransaction,
  LAMPORTS_PER_SOL 
} from '@solana/web3.js'
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base'

// Types
interface WalletContextType {
  connected: boolean
  connecting: boolean
  publicKey: PublicKey | null
  wallet: any
  balance: number
  network: WalletAdapterNetwork
  connect: () => Promise<void>
  disconnect: () => Promise<void>
  sendTransaction: (transaction: Transaction | VersionedTransaction) => Promise<string>
  signMessage: (message: Uint8Array) => Promise<Uint8Array>
  signTransaction: (transaction: Transaction) => Promise<Transaction>
  signAllTransactions: (transactions: Transaction[]) => Promise<Transaction[]>
  getBalance: () => Promise<number>
  setNetwork: (network: WalletAdapterNetwork) => void
  error: string | null
}

interface WalletProviderProps {
  children: React.ReactNode
}

// Create context
const WalletContext = createContext<WalletContextType | null>(null)

// Wallet configuration
const getNetwork = (): WalletAdapterNetwork => {
  const stored = localStorage.getItem('solana-network')
  if (stored === 'devnet' || stored === 'testnet' || stored === 'mainnet-beta') {
    return stored as WalletAdapterNetwork
  }
  return WalletAdapterNetwork.Devnet // Default to devnet
}

const getRpcEndpoint = (network: WalletAdapterNetwork): string => {
  switch (network) {
    case WalletAdapterNetwork.Mainnet:
      return import.meta.env.VITE_SOLANA_RPC_MAINNET || 'https://api.mainnet-beta.solana.com'
    case WalletAdapterNetwork.Devnet:
      return import.meta.env.VITE_SOLANA_RPC_DEVNET || 'https://api.devnet.solana.com'
    case WalletAdapterNetwork.Testnet:
      return import.meta.env.VITE_SOLANA_RPC_TESTNET || 'https://api.testnet.solana.com'
    default:
      return 'https://api.devnet.solana.com'
  }
}

// Wallet provider component
export const WalletProvider: React.FC<WalletProviderProps> = ({ children }) => {
  const [network, setNetworkState] = useState<WalletAdapterNetwork>(getNetwork())
  const [balance, setBalance] = useState<number>(0)
  const [error, setError] = useState<string | null>(null)

  // Configure wallets
  const wallets = [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter(),
    new TorusWalletAdapter(),
    new LedgerWalletAdapter(),
    new SlopeWalletAdapter()
  ]

  // Create connection
  const connection = new Connection(getRpcEndpoint(network), 'confirmed')

  return (
    <ConnectionProvider endpoint={getRpcEndpoint(network)}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <WalletContextProvider 
            network={network} 
            setNetwork={setNetworkState}
            connection={connection}
            balance={balance}
            setBalance={setBalance}
            error={error}
            setError={setError}
          >
            {children}
          </WalletContextProvider>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  )
}

// Internal wallet context provider
const WalletContextProvider: React.FC<{
  children: React.ReactNode
  network: WalletAdapterNetwork
  setNetwork: (network: WalletAdapterNetwork) => void
  connection: Connection
  balance: number
  setBalance: (balance: number) => void
  error: string | null
  setError: (error: string | null) => void
}> = ({ children, network, setNetwork, connection, balance, setBalance, error, setError }) => {
  const {
    connected,
    connecting,
    publicKey,
    wallet,
    connect: solanaConnect,
    disconnect: solanaDisconnect
  } = useSolanaWallet()

  // Connect wallet
  const connect = useCallback(async () => {
    try {
      setError(null)
      await solanaConnect()
    } catch (err) {
      console.error('Wallet connection error:', err)
      setError(err instanceof Error ? err.message : 'Failed to connect wallet')
    }
  }, [solanaConnect])

  // Disconnect wallet
  const disconnect = useCallback(async () => {
    try {
      setError(null)
      await solanaDisconnect()
      setBalance(0)
    } catch (err) {
      console.error('Wallet disconnection error:', err)
      setError(err instanceof Error ? err.message : 'Failed to disconnect wallet')
    }
  }, [solanaDisconnect])

  // Send transaction
  const sendTransaction = useCallback(async (
    transaction: Transaction | VersionedTransaction
  ): Promise<string> => {
    if (!wallet || !publicKey) {
      throw new Error('Wallet not connected')
    }

    try {
      setError(null)
      const signature = await connection.sendTransaction(transaction, [wallet])
      await connection.confirmTransaction(signature, 'confirmed')
      return signature
    } catch (err) {
      console.error('Transaction error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Transaction failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [wallet, publicKey, connection])

  // Sign message
  const signMessage = useCallback(async (message: Uint8Array): Promise<Uint8Array> => {
    if (!wallet || !wallet.signMessage) {
      throw new Error('Wallet does not support message signing')
    }

    try {
      setError(null)
      return await wallet.signMessage(message)
    } catch (err) {
      console.error('Message signing error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Message signing failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [wallet])

  // Sign transaction
  const signTransaction = useCallback(async (transaction: Transaction): Promise<Transaction> => {
    if (!wallet || !wallet.signTransaction) {
      throw new Error('Wallet does not support transaction signing')
    }

    try {
      setError(null)
      return await wallet.signTransaction(transaction)
    } catch (err) {
      console.error('Transaction signing error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Transaction signing failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [wallet])

  // Sign all transactions
  const signAllTransactions = useCallback(async (
    transactions: Transaction[]
  ): Promise<Transaction[]> => {
    if (!wallet || !wallet.signAllTransactions) {
      throw new Error('Wallet does not support signing multiple transactions')
    }

    try {
      setError(null)
      return await wallet.signAllTransactions(transactions)
    } catch (err) {
      console.error('Multiple transaction signing error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Multiple transaction signing failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [wallet])

  // Get balance
  const getBalance = useCallback(async (): Promise<number> => {
    if (!publicKey) {
      return 0
    }

    try {
      setError(null)
      const balance = await connection.getBalance(publicKey)
      const solBalance = balance / LAMPORTS_PER_SOL
      setBalance(solBalance)
      return solBalance
    } catch (err) {
      console.error('Balance fetch error:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch balance'
      setError(errorMessage)
      return 0
    }
  }, [publicKey, connection])

  // Set network
  const setNetworkHandler = useCallback((newNetwork: WalletAdapterNetwork) => {
    setNetwork(newNetwork)
    localStorage.setItem('solana-network', newNetwork)
  }, [setNetwork])

  // Auto-refresh balance when connected
  useEffect(() => {
    if (connected && publicKey) {
      getBalance()
      
      // Refresh balance every 30 seconds
      const interval = setInterval(() => {
        getBalance()
      }, 30000)

      return () => clearInterval(interval)
    }
  }, [connected, publicKey, getBalance])

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError(null)
      }, 5000)

      return () => clearTimeout(timer)
    }
  }, [error])

  const contextValue: WalletContextType = {
    connected,
    connecting,
    publicKey,
    wallet,
    balance,
    network,
    connect,
    disconnect,
    sendTransaction,
    signMessage,
    signTransaction,
    signAllTransactions,
    getBalance,
    setNetwork: setNetworkHandler,
    error
  }

  return (
    <WalletContext.Provider value={contextValue}>
      {children}
    </WalletContext.Provider>
  )
}

// Hook to use wallet context
export const useWallet = (): WalletContextType => {
  const context = useContext(WalletContext)
  if (!context) {
    throw new Error('useWallet must be used within a WalletProvider')
  }
  return context
}

// Utility functions
export const formatSolBalance = (balance: number): string => {
  return `${balance.toFixed(4)} SOL`
}

export const formatLamports = (lamports: number): string => {
  return `${(lamports / LAMPORTS_PER_SOL).toFixed(4)} SOL`
}

export const isValidPublicKey = (address: string): boolean => {
  try {
    new PublicKey(address)
    return true
  } catch {
    return false
  }
}

export const shortenAddress = (address: string, chars: number = 4): string => {
  if (address.length <= chars * 2) {
    return address
  }
  return `${address.slice(0, chars)}...${address.slice(-chars)}`
}

// Export wallet adapters for external use
export {
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  TorusWalletAdapter,
  LedgerWalletAdapter,
  SlopeWalletAdapter
}
