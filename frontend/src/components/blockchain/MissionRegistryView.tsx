import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWebSocket } from '../../contexts/WebSocketContext'
import { formatDate, formatRelativeTime, truncateAddress } from '../../lib/formatters'
import { BlockchainTransaction } from '../../types'

interface MissionRegistryViewProps {
  transactions: BlockchainTransaction[]
  onTransactionSelect?: (transaction: BlockchainTransaction) => void
  className?: string
}

interface FilterOptions {
  status: 'all' | 'verified' | 'pending' | 'failed'
  sortBy: 'newest' | 'oldest' | 'status'
}

const MissionRegistryView: React.FC<MissionRegistryViewProps> = ({
  transactions,
  onTransactionSelect,
  className = ''
}) => {
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    sortBy: 'newest'
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedTx, setSelectedTx] = useState<BlockchainTransaction | null>(null)
  const itemsPerPage = 10

  const { subscribe, unsubscribe } = useWebSocket()

  // Filter and sort transactions
  const filteredTransactions = useMemo(() => {
    let filtered = [...transactions]

    // Filter by status
    if (filters.status !== 'all') {
      filtered = filtered.filter(tx => {
        switch (filters.status) {
          case 'verified':
            return tx.status === 'confirmed' && tx.blockchain_hash
          case 'pending':
            return tx.status === 'pending'
          case 'failed':
            return tx.status === 'failed'
          default:
            return true
        }
      })
    }

    // Sort transactions
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'newest':
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        case 'oldest':
          return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        case 'status':
          return a.status.localeCompare(b.status)
        default:
          return 0
      }
    })

    return filtered
  }, [transactions, filters])

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage)
  const paginatedTransactions = filteredTransactions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // WebSocket subscription for real-time updates
  useEffect(() => {
    const handleTransactionUpdate = (message: any) => {
      if (message.type === 'blockchain_update' && message.data) {
        // Transaction updated, could trigger a re-fetch
        console.log('Transaction update received:', message.data)
      }
    }

    subscribe('blockchain_update', handleTransactionUpdate)
    return () => unsubscribe('blockchain_update', handleTransactionUpdate)
  }, [subscribe, unsubscribe])

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-600'
      case 'pending':
        return 'bg-yellow-600'
      case 'failed':
        return 'bg-red-600'
      default:
        return 'bg-gray-600'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Verified'
      case 'pending':
        return 'Pending'
      case 'failed':
        return 'Failed'
      default:
        return status
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // Could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const openInExplorer = (hash: string) => {
    const explorerUrl = `https://solscan.io/tx/${hash}`
    window.open(explorerUrl, '_blank')
  }

  return (
    <div className={`relative group ${className}`}>
      {/* Holographic glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 
                    rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
      
      {/* Main container */}
      <div className="relative backdrop-blur-md bg-slate-900/80 border border-purple-500/30 
                    rounded-lg hover:border-purple-400/50 transition-all duration-300">
        
        {/* Header */}
        <div className="p-4 border-b border-purple-500/20">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-purple-400">Mission Registry</h3>
            </div>
            
            <div className="text-sm text-gray-400">
              {filteredTransactions.length} transactions
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex gap-4">
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as any }))}
              className="bg-slate-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
            >
              <option value="all">All Status</option>
              <option value="verified">Verified</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
            
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value as any }))}
              className="bg-slate-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="status">By Status</option>
            </select>
          </div>
        </div>
        
        {/* Content */}
        <div className="p-4">
          <AnimatePresence mode="wait">
            {paginatedTransactions.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-8"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-700/50 flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-400 mb-2">No Transactions Found</h3>
                <p className="text-gray-500 text-sm">
                  No mission transactions match your current filters.
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="transactions"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-3"
              >
                {paginatedTransactions.map((transaction, index) => (
                  <motion.div
                    key={transaction.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 rounded-lg bg-slate-800/50 hover:bg-slate-800/70 
                             border border-gray-700 hover:border-purple-500/30 transition-all cursor-pointer"
                    onClick={() => {
                      setSelectedTx(transaction)
                      onTransactionSelect?.(transaction)
                    }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`px-2 py-1 rounded-full text-xs font-medium text-white
                                       ${getStatusColor(transaction.status)}`}>
                          {getStatusText(transaction.status)}
                        </div>
                        <div className="text-white font-medium">
                          {transaction.mission_name || 'Mission Transaction'}
                        </div>
                      </div>
                      
                      <div className="text-gray-400 text-sm">
                        {formatRelativeTime(transaction.timestamp)}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-gray-400 mb-1">Transaction Hash</div>
                        <div className="flex items-center gap-2">
                          <code className="text-cyan-400 font-mono">
                            {truncateAddress(transaction.transaction_hash, 8)}
                          </code>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              copyToClipboard(transaction.transaction_hash)
                            }}
                            className="text-gray-400 hover:text-white"
                            title="Copy hash"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              openInExplorer(transaction.transaction_hash)
                            }}
                            className="text-gray-400 hover:text-blue-400"
                            title="View on Solscan"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-gray-400 mb-1">IPFS Hash</div>
                        <div className="flex items-center gap-2">
                          <code className="text-green-400 font-mono">
                            {transaction.ipfs_hash ? truncateAddress(transaction.ipfs_hash, 8) : 'N/A'}
                          </code>
                          {transaction.ipfs_hash && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                copyToClipboard(transaction.ipfs_hash!)
                              }}
                              className="text-gray-400 hover:text-white"
                              title="Copy IPFS hash"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-700">
              <div className="text-sm text-gray-400">
                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredTransactions.length)} of {filteredTransactions.length} transactions
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed 
                           text-white rounded-lg transition-colors"
                >
                  Previous
                </button>
                
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = i + 1
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`px-3 py-1 rounded-lg transition-colors ${
                          currentPage === page
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-700 hover:bg-slate-600 text-white'
                        }`}
                      >
                        {page}
                      </button>
                    )
                  })}
                </div>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed 
                           text-white rounded-lg transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Scan line effect */}
      <div className="absolute inset-0 scan-line" />
    </div>
  )
}

export default MissionRegistryView
