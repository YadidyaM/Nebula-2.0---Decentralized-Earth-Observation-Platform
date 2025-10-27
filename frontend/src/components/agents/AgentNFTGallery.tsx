import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Image, 
  Star, 
  Coins, 
  TrendingUp, 
  Lock, 
  Unlock,
  Eye,
  Download,
  Share2,
  Filter,
  Search,
  Grid,
  List
} from 'lucide-react';
import { AgentNFTMetadata, AgentRarity } from '../../types';
import { useWallet } from '../../hooks';

interface AgentNFTGalleryProps {
  nfts?: AgentNFTMetadata[];
  onNFTSelect?: (nft: AgentNFTMetadata) => void;
  className?: string;
}

const AgentNFTGallery: React.FC<AgentNFTGalleryProps> = ({
  nfts: propNFTs,
  onNFTSelect,
  className = ''
}) => {
  const [selectedNFT, setSelectedNFT] = useState<AgentNFTMetadata | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterRarity, setFilterRarity] = useState<AgentRarity | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const { connected, publicKey, balance } = useWallet();

  // Mock NFT data for demonstration
  const mockNFTs: AgentNFTMetadata[] = [
    {
      id: '1',
      name: 'Forest Guardian Alpha',
      description: 'An elite AI agent specialized in forest monitoring and deforestation detection.',
      image_url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=400&fit=crop',
      rarity: 'legendary',
      agent_type: 'forestry',
      attributes: [
        { trait_type: 'Intelligence', value: 95 },
        { trait_type: 'Speed', value: 88 },
        { trait_type: 'Accuracy', value: 92 },
        { trait_type: 'Endurance', value: 90 }
      ],
      performance: {
        missions_completed: 156,
        success_rate: 0.94,
        average_confidence: 0.91
      },
      is_staked: false,
      stake_amount: 0,
      stake_yield: 0,
      mint_address: 'ABC123...XYZ789',
      owner_address: publicKey?.toString() || 'Unknown'
    },
    {
      id: '2',
      name: 'Ice Sentinel Beta',
      description: 'A specialized agent for cryosphere monitoring and climate analysis.',
      image_url: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=400&h=400&fit=crop',
      rarity: 'epic',
      agent_type: 'cryosphere',
      attributes: [
        { trait_type: 'Intelligence', value: 89 },
        { trait_type: 'Speed', value: 85 },
        { trait_type: 'Accuracy', value: 93 },
        { trait_type: 'Endurance', value: 87 }
      ],
      performance: {
        missions_completed: 98,
        success_rate: 0.89,
        average_confidence: 0.87
      },
      is_staked: true,
      stake_amount: 50,
      stake_yield: 0.12,
      mint_address: 'DEF456...UVW012',
      owner_address: publicKey?.toString() || 'Unknown'
    },
    {
      id: '3',
      name: 'Storm Tracker Gamma',
      description: 'Advanced weather monitoring agent with predictive capabilities.',
      image_url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop',
      rarity: 'rare',
      agent_type: 'weather',
      attributes: [
        { trait_type: 'Intelligence', value: 87 },
        { trait_type: 'Speed', value: 92 },
        { trait_type: 'Accuracy', value: 88 },
        { trait_type: 'Endurance', value: 85 }
      ],
      performance: {
        missions_completed: 67,
        success_rate: 0.85,
        average_confidence: 0.83
      },
      is_staked: false,
      stake_amount: 0,
      stake_yield: 0,
      mint_address: 'GHI789...RST345',
      owner_address: publicKey?.toString() || 'Unknown'
    }
  ];

  const nfts = propNFTs || mockNFTs;

  // Filter NFTs
  const filteredNFTs = nfts.filter(nft => {
    const matchesRarity = filterRarity === 'all' || nft.rarity === filterRarity;
    const matchesSearch = searchQuery === '' || 
      nft.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      nft.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesRarity && matchesSearch;
  });

  // Get rarity color
  const getRarityColor = (rarity: AgentRarity): string => {
    switch (rarity) {
      case 'common': return 'text-gray-400';
      case 'rare': return 'text-blue-400';
      case 'epic': return 'text-purple-400';
      case 'legendary': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  // Get rarity border color
  const getRarityBorderColor = (rarity: AgentRarity): string => {
    switch (rarity) {
      case 'common': return 'border-gray-500';
      case 'rare': return 'border-blue-500';
      case 'epic': return 'border-purple-500';
      case 'legendary': return 'border-yellow-500';
      default: return 'border-gray-500';
    }
  };

  // Get rarity background color
  const getRarityBackgroundColor = (rarity: AgentRarity): string => {
    switch (rarity) {
      case 'common': return 'bg-gray-500/20';
      case 'rare': return 'bg-blue-500/20';
      case 'epic': return 'bg-purple-500/20';
      case 'legendary': return 'bg-yellow-500/20';
      default: return 'bg-gray-500/20';
    }
  };

  // Handle NFT click
  const handleNFTClick = useCallback((nft: AgentNFTMetadata) => {
    setSelectedNFT(nft);
    if (onNFTSelect) {
      onNFTSelect(nft);
    }
  }, [onNFTSelect]);

  // Handle stake/unstake
  const handleStakeToggle = useCallback(async (nft: AgentNFTMetadata) => {
    if (!connected) {
      alert('Please connect your wallet to stake NFTs');
      return;
    }

    try {
      if (nft.is_staked) {
        // Unstake logic
        console.log('Unstaking NFT:', nft.id);
        // Implement unstaking logic here
      } else {
        // Stake logic
        console.log('Staking NFT:', nft.id);
        // Implement staking logic here
      }
    } catch (error) {
      console.error('Stake operation failed:', error);
    }
  }, [connected]);

  // Format performance percentage
  const formatPerformance = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Image className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-mono text-cyan-400">AGENT NFT GALLERY</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 rounded text-gray-400 hover:text-white transition-colors"
            >
              {viewMode === 'grid' ? <List className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
            </button>
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
            placeholder="Search NFTs..."
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
              <div className="flex gap-2">
                <select
                  value={filterRarity}
                  onChange={(e) => setFilterRarity(e.target.value as AgentRarity | 'all')}
                  className="flex-1 bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono"
                >
                  <option value="all">All Rarities</option>
                  <option value="common">Common</option>
                  <option value="rare">Rare</option>
                  <option value="epic">Epic</option>
                  <option value="legendary">Legendary</option>
                </select>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-yellow-400 font-mono text-lg">
              {nfts.filter(nft => nft.rarity === 'legendary').length}
            </div>
            <div className="text-gray-400">Legendary</div>
          </div>
          <div className="text-center">
            <div className="text-purple-400 font-mono text-lg">
              {nfts.filter(nft => nft.rarity === 'epic').length}
            </div>
            <div className="text-gray-400">Epic</div>
          </div>
          <div className="text-center">
            <div className="text-blue-400 font-mono text-lg">
              {nfts.filter(nft => nft.rarity === 'rare').length}
            </div>
            <div className="text-gray-400">Rare</div>
          </div>
          <div className="text-center">
            <div className="text-gray-400 font-mono text-lg">
              {nfts.filter(nft => nft.rarity === 'common').length}
            </div>
            <div className="text-gray-400">Common</div>
          </div>
        </div>
      </div>

      {/* NFT Grid/List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        {filteredNFTs.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400">
            <div className="text-center">
              <Image className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">No NFTs found</div>
            </div>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
            <AnimatePresence>
              {filteredNFTs.map((nft) => (
                <motion.div
                  key={nft.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  onClick={() => handleNFTClick(nft)}
                  className={`holo-panel rounded-lg cursor-pointer hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300 border-2 ${getRarityBorderColor(nft.rarity)} ${
                    viewMode === 'list' ? 'flex items-center p-4' : 'p-4'
                  }`}
                >
                  {viewMode === 'grid' ? (
                    <>
                      {/* NFT Image */}
                      <div className="relative mb-3">
                        <img
                          src={nft.image_url}
                          alt={nft.name}
                          className="w-full h-48 object-cover rounded border border-gray-700"
                        />
                        <div className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-mono ${getRarityBackgroundColor(nft.rarity)} ${getRarityColor(nft.rarity)}`}>
                          {nft.rarity.toUpperCase()}
                        </div>
                        {nft.is_staked && (
                          <div className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-mono bg-green-500/20 text-green-400 border border-green-500/50">
                            STAKED
                          </div>
                        )}
                      </div>

                      {/* NFT Info */}
                      <div className="space-y-2">
                        <h3 className="text-sm font-mono text-white">
                          {nft.name}
                        </h3>
                        
                        <div className="text-xs text-gray-400 line-clamp-2">
                          {nft.description}
                        </div>

                        {/* Performance */}
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-400">Missions:</span>
                            <span className="text-white font-mono">
                              {nft.performance.missions_completed}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-400">Success Rate:</span>
                            <span className="text-green-400 font-mono">
                              {formatPerformance(nft.performance.success_rate)}
                            </span>
                          </div>
                        </div>

                        {/* Staking Info */}
                        {nft.is_staked && (
                          <div className="pt-2 border-t border-gray-700">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-400">Staked:</span>
                              <span className="text-green-400 font-mono">
                                {nft.stake_amount} SOL
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-400">Yield:</span>
                              <span className="text-blue-400 font-mono">
                                {formatPerformance(nft.stake_yield)}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </>
                  ) : (
                    <>
                      {/* List View */}
                      <div className="flex-shrink-0 w-16 h-16 mr-4">
                        <img
                          src={nft.image_url}
                          alt={nft.name}
                          className="w-full h-full object-cover rounded border border-gray-700"
                        />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-mono text-white truncate">
                            {nft.name}
                          </h3>
                          <div className={`text-xs font-mono ${getRarityColor(nft.rarity)}`}>
                            {nft.rarity.toUpperCase()}
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-400 mb-2 line-clamp-1">
                          {nft.description}
                        </div>
                        
                        <div className="flex items-center gap-4 text-xs">
                          <span className="text-gray-400">
                            Missions: <span className="text-white font-mono">{nft.performance.missions_completed}</span>
                          </span>
                          <span className="text-gray-400">
                            Success: <span className="text-green-400 font-mono">{formatPerformance(nft.performance.success_rate)}</span>
                          </span>
                          {nft.is_staked && (
                            <span className="text-gray-400">
                              Staked: <span className="text-green-400 font-mono">{nft.stake_amount} SOL</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </>
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
          <span>Total NFTs: {nfts.length}</span>
          <span>Staked: {nfts.filter(nft => nft.is_staked).length}</span>
          <div className="flex items-center gap-1">
            <Coins className="w-3 h-3" />
            <span>Balance: {balance?.toFixed(2) || '0.00'} SOL</span>
          </div>
        </div>
      </div>

      {/* NFT Details Modal */}
      <AnimatePresence>
        {selectedNFT && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setSelectedNFT(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="holo-panel rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto custom-scrollbar"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-mono text-cyan-400">
                  {selectedNFT.name}
                </h3>
                <button
                  onClick={() => setSelectedNFT(null)}
                  className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* NFT Image */}
                <div>
                  <img
                    src={selectedNFT.image_url}
                    alt={selectedNFT.name}
                    className="w-full h-64 object-cover rounded border border-gray-700"
                  />
                  <div className="mt-4 flex gap-2">
                    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                      <Eye className="w-4 h-4" />
                      View
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
                      <Share2 className="w-4 h-4" />
                      Share
                    </button>
                  </div>
                </div>
                
                {/* NFT Details */}
                <div className="space-y-4">
                  <div>
                    <span className="text-gray-400">Description:</span>
                    <p className="text-white text-sm mt-1">
                      {selectedNFT.description}
                    </p>
                  </div>
                  
                  <div>
                    <span className="text-gray-400">Rarity:</span>
                    <div className={`font-mono ${getRarityColor(selectedNFT.rarity)}`}>
                      {selectedNFT.rarity.toUpperCase()}
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-gray-400">Performance:</span>
                    <div className="mt-2 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Missions Completed:</span>
                        <span className="font-mono">{selectedNFT.performance.missions_completed}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Success Rate:</span>
                        <span className="font-mono text-green-400">
                          {formatPerformance(selectedNFT.performance.success_rate)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Average Confidence:</span>
                        <span className="font-mono text-blue-400">
                          {formatPerformance(selectedNFT.performance.average_confidence)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {selectedNFT.is_staked && (
                    <div>
                      <span className="text-gray-400">Staking Info:</span>
                      <div className="mt-2 space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Stake Amount:</span>
                          <span className="font-mono text-green-400">
                            {selectedNFT.stake_amount} SOL
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Yield Rate:</span>
                          <span className="font-mono text-blue-400">
                            {formatPerformance(selectedNFT.stake_yield)}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div>
                    <span className="text-gray-400">Attributes:</span>
                    <div className="mt-2 space-y-2">
                      {selectedNFT.attributes.map((attr, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span>{attr.trait_type}:</span>
                          <span className="font-mono">{attr.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-cyan-500/30">
                <button
                  onClick={() => handleStakeToggle(selectedNFT)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    selectedNFT.is_staked
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {selectedNFT.is_staked ? (
                    <>
                      <Unlock className="w-4 h-4" />
                      Unstake
                    </>
                  ) : (
                    <>
                      <Lock className="w-4 h-4" />
                      Stake
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => setSelectedNFT(null)}
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

export default AgentNFTGallery;
