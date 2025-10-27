import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Palette,
  Bell,
  Volume2,
  Monitor,
  Mic,
  Globe,
  Save,
  RotateCcw,
  X,
  ChevronDown,
  ChevronRight,
  Check,
} from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";
import { validateUrl } from "../../lib/validators";

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

interface SettingsData {
  theme: {
    preset: string;
    customColors: {
      primary: string;
      secondary: string;
      accent: string;
    };
  };
  notifications: {
    sound: boolean;
    desktop: boolean;
    alertTypes: {
      info: boolean;
      warning: boolean;
      error: boolean;
      success: boolean;
    };
  };
  api: {
    endpoint: string;
    apiKey: string;
  };
  voice: {
    language: string;
    voiceModel: string;
  };
  performance: {
    fpsLimit: number;
    quality: "low" | "medium" | "high";
  };
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  isOpen,
  onClose,
  className = "",
}) => {
  const { theme, setTheme, presets, customizeTheme } = useTheme();
  const [settings, setSettings] = useState<SettingsData>({
    theme: {
      preset: "cyan",
      customColors: {
        primary: "#06b6d4",
        secondary: "#8b5cf6",
        accent: "#10b981",
      },
    },
    notifications: {
      sound: true,
      desktop: true,
      alertTypes: {
        info: true,
        warning: true,
        error: true,
        success: true,
      },
    },
    api: {
      endpoint: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
      apiKey: "",
    },
    voice: {
      language: "en-US",
      voiceModel: "gemini-pro",
    },
    performance: {
      fpsLimit: 60,
      quality: "medium",
    },
  });

  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["theme", "notifications"])
  );
  const [hasChanges, setHasChanges] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem("nebula-settings");
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings((prev) => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error("Failed to load settings:", error);
      }
    }
  }, []);

  // Save settings to localStorage with debounce
  useEffect(() => {
    if (!hasChanges) return;

    const timeoutId = setTimeout(() => {
      localStorage.setItem("nebula-settings", JSON.stringify(settings));
      setHasChanges(false);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [settings, hasChanges]);

  // Update theme when settings change
  useEffect(() => {
    if (settings.theme.preset !== "custom") {
      setTheme(presets[settings.theme.preset]);
    } else {
      customizeTheme(settings.theme.customColors);
    }
  }, [settings.theme, setTheme, presets, customizeTheme]);

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Update settings
  const updateSettings = (path: string, value: any) => {
    setSettings((prev) => {
      const newSettings = { ...prev };
      const keys = path.split(".");
      let current = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      setHasChanges(true);
      return newSettings;
    });
  };

  // Validate settings
  const validateSettings = () => {
    const newErrors: Record<string, string> = {};

    // Validate API endpoint
    if (settings.api.endpoint) {
      const urlValidation = validateUrl(settings.api.endpoint);
      if (!urlValidation.isValid) {
        newErrors.apiEndpoint = urlValidation.errors[0];
      }
    }

    // Validate FPS limit
    if (settings.performance.fpsLimit < 30 || settings.performance.fpsLimit > 120) {
      newErrors.fpsLimit = "FPS limit must be between 30 and 120";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Save settings
  const saveSettings = () => {
    if (!validateSettings()) return;

    localStorage.setItem("nebula-settings", JSON.stringify(settings));
    setHasChanges(false);
    
    // Show success feedback
    const saveButton = document.querySelector('[data-save-button]') as HTMLElement;
    if (saveButton) {
      saveButton.style.color = "#10b981";
      setTimeout(() => {
        saveButton.style.color = "";
      }, 1000);
    }
  };

  // Reset settings
  const resetSettings = () => {
    const defaultSettings: SettingsData = {
      theme: {
        preset: "cyan",
        customColors: {
          primary: "#06b6d4",
          secondary: "#8b5cf6",
          accent: "#10b981",
        },
      },
      notifications: {
        sound: true,
        desktop: true,
        alertTypes: {
          info: true,
          warning: true,
          error: true,
          success: true,
        },
      },
      api: {
        endpoint: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
        apiKey: "",
      },
      voice: {
        language: "en-US",
        voiceModel: "gemini-pro",
      },
      performance: {
        fpsLimit: 60,
        quality: "medium",
      },
    };

    setSettings(defaultSettings);
    setHasChanges(true);
    setShowResetConfirm(false);
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Theme presets
  const themePresets = [
    { id: "cyan", name: "Cyan", colors: ["#06b6d4", "#8b5cf6", "#10b981"] },
    { id: "purple", name: "Purple", colors: ["#8b5cf6", "#ec4899", "#06b6d4"] },
    { id: "green", name: "Green", colors: ["#10b981", "#06b6d4", "#f59e0b"] },
    { id: "amber", name: "Amber", colors: ["#f59e0b", "#ef4444", "#8b5cf6"] },
  ];

  // Voice languages
  const voiceLanguages = [
    { code: "en-US", name: "English (US)" },
    { code: "en-GB", name: "English (UK)" },
    { code: "es-ES", name: "Spanish" },
    { code: "fr-FR", name: "French" },
    { code: "de-DE", name: "German" },
    { code: "ja-JP", name: "Japanese" },
    { code: "ko-KR", name: "Korean" },
    { code: "zh-CN", name: "Chinese (Simplified)" },
  ];

  // Voice models
  const voiceModels = [
    { id: "gemini-pro", name: "Gemini Pro" },
    { id: "gemini-pro-vision", name: "Gemini Pro Vision" },
    { id: "gpt-4", name: "GPT-4" },
    { id: "claude-3", name: "Claude 3" },
  ];

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${className}`}>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg blur-xl" />
        <div className="relative backdrop-blur-md bg-slate-900/90 border border-cyan-500/30 rounded-lg shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-600/30">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-cyan-400" />
              <h2 className="text-xl font-bold text-slate-100">Settings</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-slate-100 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
            <div className="space-y-6">
              {/* Theme Section */}
              <div className="border border-slate-600/30 rounded-lg">
                <button
                  onClick={() => toggleSection("theme")}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Palette className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold text-slate-100">Theme</h3>
                  </div>
                  {expandedSections.has("theme") ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>
                <AnimatePresence>
                  {expandedSections.has("theme") && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 pt-0 space-y-4">
                        {/* Theme Presets */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-3">
                            Color Presets
                          </label>
                          <div className="grid grid-cols-2 gap-3">
                            {themePresets.map((preset) => (
                              <button
                                key={preset.id}
                                onClick={() => updateSettings("theme.preset", preset.id)}
                                className={`p-3 rounded-lg border transition-all ${
                                  settings.theme.preset === preset.id
                                    ? "border-cyan-500/50 bg-cyan-500/10"
                                    : "border-slate-600/50 hover:border-slate-500/50"
                                }`}
                              >
                                <div className="flex items-center gap-2 mb-2">
                                  <div className="flex gap-1">
                                    {preset.colors.map((color, index) => (
                                      <div
                                        key={index}
                                        className="w-3 h-3 rounded-full"
                                        style={{ backgroundColor: color }}
                                      />
                                    ))}
                                  </div>
                                  <span className="text-sm text-slate-100">{preset.name}</span>
                                </div>
                                {settings.theme.preset === preset.id && (
                                  <Check className="w-4 h-4 text-cyan-400 ml-auto" />
                                )}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Custom Colors */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-3">
                            Custom Colors
                          </label>
                          <div className="grid grid-cols-3 gap-3">
                            {Object.entries(settings.theme.customColors).map(([key, value]) => (
                              <div key={key}>
                                <label className="block text-xs text-slate-400 mb-1 capitalize">
                                  {key}
                                </label>
                                <div className="flex items-center gap-2">
                                  <input
                                    type="color"
                                    value={value}
                                    onChange={(e) =>
                                      updateSettings(`theme.customColors.${key}`, e.target.value)
                                    }
                                    className="w-8 h-8 rounded border border-slate-600/50 bg-transparent"
                                  />
                                  <input
                                    type="text"
                                    value={value}
                                    onChange={(e) =>
                                      updateSettings(`theme.customColors.${key}`, e.target.value)
                                    }
                                    className="flex-1 px-2 py-1 bg-slate-800/50 border border-slate-600/50 rounded text-slate-100 text-sm font-mono"
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Notifications Section */}
              <div className="border border-slate-600/30 rounded-lg">
                <button
                  onClick={() => toggleSection("notifications")}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Bell className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold text-slate-100">Notifications</h3>
                  </div>
                  {expandedSections.has("notifications") ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>
                <AnimatePresence>
                  {expandedSections.has("notifications") && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 pt-0 space-y-4">
                        {/* Sound Notifications */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Volume2 className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-100">Sound Notifications</span>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={settings.notifications.sound}
                              onChange={(e) =>
                                updateSettings("notifications.sound", e.target.checked)
                              }
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
                          </label>
                        </div>

                        {/* Desktop Notifications */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Monitor className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-100">Desktop Notifications</span>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={settings.notifications.desktop}
                              onChange={(e) =>
                                updateSettings("notifications.desktop", e.target.checked)
                              }
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
                          </label>
                        </div>

                        {/* Alert Types */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-3">
                            Alert Types
                          </label>
                          <div className="space-y-2">
                            {Object.entries(settings.notifications.alertTypes).map(([type, enabled]) => (
                              <div key={type} className="flex items-center justify-between">
                                <span className="text-slate-100 capitalize">{type}</span>
                                <label className="relative inline-flex items-center cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={enabled}
                                    onChange={(e) =>
                                      updateSettings(`notifications.alertTypes.${type}`, e.target.checked)
                                    }
                                    className="sr-only peer"
                                  />
                                  <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-500/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* API Section */}
              <div className="border border-slate-600/30 rounded-lg">
                <button
                  onClick={() => toggleSection("api")}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Globe className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold text-slate-100">API Configuration</h3>
                  </div>
                  {expandedSections.has("api") ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>
                <AnimatePresence>
                  {expandedSections.has("api") && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 pt-0 space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            API Endpoint
                          </label>
                          <input
                            type="url"
                            value={settings.api.endpoint}
                            onChange={(e) => updateSettings("api.endpoint", e.target.value)}
                            className={`w-full px-3 py-2 bg-slate-800/50 border rounded-lg text-slate-100 placeholder-slate-400 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 ${
                              errors.apiEndpoint ? "border-red-500/50" : "border-slate-600/50"
                            }`}
                            placeholder="https://api.nebula.protocol"
                          />
                          {errors.apiEndpoint && (
                            <p className="text-red-400 text-xs mt-1">{errors.apiEndpoint}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            API Key
                          </label>
                          <input
                            type="password"
                            value={settings.api.apiKey}
                            onChange={(e) => updateSettings("api.apiKey", e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 placeholder-slate-400 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
                            placeholder="Enter your API key"
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Voice Section */}
              <div className="border border-slate-600/30 rounded-lg">
                <button
                  onClick={() => toggleSection("voice")}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Mic className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold text-slate-100">Voice Settings</h3>
                  </div>
                  {expandedSections.has("voice") ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>
                <AnimatePresence>
                  {expandedSections.has("voice") && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 pt-0 space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Language
                          </label>
                          <select
                            value={settings.voice.language}
                            onChange={(e) => updateSettings("voice.language", e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
                          >
                            {voiceLanguages.map((lang) => (
                              <option key={lang.code} value={lang.code}>
                                {lang.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Voice Model
                          </label>
                          <select
                            value={settings.voice.voiceModel}
                            onChange={(e) => updateSettings("voice.voiceModel", e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
                          >
                            {voiceModels.map((model) => (
                              <option key={model.id} value={model.id}>
                                {model.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Performance Section */}
              <div className="border border-slate-600/30 rounded-lg">
                <button
                  onClick={() => toggleSection("performance")}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Monitor className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold text-slate-100">Performance</h3>
                  </div>
                  {expandedSections.has("performance") ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>
                <AnimatePresence>
                  {expandedSections.has("performance") && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 pt-0 space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            FPS Limit: {settings.performance.fpsLimit}
                          </label>
                          <input
                            type="range"
                            min="30"
                            max="120"
                            step="10"
                            value={settings.performance.fpsLimit}
                            onChange={(e) =>
                              updateSettings("performance.fpsLimit", parseInt(e.target.value))
                            }
                            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                          />
                          {errors.fpsLimit && (
                            <p className="text-red-400 text-xs mt-1">{errors.fpsLimit}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Quality
                          </label>
                          <select
                            value={settings.performance.quality}
                            onChange={(e) =>
                              updateSettings("performance.quality", e.target.value)
                            }
                            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg text-slate-100 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20"
                          >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                          </select>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-slate-600/30">
            <button
              onClick={() => setShowResetConfirm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-red-400 border border-slate-600/50 rounded-lg transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <div className="flex items-center gap-3">
              {hasChanges && (
                <span className="text-xs text-slate-400">Unsaved changes</span>
              )}
              <button
                onClick={saveSettings}
                data-save-button
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 text-cyan-400 border border-cyan-500/30 rounded-lg transition-all"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Reset Confirmation Modal */}
      <AnimatePresence>
        {showResetConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center z-10"
          >
            <div className="backdrop-blur-md bg-slate-900/90 border border-red-500/30 rounded-lg p-6 max-w-md mx-4">
              <h3 className="text-lg font-semibold text-slate-100 mb-2">
                Reset Settings
              </h3>
              <p className="text-slate-300 mb-4">
                Are you sure you want to reset all settings to their default values? This action cannot be undone.
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowResetConfirm(false)}
                  className="flex-1 px-4 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 border border-slate-600/50 rounded-lg transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={resetSettings}
                  className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg transition-all"
                >
                  Reset
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scan line effect */}
      <div className="absolute inset-0 scan-line opacity-20" />
    </div>
  );
};

export default SettingsPanel;
