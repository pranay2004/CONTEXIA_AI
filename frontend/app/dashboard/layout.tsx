'use client'

import { ReactNode } from 'react'
import { Sidebar } from '@/components/dashboard/sidebar'
// Header removed

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="h-screen bg-background text-foreground selection:bg-indigo-500/30 overflow-hidden flex">
      {/* Background Noise */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03] mix-blend-overlay" 
           style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }} />
      
      {/* Ambient Glows */}
      <div className="fixed top-0 left-0 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2 pointer-events-none z-0" />
      <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2 pointer-events-none z-0" />

      {/* Sidebar Area */}
      <div className="hidden lg:block w-[280px] shrink-0 relative z-20">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      {/* FIXED: Changed to overflow-y-auto to enable scrolling for all pages */}
      <main className="flex-1 h-full overflow-y-auto relative z-10 p-4 lg:p-8 pt-4 lg:pt-8 scroll-smooth">
        <div className="max-w-7xl mx-auto w-full pb-20">
          {children}
        </div>
      </main>
    </div>
  )
}