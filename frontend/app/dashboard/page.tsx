'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
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
  FileText
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { getUserAnalytics, getRecentActivity, getGeneratedContent, UserStats } from '@/lib/api-client'
import { toast } from 'sonner'
import { ContentDetailsModal } from '@/components/ContentDetailsModal'

export const dynamic = 'force-dynamic'

export default function DashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  
  // Preview Modal State
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [previewContent, setPreviewContent] = useState<any>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, activityData] = await Promise.all([
          getUserAnalytics(),
          getRecentActivity()
        ])
        
        if (statsData) setStats(statsData)
        if (activityData && Array.isArray(activityData)) setRecentActivity(activityData)
        
      } catch (error) {
        console.error('Dashboard load failed', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

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

  const statCards = [
    { 
      label: 'Total Impressions', 
      value: stats?.total_posts ? stats.total_posts.toLocaleString() : '-', 
      change: '+12%', 
      icon: Users, 
      color: 'text-blue-400' 
    },
    { 
      label: 'Avg. Engagement', 
      value: stats?.engagement_rate ? `${stats.engagement_rate}%` : '-', 
      change: '+2.1%', 
      icon: TrendingUp, 
      color: 'text-green-400' 
    },
    { 
      label: 'Content Efficiency', 
      value: stats?.hours_saved ? `${stats.hours_saved}h` : '-', 
      change: 'Saved this mo.', 
      icon: Zap, 
      color: 'text-purple-400' 
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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

      {/* Recent Activity Feed */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-panel rounded-2xl overflow-hidden border border-white/10"
      >
        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" />
            <h3 className="font-bold">Recent Generation Events</h3>
          </div>
        </div>
        
        <div className="divide-y divide-white/5">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading neural logs...</div>
          ) : recentActivity.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No recent activity detected.</div>
          ) : (
            recentActivity.map((item, i) => {
              const isClickable = item.id && item.id.toString().startsWith('gen-');
              
              return (
                <div 
                  key={i} 
                  onClick={() => handleActivityClick(item)}
                  className={cn(
                    "p-4 flex items-center justify-between transition-all duration-200 group border-l-2 border-transparent",
                    isClickable 
                      ? "hover:bg-white/[0.05] cursor-pointer hover:border-indigo-500 hover:pl-5" 
                      : "hover:bg-white/[0.02] cursor-default"
                  )}
                >
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                      isClickable ? "bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500/20 group-hover:text-indigo-300" : "bg-slate-800 text-slate-500"
                    )}>
                      {item.platform === 'system' ? <FileText className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                    </div>
                    <div>
                      <p className={cn("font-medium text-sm transition-colors", isClickable ? "text-gray-200 group-hover:text-white" : "text-gray-400")}>
                        {item.description || 'System Event'}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {item.time_ago}
                        </span>
                        <span className="text-xs bg-white/5 px-2 py-0.5 rounded text-gray-400 capitalize">
                          {item.platform}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {item.status === 'completed' ? (
                      <span className="text-xs text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">Completed</span>
                    ) : (
                      <span className="text-xs text-amber-400 bg-amber-400/10 px-2 py-1 rounded-full">Processing</span>
                    )}
                    {isClickable && (
                      <ArrowUpRight className="w-4 h-4 text-gray-600 group-hover:text-indigo-400 transition-colors transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </motion.div>
    </div>
  )
}