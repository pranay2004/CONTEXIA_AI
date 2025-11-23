'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  Eye, 
  ThumbsUp, 
  MessageSquare,
  ArrowUpRight,
  Linkedin,
  Twitter,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { socialApi, AnalyticsSummary, DashboardData } from '@/lib/api/social'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'

export default function AnalyticsPage() {
  const router = useRouter()
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [graphData, setGraphData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const [summaryData, dashData] = await Promise.all([
        socialApi.getAnalyticsSummary(),
        socialApi.getDashboardData()
      ])
      setSummary(summaryData)
      setGraphData(dashData)
    } catch (error) {
      console.error("Failed to load analytics", error)
      toast.error("Could not load analytics data")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="h-[50vh] flex flex-col items-center justify-center text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin mb-4 text-indigo-500" />
        <p>Gathering insights...</p>
      </div>
    )
  }

  // If no posts ever, show empty state prompting connection
  if (summary && summary.total_posts === 0) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-center space-y-6">
        <div className="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center">
          <BarChart3 className="w-10 h-10 text-indigo-500" />
        </div>
        <div className="max-w-md">
          <h2 className="text-2xl font-bold text-white mb-2">No Analytics Yet</h2>
          <p className="text-gray-400 mb-6">Connect your social accounts and start publishing to see real-time performance data here.</p>
          <Button onClick={() => router.push('/dashboard/content')} className="bg-indigo-600 hover:bg-indigo-500">
            Go to Content Lab
          </Button>
        </div>
      </div>
    )
  }

  const stats = [
    { 
      label: 'Total Impressions', 
      value: summary?.total_impressions?.toLocaleString() || '0', 
      icon: Eye,
      color: 'text-blue-400'
    },
    { 
      label: 'Avg. Engagement', 
      value: `${summary?.avg_engagement_rate?.toFixed(1) || '0'}%`, 
      icon: TrendingUp,
      color: 'text-green-400'
    },
    { 
      label: 'Total Likes', 
      value: summary?.total_likes?.toLocaleString() || '0', 
      icon: ThumbsUp,
      color: 'text-pink-400'
    },
    { 
      label: 'Total Comments', 
      value: summary?.total_comments?.toLocaleString() || '0', 
      icon: MessageSquare,
      color: 'text-purple-400'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Performance Analytics</h1>
          <p className="text-gray-400">Real-time insights from your connected social accounts</p>
        </div>
        <Button variant="outline" onClick={loadAnalytics} className="gap-2">
          <TrendingUp className="w-4 h-4" /> Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel p-6 rounded-2xl relative overflow-hidden"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`p-3 rounded-xl bg-white/5 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
            <div>
              <p className="text-gray-400 text-sm font-medium mb-1">{stat.label}</p>
              <h3 className="text-3xl font-bold text-white">{stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Engagement Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl">
          <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
            30-Day Activity
          </h3>
          
          {graphData?.engagement_trend && graphData.engagement_trend.length > 0 ? (
            <div className="h-[300px] flex items-end gap-2 px-4 pb-4 border-b border-white/5">
              {graphData.engagement_trend.map((day, i) => {
                // Simple normalization for bar height (max 100%)
                const maxImpressions = Math.max(...graphData.engagement_trend.map(d => d.impressions)) || 1;
                const height = (day.impressions / maxImpressions) * 100;
                
                return (
                  <div key={i} className="flex-1 group relative flex flex-col justify-end h-full">
                    <div 
                      className="w-full bg-indigo-500/20 hover:bg-indigo-500/40 rounded-t-sm transition-all duration-300 relative min-h-[4px]"
                      style={{ height: `${height}%` }}
                    >
                      <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-900 text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10 pointer-events-none z-10">
                        {new Date(day.date).toLocaleDateString()} <br/>
                        {day.impressions} views
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500 border-b border-white/5">
              No engagement data recorded yet
            </div>
          )}
        </div>

        {/* Platform Breakdown */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-lg font-semibold mb-6">Platform Performance</h3>
          <div className="space-y-6">
            {(!summary?.platform_breakdown || summary.platform_breakdown.length === 0) && (
               <div className="text-center py-8 text-gray-500">
                 <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                 <p className="text-sm">No active platforms</p>
               </div>
            )}
            
            {summary?.platform_breakdown?.map((platform) => (
              <div key={platform.scheduled_post__social_account__platform} className="group">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                      {platform.scheduled_post__social_account__platform === 'linkedin' ? <Linkedin className="w-4 h-4" /> : <Twitter className="w-4 h-4" />}
                    </div>
                    <span className="capitalize font-medium text-sm">{platform.scheduled_post__social_account__platform}</span>
                  </div>
                  <div className="text-right">
                    <span className="block text-sm font-bold">{platform.count} Posts</span>
                    <span className="text-xs text-gray-500">{platform.engagement.toFixed(1)}% Eng.</span>
                  </div>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-blue-500 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${(platform.count / (summary.total_posts || 1)) * 100}%` }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}