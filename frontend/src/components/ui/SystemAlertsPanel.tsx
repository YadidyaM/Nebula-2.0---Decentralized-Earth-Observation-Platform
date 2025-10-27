import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  X,
  Volume2,
  VolumeX,
  History,
  Bell,
  BellOff,
} from "lucide-react";
import { formatDate, formatRelativeTime } from "../../lib/formatters";
import { useWebSocket } from "../../contexts/WebSocketContext";

interface Alert {
  id: string;
  type: "info" | "warning" | "error" | "success";
  title: string;
  message: string;
  timestamp: string;
  source?: string;
  priority?: "low" | "medium" | "high" | "critical";
  autoDismiss?: boolean;
  dismissAfter?: number; // seconds
}

interface SystemAlertsPanelProps {
  className?: string;
}

const SystemAlertsPanel: React.FC<SystemAlertsPanelProps> = ({
  className = "",
}) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [maxVisibleAlerts] = useState(5);
  const [alertHistory, setAlertHistory] = useState<Alert[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const { subscribe, isConnected } = useWebSocket();

  // Alert type configurations
  const alertTypes = {
    info: {
      icon: Info,
      color: "text-blue-400",
      bgColor: "bg-blue-500/20",
      borderColor: "border-blue-500/30",
      sound: "/sounds/info.mp3",
    },
    warning: {
      icon: AlertTriangle,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/20",
      borderColor: "border-yellow-500/30",
      sound: "/sounds/warning.mp3",
    },
    error: {
      icon: XCircle,
      color: "text-red-400",
      bgColor: "bg-red-500/20",
      borderColor: "border-red-500/30",
      sound: "/sounds/error.mp3",
    },
    success: {
      icon: CheckCircle,
      color: "text-green-400",
      bgColor: "bg-green-500/20",
      borderColor: "border-green-500/30",
      sound: "/sounds/success.mp3",
    },
  };

  // Play alert sound
  const playAlertSound = (type: keyof typeof alertTypes) => {
    if (!soundEnabled) return;

    try {
      const audio = new Audio(alertTypes[type].sound);
      audio.volume = 0.3;
      audio.play().catch(() => {
        // Fallback to system beep if custom sound fails
        console.log("Alert sound played");
      });
    } catch (error) {
      console.log("Could not play alert sound:", error);
    }
  };

  // Show browser notification
  const showBrowserNotification = (alert: Alert) => {
    if (!notificationsEnabled || !("Notification" in window)) return;

    if (Notification.permission === "granted") {
      new Notification(alert.title, {
        body: alert.message,
        icon: "/favicon.ico",
        tag: alert.id,
      });
    } else if (Notification.permission !== "denied") {
      Notification.requestPermission().then((permission) => {
        if (permission === "granted") {
          new Notification(alert.title, {
            body: alert.message,
            icon: "/favicon.ico",
            tag: alert.id,
          });
        }
      });
    }
  };

  // Add new alert
  const addAlert = (alert: Alert) => {
    const newAlert = {
      ...alert,
      id: alert.id || `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: alert.timestamp || new Date().toISOString(),
      autoDismiss: alert.autoDismiss !== false,
      dismissAfter: alert.dismissAfter || 5,
    };

    setAlerts((prev) => {
      const updated = [newAlert, ...prev].slice(0, maxVisibleAlerts);
      return updated;
    });

    // Add to history
    setAlertHistory((prev) => [newAlert, ...prev].slice(0, 50));

    // Play sound and show notification
    playAlertSound(newAlert.type);
    showBrowserNotification(newAlert);

    // Auto-dismiss after specified time
    if (newAlert.autoDismiss) {
      setTimeout(() => {
        dismissAlert(newAlert.id);
      }, newAlert.dismissAfter! * 1000);
    }
  };

  // Dismiss alert
  const dismissAlert = (alertId: string) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
  };

  // Clear all alerts
  const clearAllAlerts = () => {
    setAlerts([]);
  };

  // WebSocket subscription for alerts
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribe = subscribe("risk_alert", (message) => {
      addAlert({
        type: "warning",
        title: "Risk Alert",
        message: message.description,
        source: message.source,
        priority: message.severity,
      });
    });

    const unsubscribe2 = subscribe("mission_update", (message) => {
      addAlert({
        type: message.status === "completed" ? "success" : "info",
        title: "Mission Update",
        message: `Mission "${message.name}" is now ${message.status}`,
        source: "Mission Control",
      });
    });

    const unsubscribe3 = subscribe("agent_status_update", (message) => {
      if (message.status === "error") {
        addAlert({
          type: "error",
          title: "Agent Error",
          message: `Agent ${message.agent_id} encountered an error: ${message.error}`,
          source: "Agent System",
          priority: "high",
        });
      } else if (message.status === "offline") {
        addAlert({
          type: "warning",
          title: "Agent Offline",
          message: `Agent ${message.agent_id} has gone offline`,
          source: "Agent System",
        });
      }
    });

    return () => {
      unsubscribe();
      unsubscribe2();
      unsubscribe3();
    };
  }, [subscribe, isConnected]);

  // Load settings from localStorage
  useEffect(() => {
    const savedSoundEnabled = localStorage.getItem("nebula-sound-enabled");
    const savedNotificationsEnabled = localStorage.getItem("nebula-notifications-enabled");

    if (savedSoundEnabled !== null) {
      setSoundEnabled(JSON.parse(savedSoundEnabled));
    }
    if (savedNotificationsEnabled !== null) {
      setNotificationsEnabled(JSON.parse(savedNotificationsEnabled));
    }
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem("nebula-sound-enabled", JSON.stringify(soundEnabled));
  }, [soundEnabled]);

  useEffect(() => {
    localStorage.setItem("nebula-notifications-enabled", JSON.stringify(notificationsEnabled));
  }, [notificationsEnabled]);

  return (
    <div className={`fixed top-4 right-4 z-50 w-96 max-w-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-cyan-400" />
          <h3 className="text-lg font-semibold text-slate-100">System Alerts</h3>
          {alerts.length > 0 && (
            <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-full">
              {alerts.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`p-1 rounded transition-all ${
              soundEnabled
                ? "text-green-400 hover:text-green-300"
                : "text-slate-400 hover:text-slate-300"
            }`}
            title={soundEnabled ? "Disable sounds" : "Enable sounds"}
          >
            {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setNotificationsEnabled(!notificationsEnabled)}
            className={`p-1 rounded transition-all ${
              notificationsEnabled
                ? "text-blue-400 hover:text-blue-300"
                : "text-slate-400 hover:text-slate-300"
            }`}
            title={notificationsEnabled ? "Disable notifications" : "Enable notifications"}
          >
            {notificationsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className={`p-1 rounded transition-all ${
              showHistory
                ? "text-cyan-400 hover:text-cyan-300"
                : "text-slate-400 hover:text-slate-300"
            }`}
            title="Toggle alert history"
          >
            <History className="w-4 h-4" />
          </button>
          {alerts.length > 0 && (
            <button
              onClick={clearAllAlerts}
              className="p-1 rounded text-slate-400 hover:text-red-400 transition-all"
              title="Clear all alerts"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Alert History */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 max-h-64 overflow-y-auto"
          >
            <div className="backdrop-blur-md bg-slate-900/90 border border-slate-600/30 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-slate-100 mb-3">Alert History</h4>
              <div className="space-y-2">
                {alertHistory.slice(0, 10).map((alert) => {
                  const config = alertTypes[alert.type];
                  const Icon = config.icon;
                  return (
                    <div
                      key={alert.id}
                      className={`p-2 rounded border ${config.bgColor} ${config.borderColor}`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={`w-3 h-3 ${config.color}`} />
                        <span className="text-xs font-medium text-slate-100">
                          {alert.title}
                        </span>
                        <span className="text-xs text-slate-400 ml-auto">
                          {formatRelativeTime(alert.timestamp)}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300">{alert.message}</p>
                    </div>
                  );
                })}
                {alertHistory.length === 0 && (
                  <p className="text-slate-400 text-sm text-center py-4">
                    No alert history
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active Alerts */}
      <div className="space-y-3">
        <AnimatePresence>
          {alerts.map((alert) => {
            const config = alertTypes[alert.type];
            const Icon = config.icon;
            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: 300, scale: 0.9 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 300, scale: 0.9 }}
                transition={{ type: "spring", damping: 20, stiffness: 300 }}
                className={`relative backdrop-blur-md bg-slate-900/90 border rounded-lg p-4 shadow-xl ${config.bgColor} ${config.borderColor}`}
              >
                {/* Alert Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${config.color}`} />
                    <h4 className="font-semibold text-slate-100">{alert.title}</h4>
                    {alert.priority === "critical" && (
                      <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 text-xs rounded-full border border-red-500/30">
                        CRITICAL
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="p-1 rounded text-slate-400 hover:text-slate-200 transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Alert Message */}
                <p className="text-slate-300 text-sm mb-3">{alert.message}</p>

                {/* Alert Footer */}
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-3">
                    <span>{formatDate(alert.timestamp, "HH:mm:ss")}</span>
                    {alert.source && (
                      <span className="px-1.5 py-0.5 bg-slate-700/50 rounded">
                        {alert.source}
                      </span>
                    )}
                  </div>
                  {alert.autoDismiss && (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                      <span>Auto-dismiss</span>
                    </div>
                  )}
                </div>

                {/* Scan line effect */}
                <div className="absolute inset-0 scan-line opacity-30" />
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Empty State */}
        {alerts.length === 0 && !showHistory && (
          <div className="text-center py-8">
            <Bell className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-slate-400 text-sm">No active alerts</p>
            <p className="text-slate-500 text-xs mt-1">
              System alerts will appear here
            </p>
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`} />
          <span>{isConnected ? "Connected" : "Disconnected"}</span>
        </div>
      </div>
    </div>
  );
};

export default SystemAlertsPanel;
