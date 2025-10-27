/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'holo-cyan': '#00c8ff',
        'holo-cyan-secondary': '#00aaff',
        'holo-cyan-tertiary': '#0088ff',
        'space-black': '#000814',
        'dark-slate': '#1e293b',
        'success-green': '#00ff88',
        'warning-yellow': '#ffaa00',
        'error-red': '#ff4444',
        'info-blue': '#3b82f6',
      },
      fontFamily: {
        'mono': ['Courier New', 'monospace'],
        'display': ['Orbitron', 'sans-serif'],
        'body': ['system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'holo-flicker': 'flicker 3s infinite',
        'scan': 'scan 2s linear infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        pulseGlow: {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(0, 200, 255, 0.3)',
            borderColor: 'rgba(0, 200, 255, 0.4)'
          },
          '50%': { 
            boxShadow: '0 0 40px rgba(0, 200, 255, 0.6)',
            borderColor: 'rgba(0, 200, 255, 0.6)'
          },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { 
            boxShadow: '0 0 5px rgba(0, 200, 255, 0.2)',
            textShadow: '0 0 5px rgba(0, 200, 255, 0.2)'
          },
          '100%': { 
            boxShadow: '0 0 20px rgba(0, 200, 255, 0.4)',
            textShadow: '0 0 10px rgba(0, 200, 255, 0.4)'
          },
        },
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'holo': '0 0 20px rgba(0, 200, 255, 0.3)',
        'holo-lg': '0 0 40px rgba(0, 200, 255, 0.5)',
        'holo-xl': '0 0 60px rgba(0, 200, 255, 0.7)',
      },
    },
  },
  plugins: [],
}
