'use client'

import { Sparkles, Bell, Search, Command } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'

export function Header() {
  const router = useRouter()
  const { data: session } = useSession()

  return (
    <header className="h-20 px-8 flex items-center justify-between sticky top-0 z-30">
      {/* Context Breadcrumb / Search */}
      <div className="flex items-center gap-4 flex-1">
        <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-gray-900/50 border border-white/10 rounded-full text-sm text-gray-400 w-96 hover:border-indigo-500/30 transition-colors group cursor-text">
          <Search className="w-4 h-4 group-hover:text-indigo-400 transition-colors" />
          <span className="opacity-50">Search context, trends, or assets...</span>
          <div className="ml-auto flex gap-1">
            <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-[10px] font-mono">⌘</kbd>
            <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-[10px] font-mono">K</kbd>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon"
          className="text-gray-400 hover:text-white hover:bg-white/5 rounded-full"
        >
          <Bell className="w-5 h-5" />
        </Button>

        <div className="h-8 w-[1px] bg-white/10 mx-2" />

        <Button
          onClick={() => router.push('/dashboard/content')}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/25 rounded-full px-6"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Create New
        </Button>

        <div className="flex items-center gap-3 pl-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-gray-700 to-gray-600 border border-white/10 flex items-center justify-center text-xs font-bold">
            {session?.user?.name?.[0] || 'U'}
          </div>
        </div>
      </div>
    </header>
  )
}