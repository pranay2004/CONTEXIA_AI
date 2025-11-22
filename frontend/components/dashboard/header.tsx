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
      {/* Actions */}
      <div className="flex items-center gap-4">
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