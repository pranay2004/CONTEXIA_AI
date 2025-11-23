'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  LayoutDashboard, 
  Sparkles, 
  BarChart3, 
  LogOut,
  CalendarClock,
  Settings
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { signOut, useSession } from 'next-auth/react'
import { Logo } from '@/components/logo'

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Content Lab', href: '/dashboard/content', icon: Sparkles },
  { name: 'Social & Schedule', href: '/dashboard/social', icon: CalendarClock },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const { data: session } = useSession()

  return (
    // FIX: Removed mx-4 my-4 margins that were causing overflow. Parent container handles spacing.
    <motion.aside 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="flex flex-col h-full w-full glass-panel rounded-2xl overflow-hidden border border-white/10 bg-[#0F172A]/60 backdrop-blur-xl"
    >
      {/* Branding */}
      <div className="p-6 flex items-center gap-3 border-b border-white/5">
        <div className="relative">
          <div className="absolute inset-0 bg-indigo-500/20 blur-lg rounded-full" />
          <Logo className="w-10 h-10 relative z-10" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight text-white block leading-none">CONTEXIA</span>
          <span className="text-[10px] text-emerald-400 font-medium">System Online</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
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

      {/* User Profile */}
      <div className="p-3 mt-auto border-t border-white/5 bg-black/20">
        <div className="flex items-center gap-3 px-3 py-3 mb-2 rounded-xl bg-white/5 border border-white/5">
          <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold text-white">
            {session?.user?.name?.[0] || 'U'}
          </div>
          <div className="flex-1 min-w-0">
             <p className="text-sm font-medium text-white truncate">{session?.user?.name || 'User'}</p>
             <p className="text-xs text-gray-400 truncate">{session?.user?.email || 'user@example.com'}</p>
          </div>
        </div>

        <button 
          onClick={() => signOut({ callbackUrl: '/' })}
          className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-colors group"
        >
          <LogOut className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          <span className="font-medium text-xs">Sign Out</span>
        </button>
      </div>
    </motion.aside>
  )
}