'use client'

import { useEffect, useState } from 'react'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts'
import { 
  ArrowUpRight, 
  Download, 
  Filter,
  PieChart,
  Share2,
  TrendingUp // <--- Added missing import
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
// Ensure getAnalyticsSummary exists in your api-client or remove if unused
import { getAnalyticsSummary } from '@/lib/api-client' 

export default function AnalyticsPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulation of fetching detailed time-series data
    setTimeout(() => {
      setData([
        { name: 'Mon', reach: 4000, engagement: 2400 },
        { name: 'Tue', reach: 3000, engagement: 1398 },
        { name: 'Wed', reach: 2000, engagement: 9800 },
        { name: 'Thu', reach: 2780, engagement: 3908 },
        { name: 'Fri', reach: 1890, engagement: 4800 },
        { name: 'Sat', reach: 2390, engagement: 3800 },
        { name: 'Sun', reach: 3490, engagement: 4300 },
      ])
      setLoading(false)
    }, 1000)
  }, [])

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Performance Matrix</h1>
          <p className="text-gray-400">Real-time impact analysis across all connected nodes.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-white/10 hover:bg-white/5">
            <Filter className="w-4 h-4 mr-2" /> 7 Days
          </Button>
          <Button variant="outline" className="border-white/10 hover:bg-white/5">
            <Download className="w-4 h-4 mr-2" /> Export
          </Button>
        </div>
      </div>

      {/* Main Growth Chart */}
      <div className="glass-panel p-6 rounded-2xl h-[400px] relative">
        <div className="mb-6 flex justify-between items-center">
           <h3 className="font-bold text-lg flex items-center gap-2">
             <TrendingUp className="w-5 h-5 text-indigo-400" />
             Audience Growth & Reach
           </h3>
        </div>
        
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="85%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorReach" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
              <XAxis dataKey="name" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px', color: '#fff' }}
                 itemStyle={{ color: '#fff' }}
              />
              <Area 
                 type="monotone" 
                 dataKey="reach" 
                 stroke="#6366f1" 
                 strokeWidth={3}
                 fillOpacity={1} 
                 fill="url(#colorReach)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Platform Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
         {/* Engagement Bar Chart */}
         <div className="glass-panel p-6 rounded-2xl h-[300px]">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5 text-purple-400" />
              Engagement Intensity
            </h3>
            <ResponsiveContainer width="100%" height="80%">
               <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="name" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip 
                     cursor={{fill: 'transparent'}}
                     contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  />
                  <Bar dataKey="engagement" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
               </BarChart>
            </ResponsiveContainer>
         </div>

         {/* Top Content List */}
         <div className="glass-panel p-6 rounded-2xl">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <Share2 className="w-5 h-5 text-green-400" />
              Top Performing Vectors
            </h3>
            <div className="space-y-3">
               {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors">
                     <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-800 to-black border border-white/10" />
                     <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm truncate text-gray-200">Q3 Analysis & Future Trends</div>
                        <div className="text-xs text-gray-500">LinkedIn • 4.2k views</div>
                     </div>
                     <div className="text-right">
                        <div className="font-bold text-emerald-400 text-sm">98%</div>
                        <div className="text-[10px] text-gray-500">Score</div>
                     </div>
                  </div>
               ))}
            </div>
         </div>
      </div>
    </div>
  )
}