import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Play, 
  Target, 
  Users, 
  MapPin, 
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { MissionType, Priority, CreateMissionRequest } from '../../types';
import { useMissions } from '../../hooks';

interface MissionLaunchSequenceProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const MissionLaunchSequence: React.FC<MissionLaunchSequenceProps> = ({
  isOpen,
  onClose,
  className = ''
}) => {
  const [step, setStep] = useState(0);
  const [countdown, setCountdown] = useState(5);
  const [isLaunching, setIsLaunching] = useState(false);
  const [missionData, setMissionData] = useState<CreateMissionRequest>({
    name: '',
    type: 'forestry',
    priority: 'medium',
    target_area: {
      latitude: 0,
      longitude: 0,
      radius_km: 10,
      description: ''
    }
  });

  const { createMission, isLoading } = useMissions();

  // Countdown effect
  useEffect(() => {
    if (step === 3 && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (step === 3 && countdown === 0) {
      handleLaunch();
    }
  }, [step, countdown]);

  // Handle launch
  const handleLaunch = async () => {
    setIsLaunching(true);
    try {
      await createMission(missionData);
      setStep(4); // Success step
    } catch (error) {
      console.error('Mission launch failed:', error);
      setStep(5); // Error step
    } finally {
      setIsLaunching(false);
    }
  };

  // Handle input change
  const handleInputChange = (field: string, value: any) => {
    setMissionData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle target area change
  const handleTargetAreaChange = (field: string, value: any) => {
    setMissionData(prev => ({
      ...prev,
      target_area: {
        ...prev.target_area,
        [field]: value
      }
    }));
  };

  // Reset form
  const resetForm = () => {
    setStep(0);
    setCountdown(5);
    setIsLaunching(false);
    setMissionData({
      name: '',
      type: 'forestry',
      priority: 'medium',
      target_area: {
        latitude: 0,
        longitude: 0,
        radius_km: 10,
        description: ''
      }
    });
  };

  // Handle close
  const handleClose = () => {
    resetForm();
    onClose();
  };

  // Mission type options
  const missionTypes: { value: MissionType; label: string }[] = [
    { value: 'forestry', label: 'Forestry Monitoring' },
    { value: 'cryosphere', label: 'Cryosphere Analysis' },
    { value: 'disaster_management', label: 'Disaster Management' },
    { value: 'security', label: 'Security Surveillance' },
    { value: 'weather', label: 'Weather Monitoring' },
    { value: 'hydrology', label: 'Hydrology Analysis' },
    { value: 'urban_infrastructure', label: 'Urban Infrastructure' },
    { value: 'land_monitoring', label: 'Land Monitoring' }
  ];

  // Priority options
  const priorities: { value: Priority; label: string; color: string }[] = [
    { value: 'low', label: 'Low', color: 'text-gray-400' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400' },
    { value: 'high', label: 'High', color: 'text-orange-400' },
    { value: 'critical', label: 'Critical', color: 'text-red-400' }
  ];

  const steps = [
    { title: 'Mission Parameters', description: 'Configure mission details' },
    { title: 'Target Area', description: 'Set target coordinates and radius' },
    { title: 'Agent Assignment', description: 'Select agents for mission' },
    { title: 'Launch Sequence', description: 'Final confirmation and launch' },
    { title: 'Mission Launched', description: 'Mission successfully deployed' },
    { title: 'Launch Failed', description: 'Mission launch encountered an error' }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center ${className}`}
          onClick={handleClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="holo-panel rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto custom-scrollbar"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Play className="w-6 h-6 text-green-400" />
                <h2 className="text-2xl font-mono text-cyan-400">
                  MISSION LAUNCH SEQUENCE
                </h2>
              </div>
              <button
                onClick={handleClose}
                className="p-2 rounded text-gray-400 hover:text-white hover:bg-slate-700/50 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Progress Steps */}
            <div className="flex items-center justify-between mb-6">
              {steps.map((stepInfo, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-mono ${
                    index <= step
                      ? 'bg-cyan-600 text-white'
                      : 'bg-gray-700 text-gray-400'
                  }`}>
                    {index < step ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  <div className="text-xs text-gray-400 mt-1 text-center">
                    {stepInfo.title}
                  </div>
                </div>
              ))}
            </div>

            {/* Step Content */}
            <div className="min-h-[400px]">
              {/* Step 0: Mission Parameters */}
              {step === 0 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-mono text-white mb-4">Mission Parameters</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Mission Name</label>
                      <input
                        type="text"
                        value={missionData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="Enter mission name..."
                        className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Mission Type</label>
                      <select
                        value={missionData.type}
                        onChange={(e) => handleInputChange('type', e.target.value)}
                        className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                      >
                        {missionTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Priority</label>
                      <select
                        value={missionData.priority}
                        onChange={(e) => handleInputChange('priority', e.target.value)}
                        className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                      >
                        {priorities.map(priority => (
                          <option key={priority.value} value={priority.value}>
                            {priority.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 1: Target Area */}
              {step === 1 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-mono text-white mb-4">Target Area</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Latitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={missionData.target_area.latitude}
                        onChange={(e) => handleTargetAreaChange('latitude', parseFloat(e.target.value))}
                        className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Longitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={missionData.target_area.longitude}
                        onChange={(e) => handleTargetAreaChange('longitude', parseFloat(e.target.value))}
                        className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Radius (km)</label>
                    <input
                      type="number"
                      min="1"
                      max="1000"
                      value={missionData.target_area.radius_km}
                      onChange={(e) => handleTargetAreaChange('radius_km', parseInt(e.target.value))}
                      className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Description</label>
                    <textarea
                      value={missionData.target_area.description}
                      onChange={(e) => handleTargetAreaChange('description', e.target.value)}
                      placeholder="Describe the target area..."
                      rows={3}
                      className="w-full bg-slate-800/80 text-white px-4 py-2 rounded border border-cyan-500/30 focus:border-cyan-400 focus:outline-none font-mono resize-none"
                    />
                  </div>
                </motion.div>
              )}

              {/* Step 2: Agent Assignment */}
              {step === 2 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-4"
                >
                  <h3 className="text-lg font-mono text-white mb-4">Agent Assignment</h3>
                  
                  <div className="text-gray-400 text-sm">
                    Agents will be automatically assigned based on mission type and availability.
                  </div>
                  
                  <div className="holo-panel p-4 rounded">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-4 h-4 text-purple-400" />
                      <span className="text-white font-mono">Available Agents</span>
                    </div>
                    <div className="text-sm text-gray-400">
                      • Forest Guardian (Forestry missions)
                      <br />
                      • Ice Sentinel (Cryosphere missions)
                      <br />
                      • Storm Tracker (Weather missions)
                      <br />
                      • Water Watcher (Hydrology missions)
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 3: Launch Sequence */}
              {step === 3 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-center space-y-6"
                >
                  <h3 className="text-lg font-mono text-white mb-4">Launch Sequence</h3>
                  
                  <div className="holo-panel p-6 rounded">
                    <div className="text-6xl font-mono text-cyan-400 mb-4">
                      {countdown}
                    </div>
                    <div className="text-gray-400 text-sm">
                      Mission launching in {countdown} seconds...
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-400">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Target className="w-4 h-4" />
                      <span>{missionData.name}</span>
                    </div>
                    <div className="flex items-center justify-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>
                        {missionData.target_area.latitude.toFixed(4)}, {missionData.target_area.longitude.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 4: Success */}
              {step === 4 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center space-y-6"
                >
                  <div className="text-6xl text-green-400 mb-4">
                    <CheckCircle className="w-16 h-16 mx-auto" />
                  </div>
                  <h3 className="text-lg font-mono text-white">Mission Launched Successfully!</h3>
                  <div className="text-gray-400 text-sm">
                    Mission "{missionData.name}" has been deployed and is now active.
                  </div>
                </motion.div>
              )}

              {/* Step 5: Error */}
              {step === 5 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center space-y-6"
                >
                  <div className="text-6xl text-red-400 mb-4">
                    <AlertCircle className="w-16 h-16 mx-auto" />
                  </div>
                  <h3 className="text-lg font-mono text-white">Launch Failed</h3>
                  <div className="text-gray-400 text-sm">
                    Mission launch encountered an error. Please try again.
                  </div>
                </motion.div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between mt-6 pt-6 border-t border-cyan-500/30">
              <button
                onClick={handleClose}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              
              <div className="flex gap-3">
                {step > 0 && step < 3 && (
                  <button
                    onClick={() => setStep(step - 1)}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                  >
                    Previous
                  </button>
                )}
                
                {step < 3 && (
                  <button
                    onClick={() => setStep(step + 1)}
                    disabled={!missionData.name.trim()}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                )}
                
                {step === 3 && (
                  <button
                    onClick={() => setStep(3)}
                    disabled={isLaunching}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    {isLaunching ? 'Launching...' : 'Launch Mission'}
                  </button>
                )}
                
                {(step === 4 || step === 5) && (
                  <button
                    onClick={handleClose}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    Close
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default MissionLaunchSequence;
