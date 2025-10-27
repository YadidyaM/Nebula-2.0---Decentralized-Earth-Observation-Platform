import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface HolographicOverlayProps {
  className?: string;
  intensity?: 'low' | 'medium' | 'high';
  showScanLines?: boolean;
  showCornerDecorations?: boolean;
  showGrid?: boolean;
}

const HolographicOverlay: React.FC<HolographicOverlayProps> = ({
  className = '',
  intensity = 'medium',
  showScanLines = true,
  showCornerDecorations = true,
  showGrid = true
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Handle mouse movement for parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      setMousePosition({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Get intensity values
  const getIntensityValues = () => {
    switch (intensity) {
      case 'low':
        return {
          opacity: 0.1,
          blur: 2,
          glow: 5
        };
      case 'medium':
        return {
          opacity: 0.2,
          blur: 4,
          glow: 10
        };
      case 'high':
        return {
          opacity: 0.3,
          blur: 6,
          glow: 15
        };
      default:
        return {
          opacity: 0.2,
          blur: 4,
          glow: 10
        };
    }
  };

  const intensityValues = getIntensityValues();

  return (
    <div className={`fixed inset-0 pointer-events-none z-10 ${className}`}>
      {/* Background Grid */}
      {showGrid && (
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 200, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 200, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`
          }}
        />
      )}

      {/* Scan Lines */}
      {showScanLines && (
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute inset-0"
            style={{
              background: `linear-gradient(
                90deg,
                transparent 0%,
                rgba(0, 200, 255, 0.1) 50%,
                transparent 100%
              )`,
              height: '2px',
              width: '100%',
              transform: `translateY(${mousePosition.y * 0.5}px)`
            }}
            animate={{
              y: ['-100%', '100%']
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'linear'
            }}
          />
          
          <motion.div
            className="absolute inset-0"
            style={{
              background: `linear-gradient(
                90deg,
                transparent 0%,
                rgba(0, 200, 255, 0.05) 50%,
                transparent 100%
              )`,
              height: '1px',
              width: '100%',
              transform: `translateY(${mousePosition.y * 0.3}px)`
            }}
            animate={{
              y: ['-100%', '100%']
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'linear',
              delay: 1
            }}
          />
        </div>
      )}

      {/* Corner Decorations */}
      {showCornerDecorations && (
        <>
          {/* Top Left */}
          <div className="absolute top-4 left-4 w-16 h-16">
            <div className="relative w-full h-full">
              <div 
                className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-400"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow}px rgba(0, 200, 255, ${intensityValues.opacity})`
                }}
              />
              <div 
                className="absolute top-2 left-2 w-4 h-4 border-t border-l border-cyan-300"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow * 0.5}px rgba(0, 200, 255, ${intensityValues.opacity * 0.5})`
                }}
              />
            </div>
          </div>

          {/* Top Right */}
          <div className="absolute top-4 right-4 w-16 h-16">
            <div className="relative w-full h-full">
              <div 
                className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-400"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow}px rgba(0, 200, 255, ${intensityValues.opacity})`
                }}
              />
              <div 
                className="absolute top-2 right-2 w-4 h-4 border-t border-r border-cyan-300"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow * 0.5}px rgba(0, 200, 255, ${intensityValues.opacity * 0.5})`
                }}
              />
            </div>
          </div>

          {/* Bottom Left */}
          <div className="absolute bottom-4 left-4 w-16 h-16">
            <div className="relative w-full h-full">
              <div 
                className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-400"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow}px rgba(0, 200, 255, ${intensityValues.opacity})`
                }}
              />
              <div 
                className="absolute bottom-2 left-2 w-4 h-4 border-b border-l border-cyan-300"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow * 0.5}px rgba(0, 200, 255, ${intensityValues.opacity * 0.5})`
                }}
              />
            </div>
          </div>

          {/* Bottom Right */}
          <div className="absolute bottom-4 right-4 w-16 h-16">
            <div className="relative w-full h-full">
              <div 
                className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-400"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow}px rgba(0, 200, 255, ${intensityValues.opacity})`
                }}
              />
              <div 
                className="absolute bottom-2 right-2 w-4 h-4 border-b border-r border-cyan-300"
                style={{
                  boxShadow: `0 0 ${intensityValues.glow * 0.5}px rgba(0, 200, 255, ${intensityValues.opacity * 0.5})`
                }}
              />
            </div>
          </div>
        </>
      )}

      {/* Pulsing Glow Effects */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-1/4 left-1/4 w-32 h-32 rounded-full"
          style={{
            background: `radial-gradient(circle, rgba(0, 200, 255, ${intensityValues.opacity * 0.3}) 0%, transparent 70%)`,
            filter: `blur(${intensityValues.blur}px)`
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
        
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-24 h-24 rounded-full"
          style={{
            background: `radial-gradient(circle, rgba(0, 200, 255, ${intensityValues.opacity * 0.2}) 0%, transparent 70%)`,
            filter: `blur(${intensityValues.blur}px)`
          }}
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1
          }}
        />
      </div>

      {/* Edge Glow */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            linear-gradient(90deg, rgba(0, 200, 255, ${intensityValues.opacity * 0.1}) 0%, transparent 2%, transparent 98%, rgba(0, 200, 255, ${intensityValues.opacity * 0.1}) 100%),
            linear-gradient(0deg, rgba(0, 200, 255, ${intensityValues.opacity * 0.1}) 0%, transparent 2%, transparent 98%, rgba(0, 200, 255, ${intensityValues.opacity * 0.1}) 100%)
          `
        }}
      />

      {/* Flicker Effect */}
      <motion.div
        className="absolute inset-0 bg-cyan-400"
        style={{
          opacity: 0,
          mixBlendMode: 'screen'
        }}
        animate={{
          opacity: [0, 0.02, 0, 0.01, 0]
        }}
        transition={{
          duration: 0.1,
          repeat: Infinity,
          repeatDelay: Math.random() * 3 + 1
        }}
      />
    </div>
  );
};

export default HolographicOverlay;
