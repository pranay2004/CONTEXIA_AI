'use client'

import { useEffect, useState } from 'react'
import { 
  Linkedin, 
  Twitter, 
  Trash2, 
  CheckCircle2, 
  Clock, 
  Plus,
  RefreshCw,
  User
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { socialApi, SocialAccount, ScheduledPost } from '@/lib/api/social'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { useRouter } from 'next/navigation'

export default function SocialManagePage() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [queue, setQueue] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [accData, queueData] = await Promise.all([
        socialApi.getAccounts().catch(() => []), // Return empty array on error
        socialApi.getScheduledPosts().catch(() => []) // Return empty array on error
      ])
      setAccounts(accData)
      setQueue(queueData)
    } catch (error) {
      console.error("Failed to load social data:", error)
      // Don't show error toast, just set empty data
      setAccounts([])
      setQueue([])
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = async (id: number, platform: string) => {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return
    try {
      await socialApi.disconnectAccount(id)
      toast.success(`Disconnected ${platform}`)
      loadData() // Refresh data
    } catch (error) {
      toast.error("Failed to disconnect")
    }
  }

  const handleCancelPost = async (id: number) => {
    if (!confirm("Cancel this scheduled post?")) return
    try {
      await socialApi.cancelScheduledPost(id)
      toast.success("Post cancelled")
      loadData() // Refresh data
    } catch (error) {
      toast.error("Failed to cancel post")
    }
  }

  const handleConnect = async (platform: string) => {
    try {
      localStorage.setItem('oauth_pending_platform', platform)
      const { authorization_url } = await socialApi.getAuthUrl(platform)
      if (authorization_url) {
        window.location.href = authorization_url
      } else {
        toast.error("Could not initiate connection")
      }
    } catch (error: any) {
      console.error("Connection error:", error)
      toast.error(error.response?.data?.error || "Connection failed")
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Social Command Center</h1>
          <p className="text-gray-400">Manage connections and review your content calendar</p>
        </div>
        <Button onClick={loadData} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Accounts */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <User className="w-5 h-5 text-indigo-400" /> Accounts
          </h2>
          
          <div className="space-y-4">
            {['linkedin', 'twitter'].map(platform => {
              const account = accounts.find(a => a.platform === platform && a.is_active)
              const PlatformIcon = platform === 'linkedin' ? Linkedin : Twitter
              
              return (
                <div key={platform} className="glass-panel p-4 rounded-xl border border-white/5 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${account ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-800 text-gray-500'}`}>
                      <PlatformIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium capitalize text-white">{platform}</h3>
                      <p className="text-xs text-gray-400">
                        {account ? (
                          <span className="flex items-center gap-1 text-emerald-400">
                            <CheckCircle2 className="w-3 h-3" /> Connected as {account.account_name}
                          </span>
                        ) : 'Not connected'}
                      </p>
                    </div>
                  </div>
                  
                  {account ? (
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="text-red-400 hover:bg-red-500/10"
                      onClick={() => handleDisconnect(account.id, platform)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  ) : (
                    <Button 
                      size="sm" 
                      variant="secondary"
                      onClick={() => handleConnect(platform)}
                    >
                      Connect
                    </Button>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column: Scheduled Queue */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-400" /> Scheduled Queue
            </h2>
            <Button 
              size="sm" 
              className="bg-indigo-600 hover:bg-indigo-500"
              onClick={() => router.push('/dashboard/content')}
            >
              <Plus className="w-4 h-4 mr-2" /> New Post
            </Button>
          </div>

          <div className="space-y-4">
            {!Array.isArray(queue) || queue.length === 0 ? (
              <div className="glass-panel p-12 rounded-xl border-dashed border border-white/10 text-center">
                <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-300">Queue is empty</h3>
                <p className="text-gray-500 text-sm mt-1">Schedule posts from the Content Lab to see them here.</p>
              </div>
            ) : (
              queue.map((post) => (
                <div key={post.id} className="glass-panel p-5 rounded-xl border border-white/5 group hover:border-indigo-500/30 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${
                        post.social_account_platform === 'linkedin' ? 'bg-blue-500/20 text-blue-300' : 'bg-sky-500/20 text-sky-300'
                      }`}>
                        {post.social_account_platform}
                      </span>
                      <span className="text-xs text-gray-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {format(new Date(post.scheduled_time), 'MMM d, yyyy @ h:mm a')}
                      </span>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-6 w-6 text-gray-500 hover:text-red-400 -mr-2"
                      onClick={() => handleCancelPost(post.id)}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                  <p className="text-sm text-gray-300 line-clamp-2 font-medium">
                    {post.content_text}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  )
}
