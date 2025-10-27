import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wallet, 
  Send, 
  Download, 
  Upload, 
  Copy, 
  CheckCircle, 
  XCircle,
  Eye,
  EyeOff,
  Settings,
  TrendingUp,
  TrendingDown,
  Coins,
  Lock,
  Unlock
} from 'lucide-react';
import { useWallet } from '../../hooks';

interface WalletManagerProps {
  className?: string;
}

const WalletManager: React.FC<WalletManagerProps> = ({ className = '' }) => {
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [copiedAddress, setCopiedAddress] = useState<string | null>(null);
  const [sendAmount, setSendAmount] = useState('');
  const [sendAddress, setSendAddress] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [showReceiveModal, setShowReceiveModal] = useState(false);

  const { 
    connected, 
    publicKey, 
    wallet, 
    balance, 
    loading, 
    error, 
    connect, 
    disconnect, 
    fetchBalance 
  } = useWallet();

  // Mock transaction history
  const mockTransactions = [
    {
      id: '1',
      type: 'received',
      amount: 5.5,
      from: 'ABC123...XYZ789',
      to: publicKey?.toString() || 'Unknown',
      timestamp: new Date().toISOString(),
      signature: 'DEF456...UVW012'
    },
    {
      id: '2',
      type: 'sent',
      amount: 2.3,
      from: publicKey?.toString() || 'Unknown',
      to: 'GHI789...RST345',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      signature: 'JKL012...MNO678'
    },
    {
      id: '3',
      type: 'staked',
      amount: 10.0,
      from: publicKey?.toString() || 'Unknown',
      to: 'Staking Pool',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      signature: 'PQR345...STU901'
    }
  ];

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

  // Handle send transaction
  const handleSend = useCallback(async () => {
    if (!sendAmount || !sendAddress) return;
    
    setIsSending(true);
    try {
      // Implement send transaction logic here
      console.log('Sending', sendAmount, 'SOL to', sendAddress);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSendAmount('');
      setSendAddress('');
      setShowSendModal(false);
    } catch (error) {
      console.error('Send transaction failed:', error);
    } finally {
      setIsSending(false);
    }
  }, [sendAmount, sendAddress]);

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

  // Get transaction type color
  const getTransactionTypeColor = (type: string): string => {
    switch (type) {
      case 'received': return 'text-green-400';
      case 'sent': return 'text-red-400';
      case 'staked': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  // Get transaction type icon
  const getTransactionTypeIcon = (type: string) => {
    switch (type) {
      case 'received': return <TrendingUp className="w-4 h-4" />;
      case 'sent': return <TrendingDown className="w-4 h-4" />;
      case 'staked': return <Lock className="w-4 h-4" />;
      default: return <Coins className="w-4 h-4" />;
    }
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Wallet className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-mono text-cyan-400">WALLET MANAGER</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowPrivateKey(!showPrivateKey)}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              {showPrivateKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
            <button className="p-2 rounded text-gray-400 hover:text-white transition-colors">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Wallet Status */}
        <div className="holo-panel p-4 rounded mb-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
              <span className="text-sm font-mono text-gray-400">
                {connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>
            {wallet && (
              <span className="text-sm font-mono text-gray-400">
                {wallet.adapter.name}
              </span>
            )}
          </div>
          
          {connected && publicKey ? (
            <div className="space-y-3">
              <div>
                <span className="text-gray-400 text-sm">Address:</span>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-white font-mono text-sm">
                    {formatAddress(publicKey.toString())}
                  </span>
                  <button
                    onClick={() => copyToClipboard(publicKey.toString(), 'address')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {copiedAddress === 'address' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <div>
                <span className="text-gray-400 text-sm">Balance:</span>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-green-400 font-mono text-lg">
                    {balance?.toFixed(4) || '0.0000'} SOL
                  </span>
                  <button
                    onClick={fetchBalance}
                    disabled={loading}
                    className="text-gray-400 hover:text-white transition-colors disabled:opacity-50"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <div className="text-gray-400 text-sm mb-3">
                Connect your wallet to view details
              </div>
              <button
                onClick={connect}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Connecting...' : 'Connect Wallet'}
              </button>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {connected && (
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setShowSendModal(true)}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-red-600/80 hover:bg-red-500/80 text-white rounded-lg transition-colors border border-red-400/50"
            >
              <Send className="w-4 h-4" />
              <span className="font-mono text-sm">SEND</span>
            </button>
            
            <button
              onClick={() => setShowReceiveModal(true)}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-green-600/80 hover:bg-green-500/80 text-white rounded-lg transition-colors border border-green-400/50"
            >
              <Upload className="w-4 h-4" />
              <span className="font-mono text-sm">RECEIVE</span>
            </button>
          </div>
        )}
      </div>

      {/* Transaction History */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        <h3 className="text-sm font-mono text-cyan-400 mb-3">Transaction History</h3>
        
        {connected ? (
          <div className="space-y-3">
            {mockTransactions.map((tx) => (
              <motion.div
                key={tx.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="holo-panel p-3 rounded"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`flex items-center gap-2 ${getTransactionTypeColor(tx.type)}`}>
                    {getTransactionTypeIcon(tx.type)}
                    <span className="text-sm font-mono">
                      {tx.type.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="text-right">
                    <div className={`text-sm font-mono ${getTransactionTypeColor(tx.type)}`}>
                      {tx.type === 'sent' ? '-' : '+'}{tx.amount} SOL
                    </div>
                    <div className="text-xs text-gray-400">
                      {formatDate(tx.timestamp)}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">From:</span>
                    <span className="text-white font-mono">
                      {formatAddress(tx.from)}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">To:</span>
                    <span className="text-white font-mono">
                      {formatAddress(tx.to)}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Signature:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-400 font-mono">
                        {formatAddress(tx.signature)}
                      </span>
                      <button
                        onClick={() => copyToClipboard(tx.signature, `signature-${tx.id}`)}
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        {copiedAddress === `signature-${tx.id}` ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Wallet className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">Connect wallet to view transactions</div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-cyan-500/30">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Network: Solana Devnet</span>
          <span>RPC: {import.meta.env.VITE_SOLANA_RPC_URL || 'Default'}</span>
          {connected && (
            <button
              onClick={disconnect}
              className="text-red-400 hover:text-red-300 transition-colors"
            >
              Disconnect
            </button>
          )}
        </div>
      </div>

      {/* Send Modal */}
      <AnimatePresence>
        {showSendModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setShowSendModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="holo-panel rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-mono text-cyan-400">Send SOL</h3>
                <button
                  onClick={() => setShowSendModal(false)}
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Recipient Address</label>
                  <input
                    type="text"
                    value={sendAddress}
                    onChange={(e) => setSendAddress(e.target.value)}
                    placeholder="Enter recipient address..."
                    className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Amount (SOL)</label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    max={balance}
                    value={sendAmount}
                    onChange={(e) => setSendAmount(e.target.value)}
                    placeholder="0.000"
                    className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono text-sm"
                  />
                </div>
                
                <div className="text-xs text-gray-400">
                  Available: {balance?.toFixed(4) || '0.0000'} SOL
                </div>
              </div>
              
              <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-cyan-500/30">
                <button
                  onClick={() => setShowSendModal(false)}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                
                <button
                  onClick={handleSend}
                  disabled={!sendAmount || !sendAddress || isSending}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSending ? 'Sending...' : 'Send'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Receive Modal */}
      <AnimatePresence>
        {showReceiveModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setShowReceiveModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="holo-panel rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-mono text-cyan-400">Receive SOL</h3>
                <button
                  onClick={() => setShowReceiveModal(false)}
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-sm text-gray-400 mb-2">Your Address</div>
                  <div className="bg-slate-800/80 p-3 rounded border border-cyan-500/30">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-mono text-sm flex-1">
                        {publicKey?.toString() || 'Not connected'}
                      </span>
                      <button
                        onClick={() => copyToClipboard(publicKey?.toString() || '', 'receive-address')}
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        {copiedAddress === 'receive-address' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="text-xs text-gray-400 text-center">
                  Share this address to receive SOL tokens
                </div>
              </div>
              
              <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-cyan-500/30">
                <button
                  onClick={() => setShowReceiveModal(false)}
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

export default WalletManager;
