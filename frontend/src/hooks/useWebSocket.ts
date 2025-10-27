import { useState, useEffect, useCallback, useRef } from "react";
import { wsManager } from "../services/websocket";
import {
  WebSocketMessageType,
  WebSocketMessage,
  ChatMessage,
  SystemAlert,
  Mission,
  Agent,
  TelemetryData,
  RiskPoint,
} from "../types";

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionState: string;
  lastMessage: WebSocketMessage | null;
  reconnectAttempts: number;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendMessage: (message: WebSocketMessage) => boolean;
  subscribe: (
    type: WebSocketMessageType,
    handler: (data: any) => void
  ) => () => void;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState("disconnected");
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const messageHandlers = useRef<
    Map<WebSocketMessageType, ((data: any) => void)[]>
  >(new Map());

  // Connection management
  const connect = useCallback(async () => {
    try {
      await wsManager.connect();
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
    }
  }, []);

  const disconnect = useCallback(() => {
    wsManager.disconnect();
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage): boolean => {
    return wsManager.sendMessage(message);
  }, []);

  const subscribe = useCallback(
    (
      type: WebSocketMessageType,
      handler: (data: any) => void
    ): (() => void) => {
      // Store handler reference
      if (!messageHandlers.current.has(type)) {
        messageHandlers.current.set(type, []);
      }
      messageHandlers.current.get(type)!.push(handler);

      // Subscribe to WebSocket manager
      const unsubscribe = wsManager.subscribe(type, (data) => {
        setLastMessage({
          type,
          data,
          timestamp: new Date().toISOString(),
        });
        handler(data);
      });

      // Return combined unsubscribe function
      return () => {
        unsubscribe();
        const handlers = messageHandlers.current.get(type);
        if (handlers) {
          const index = handlers.indexOf(handler);
          if (index > -1) {
            handlers.splice(index, 1);
          }
        }
      };
    },
    []
  );

  // Effect to manage connection state
  useEffect(() => {
    const unsubscribeConnection = wsManager.onConnectionChange((connected) => {
      setIsConnected(connected);
      setConnectionState(wsManager.getConnectionState());
      setReconnectAttempts(wsManager.getReconnectAttempts());
    });

    // Initial state
    setIsConnected(wsManager.isConnected());
    setConnectionState(wsManager.getConnectionState());
    setReconnectAttempts(wsManager.getReconnectAttempts());

    // Auto-connect on mount
    if (!wsManager.isConnected()) {
      connect();
    }

    return () => {
      unsubscribeConnection();
    };
  }, [connect]);

  // Effect to update connection state periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setConnectionState(wsManager.getConnectionState());
      setReconnectAttempts(wsManager.getReconnectAttempts());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return {
    isConnected,
    connectionState,
    lastMessage,
    reconnectAttempts,
    connect,
    disconnect,
    sendMessage,
    subscribe,
  };
};

// Chat-specific hook
export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.CHAT_MESSAGE,
      (data: ChatMessage) => {
        setMessages((prev) => [...prev, data]);
        setIsTyping(false);
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const sendMessage = useCallback(
    (content: string, type: "command" | "response" = "command") => {
      const message: ChatMessage = {
        id: `msg_${Date.now()}`,
        type: type === "command" ? "command" : "response",
        content,
        timestamp: new Date().toISOString(),
        sender: "user",
      };

      const success = wsManager.sendChatMessage(content, type);
      if (success) {
        setMessages((prev) => [...prev, message]);
        setIsTyping(true);
      }

      return success;
    },
    []
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isTyping,
    sendMessage,
    clearMessages,
  };
};

// System alerts hook
export const useSystemAlerts = () => {
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.SYSTEM_ALERT,
      (data: SystemAlert) => {
        setAlerts((prev) => [...prev, data]);
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const dismissAlert = useCallback((alertId: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === alertId ? { ...alert, dismissed: true } : alert
      )
    );
  }, []);

  const clearDismissedAlerts = useCallback(() => {
    setAlerts((prev) => prev.filter((alert) => !alert.dismissed));
  }, []);

  return {
    alerts,
    dismissAlert,
    clearDismissedAlerts,
  };
};

// Mission updates hook
export const useMissionUpdates = () => {
  const [missionUpdates, setMissionUpdates] = useState<Mission[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.MISSION_UPDATE,
      (data: Mission) => {
        setMissionUpdates((prev) => {
          const existingIndex = prev.findIndex((m) => m.id === data.id);
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = data;
            return updated;
          }
          return [...prev, data];
        });
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const clearUpdates = useCallback(() => {
    setMissionUpdates([]);
  }, []);

  return {
    missionUpdates,
    clearUpdates,
  };
};

// Agent updates hook
export const useAgentUpdates = () => {
  const [agentUpdates, setAgentUpdates] = useState<Agent[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.AGENT_STATUS_UPDATE,
      (data: Agent) => {
        setAgentUpdates((prev) => {
          const existingIndex = prev.findIndex((a) => a.id === data.id);
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = data;
            return updated;
          }
          return [...prev, data];
        });
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const clearUpdates = useCallback(() => {
    setAgentUpdates([]);
  }, []);

  return {
    agentUpdates,
    clearUpdates,
  };
};

// Telemetry updates hook
export const useTelemetryUpdates = () => {
  const [telemetryUpdates, setTelemetryUpdates] = useState<TelemetryData[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.TELEMETRY_UPDATE,
      (data: TelemetryData) => {
        setTelemetryUpdates((prev) => {
          // Keep only the last 100 updates to prevent memory issues
          const updated = [...prev, data].slice(-100);
          return updated;
        });
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const clearUpdates = useCallback(() => {
    setTelemetryUpdates([]);
  }, []);

  return {
    telemetryUpdates,
    clearUpdates,
  };
};

// Risk alerts hook
export const useRiskAlerts = () => {
  const [riskAlerts, setRiskAlerts] = useState<RiskPoint[]>([]);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe(
      WebSocketMessageType.RISK_ALERT,
      (data: RiskPoint) => {
        setRiskAlerts((prev) => {
          const existingIndex = prev.findIndex((r) => r.id === data.id);
          if (existingIndex >= 0) {
            const updated = [...prev];
            updated[existingIndex] = data;
            return updated;
          }
          return [...prev, data];
        });
      }
    );

    return unsubscribe;
  }, [subscribe]);

  const clearAlerts = useCallback(() => {
    setRiskAlerts([]);
  }, []);

  return {
    riskAlerts,
    clearAlerts,
  };
};
