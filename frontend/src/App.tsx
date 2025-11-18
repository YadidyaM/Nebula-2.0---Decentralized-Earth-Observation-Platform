// Main React application component with 3D Earth visualization, Gemini AI chat, and real-time satellite telemetry
import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Components
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import EarthScene from './components/3d/EarthScene'
import HolographicOverlay from './components/ui/HolographicOverlay'
import SatelliteChat from './components/chat/SatelliteChat'
import TopToolbar from './components/ui/TopToolbar'
import MissionControlHeader from './components/ui/MissionControlHeader'
import WalletConnectButton from './components/blockchain/WalletConnectButton'
import TokenBalanceDisplay from './components/blockchain/TokenBalanceDisplay'
import AgentNFTGallery from './components/agents/AgentNFTGallery'
import MissionRegistryView from './components/blockchain/MissionRegistryView'
import AgentStatusGrid from './components/agents/AgentStatusGrid'
import MissionQueuePanel from './components/missions/MissionQueuePanel'
import TelemetryTrendsChart from './components/telemetry/TelemetryTrendsChart'
import OrbitalPassPredictor from './components/telemetry/OrbitalPassPredictor'
import RiskHeatmap from './components/telemetry/RiskHeatmap'

// Hooks
import { useWebSocket } from './hooks/useWebSocket'
import { useWallet } from './hooks/useWallet'
import { useMissions } from './hooks/useMissions'

// Types
import { Mission } from './types/missions'

function App() {
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentMission, setCurrentMission] = useState<Mission | null>(null)
  const [showMissionViewer, setShowMissionViewer] = useState(false)
  const [activePanel, setActivePanel] = useState<string | null>(null)
  
  // WebSocket connection for real-time updates
  const { isConnected, lastMessage } = useWebSocket()
  
  // Wallet connection
  const { connected, publicKey, balance } = useWallet()
  
  // Mission management
  const { missions, createMission, updateMission } = useMissions()

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage)
      
      switch (message.type) {
        case 'mission_update':
          // Update mission status
          if (message.data) {
            updateMission(message.data)
          }
          break
        case 'agent_status_update':
          // Update agent status
          console.log('Agent status update:', message.data)
          break
        case 'telemetry_update':
          // Update telemetry data
          console.log('Telemetry update:', message.data)
          break
        case 'risk_alert':
          // Handle risk alerts
          console.log('Risk alert:', message.data)
          break
        default:
          console.log('Unknown message type:', message.type)
      }
    }
  }, [lastMessage, updateMission])

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black">
      {/* Background Layers */}
      <AnimatedBackground />
      <EarthScene />
      <HolographicOverlay />
      
      {/* Main UI Components */}
      <SatelliteChat 
        isMinimized={isChatMinimized}
        onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
      />
      
      <TopToolbar 
        activePanel={activePanel}
        onPanelChange={setActivePanel}
      />
      
      <MissionControlHeader 
        isConnected={isConnected}
        missionCount={missions.length}
        activeMission={currentMission}
      />
      
      {/* Wallet Integration */}
      <div className="fixed top-4 right-4 z-50 flex gap-2">
        <WalletConnectButton />
        {connected && <TokenBalanceDisplay />}
      </div>
      
      {/* Main Content */}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
      
      {/* Modal Panels */}
      <AnimatePresence>
        {activePanel === 'agents' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <AgentStatusGrid />
          </motion.div>
        )}
        
        {activePanel === 'missions' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <MissionQueuePanel 
              missions={missions}
              onMissionSelect={setCurrentMission}
            />
          </motion.div>
        )}
        
        {activePanel === 'telemetry' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <TelemetryTrendsChart />
          </motion.div>
        )}
        
        {activePanel === 'passes' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <OrbitalPassPredictor />
          </motion.div>
        )}
        
        {activePanel === 'heatmap' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <RiskHeatmap />
          </motion.div>
        )}
        
        {activePanel === 'wallet' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <div className="p-6">
              <h2 className="text-xl font-bold text-cyan-400 mb-4">Wallet Management</h2>
              <div className="space-y-4">
                <WalletConnectButton />
                {connected && <TokenBalanceDisplay />}
              </div>
            </div>
          </motion.div>
        )}
        
        {activePanel === 'nfts' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <AgentNFTGallery />
          </motion.div>
        )}
        
        {activePanel === 'blockchain' && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
            className="fixed top-0 right-0 h-full w-96 bg-black/95 backdrop-blur-sm border-l border-gray-700 z-50 overflow-y-auto custom-scrollbar"
          >
            <MissionRegistryView />
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Mission Viewer Modal */}
      <AnimatePresence>
        {showMissionViewer && currentMission && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center"
            onClick={() => setShowMissionViewer(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-slate-900 rounded-lg p-6 max-w-2xl w-full mx-4 border border-cyan-500/30"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold text-cyan-400 mb-4">
                Mission: {currentMission.name}
              </h2>
              <div className="space-y-4">
                <div>
                  <span className="text-gray-400">Type:</span>
                  <span className="ml-2 text-white">{currentMission.type}</span>
                </div>
                <div>
                  <span className="text-gray-400">Status:</span>
                  <span className="ml-2 text-white">{currentMission.status}</span>
                </div>
                <div>
                  <span className="text-gray-400">Priority:</span>
                  <span className="ml-2 text-white">{currentMission.priority}</span>
                </div>
                <div>
                  <span className="text-gray-400">Location:</span>
                  <span className="ml-2 text-white">
                    {currentMission.target_area.lat.toFixed(4)}, {currentMission.target_area.lng.toFixed(4)}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setShowMissionViewer(false)}
                className="mt-6 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Animated background component
const AnimatedBackground = () => (
  <div className="absolute inset-0 overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-cyan-900/20" />
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-blue-500/5 to-transparent" />
  </div>
)

export default App
