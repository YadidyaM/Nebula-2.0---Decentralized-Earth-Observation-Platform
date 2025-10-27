import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { EventEmitter } from 'events'

// Types
interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: string
  [key: string]: any
}

interface WebSocketContextType {
  isConnected: boolean
  isConnecting: boolean
  lastMessage: string | null
  error: string | null
  subscribe: (type: string, callback: (message: WebSocketMessage) => void) => void
  unsubscribe: (type: string, callback?: (message: WebSocketMessage) => void) => void
  send: (message: WebSocketMessage) => void
  connect: () => void
  disconnect: () => void
  reconnect: () => void
}

interface WebSocketProviderProps {
  children: React.ReactNode
  url?: string
  autoConnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

// Create context
const WebSocketContext = createContext<WebSocketContextType | null>(null)

// WebSocket provider component
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  autoConnect = true,
  reconnectInterval = 5000,
  maxReconnectAttempts = 10
}) => {
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [lastMessage, setLastMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const eventEmitterRef = useRef(new EventEmitter())
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnecting) {
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setIsConnecting(false)
        setError(null)
        reconnectAttemptsRef.current = 0

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setLastMessage(event.data)

          // Handle pong responses
          if (message.type === 'pong') {
            return
          }

          // Emit message to subscribers
          eventEmitterRef.current.emit('message', message)
          eventEmitterRef.current.emit(`message:${message.type}`, message)
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
          setError('Failed to parse message')
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setIsConnecting(false)
        
        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
          heartbeatIntervalRef.current = null
        }

        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Failed to reconnect after maximum attempts')
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
        setIsConnecting(false)
      }

    } catch (err) {
      console.error('Error creating WebSocket connection:', err)
      setError('Failed to create WebSocket connection')
      setIsConnecting(false)
    }
  }, [url, isConnecting, reconnectInterval, maxReconnectAttempts])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
      wsRef.current = null
    }

    setIsConnected(false)
    setIsConnecting(false)
    reconnectAttemptsRef.current = 0
  }, [])

  // Reconnect to WebSocket
  const reconnect = useCallback(() => {
    disconnect()
    setTimeout(() => {
      connect()
    }, 1000)
  }, [connect, disconnect])

  // Send message
  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        const messageWithTimestamp = {
          ...message,
          timestamp: new Date().toISOString()
        }
        wsRef.current.send(JSON.stringify(messageWithTimestamp))
      } catch (err) {
        console.error('Error sending WebSocket message:', err)
        setError('Failed to send message')
      }
    } else {
      console.warn('WebSocket is not connected')
      setError('WebSocket is not connected')
    }
  }, [])

  // Subscribe to message types
  const subscribe = useCallback((
    type: string, 
    callback: (message: WebSocketMessage) => void
  ) => {
    eventEmitterRef.current.on(`message:${type}`, callback)
  }, [])

  // Unsubscribe from message types
  const unsubscribe = useCallback((
    type: string, 
    callback?: (message: WebSocketMessage) => void
  ) => {
    if (callback) {
      eventEmitterRef.current.off(`message:${type}`, callback)
    } else {
      eventEmitterRef.current.removeAllListeners(`message:${type}`)
    }
  }, [])

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  const contextValue: WebSocketContextType = {
    isConnected,
    isConnecting,
    lastMessage,
    error,
    subscribe,
    unsubscribe,
    send,
    connect,
    disconnect,
    reconnect
  }

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  )
}

// Hook to use WebSocket context
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

// Hook for subscribing to specific message types
export const useWebSocketSubscription = (
  type: string,
  callback: (message: WebSocketMessage) => void,
  deps: React.DependencyList = []
) => {
  const { subscribe, unsubscribe } = useWebSocket()

  useEffect(() => {
    subscribe(type, callback)
    return () => unsubscribe(type, callback)
  }, [subscribe, unsubscribe, type, ...deps])
}

// Hook for sending messages
export const useWebSocketSend = () => {
  const { send } = useWebSocket()
  return send
}

// Utility functions
export const createWebSocketMessage = (
  type: string,
  data?: any
): WebSocketMessage => ({
  type,
  data,
  timestamp: new Date().toISOString()
})

export const isWebSocketMessage = (obj: any): obj is WebSocketMessage => {
  return obj && typeof obj === 'object' && typeof obj.type === 'string'
}

// Message type constants
export const MESSAGE_TYPES = {
  PING: 'ping',
  PONG: 'pong',
  HEARTBEAT: 'heartbeat',
  MISSION_UPDATE: 'mission_update',
  AGENT_STATUS_UPDATE: 'agent_status_update',
  TELEMETRY_UPDATE: 'telemetry_update',
  RISK_ALERT: 'risk_alert',
  BLOCKCHAIN_UPDATE: 'blockchain_update',
  SYSTEM_ALERT: 'system_alert',
  SUBSCRIBE_ROOM: 'subscribe_room',
  UNSUBSCRIBE_ROOM: 'unsubscribe_room',
  SUBSCRIPTION_CONFIRMED: 'subscription_confirmed',
  UNSUBSCRIPTION_CONFIRMED: 'unsubscription_confirmed'
} as const

// Room subscription helpers
export const useRoomSubscription = (roomId: string) => {
  const { send, subscribe, unsubscribe } = useWebSocket()

  const subscribeToRoom = useCallback(() => {
    send(createWebSocketMessage(MESSAGE_TYPES.SUBSCRIBE_ROOM, { room_id: roomId }))
  }, [send, roomId])

  const unsubscribeFromRoom = useCallback(() => {
    send(createWebSocketMessage(MESSAGE_TYPES.UNSUBSCRIBE_ROOM, { room_id: roomId }))
  }, [send, roomId])

  const subscribeToRoomMessages = useCallback((
    callback: (message: WebSocketMessage) => void
  ) => {
    subscribe(`room:${roomId}`, callback)
    return () => unsubscribe(`room:${roomId}`, callback)
  }, [subscribe, unsubscribe, roomId])

  return {
    subscribeToRoom,
    unsubscribeFromRoom,
    subscribeToRoomMessages
  }
}

// Agent-specific subscription helpers
export const useAgentSubscription = (agentId: string) => {
  const { subscribe, unsubscribe } = useWebSocket()

  const subscribeToAgentUpdates = useCallback((
    callback: (message: WebSocketMessage) => void
  ) => {
    subscribe(`agent:${agentId}`, callback)
    return () => unsubscribe(`agent:${agentId}`, callback)
  }, [subscribe, unsubscribe, agentId])

  return {
    subscribeToAgentUpdates
  }
}

// Mission-specific subscription helpers
export const useMissionSubscription = (missionId: string) => {
  const { subscribe, unsubscribe } = useWebSocket()

  const subscribeToMissionUpdates = useCallback((
    callback: (message: WebSocketMessage) => void
  ) => {
    subscribe(`mission:${missionId}`, callback)
    return () => unsubscribe(`mission:${missionId}`, callback)
  }, [subscribe, unsubscribe, missionId])

  return {
    subscribeToMissionUpdates
  }
}
