import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWallet } from '../../contexts/WalletContext'
import { shortenAddress } from '../../lib/formatters'

interface WalletConnectButtonProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'secondary' | 'ghost'
  showNetwork?: boolean
  showBalance?: boolean
}

const WalletConnectButton: React.FC<WalletConnectButtonProps> = ({
  className = '',
  size = 'md',
  variant = 'primary',
  showNetwork = true,
  showBalance = false
}) => {
  const { 
    connected, 
    connecting, 
    publicKey, 
    wallet, 
    balance, 
    network, 
    connect, 
    disconnect, 
    error 
  } = useWallet()

  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false)

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }

  // Variant classes
  const variantClasses = {
    primary: 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500',
    secondary: 'bg-slate-700 hover:bg-slate-600 border border-slate-600',
    ghost: 'bg-transparent hover:bg-slate-800 border border-slate-600'
  }

  // Network badge colors
  const networkColors = {
    'mainnet-beta': 'bg-green-600',
    'devnet': 'bg-yellow-600',
    'testnet': 'bg-blue-600'
  }

  const handleConnect = async () => {
    try {
      await connect()
    } catch (error) {
      console.error('Connection error:', error)
    }
  }

  const handleDisconnect = async () => {
    try {
      await disconnect()
      setShowDisconnectConfirm(false)
    } catch (error) {
      console.error('Disconnection error:', error)
    }
  }

  const copyAddress = async () => {
    if (publicKey) {
      try {
        await navigator.clipboard.writeText(publicKey.toString())
        // Could add a toast notification here
      } catch (error) {
        console.error('Failed to copy address:', error)
      }
    }
  }

  if (!connected) {
    return (
      <div className={`relative group ${className}`}>
        {/* Holographic glow effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 
                      rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
        
        {/* Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleConnect}
          disabled={connecting}
          className={`relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 
                    rounded-lg hover:border-cyan-400/50 transition-all duration-300
                    ${sizeClasses[size]} ${variantClasses[variant]}
                    text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed
                    flex items-center gap-2`}
        >
          {connecting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              <span>Connecting...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>Connect Wallet</span>
            </>
          )}
        </motion.button>
        
        {/* Scan line effect */}
        <div className="absolute inset-0 scan-line" />
        
        {/* Error tooltip */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-full left-0 mt-2 p-2 bg-red-900/80 backdrop-blur-md 
                     border border-red-500/30 rounded-lg text-red-400 text-sm z-50"
          >
            {error}
          </motion.div>
        )}
      </div>
    )
  }

  return (
    <div className={`relative group ${className}`}>
      {/* Holographic glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-emerald-500/20 
                    rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      
      {/* Connected state */}
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="relative backdrop-blur-md bg-slate-900/80 border border-green-500/30 
                 rounded-lg hover:border-green-400/50 transition-all duration-300
                 flex items-center gap-2"
      >
        {/* Wallet info */}
        <div className="flex items-center gap-3 px-4 py-2">
          {/* Wallet icon */}
          <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          
          {/* Address */}
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-white font-medium">
                {shortenAddress(publicKey?.toString() || '', 4)}
              </span>
              <button
                onClick={copyAddress}
                className="text-gray-400 hover:text-white transition-colors"
                title="Copy address"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
            
            {/* Balance */}
            {showBalance && (
              <span className="text-green-400 text-sm">
                {balance.toFixed(4)} SOL
              </span>
            )}
          </div>
          
          {/* Network badge */}
          {showNetwork && (
            <div className={`px-2 py-1 rounded-full text-xs font-medium text-white
                           ${networkColors[network] || 'bg-gray-600'}`}>
              {network === 'mainnet-beta' ? 'Mainnet' : network}
            </div>
          )}
          
          {/* Disconnect button */}
          <button
            onClick={() => setShowDisconnectConfirm(true)}
            className="text-gray-400 hover:text-red-400 transition-colors p-1"
            title="Disconnect wallet"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </motion.div>
      
      {/* Scan line effect */}
      <div className="absolute inset-0 scan-line" />
      
      {/* Disconnect confirmation modal */}
      <AnimatePresence>
        {showDisconnectConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            {/* Backdrop */}
            <div 
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              onClick={() => setShowDisconnectConfirm(false)}
            />
            
            {/* Modal */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="relative bg-slate-900/90 backdrop-blur-md border border-red-500/30 
                       rounded-lg p-6 max-w-md w-full"
            >
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                
                <h3 className="text-lg font-bold text-white mb-2">Disconnect Wallet</h3>
                <p className="text-gray-400 mb-6">
                  Are you sure you want to disconnect your wallet? You'll need to reconnect to access wallet features.
                </p>
                
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowDisconnectConfirm(false)}
                    className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white 
                             rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDisconnect}
                    className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white 
                             rounded-lg transition-colors"
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default WalletConnectButton
