import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWallet } from '../../contexts/WalletContext'
import { formatCrypto, formatCurrency } from '../../lib/formatters'

interface TokenBalanceDisplayProps {
  className?: string
  showUSD?: boolean
  showRefresh?: boolean
  autoRefresh?: boolean
  refreshInterval?: number
  tokens?: Array<{
    symbol: string
    mint: string
    decimals: number
    name: string
  }>
}

interface TokenBalance {
  symbol: string
  balance: number
  usdValue?: number
  mint: string
  name: string
}

const TokenBalanceDisplay: React.FC<TokenBalanceDisplayProps> = ({
  className = '',
  showUSD = true,
  showRefresh = true,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
  tokens = [
    {
      symbol: 'SOL',
      mint: 'So11111111111111111111111111111111111111112',
      decimals: 9,
      name: 'Solana'
    },
    {
      symbol: 'NEBULA',
      mint: 'NEBULA1111111111111111111111111111111111111',
      decimals: 6,
      name: 'Nebula Protocol Token'
    }
  ]
}) => {
  const { connected, publicKey, getBalance } = useWallet()
  const [balances, setBalances] = useState<TokenBalance[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  // Fetch token balances
  const fetchBalances = async () => {
    if (!connected || !publicKey) {
      setBalances([])
      return
    }

    setLoading(true)
    setError(null)

    try {
      const newBalances: TokenBalance[] = []

      // Fetch SOL balance
      const solBalance = await getBalance()
      newBalances.push({
        symbol: 'SOL',
        balance: solBalance,
        usdValue: solBalance * 100, // Mock USD price - replace with real price feed
        mint: 'So11111111111111111111111111111111111111112',
        name: 'Solana'
      })

      // Fetch other token balances (mock implementation)
      for (const token of tokens) {
        if (token.symbol !== 'SOL') {
          // Mock balance - replace with real token account fetching
          const mockBalance = Math.random() * 1000
          newBalances.push({
            symbol: token.symbol,
            balance: mockBalance,
            usdValue: mockBalance * 0.1, // Mock USD price
            mint: token.mint,
            name: token.name
          })
        }
      }

      setBalances(newBalances)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Error fetching balances:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch balances')
    } finally {
      setLoading(false)
    }
  }

  // Initial fetch
  useEffect(() => {
    fetchBalances()
  }, [connected, publicKey])

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh || !connected) return

    const interval = setInterval(fetchBalances, refreshInterval)
    return () => clearInterval(interval)
  }, [autoRefresh, connected, refreshInterval])

  // Animated number counter
  const AnimatedNumber: React.FC<{ value: number; decimals?: number }> = ({ 
    value, 
    decimals = 4 
  }) => {
    const [displayValue, setDisplayValue] = useState(0)

    useEffect(() => {
      const startValue = displayValue
      const endValue = value
      const duration = 1000 // 1 second
      const startTime = Date.now()

      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / duration, 1)
        
        // Easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3)
        const currentValue = startValue + (endValue - startValue) * easeOutCubic
        
        setDisplayValue(currentValue)

        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }

      requestAnimationFrame(animate)
    }, [value])

    return <span>{displayValue.toFixed(decimals)}</span>
  }

  if (!connected) {
    return (
      <div className={`relative group ${className}`}>
        <div className="absolute inset-0 bg-gradient-to-r from-gray-500/20 to-gray-600/20 
                      rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
        
        <div className="relative backdrop-blur-md bg-slate-900/80 border border-gray-500/30 
                      rounded-lg p-4 text-center">
          <div className="text-gray-400 text-sm">
            Connect wallet to view balances
          </div>
        </div>
        
        <div className="absolute inset-0 scan-line" />
      </div>
    )
  }

  return (
    <div className={`relative group ${className}`}>
      {/* Holographic glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 
                    rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      
      {/* Main container */}
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 
                    rounded-lg hover:border-cyan-400/50 transition-all duration-300">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cyan-500/20">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-cyan-400">Token Balances</h3>
          </div>
          
          {/* Refresh button */}
          {showRefresh && (
            <button
              onClick={fetchBalances}
              disabled={loading}
              className="text-gray-400 hover:text-cyan-400 transition-colors disabled:opacity-50"
              title="Refresh balances"
            >
              <motion.div
                animate={{ rotate: loading ? 360 : 0 }}
                transition={{ duration: 1, repeat: loading ? Infinity : 0, ease: "linear" }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </motion.div>
            </button>
          )}
        </div>
        
        {/* Content */}
        <div className="p-4">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-3"
              >
                {[1, 2].map((i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gray-700 animate-pulse" />
                      <div className="space-y-1">
                        <div className="h-4 w-16 bg-gray-700 rounded animate-pulse" />
                        <div className="h-3 w-12 bg-gray-700 rounded animate-pulse" />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="h-4 w-20 bg-gray-700 rounded animate-pulse" />
                      {showUSD && (
                        <div className="h-3 w-16 bg-gray-700 rounded animate-pulse" />
                      )}
                    </div>
                  </div>
                ))}
              </motion.div>
            ) : error ? (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-4"
              >
                <div className="text-red-400 mb-2">
                  <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <p className="text-red-400 text-sm">{error}</p>
                <button
                  onClick={fetchBalances}
                  className="mt-2 text-cyan-400 hover:text-cyan-300 text-sm underline"
                >
                  Try again
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="balances"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-3"
              >
                {balances.map((balance, index) => (
                  <motion.div
                    key={balance.symbol}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 
                             hover:bg-slate-800/70 transition-colors"
                  >
                    {/* Token info */}
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 
                                    flex items-center justify-center text-white font-bold text-sm">
                        {balance.symbol.charAt(0)}
                      </div>
                      <div>
                        <div className="text-white font-medium">{balance.symbol}</div>
                        <div className="text-gray-400 text-sm">{balance.name}</div>
                      </div>
                    </div>
                    
                    {/* Balance */}
                    <div className="text-right">
                      <div className="text-white font-medium">
                        <AnimatedNumber value={balance.balance} />
                      </div>
                      {showUSD && balance.usdValue && (
                        <div className="text-gray-400 text-sm">
                          {formatCurrency(balance.usdValue, 'USD')}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
                
                {/* Last update */}
                {lastUpdate && (
                  <div className="text-center pt-2 border-t border-gray-700">
                    <p className="text-gray-500 text-xs">
                      Last updated: {lastUpdate.toLocaleTimeString()}
                    </p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {/* Scan line effect */}
      <div className="absolute inset-0 scan-line" />
    </div>
  )
}

export default TokenBalanceDisplay
