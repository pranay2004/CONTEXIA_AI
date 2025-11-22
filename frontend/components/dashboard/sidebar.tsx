'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  Sparkles, 
  BarChart3, 
  LogOut,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { signOut } from 'next-auth/react'

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Content Lab', href: '/dashboard/content', icon: Sparkles },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <motion.aside 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="fixed left-4 top-24 bottom-4 w-64 flex flex-col glass-panel rounded-2xl z-40 overflow-hidden border border-white/10 bg-[#0F172A]/60 backdrop-blur-xl"
    >
      {/* Branding & Status */}
      <div className="p-6 flex items-center gap-3 border-b border-white/5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Zap className="w-4 h-4 text-white fill-white" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight text-white block leading-none">CONTEXIA</span>
          <span className="text-[10px] text-emerald-400 font-medium">System Online</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-6 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          
          return (
            <Link key={item.name} href={item.href} className="relative block group">
              {isActive && (
                <motion.div
                  layoutId="activeNav"
                  className="absolute inset-0 bg-indigo-500/10 border border-indigo-500/20 rounded-xl"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
              <div className={cn(
                "relative flex items-center gap-3 px-4 py-3 rounded-xl transition-colors duration-200",
                isActive ? "text-indigo-400" : "text-gray-400 group-hover:text-gray-200 group-hover:bg-white/5"
              )}>
                <item.icon className={cn("w-5 h-5", isActive && "text-indigo-400 drop-shadow-[0_0_8px_rgba(99,102,241,0.5)]")} />
                <span className="font-medium text-sm">{item.name}</span>
              </div>
            </Link>
          )
        })}
      </nav>

      {/* User Actions */}
      <div className="p-3 mt-auto border-t border-white/5">
        <button 
          onClick={() => signOut({ callbackUrl: '/' })}
          className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-colors mt-1 group"
        >
          <LogOut className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          <span className="font-medium text-sm">Sign Out</span>
        </button>
      </div>
    </motion.aside>
  )
}