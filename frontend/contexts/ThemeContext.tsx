'use client'

import { createContext, useContext, useEffect } from 'react'

type Theme = 'dark'

interface ThemeContextType {
  theme: Theme
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Always use dark theme
  const theme: Theme = 'dark'

  // Apply dark theme to document on mount
  useEffect(() => {
    const root = document.documentElement
    root.classList.add('dark')
  }, [])

  return (
    <ThemeContext.Provider value={{ theme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
