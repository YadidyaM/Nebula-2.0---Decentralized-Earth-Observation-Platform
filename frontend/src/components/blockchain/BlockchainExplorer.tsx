import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  Search, 
  Filter, 
  ExternalLink, 
  Copy, 
  CheckCircle, 
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Eye,
  Download
} from 'lucide-react';
import { BlockchainRecord, TransactionType } from '../../types';
import { useBlockchain } from '../../hooks';

interface BlockchainExplorerProps {
  records?: BlockchainRecord[];
  onRecordClick?: (record: BlockchainRecord) => void;
  className?: string;
}

const BlockchainExplorer: React.FC<BlockchainExplorerProps> = ({
  records: propRecords,
  onRecordClick,
  className = ''
}) => {
  const [selectedRecord, setSelectedRecord] = useState<BlockchainRecord | null>(null);
  const [filterType, setFilterType] = useState<TransactionType | 'all'>('all');
  const [filterStatus, setFilterStatus] = useState<'success' | 'failed' | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [copiedAddress, setCopiedAddress] = useState<string | null>(null);

  // Use blockchain hook if no records provided
  const { records: hookRecords, isLoading } = useBlockchain();
  const records = propRecords || hookRecords;

  // Filter records
  const filteredRecords = records.filter(record => {
    const matchesType = filterType === 'all' || record.type === filterType;
    const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
    const matchesSearch = searchQuery === '' || 
      record.transaction_signature.toLowerCase().includes(searchQuery.toLowerCase()) ||
      record.sender_address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (record.receiver_address && record.receiver_address.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesType && matchesStatus && matchesSearch;
  });

  // Get transaction type color
  const getTypeColor = (type: TransactionType): string => {
    switch (type) {
      case 'mission_log': return 'text-blue-400';
      case 'agent_stake': return 'text-green-400';
      case 'nft_mint': return 'text-purple-400';
      case 'token_transfer': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  // Get transaction type icon
  const getTypeIcon = (type: TransactionType) => {
    switch (type) {
      case 'mission_log': return <Database className="w-4 h-4" />;
      case 'agent_stake': return <TrendingUp className="w-4 h-4" />;
      case 'nft_mint': return <Eye className="w-4 h-4" />;
      case 'token_transfer': return <TrendingDown className="w-4 h-4" />;
      default: return <Database className="w-4 h-4" />;
    }
  };

  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'success': return 'text-green-400';
      case 'failed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  // Format transaction type
  const formatTransactionType = (type: TransactionType): string => {
    return type.replace('_', ' ').toUpperCase();
  };

  // Format date
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format address
  const formatAddress = (address: string): string => {
    return `${address.substring(0, 8)}...${address.substring(address.length - 8)}`;
  };

  // Copy to clipboard
  const copyToClipboard = useCallback(async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedAddress(type);
      setTimeout(() => setCopiedAddress(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  }, []);

  // Handle record click
  const handleRecordClick = useCallback((record: BlockchainRecord) => {
    setSelectedRecord(record);
    if (onRecordClick) {
      onRecordClick(record);
    }
  }, [onRecordClick]);

  // Get transaction type options
  const transactionTypes: { value: TransactionType | 'all'; label: string }[] = [
    { value: 'all', label: 'All Types' },
    { value: 'mission_log', label: 'Mission Log' },
    { value: 'agent_stake', label: 'Agent Stake' },
    { value: 'nft_mint', label: 'NFT Mint' },
    { value: 'token_transfer', label: 'Token Transfer' }
  ];

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-mono text-cyan-400">BLOCKCHAIN EXPLORER</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by transaction signature or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800/80 text-white pl-10 pr-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono placeholder-gray-400"
          />
        </div>

        {/* Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4"
            >
              <div className="grid grid-cols-2 gap-2">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as TransactionType | 'all')}
                  className="bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  {transactionTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as 'success' | 'failed' | 'all')}
                  className="bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  <option value="all">All Status</option>
                  <option value="success">Success</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-green-400 font-mono text-lg">
              {records.filter(r => r.status === 'success').length}
            </div>
            <div className="text-gray-400">Success</div>
          </div>
          <div className="text-center">
            <div className="text-red-400 font-mono text-lg">
              {records.filter(r => r.status === 'failed').length}
            </div>
            <div className="text-gray-400">Failed</div>
          </div>
          <div className="text-center">
            <div className="text-blue-400 font-mono text-lg">
              {records.filter(r => r.type === 'mission_log').length}
            </div>
            <div className="text-gray-400">Missions</div>
          </div>
          <div className="text-center">
            <div className="text-purple-400 font-mono text-lg">
              {records.filter(r => r.type === 'nft_mint').length}
            </div>
            <div className="text-gray-400">NFTs</div>
          </div>
        </div>
      </div>

      {/* Records List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="holo-spinner"></div>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No records found</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filteredRecords.map((record) => (
                <motion.div
                  key={record.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  onClick={() => handleRecordClick(record)}
                  className="holo-panel p-4 rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`flex items-center gap-1 ${getTypeColor(record.type)}`}>
                          {getTypeIcon(record.type)}
                          <span className="text-sm font-mono">
                            {formatTransactionType(record.type)}
                          </span>
                        </div>
                        
                        <div className={`flex items-center gap-1 ${getStatusColor(record.status)}`}>
                          {getStatusIcon(record.status)}
                          <span className="text-xs font-mono">
                            {record.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-xs text-gray-400 mb-2">
                        {formatDate(record.created_at)}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-xs text-gray-400">
                        Fee: {record.fee} SOL
                      </div>
                      {record.amount && (
                        <div className="text-xs text-white font-mono">
                          {record.amount} SOL
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">From:</span>
                      <div className="flex items-center gap-2">
                        <span className="text-white font-mono">
                          {formatAddress(record.sender_address)}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(record.sender_address, 'sender');
                          }}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {copiedAddress === 'sender' ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </div>
                    
                    {record.receiver_address && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">To:</span>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-mono">
                            {formatAddress(record.receiver_address)}
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(record.receiver_address!, 'receiver');
                            }}
                            className="text-gray-400 hover:text-white transition-colors"
                          >
                            {copiedAddress === 'receiver' ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                          </button>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Signature:</span>
                      <div className="flex items-center gap-2">
                        <span className="text-cyan-400 font-mono">
                          {formatAddress(record.transaction_signature)}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(record.transaction_signature, 'signature');
                          }}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {copiedAddress === 'signature' ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {record.data && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="text-xs text-gray-400">
                        Data: {JSON.stringify(record.data).substring(0, 100)}...
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-cyan-500/30">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Total Records: {records.length}</span>
          <span>Filtered: {filteredRecords.length}</span>
          <div className="flex items-center gap-1">
            <Database className="w-3 h-3" />
            <span>Solana Network</span>
          </div>
        </div>
      </div>

      {/* Record Details Modal */}
      <AnimatePresence>
        {selectedRecord && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setSelectedRecord(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="holo-panel rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto custom-scrollbar"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Database className="w-6 h-6 text-green-400" />
                  <h2 className="text-2xl font-mono text-cyan-400">
                    Transaction Details
                  </h2>
                </div>
                <button
                  onClick={() => setSelectedRecord(null)}
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column - Basic Info */}
                <div className="space-y-4">
                  <div className="holo-panel p-4 rounded">
                    <h3 className="text-lg font-mono text-white mb-3">Transaction Info</h3>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Type:</span>
                        <div className={`flex items-center gap-2 ${getTypeColor(selectedRecord.type)}`}>
                          {getTypeIcon(selectedRecord.type)}
                          <span className="font-mono">
                            {formatTransactionType(selectedRecord.type)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Status:</span>
                        <div className={`flex items-center gap-2 ${getStatusColor(selectedRecord.status)}`}>
                          {getStatusIcon(selectedRecord.status)}
                          <span className="font-mono">
                            {selectedRecord.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Fee:</span>
                        <span className="text-white font-mono">
                          {selectedRecord.fee} SOL
                        </span>
                      </div>
                      
                      {selectedRecord.amount && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">Amount:</span>
                          <span className="text-white font-mono">
                            {selectedRecord.amount} SOL
                          </span>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Created:</span>
                        <span className="text-white font-mono text-sm">
                          {formatDate(selectedRecord.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Addresses */}
                  <div className="holo-panel p-4 rounded">
                    <h3 className="text-lg font-mono text-white mb-3">Addresses</h3>
                    
                    <div className="space-y-3">
                      <div>
                        <span className="text-gray-400">From:</span>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-white font-mono text-sm">
                            {selectedRecord.sender_address}
                          </span>
                          <button
                            onClick={() => copyToClipboard(selectedRecord.sender_address, 'sender')}
                            className="text-gray-400 hover:text-white transition-colors"
                          >
                            {copiedAddress === 'sender' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                      
                      {selectedRecord.receiver_address && (
                        <div>
                          <span className="text-gray-400">To:</span>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-white font-mono text-sm">
                              {selectedRecord.receiver_address}
                            </span>
                            <button
                              onClick={() => copyToClipboard(selectedRecord.receiver_address!, 'receiver')}
                              className="text-gray-400 hover:text-white transition-colors"
                            >
                              {copiedAddress === 'receiver' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right Column - Signature & Data */}
                <div className="space-y-4">
                  {/* Transaction Signature */}
                  <div className="holo-panel p-4 rounded">
                    <h3 className="text-lg font-mono text-white mb-3">Transaction Signature</h3>
                    
                    <div className="space-y-3">
                      <div>
                        <span className="text-gray-400">Signature:</span>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-cyan-400 font-mono text-sm">
                            {selectedRecord.transaction_signature}
                          </span>
                          <button
                            onClick={() => copyToClipboard(selectedRecord.transaction_signature, 'signature')}
                            className="text-gray-400 hover:text-white transition-colors"
                          >
                            {copiedAddress === 'signature' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-400">Program ID:</span>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-white font-mono text-sm">
                            {selectedRecord.program_id}
                          </span>
                          <button
                            onClick={() => copyToClipboard(selectedRecord.program_id, 'program')}
                            className="text-gray-400 hover:text-white transition-colors"
                          >
                            {copiedAddress === 'program' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Transaction Data */}
                  {selectedRecord.data && (
                    <div className="holo-panel p-4 rounded">
                      <h3 className="text-lg font-mono text-white mb-3">Transaction Data</h3>
                      
                      <div className="bg-slate-900/50 p-3 rounded border border-gray-700">
                        <pre className="text-xs text-gray-300 font-mono overflow-x-auto">
                          {JSON.stringify(selectedRecord.data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-cyan-500/30">
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                  <ExternalLink className="w-4 h-4" />
                  View on Solana Explorer
                </button>
                
                <button className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
                  <Download className="w-4 h-4" />
                  Export
                </button>
                
                <button
                  onClick={() => setSelectedRecord(null)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BlockchainExplorer;
