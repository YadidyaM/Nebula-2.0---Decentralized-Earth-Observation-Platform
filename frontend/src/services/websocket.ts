import {
  WebSocketMessage,
  WebSocketMessageType,
  ChatMessage,
  SystemAlert,
  Mission,
  Agent,
  TelemetryData,
  RiskPoint,
} from "../types";

type MessageHandler = (data: any) => void;
type ConnectionHandler = (connected: boolean) => void;

class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private messageHandlers = new Map<WebSocketMessageType, MessageHandler[]>();
  private connectionHandlers: ConnectionHandler[] = [];
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastHeartbeat = 0;

  constructor() {
    this.url = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
  }

  // Connection Management
  async connect(): Promise<void> {
    if (
      this.isConnecting ||
      (this.ws && this.ws.readyState === WebSocket.OPEN)
    ) {
      return;
    }

    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error("WebSocket connection error:", error);
      this.isConnecting = false;
      throw error;
    }
  }

  private handleOpen() {
    console.log("WebSocket connected");
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.startHeartbeat();
    this.notifyConnectionHandlers(true);
  }

  private handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      // Update last heartbeat
      if (
        message.type === WebSocketMessageType.SYSTEM_ALERT &&
        message.data?.type === "heartbeat"
      ) {
        this.lastHeartbeat = Date.now();
        return;
      }

      // Notify handlers
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach((handler) => {
          try {
            handler(message.data);
          } catch (error) {
            console.error(
              `Error in message handler for ${message.type}:`,
              error
            );
          }
        });
      }

      // Log message for debugging
      if (import.meta.env.VITE_DEBUG === "true") {
        console.log("WebSocket message received:", message);
      }
    } catch (error) {
      console.error("Error parsing WebSocket message:", error);
    }
  }

  private handleClose(event: CloseEvent) {
    console.log("WebSocket disconnected:", event.code, event.reason);
    this.isConnecting = false;
    this.stopHeartbeat();
    this.notifyConnectionHandlers(false);

    // Attempt reconnection if not a clean close
    if (
      event.code !== 1000 &&
      this.reconnectAttempts < this.maxReconnectAttempts
    ) {
      this.scheduleReconnect();
    }
  }

  private handleError(error: Event) {
    console.error("WebSocket error:", error);
    this.isConnecting = false;
  }

  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`
    );

    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect();
      }
    }, delay);
  }

  // Heartbeat Management
  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.sendHeartbeat();
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private sendHeartbeat() {
    const message: WebSocketMessage = {
      type: WebSocketMessageType.SYSTEM_ALERT,
      data: { type: "heartbeat", timestamp: new Date().toISOString() },
      timestamp: new Date().toISOString(),
    };

    this.sendMessage(message);
  }

  // Message Subscription
  subscribe(type: WebSocketMessageType, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }

    this.messageHandlers.get(type)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  // Connection Status Subscription
  onConnectionChange(handler: ConnectionHandler): () => void {
    this.connectionHandlers.push(handler);

    // Return unsubscribe function
    return () => {
      const index = this.connectionHandlers.indexOf(handler);
      if (index > -1) {
        this.connectionHandlers.splice(index, 1);
      }
    };
  }

  private notifyConnectionHandlers(connected: boolean) {
    this.connectionHandlers.forEach((handler) => {
      try {
        handler(connected);
      } catch (error) {
        console.error("Error in connection handler:", error);
      }
    });
  }

  // Message Sending
  sendMessage(message: WebSocketMessage): boolean {
    if (!this.isConnected()) {
      console.warn("WebSocket not connected, cannot send message");
      return false;
    }

    try {
      this.ws!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error("Error sending WebSocket message:", error);
      return false;
    }
  }

  // Convenience methods for specific message types
  sendChatMessage(
    content: string,
    type: "command" | "response" = "command"
  ): boolean {
    const message: WebSocketMessage = {
      type: WebSocketMessageType.CHAT_MESSAGE,
      data: {
        content,
        type,
        timestamp: new Date().toISOString(),
        sender: "user",
      },
      timestamp: new Date().toISOString(),
    };

    return this.sendMessage(message);
  }

  sendVoiceCommand(text: string, confidence: number): boolean {
    const message: WebSocketMessage = {
      type: WebSocketMessageType.VOICE_COMMAND,
      data: {
        text,
        confidence,
        timestamp: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    };

    return this.sendMessage(message);
  }

  // Status Methods
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return "disconnected";

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return "connecting";
      case WebSocket.OPEN:
        return "connected";
      case WebSocket.CLOSING:
        return "closing";
      case WebSocket.CLOSED:
        return "disconnected";
      default:
        return "unknown";
    }
  }

  getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  // Cleanup
  disconnect(): void {
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.messageHandlers.clear();
    this.connectionHandlers = [];
  }

  // Utility Methods
  getLastHeartbeat(): number {
    return this.lastHeartbeat;
  }

  isHeartbeatHealthy(): boolean {
    const now = Date.now();
    const timeSinceLastHeartbeat = now - this.lastHeartbeat;
    return timeSinceLastHeartbeat < 60000; // Consider healthy if heartbeat within last minute
  }
}

// Create singleton instance
export const wsManager = new WebSocketManager();
export default wsManager;
