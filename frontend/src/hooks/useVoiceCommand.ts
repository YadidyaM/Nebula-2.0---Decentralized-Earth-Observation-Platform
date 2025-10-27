import { useState, useEffect, useCallback, useRef } from "react";
import { geminiClient } from "../services/gemini";
import { VoiceCommand, ChatMessage } from "../types";

interface UseVoiceCommandReturn {
  isListening: boolean;
  isProcessing: boolean;
  lastCommand: VoiceCommand | null;
  error: string | null;
  startListening: () => void;
  stopListening: () => void;
  processCommand: (text: string) => Promise<string>;
  clearError: () => void;
}

export const useVoiceCommand = (): UseVoiceCommandReturn => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastCommand, setLastCommand] = useState<VoiceCommand | null>(null);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = "en-US";
        recognitionRef.current.maxAlternatives = 1;

        recognitionRef.current.onstart = () => {
          setIsListening(true);
          setError(null);
        };

        recognitionRef.current.onresult = (event) => {
          const result = event.results[event.results.length - 1];

          if (result.isFinal) {
            const transcript = result[0].transcript.trim();
            const confidence = result[0].confidence;

            if (transcript) {
              const command: VoiceCommand = {
                id: `cmd_${Date.now()}`,
                text: transcript,
                confidence,
                timestamp: new Date().toISOString(),
                processed: false,
              };

              setLastCommand(command);
              processCommand(transcript);
            }
          }
        };

        recognitionRef.current.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          setError(`Speech recognition error: ${event.error}`);
          setIsListening(false);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      } else {
        setError("Speech recognition not supported in this browser");
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Start listening
  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setError("Speech recognition not available");
      return;
    }

    if (isListening) {
      return;
    }

    try {
      recognitionRef.current.start();

      // Set timeout to stop listening after 30 seconds
      timeoutRef.current = setTimeout(() => {
        stopListening();
      }, 30000);
    } catch (err: any) {
      setError(`Failed to start listening: ${err.message}`);
    }
  }, [isListening]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, [isListening]);

  // Process command with Gemini AI
  const processCommand = useCallback(async (text: string): Promise<string> => {
    if (!text.trim()) {
      return "No command received";
    }

    setIsProcessing(true);
    setError(null);

    try {
      const command: VoiceCommand = {
        id: `cmd_${Date.now()}`,
        text,
        confidence: 1.0,
        timestamp: new Date().toISOString(),
        processed: false,
      };

      const response = await geminiClient.processVoiceCommand(command);

      // Mark command as processed
      command.processed = true;
      command.response = response;
      setLastCommand(command);

      return response;
    } catch (err: any) {
      const errorMsg = err.message || "Failed to process voice command";
      setError(errorMsg);
      console.error("Voice command processing error:", err);
      return errorMsg;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Auto-stop listening when processing starts
  useEffect(() => {
    if (isProcessing && isListening) {
      stopListening();
    }
  }, [isProcessing, isListening, stopListening]);

  return {
    isListening,
    isProcessing,
    lastCommand,
    error,
    startListening,
    stopListening,
    processCommand,
    clearError,
  };
};

// Chat-specific hook with Gemini AI
export const useChatAI = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processMessage = useCallback(
    async (message: ChatMessage): Promise<string> => {
      setIsProcessing(true);
      setError(null);

      try {
        const response = await geminiClient.processChatMessage(message);
        return response;
      } catch (err: any) {
        const errorMsg = err.message || "Failed to process chat message";
        setError(errorMsg);
        console.error("Chat message processing error:", err);
        return errorMsg;
      } finally {
        setIsProcessing(false);
      }
    },
    []
  );

  const extractMissionParameters = useCallback(
    async (naturalLanguage: string): Promise<any> => {
      setIsProcessing(true);
      setError(null);

      try {
        const parameters = await geminiClient.extractMissionParameters(
          naturalLanguage
        );
        return parameters;
      } catch (err: any) {
        const errorMsg = err.message || "Failed to extract mission parameters";
        setError(errorMsg);
        console.error("Mission parameter extraction error:", err);
        return null;
      } finally {
        setIsProcessing(false);
      }
    },
    []
  );

  const analyzeRiskData = useCallback(
    async (riskData: any): Promise<string> => {
      setIsProcessing(true);
      setError(null);

      try {
        const analysis = await geminiClient.analyzeRiskData(riskData);
        return analysis;
      } catch (err: any) {
        const errorMsg = err.message || "Failed to analyze risk data";
        setError(errorMsg);
        console.error("Risk data analysis error:", err);
        return errorMsg;
      } finally {
        setIsProcessing(false);
      }
    },
    []
  );

  const analyzeTelemetryData = useCallback(
    async (telemetryData: any): Promise<string> => {
      setIsProcessing(true);
      setError(null);

      try {
        const analysis = await geminiClient.analyzeTelemetryData(telemetryData);
        return analysis;
      } catch (err: any) {
        const errorMsg = err.message || "Failed to analyze telemetry data";
        setError(errorMsg);
        console.error("Telemetry data analysis error:", err);
        return errorMsg;
      } finally {
        setIsProcessing(false);
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isProcessing,
    error,
    processMessage,
    extractMissionParameters,
    analyzeRiskData,
    analyzeTelemetryData,
    clearError,
  };
};
