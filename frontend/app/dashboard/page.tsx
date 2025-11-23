'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { 
  ArrowUpRight, 
  TrendingUp, 
  Users, 
  Activity, 
  Sparkles,
  Zap,
  Clock,
  Loader2,
  FileText,
  Linkedin,
  Twitter,
  Send,
  Filter,
  Search,
  Calendar,
  Eye,
  Download,
  Trash2,
  MoreVertical,
  CheckCircle2,
  XCircle,
  Youtube,
  FileCode,
  Mail,
  Image as ImageIcon,
  BarChart3,
  RefreshCw
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { getUserAnalytics, getRecentActivity, getGeneratedContent, UserStats } from '@/lib/api-client'
import { socialApi } from '@/lib/api/social'
import { toast } from 'sonner'
import { ContentDetailsModal } from '@/components/ContentDetailsModal'
import { format } from 'date-fns'

export const dynamic = 'force-dynamic'

type FilterType = 'all' | 'completed' | 'processing' | 'failed'
type ViewMode = 'grid' | 'list'

export default function DashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  const [filteredActivity, setFilteredActivity] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  
  // Preview Modal State
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [previewContent, setPreviewContent] = useState<any>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [postingTo, setPostingTo] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, activityData] = await Promise.all([
          getUserAnalytics(),
          getRecentActivity()
        ])
        
        if (statsData) setStats(statsData)
        if (activityData && Array.isArray(activityData)) {
          setRecentActivity(activityData)
          setFilteredActivity(activityData)
        }
        
      } catch (error) {
        console.error('Dashboard load failed', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // Filter and search logic
  useEffect(() => {
    let filtered = recentActivity

    // Apply status filter
    if (filterType !== 'all') {
      filtered = filtered.filter(item => item.status === filterType)
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(item => 
        item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.platform?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredActivity(filtered)
  }, [filterType, searchQuery, recentActivity])

  const refreshData = async () => {
    setLoading(true)
    try {
      const [statsData, activityData] = await Promise.all([
        getUserAnalytics(),
        getRecentActivity()
      ])
      if (statsData) setStats(statsData)
      if (activityData && Array.isArray(activityData)) {
        setRecentActivity(activityData)
        setFilteredActivity(activityData)
      }
      toast.success('Dashboard refreshed')
    } catch (error) {
      toast.error('Failed to refresh data')
    } finally {
      setLoading(false)
    }
  }

  // Handle Post to Social Media
  const handlePostToSocial = async (e: React.MouseEvent, platform: 'linkedin' | 'twitter', content: any, item: any) => {
    e.stopPropagation() // Prevent preview modal from opening
    
    try {
      setPostingTo(`${item.id}-${platform}`)
      
      // Check if account is connected
      const accounts = await socialApi.getAccounts()
      const connected = accounts.some((acc: any) => acc.platform === platform && acc.is_active)
      
      if (!connected) {
        // Initiate OAuth
        localStorage.setItem('oauth_pending_platform', platform)
        const { authorization_url } = await socialApi.getAuthUrl(platform)
        if (authorization_url) {
          window.location.href = authorization_url
        }
        return
      }
      
      // Post content
      const text = platform === 'linkedin' ? content.text : content.first_tweet
      if (!text) {
        toast.error('No content available to post')
        return
      }
      
      await socialApi.directPost(platform, text)
      toast.success(`Successfully posted to ${platform === 'linkedin' ? 'LinkedIn' : 'Twitter'}!`)
    } catch (error) {
      console.error('Post error:', error)
      toast.error(`Failed to post to ${platform === 'linkedin' ? 'LinkedIn' : 'Twitter'}`)
    } finally {
      setPostingTo(null)
    }
  }

  // Handle Click on Activity Item
  const handleActivityClick = async (item: any) => {
    console.log("Clicked item:", item) // Debug Log
    if (item.id && item.id.toString().startsWith('gen-')) {
      const contentId = item.id.split('-')[1]
      setLoadingPreview(true)
      try {
        const data = await getGeneratedContent(parseInt(contentId))
        if (data && data.content_json) {
          setPreviewContent(data.content_json)
          setIsPreviewOpen(true) // Opens the new Safe Modal
        } else {
          toast.error('Content details not found')
        }
      } catch (error) {
        console.error('Fetch error:', error)
        toast.error('Could not load content')
      } finally {
        setLoadingPreview(false)
      }
    }
  }

  // Get platform icon
  const getPlatformIcon = (platform: string) => {
    switch(platform) {
      case 'linkedin': return Linkedin
      case 'twitter': return Twitter
      case 'youtube': return Youtube
      case 'blog': return FileCode
      case 'email': return Mail
      case 'images': return ImageIcon
      default: return FileText
    }
  }

  // Get platform color
  const getPlatformColor = (platform: string) => {
    switch(platform) {
      case 'linkedin': return 'text-blue-400 bg-blue-500/10'
      case 'twitter': return 'text-sky-400 bg-sky-500/10'
      case 'youtube': return 'text-red-400 bg-red-500/10'
      case 'blog': return 'text-purple-400 bg-purple-500/10'
      case 'email': return 'text-green-400 bg-green-500/10'
      case 'images': return 'text-indigo-400 bg-indigo-500/10'
      default: return 'text-gray-400 bg-gray-500/10'
    }
  }

  const statCards = [
    { 
      label: 'Total Content', 
      value: recentActivity.length.toString(), 
      change: `+${recentActivity.filter(i => i.status === 'completed').length} completed`, 
      icon: FileText, 
      color: 'text-blue-400' 
    },
    { 
      label: 'Success Rate', 
      value: recentActivity.length > 0 
        ? `${Math.round((recentActivity.filter(i => i.status === 'completed').length / recentActivity.length) * 100)}%`
        : '0%', 
      change: 'Generation quality', 
      icon: CheckCircle2, 
      color: 'text-green-400' 
    },
    { 
      label: 'Time Saved', 
      value: `${Math.round(recentActivity.length * 1.5)}h`, 
      change: 'Automation efficiency', 
      icon: Zap, 
      color: 'text-purple-400' 
    },
    { 
      label: 'Active Platforms', 
      value: new Set(recentActivity.map(i => i.platform)).size.toString(), 
      change: 'Multi-channel', 
      icon: BarChart3, 
      color: 'text-indigo-400' 
    },
  ]

  return (
    <div className="space-y-8 max-w-6xl mx-auto relative">
      {/* Loading Overlay for Preview */}
      {loadingPreview && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white dark:bg-slate-900 p-4 rounded-xl flex items-center gap-3 shadow-xl border border-slate-200 dark:border-slate-800">
            <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
            <span className="font-medium text-slate-900 dark:text-white">Fetching from database...</span>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      <ContentDetailsModal 
        isOpen={isPreviewOpen} 
        onClose={() => setIsPreviewOpen(false)} 
        content={previewContent} 
      />

      {/* Hero Section */}
      <div className="flex flex-col md:flex-row items-start md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">System Overview</h1>
          <p className="text-gray-400">
            Neural Engine Status: <span className="text-emerald-400 font-medium">Operational</span>
          </p>
        </div>
        <Button 
          onClick={() => router.push('/dashboard/content')}
          className="h-12 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/25 rounded-xl font-semibold"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Launch Content Lab
        </Button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-32 relative overflow-hidden group hover:border-indigo-500/30 transition-colors"
          >
            <div className="flex justify-between items-start relative z-10">
              <div>
                <p className="text-sm text-gray-400 font-medium">{stat.label}</p>
                <h3 className="text-3xl font-bold mt-1">{loading ? '...' : stat.value}</h3>
              </div>
              <div className={cn("p-2 rounded-lg bg-white/5", stat.color)}>
                <stat.icon className="w-5 h-5" />
              </div>
            </div>
            <div className="relative z-10">
              <span className="text-xs font-medium text-gray-500 bg-white/5 px-2 py-1 rounded-full">
                {stat.change}
              </span>
            </div>
            <div className={cn(
              "absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-2xl opacity-10 transition-opacity group-hover:opacity-20",
              stat.color.replace('text-', 'bg-')
            )} />
          </motion.div>
        ))}
      </div>

      {/* Enhanced Previously Generated Content Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-panel rounded-2xl overflow-hidden border border-white/10"
      >
        <div className="p-6 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white/[0.02]">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            <h3 className="font-bold text-lg">Previously Generated Content</h3>
            <span className="text-xs px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded-full">
              {filteredActivity.length}
            </span>
          </div>
          
          <div className="flex items-center gap-3 flex-wrap">
            {/* Search */}
            <div className="relative flex-1 md:flex-none md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-10 pl-10 pr-4 bg-black/20 border border-white/10 rounded-lg text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none"
              />
            </div>
            
            {/* Filter */}
            <div className="flex items-center gap-1 bg-black/20 p-1 rounded-lg border border-white/10">
              {(['all', 'completed', 'processing', 'failed'] as FilterType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium rounded-md transition-all capitalize",
                    filterType === type 
                      ? "bg-indigo-500 text-white" 
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  )}
                >
                  {type}
                </button>
              ))}
            </div>
            
            {/* Refresh Button */}
            <Button
              onClick={refreshData}
              disabled={loading}
              variant="outline"
              size="sm"
              className="h-10"
            >
              <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
            </Button>
          </div>
        </div>
        
        <div className="divide-y divide-white/5">
          {loading ? (
            <div className="p-12 text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-4 text-indigo-500 animate-spin" />
              <p className="text-gray-400">Loading content history...</p>
            </div>
          ) : filteredActivity.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 mb-2">
                {searchQuery || filterType !== 'all' 
                  ? 'No content matches your filters' 
                  : 'No content generated yet'}
              </p>
              {(!searchQuery && filterType === 'all') && (
                <Button 
                  onClick={() => router.push('/dashboard/content')}
                  className="mt-4"
                  variant="outline"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Create Your First Content
                </Button>
              )}
            </div>
          ) : (
            <AnimatePresence>
              {filteredActivity.map((item, i) => {
                const isClickable = item.id && item.id.toString().startsWith('gen-');
                const PlatformIcon = getPlatformIcon(item.platform)
                const platformColor = getPlatformColor(item.platform)
              
                return (
                  <motion.div 
                    key={item.id || i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => isClickable && handleActivityClick(item)}
                    className={cn(
                      "p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-200 group border-l-4 border-transparent",
                      isClickable 
                        ? "hover:bg-white/[0.05] cursor-pointer hover:border-indigo-500 hover:pl-6" 
                        : "hover:bg-white/[0.02] cursor-default"
                    )}
                  >
                    <div className="flex items-start md:items-center gap-4 flex-1">
                      <div className={cn(
                        "w-12 h-12 rounded-xl flex items-center justify-center transition-all shrink-0",
                        platformColor,
                        isClickable && "group-hover:scale-110 group-hover:shadow-lg"
                      )}>
                        <PlatformIcon className="w-6 h-6" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className={cn(
                            "font-medium text-sm transition-colors",
                            isClickable ? "text-gray-200 group-hover:text-white" : "text-gray-400"
                          )}>
                            {item.description || 'System Event'}
                          </p>
                          <span className={cn(
                            "text-xs px-2 py-1 rounded-full capitalize shrink-0",
                            item.status === 'completed' 
                              ? "bg-emerald-500/20 text-emerald-300"
                              : item.status === 'processing'
                              ? "bg-amber-500/20 text-amber-300"
                              : "bg-red-500/20 text-red-300"
                          )}>
                            {item.status || 'unknown'}
                          </span>
                        </div>
                        <div className="flex items-center gap-3 mt-2 flex-wrap">
                          <span className="text-xs text-gray-500 flex items-center gap-1.5">
                            <Clock className="w-3 h-3" /> {item.time_ago || 'Unknown time'}
                          </span>
                          <span className="text-xs bg-white/5 px-2 py-1 rounded text-gray-400 capitalize">
                            {item.platform}
                          </span>
                          {isClickable && (
                            <span className="text-xs text-indigo-400 font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Eye className="w-3 h-3" /> View Details
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 md:ml-4">
                      {/* Social Post Buttons */}
                      {item.linkedin_content && item.linkedin_content.text && (
                        <button
                          onClick={(e) => handlePostToSocial(e, 'linkedin', item.linkedin_content, item)}
                          disabled={postingTo === `${item.id}-linkedin`}
                          className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-all hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Post to LinkedIn"
                        >
                          {postingTo === `${item.id}-linkedin` ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Linkedin className="w-4 h-4" />
                          )}
                        </button>
                      )}
                      {item.twitter_content && item.twitter_content.first_tweet && (
                        <button
                          onClick={(e) => handlePostToSocial(e, 'twitter', item.twitter_content, item)}
                          disabled={postingTo === `${item.id}-twitter`}
                          className="p-2.5 rounded-lg bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 transition-all hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Post to Twitter"
                        >
                          {postingTo === `${item.id}-twitter` ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Twitter className="w-4 h-4" />
                          )}
                        </button>
                      )}
                      
                      {isClickable && (
                        <ArrowUpRight className="w-5 h-5 text-gray-600 group-hover:text-indigo-400 transition-all transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:scale-110" />
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          )}
        </div>
      </motion.div>
    </div>
  )
}