import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'

// Theme types
export type ThemePreference = 'cyan' | 'purple' | 'green' | 'amber'

export interface ThemeColors {
  primary: string
  secondary: string
  accent: string
  background: string
  surface: string
  text: string
  textSecondary: string
  border: string
  success: string
  warning: string
  error: string
  info: string
}

export interface ThemeEffects {
  glow: string
  shadow: string
  blur: string
  scanLine: string
}

export interface Theme {
  name: string
  colors: ThemeColors
  effects: ThemeEffects
  fonts: {
    heading: string
    body: string
    mono: string
  }
}

// Context type
interface ThemeContextType {
  theme: Theme
  currentTheme: ThemePreference
  setTheme: (theme: ThemePreference) => void
  customizeTheme: (customizations: Partial<Theme>) => void
  presets: Record<ThemePreference, Theme>
  resetTheme: () => void
}

// Theme presets
const themePresets: Record<ThemePreference, Theme> = {
  cyan: {
    name: 'Cyan',
    colors: {
      primary: '#06b6d4',
      secondary: '#0891b2',
      accent: '#67e8f9',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#f8fafc',
      textSecondary: '#cbd5e1',
      border: '#334155',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#06b6d4'
    },
    effects: {
      glow: '0 0 20px rgba(6, 182, 212, 0.3)',
      shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      blur: 'blur(8px)',
      scanLine: 'linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.1), transparent)'
    },
    fonts: {
      heading: 'Orbitron, monospace',
      body: 'Inter, sans-serif',
      mono: 'JetBrains Mono, monospace'
    }
  },
  purple: {
    name: 'Purple',
    colors: {
      primary: '#8b5cf6',
      secondary: '#7c3aed',
      accent: '#c4b5fd',
      background: '#0f0b1a',
      surface: '#1e1b2e',
      text: '#f8fafc',
      textSecondary: '#cbd5e1',
      border: '#334155',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#8b5cf6'
    },
    effects: {
      glow: '0 0 20px rgba(139, 92, 246, 0.3)',
      shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      blur: 'blur(8px)',
      scanLine: 'linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.1), transparent)'
    },
    fonts: {
      heading: 'Orbitron, monospace',
      body: 'Inter, sans-serif',
      mono: 'JetBrains Mono, monospace'
    }
  },
  green: {
    name: 'Green',
    colors: {
      primary: '#10b981',
      secondary: '#059669',
      accent: '#6ee7b7',
      background: '#0f1a0f',
      surface: '#1e2e1e',
      text: '#f8fafc',
      textSecondary: '#cbd5e1',
      border: '#334155',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#10b981'
    },
    effects: {
      glow: '0 0 20px rgba(16, 185, 129, 0.3)',
      shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      blur: 'blur(8px)',
      scanLine: 'linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.1), transparent)'
    },
    fonts: {
      heading: 'Orbitron, monospace',
      body: 'Inter, sans-serif',
      mono: 'JetBrains Mono, monospace'
    }
  },
  amber: {
    name: 'Amber',
    colors: {
      primary: '#f59e0b',
      secondary: '#d97706',
      accent: '#fcd34d',
      background: '#1a0f0f',
      surface: '#2e1e1e',
      text: '#f8fafc',
      textSecondary: '#cbd5e1',
      border: '#334155',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#f59e0b'
    },
    effects: {
      glow: '0 0 20px rgba(245, 158, 11, 0.3)',
      shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      blur: 'blur(8px)',
      scanLine: 'linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.1), transparent)'
    },
    fonts: {
      heading: 'Orbitron, monospace',
      body: 'Inter, sans-serif',
      mono: 'JetBrains Mono, monospace'
    }
  }
}

// Create context
const ThemeContext = createContext<ThemeContextType | null>(null)

// Theme provider component
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<ThemePreference>(() => {
    const stored = localStorage.getItem('nebula-theme') as ThemePreference
    return stored && themePresets[stored] ? stored : 'cyan'
  })

  const [customTheme, setCustomTheme] = useState<Partial<Theme> | null>(null)

  // Get current theme (preset + customizations)
  const theme = React.useMemo(() => {
    const baseTheme = themePresets[currentTheme]
    if (customTheme) {
      return {
        ...baseTheme,
        ...customTheme,
        colors: { ...baseTheme.colors, ...customTheme.colors },
        effects: { ...baseTheme.effects, ...customTheme.effects },
        fonts: { ...baseTheme.fonts, ...customTheme.fonts }
      }
    }
    return baseTheme
  }, [currentTheme, customTheme])

  // Apply theme to CSS variables
  useEffect(() => {
    const root = document.documentElement
    
    // Apply color variables
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })

    // Apply effect variables
    Object.entries(theme.effects).forEach(([key, value]) => {
      root.style.setProperty(`--effect-${key}`, value)
    })

    // Apply font variables
    Object.entries(theme.fonts).forEach(([key, value]) => {
      root.style.setProperty(`--font-${key}`, value)
    })

    // Apply theme class to body
    document.body.className = `theme-${currentTheme}`
    
  }, [theme, currentTheme])

  // Set theme
  const setTheme = useCallback((newTheme: ThemePreference) => {
    setCurrentTheme(newTheme)
    setCustomTheme(null) // Clear customizations when switching presets
    localStorage.setItem('nebula-theme', newTheme)
  }, [])

  // Customize theme
  const customizeTheme = useCallback((customizations: Partial<Theme>) => {
    setCustomTheme(customizations)
    localStorage.setItem('nebula-theme-custom', JSON.stringify(customizations))
  }, [])

  // Reset theme
  const resetTheme = useCallback(() => {
    setCustomTheme(null)
    localStorage.removeItem('nebula-theme-custom')
  }, [])

  // Load custom theme on mount
  useEffect(() => {
    const storedCustom = localStorage.getItem('nebula-theme-custom')
    if (storedCustom) {
      try {
        const custom = JSON.parse(storedCustom)
        setCustomTheme(custom)
      } catch (error) {
        console.error('Error loading custom theme:', error)
        localStorage.removeItem('nebula-theme-custom')
      }
    }
  }, [])

  const contextValue: ThemeContextType = {
    theme,
    currentTheme,
    setTheme,
    customizeTheme,
    presets: themePresets,
    resetTheme
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

// Hook to use theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// Hook for theme-aware styling
export const useThemeStyles = () => {
  const { theme } = useTheme()

  return {
    // Color utilities
    colors: theme.colors,
    
    // Common style objects
    card: {
      backgroundColor: theme.colors.surface,
      border: `1px solid ${theme.colors.border}`,
      borderRadius: '8px',
      padding: '16px',
      boxShadow: theme.effects.shadow
    },
    
    button: {
      backgroundColor: theme.colors.primary,
      color: theme.colors.text,
      border: 'none',
      borderRadius: '6px',
      padding: '8px 16px',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    },
    
    input: {
      backgroundColor: theme.colors.surface,
      color: theme.colors.text,
      border: `1px solid ${theme.colors.border}`,
      borderRadius: '6px',
      padding: '8px 12px',
      outline: 'none'
    },
    
    glow: {
      boxShadow: theme.effects.glow
    },
    
    blur: {
      backdropFilter: theme.effects.blur
    },
    
    scanLine: {
      background: theme.effects.scanLine,
      backgroundSize: '200% 100%',
      animation: 'scan 2s linear infinite'
    }
  }
}

// Theme toggle component
export const ThemeToggle: React.FC = () => {
  const { currentTheme, setTheme, presets } = useTheme()

  return (
    <div className="flex gap-2 p-2 bg-slate-800 rounded-lg">
      {Object.entries(presets).map(([key, preset]) => (
        <button
          key={key}
          onClick={() => setTheme(key as ThemePreference)}
          className={`w-8 h-8 rounded-full border-2 transition-all ${
            currentTheme === key
              ? 'border-white scale-110'
              : 'border-gray-600 hover:border-gray-400'
          }`}
          style={{ backgroundColor: preset.colors.primary }}
          title={preset.name}
        />
      ))}
    </div>
  )
}

// Theme-aware component wrapper
export const ThemedComponent: React.FC<{
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
}> = ({ children, className = '', style = {} }) => {
  const { theme } = useTheme()

  return (
    <div
      className={`themed-component ${className}`}
      style={{
        color: theme.colors.text,
        backgroundColor: theme.colors.background,
        ...style
      }}
    >
      {children}
    </div>
  )
}

// Utility functions
export const getThemeColor = (color: keyof ThemeColors, theme: Theme = themePresets.cyan): string => {
  return theme.colors[color]
}

export const getThemeEffect = (effect: keyof ThemeEffects, theme: Theme = themePresets.cyan): string => {
  return theme.effects[effect]
}

export const createThemeVariant = (baseTheme: Theme, overrides: Partial<Theme>): Theme => {
  return {
    ...baseTheme,
    ...overrides,
    colors: { ...baseTheme.colors, ...overrides.colors },
    effects: { ...baseTheme.effects, ...overrides.effects },
    fonts: { ...baseTheme.fonts, ...overrides.fonts }
  }
}

// Export theme presets for external use
export { themePresets }
