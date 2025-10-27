import React from 'react';
import { motion } from 'framer-motion';
import {
  Satellite,
  Target,
  Users,
  TrendingUp,
  Radio,
  Flame,
  Coins,
  Shield,
  Database,
  AlertTriangle
} from 'lucide-react';

interface TopToolbarProps {
  activePanel?: string | null;
  onPanelChange?: (panel: string | null) => void;
  className?: string;
}

interface ToolbarButton {
  id: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  description: string;
  color: string;
}

const TopToolbar: React.FC<TopToolbarProps> = ({
  activePanel = null,
  onPanelChange,
  className = ''
}) => {
  const buttons: ToolbarButton[] = [
    {
      id: 'telemetry',
      icon: Satellite,
      label: 'Telemetry',
      description: 'Satellite telemetry data',
      color: 'text-blue-400'
    },
    {
      id: 'missions',
      icon: Target,
      label: 'Missions',
      description: 'Mission queue and management',
      color: 'text-green-400'
    },
    {
      id: 'agents',
      icon: Users,
      label: 'Agents',
      description: 'AI agent status and control',
      color: 'text-purple-400'
    },
    {
      id: 'trends',
      icon: TrendingUp,
      label: 'Trends',
      description: 'Telemetry trends and analytics',
      color: 'text-yellow-400'
    },
    {
      id: 'passes',
      icon: Radio,
      label: 'Passes',
      description: 'Orbital pass predictions',
      color: 'text-cyan-400'
    },
    {
      id: 'heatmap',
      icon: Flame,
      label: 'Heatmap',
      description: 'Risk heatmap visualization',
      color: 'text-red-400'
    },
    {
      id: 'wallet',
      icon: Coins,
      label: 'Wallet',
      description: 'Solana wallet management',
      color: 'text-orange-400'
    },
    {
      id: 'nfts',
      icon: Shield,
      label: 'NFTs',
      description: 'Agent NFT gallery',
      color: 'text-pink-400'
    },
    {
      id: 'blockchain',
      icon: Database,
      label: 'Blockchain',
      description: 'Mission registry and records',
      color: 'text-indigo-400'
    },
    {
      id: 'alerts',
      icon: AlertTriangle,
      label: 'Alerts',
      description: 'System alerts and notifications',
      color: 'text-red-400'
    }
  ];

  const handleButtonClick = (buttonId: string) => {
    if (onPanelChange) {
      // Toggle panel - if already active, close it
      if (activePanel === buttonId) {
        onPanelChange(null);
      } else {
        onPanelChange(buttonId);
      }
    }
  };

  const getButtonClasses = (buttonId: string, isActive: boolean): string => {
    const baseClasses = 'relative p-3 rounded-full transition-all duration-300 border group';
    const activeClasses = isActive
      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30 border-blue-400/50'
      : 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white border-gray-600/50 hover:border-gray-500/50';
    
    return `${baseClasses} ${activeClasses}`;
  };

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1], delay: 0.1 }}
      className={`fixed top-16 left-1/2 transform -translate-x-1/2 z-30 ${className}`}
    >
      <div className="holo-panel rounded-lg p-2">
        <div className="flex items-center gap-2">
          {buttons.map((button, index) => {
            const Icon = button.icon;
            const isActive = activePanel === button.id;
            
            return (
              <motion.button
                key={button.id}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.3, 
                  ease: [0.4, 0, 0.2, 1], 
                  delay: index * 0.05 
                }}
                whileHover={{ 
                  scale: 1.1,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ 
                  scale: 0.95,
                  transition: { duration: 0.1 }
                }}
                onClick={() => handleButtonClick(button.id)}
                className={getButtonClasses(button.id, isActive)}
                title={`${button.label} - ${button.description}`}
              >
                <Icon className="w-5 h-5" />
                
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-black"
                  />
                )}
                
                {/* Hover tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-black/90 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                  <div className="font-semibold">{button.label}</div>
                  <div className="text-gray-300">{button.description}</div>
                  
                  {/* Tooltip arrow */}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-black/90"></div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};

export default TopToolbar;
