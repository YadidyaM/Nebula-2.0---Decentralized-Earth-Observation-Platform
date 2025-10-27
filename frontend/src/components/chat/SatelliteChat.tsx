import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Minimize2, 
  Maximize2, 
  Mic, 
  MicOff, 
  Send, 
  Radio,
  MessageSquare
} from 'lucide-react';
import { ChatMode, MessageType, ChatMessage } from '../../types';
import { useChat, useVoiceCommand, useChatAI } from '../../hooks';
import { wsManager } from '../../services/websocket';

interface SatelliteChatProps {
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
  className?: string;
}

const SatelliteChat: React.FC<SatelliteChatProps> = ({
  isMinimized = false,
  onToggleMinimize,
  className = ''
}) => {
  const [chatMode, setChatMode] = useState<ChatMode>('monitor');
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const { messages, sendMessage, clearMessages } = useChat();
  const { 
    isListening, 
    isProcessing: isVoiceProcessing, 
    lastCommand, 
    startListening, 
    stopListening 
  } = useVoiceCommand();
  const { 
    isProcessing: isAIProcessing, 
    processMessage, 
    extractMissionParameters 
  } = useChatAI();

  // Scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle voice command processing
  useEffect(() => {
    if (lastCommand && lastCommand.processed && lastCommand.response) {
      // Add AI response to chat
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        type: 'response',
        content: lastCommand.response,
        timestamp: new Date().toISOString(),
        sender: 'AI'
      };
      
      // This would normally be handled by the chat hook
      console.log('Voice command processed:', lastCommand);
    }
  }, [lastCommand]);

  // Handle send message
  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim()) return;

    const messageText = inputValue.trim();
    setInputValue('');
    setIsTyping(true);

    try {
      // Send user message
      const success = sendMessage(messageText, 'command');
      
      if (success && chatMode === 'interactive') {
        // Process with AI if in interactive mode
        const userMessage: ChatMessage = {
          id: `user_${Date.now()}`,
          type: 'command',
          content: messageText,
          timestamp: new Date().toISOString(),
          sender: 'user'
        };

        const aiResponse = await processMessage(userMessage);
        
        // Send AI response
        sendMessage(aiResponse, 'response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'error',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date().toISOString(),
        sender: 'system'
      };
      // This would be handled by the chat hook
    } finally {
      setIsTyping(false);
    }
  }, [inputValue, sendMessage, chatMode, processMessage]);

  // Handle voice command
  const toggleVoiceListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Handle key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  // Handle mode change
  const handleModeChange = useCallback((mode: ChatMode) => {
    setChatMode(mode);
    if (mode === 'monitor') {
      // Clear any ongoing voice commands
      if (isListening) {
        stopListening();
      }
    }
  }, [isListening, stopListening]);

  // Format message timestamp
  const formatTimestamp = useCallback((timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }, []);

  // Get message type color
  const getMessageTypeColor = useCallback((type: MessageType) => {
    switch (type) {
      case 'autonomous':
        return 'text-blue-400';
      case 'command':
        return 'text-cyan-400';
      case 'response':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'system':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  }, []);

  // Get message type icon
  const getMessageTypeIcon = useCallback((type: MessageType) => {
    switch (type) {
      case 'autonomous':
        return <Radio className="w-3 h-3" />;
      case 'command':
        return <MessageSquare className="w-3 h-3" />;
      case 'response':
        return <Radio className="w-3 h-3" />;
      case 'error':
        return <Radio className="w-3 h-3" />;
      case 'system':
        return <Radio className="w-3 h-3" />;
      default:
        return <Radio className="w-3 h-3" />;
    }
  }, []);

  if (isMinimized) {
    return (
      <motion.div
        initial={{ x: -400, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: -400, opacity: 0 }}
        className={`fixed left-4 top-1/2 transform -translate-y-1/2 z-50 ${className}`}
      >
        <div className="holo-panel rounded-lg p-4 w-80">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-mono text-cyan-400">SATELLITE COMMS</span>
            </div>
            <button
              onClick={onToggleMinimize}
              className="text-cyan-300 hover:text-white transition-colors p-1 rounded hover:bg-slate-700/50"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
          
          <div className="text-xs text-gray-400 mb-2">
            Mode: <span className="text-cyan-400">{chatMode.toUpperCase()}</span>
          </div>
          
          <div className="text-xs text-gray-400">
            Messages: <span className="text-green-400">{messages.length}</span>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ x: -400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -400, opacity: 0 }}
      className={`fixed left-4 top-1/2 transform -translate-y-1/2 z-50 ${className}`}
    >
      <div className="holo-panel rounded-lg w-96 h-96 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cyan-500/30">
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-cyan-400" />
            <span className="text-sm font-mono text-cyan-400">SATELLITE COMMS</span>
          </div>
          <button
            onClick={onToggleMinimize}
            className="text-cyan-300 hover:text-white transition-colors p-1 rounded hover:bg-slate-700/50"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
        </div>

        {/* Mode Toggle */}
        <div className="flex gap-2 p-4 border-b border-cyan-500/30">
          <button
            onClick={() => handleModeChange('monitor')}
            className={`flex-1 px-3 py-2 text-xs font-mono rounded transition-all duration-300 ${
              chatMode === 'monitor'
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30 border border-cyan-400/50'
                : 'text-cyan-300 hover:text-white hover:bg-slate-700/50 hover:border-slate-500/50 border border-transparent'
            }`}
          >
            MONITOR
          </button>
          <button
            onClick={() => handleModeChange('interactive')}
            className={`flex-1 px-3 py-2 text-xs font-mono rounded transition-all duration-300 ${
              chatMode === 'interactive'
                ? 'bg-green-600 text-white shadow-lg shadow-green-600/30 border border-green-400/50'
                : 'text-green-300 hover:text-white hover:bg-slate-700/50 hover:border-slate-500/50 border border-transparent'
            }`}
          >
            COMMS
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex gap-2"
              >
                <div className="flex-shrink-0">
                  <div className={`p-1 rounded ${getMessageTypeColor(message.type)}`}>
                    {getMessageTypeIcon(message.type)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-gray-400">
                      {formatTimestamp(message.timestamp)}
                    </span>
                    <span className={`text-xs font-mono ${getMessageTypeColor(message.type)}`}>
                      {message.type.toUpperCase()}
                    </span>
                    {message.sender && (
                      <span className="text-xs text-gray-500">
                        {message.sender}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-white break-words">
                    {message.content}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {/* Typing indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-2"
            >
              <div className="flex-shrink-0">
                <div className="p-1 rounded text-green-400">
                  <Radio className="w-3 h-3" />
                </div>
              </div>
              <div className="text-sm text-gray-400 italic">
                AI is processing...
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-cyan-500/30">
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="ENTER COMMAND..."
                className="w-full bg-slate-800/80 text-white px-3 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none text-sm font-mono placeholder-slate-400 focus:shadow-lg focus:shadow-cyan-500/20 transition-all duration-300"
                disabled={isAIProcessing || isVoiceProcessing}
              />
            </div>
            
            {/* Voice Command Button */}
            <button
              onClick={toggleVoiceListening}
              disabled={isAIProcessing || isVoiceProcessing}
              className={`p-2 rounded transition-all duration-300 border ${
                isListening
                  ? 'bg-red-600/80 border-red-400/50 animate-pulse shadow-lg shadow-red-600/30'
                  : 'bg-slate-700/80 border-slate-600/50 hover:bg-slate-600/80 hover:border-slate-500/50'
              }`}
            >
              {isListening ? (
                <MicOff className="w-4 h-4 text-white" />
              ) : (
                <Mic className="w-4 h-4 text-gray-300" />
              )}
            </button>
            
            {/* Send Button */}
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isAIProcessing || isVoiceProcessing}
              className="bg-cyan-600/80 hover:bg-cyan-500/80 text-white p-2 rounded transition-all duration-300 border border-cyan-400/50 hover:shadow-lg hover:shadow-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <div className="flex items-center gap-4">
              <span>Mode: <span className="text-cyan-400">{chatMode.toUpperCase()}</span></span>
              {isListening && <span className="text-red-400 animate-pulse">LISTENING</span>}
              {isAIProcessing && <span className="text-green-400">PROCESSING</span>}
            </div>
            <button
              onClick={clearMessages}
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SatelliteChat;
