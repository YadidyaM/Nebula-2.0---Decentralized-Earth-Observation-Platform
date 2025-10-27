import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ErrorBoundary } from 'react-error-boundary'

// Components
import EarthScene from '../components/3d/EarthScene'
import HolographicOverlay from '../components/ui/HolographicOverlay'
import SatelliteChat from '../components/chat/SatelliteChat'
import TopToolbar from '../components/ui/TopToolbar'
import MissionControlHeader from '../components/ui/MissionControlHeader'
import WalletConnectButton from '../components/blockchain/WalletConnectButton'
import TokenBalanceDisplay from '../components/blockchain/TokenBalanceDisplay'
import AgentNFTGallery from '../components/agents/AgentNFTGallery'
import MissionRegistryView from '../components/blockchain/MissionRegistryView'
import AgentStatusGrid from '../components/agents/AgentStatusGrid'
import MissionQueuePanel from '../components/missions/MissionQueuePanel'
import TelemetryTrendsChart from '../components/telemetry/TelemetryTrendsChart'
import OrbitalPassPredictor from '../components/telemetry/OrbitalPassPredictor'
import RiskHeatmap from '../components/telemetry/RiskHeatmap'
import SatelliteTelemetryPanel from '../components/telemetry/SatelliteTelemetryPanel'
import SystemAlertsPanel from '../components/ui/SystemAlertsPanel'
import SettingsPanel from '../components/ui/SettingsPanel'

// Hooks
import { useWebSocket } from '../hooks/useWebSocket'
import { useWallet } from '../hooks/useWallet'
import { useMissions } from '../hooks/useMissions'
import { useAgents } from '../hooks/useAgents'
import { useTelemetry } from '../hooks/useTelemetry'
import { useBlockchain } from '../hooks/useBlockchain'

// Types
import { Mission, Agent, TelemetryData, BlockchainTransaction, Alert } from '../types'

// Services
import { apiClient } from '../services/api'

interface DashboardState {
  activePanel: string | null
  currentMission: Mission | null
  selectedAgent: Agent | null
  alerts: Alert[]
  isLoading: boolean
  error: string | null
  lastUpdate: Date
}

const Dashboard: React.FC = () => {
  // State management
  const [state, setState] = useState<DashboardState>({
    activePanel: null,
    currentMission: null,
    selectedAgent: null,
    alerts: [],
    isLoading: true,
    error: null,
    lastUpdate: new Date()
  })

  // WebSocket connection
  const { isConnected, lastMessage, sendMessage } = useWebSocket()
  
  // Wallet connection
  const { connected, publicKey, balance, connect, disconnect } = useWallet()
  
  // Data hooks
  const { missions, createMission, updateMission, deleteMission } = useMissions()
  const { agents, updateAgent, stakeAgent, unstakeAgent } = useAgents()
  const { telemetryData, getTelemetryTrends } = useTelemetry()
  const { transactions, getWalletBalance } = useBlockchain()

  // Panel configurations
  const panelConfigs = useMemo(() => ({
    telemetry: {
      component: <TelemetryTrendsChart agentId={state.selectedAgent?.id} />,
      title: 'Telemetry Trends',
      icon: '📊'
    },
    missions: {
      component: <MissionQueuePanel 
        missions={missions}
        onMissionSelect={setCurrentMission}
        onCreateMission={createMission}
        onUpdateMission={updateMission}
        onDeleteMission={deleteMission}
      />,
      title: 'Mission Queue',
      icon: '🎯'
    },
    agents: {
      component: <AgentStatusGrid 
        agents={agents}
        onAgentSelect={setSelectedAgent}
        onUpdateAgent={updateAgent}
        onStakeAgent={stakeAgent}
        onUnstakeAgent={unstakeAgent}
      />,
      title: 'Agent Status',
      icon: '🤖'
    },
    trends: {
      component: <TelemetryTrendsChart agentId={state.selectedAgent?.id} />,
      title: 'Analytics Trends',
      icon: '📈'
    },
    passes: {
      component: <OrbitalPassPredictor />,
      title: 'Orbital Passes',
      icon: '🛰️'
    },
    heatmap: {
      component: <RiskHeatmap />,
      title: 'Risk Heatmap',
      icon: '🔥'
    },
    wallet: {
      component: <div className="p-6">
        <WalletConnectButton />
        {connected && <TokenBalanceDisplay />}
      </div>,
      title: 'Wallet Manager',
      icon: '💰'
    },
    nfts: {
      component: <AgentNFTGallery 
        agents={agents}
        onAgentSelect={setSelectedAgent}
      />,
      title: 'Agent NFTs',
      icon: '🖼️'
    },
    blockchain: {
      component: <MissionRegistryView 
        transactions={transactions}
        onTransactionSelect={(tx) => console.log('Selected transaction:', tx)}
      />,
      title: 'Blockchain Explorer',
      icon: '⛓️'
    },
    alerts: {
      component: <SystemAlertsPanel 
        alerts={state.alerts}
        onAlertDismiss={removeAlert}
      />,
      title: 'System Alerts',
      icon: '⚠️'
    },
    settings: {
      component: <SettingsPanel />,
      title: 'Settings',
      icon: '⚙️'
    }
  }), [missions, agents, transactions, state.selectedAgent, state.alerts, connected])

  // Panel management
  const setActivePanel = useCallback((panelId: string | null) => {
    setState(prev => ({ ...prev, activePanel: panelId }))
  }, [])

  const setCurrentMission = useCallback((mission: Mission | null) => {
    setState(prev => ({ ...prev, currentMission: mission }))
  }, [])

  const setSelectedAgent = useCallback((agent: Agent | null) => {
    setState(prev => ({ ...prev, selectedAgent: agent }))
  }, [])

  const addAlert = useCallback((alert: Alert) => {
    setState(prev => ({
      ...prev,
      alerts: [...prev.alerts, { ...alert, id: Date.now().toString() }]
    }))
  }, [])

  const removeAlert = useCallback((alertId: string) => {
    setState(prev => ({
      ...prev,
      alerts: prev.alerts.filter(alert => alert.id !== alertId)
    }))
  }, [])

  // WebSocket message handling
  useEffect(() => {
    if (!lastMessage) return

    try {
      const message = JSON.parse(lastMessage)
      
      switch (message.type) {
        case 'mission_update':
          if (message.data) {
            updateMission(message.data)
            addAlert({
              type: 'info',
              title: 'Mission Update',
              message: `Mission "${message.data.name}" status updated to ${message.data.status}`,
              timestamp: new Date()
            })
          }
          break

        case 'agent_status_update':
          if (message.data) {
            updateAgent(message.data.id, message.data)
            addAlert({
              type: 'info',
              title: 'Agent Status',
              message: `Agent "${message.data.name}" is now ${message.data.status}`,
              timestamp: new Date()
            })
          }
          break

        case 'telemetry_update':
          if (message.data) {
            addAlert({
              type: 'info',
              title: 'Telemetry Update',
              message: `New telemetry data from ${message.data.agent_id}`,
              timestamp: new Date()
            })
          }
          break

        case 'risk_alert':
          if (message.data) {
            addAlert({
              type: 'warning',
              title: 'Risk Alert',
              message: message.data.description,
              timestamp: new Date()
            })
          }
          break

        case 'blockchain_update':
          if (message.data) {
            addAlert({
              type: 'success',
              title: 'Blockchain Update',
              message: `Transaction ${message.data.transaction_hash} confirmed`,
              timestamp: new Date()
            })
          }
          break

        case 'heartbeat':
          setState(prev => ({ ...prev, lastUpdate: new Date() }))
          break

        default:
          console.log('Unknown message type:', message.type)
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }, [lastMessage, updateMission, updateAgent, addAlert])

  // Initial data loading
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setState(prev => ({ ...prev, isLoading: true, error: null }))

        // Load initial data in parallel
        await Promise.all([
          // Missions, agents, telemetry data will be loaded by their respective hooks
          // Additional API calls can be added here
        ])

        setState(prev => ({ ...prev, isLoading: false }))
      } catch (error) {
        console.error('Error loading initial data:', error)
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: error instanceof Error ? error.message : 'Failed to load data'
        }))
      }
    }

    loadInitialData()
  }, [])

  // Auto-refresh data
  useEffect(() => {
    const interval = setInterval(() => {
      setState(prev => ({ ...prev, lastUpdate: new Date() }))
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  // Error boundary fallback
  const ErrorFallback = ({ error, resetErrorBoundary }: { error: Error, resetErrorBoundary: () => void }) => (
    <div className="flex items-center justify-center min-h-screen bg-black text-red-400">
      <div className="text-center p-8">
        <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
        <p className="text-gray-400 mb-6">{error.message}</p>
        <button
          onClick={resetErrorBoundary}
          className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  )

  // Loading skeleton
  if (state.isLoading) {
    return (
      <div className="relative w-screen h-screen overflow-hidden bg-black">
        <EarthScene />
        <HolographicOverlay />
        
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-400 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-cyan-400 mb-2">Initializing Mission Control</h2>
            <p className="text-gray-400">Loading satellite networks...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <div className="relative w-screen h-screen overflow-hidden bg-black">
        {/* Background Layers */}
        <EarthScene />
        <HolographicOverlay />
        
        {/* Main UI Components */}
        <SatelliteChat />
        
        <TopToolbar 
          activePanel={state.activePanel}
          onPanelChange={setActivePanel}
        />
        
        <MissionControlHeader 
          isConnected={isConnected}
          missionCount={missions.length}
          activeMission={state.currentMission}
          lastUpdate={state.lastUpdate}
        />
        
        {/* Wallet Integration */}
        <div className="fixed top-4 right-4 z-50 flex gap-2">
          <WalletConnectButton />
          {connected && <TokenBalanceDisplay />}
        </div>
        
        {/* System Alerts */}
        <SystemAlertsPanel 
          alerts={state.alerts}
          onAlertDismiss={removeAlert}
        />
        
        {/* Error Display */}
        {state.error && (
          <div className="fixed top-20 right-4 z-50 max-w-md">
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              className="bg-red-900/80 backdrop-blur-md border border-red-500/30 rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-red-400 font-bold">Error</h3>
                  <p className="text-gray-300 text-sm">{state.error}</p>
                </div>
                <button
                  onClick={() => setState(prev => ({ ...prev, error: null }))}
                  className="text-red-400 hover:text-red-300"
                >
                  ✕
                </button>
              </div>
            </motion.div>
          </div>
        )}
        
        {/* Panel Modal */}
        <AnimatePresence>
          {state.activePanel && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 flex items-center justify-center p-4"
            >
              {/* Backdrop */}
              <div 
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={() => setActivePanel(null)}
              />
              
              {/* Panel Content */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className="relative w-full max-w-6xl max-h-[90vh] overflow-hidden"
              >
                <div className="relative group">
                  {/* Holographic glow effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 
                                rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300" />
                  
                  {/* Panel container */}
                  <div className="relative backdrop-blur-md bg-slate-900/80 border border-cyan-500/30 
                                rounded-lg hover:border-cyan-400/50 transition-all">
                    
                    {/* Panel header */}
                    <div className="flex items-center justify-between p-4 border-b border-cyan-500/20">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{panelConfigs[state.activePanel]?.icon}</span>
                        <h2 className="text-xl font-bold text-cyan-400">
                          {panelConfigs[state.activePanel]?.title}
                        </h2>
                      </div>
                      
                      <button
                        onClick={() => setActivePanel(null)}
                        className="text-gray-400 hover:text-cyan-400 transition-colors p-2"
                      >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    
                    {/* Panel content */}
                    <div className="p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
                      {panelConfigs[state.activePanel]?.component}
                    </div>
                  </div>
                  
                  {/* Scan line effect */}
                  <div className="absolute inset-0 scan-line" />
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Connection Status Indicator */}
        <div className="fixed bottom-4 left-4 z-50">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg backdrop-blur-md border ${
            isConnected 
              ? 'bg-green-900/80 border-green-500/30 text-green-400' 
              : 'bg-red-900/80 border-red-500/30 text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`} />
            <span className="text-sm font-medium">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        
        {/* Wallet Connection Prompt */}
        {!connected && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-4 right-4 z-50"
          >
            <div className="bg-blue-900/80 backdrop-blur-md border border-blue-500/30 rounded-lg p-4 max-w-sm">
              <h3 className="text-blue-400 font-bold mb-2">Connect Wallet</h3>
              <p className="text-gray-300 text-sm mb-3">
                Connect your Solana wallet to access all features and manage your agents.
              </p>
              <WalletConnectButton />
            </div>
          </motion.div>
        )}
      </div>
    </ErrorBoundary>
  )
}

export default Dashboard
