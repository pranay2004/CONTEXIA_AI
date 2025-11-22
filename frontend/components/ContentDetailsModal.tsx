'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { 
  Linkedin, 
  Twitter, 
  Youtube, 
  FileCode, 
  Copy, 
  MonitorPlay,
  X
} from "lucide-react"
import { toast } from "sonner"
import { cn } from '@/lib/utils'

interface ContentDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  content: any
}

export function ContentDetailsModal({ isOpen, onClose, content }: ContentDetailsModalProps) {
  const [activeTab, setActiveTab] = useState('linkedin')

  useEffect(() => {
    if (isOpen) setActiveTab('linkedin')
  }, [isOpen])

  if (!isOpen || !content) return null

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  // ✅ HELPER: Safely converts script object/string to text
  const getScriptText = (script: any) => {
    if (!script) return 'No script available'
    if (typeof script === 'string') return script
    
    // If it's an object (from advanced AI agent), format it nicely
    let formatted = ''
    if (script.intro) formatted += `[INTRO]\n${script.intro}\n\n`
    if (script.story_problem) formatted += `[STORY & PROBLEM]\n${script.story_problem}\n\n`
    if (script.main_content) formatted += `[MAIN CONTENT]\n${script.main_content}\n\n`
    if (script.key_takeaways) formatted += `[TAKEAWAYS]\n${script.key_takeaways}\n\n`
    if (script.cta) formatted += `[CTA]\n${script.cta}\n\n`
    if (script.outro) formatted += `[OUTRO]\n${script.outro}`
    
    // Fallback: Just dump keys if structure doesn't match above
    if (!formatted) {
      return Object.entries(script)
        .map(([key, val]) => `[${key.toUpperCase().replace(/_/g, ' ')}]\n${val}`)
        .join('\n\n')
    }
    return formatted
  }

  // --- Views ---

  const LinkedInView = () => {
    const data = content.linkedin || {}
    const text = data.post_text || data.text || data.content || "No content available"
    
    return (
      <div className="space-y-4 max-w-2xl mx-auto">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-blue-600 font-bold">In</div>
            <div>
              <div className="font-semibold text-sm">LinkedIn Preview</div>
              <div className="text-xs text-slate-500">Saved Content</div>
            </div>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800 dark:text-slate-200 font-sans">
            {text}
          </p>
        </div>
        <Button onClick={() => copyToClipboard(text)} className="w-full bg-[#0077b5] hover:bg-[#00669c] text-white">
          <Copy className="w-4 h-4 mr-2" /> Copy Post
        </Button>
      </div>
    )
  }

  const TwitterView = () => {
    const thread = content.twitter_thread || content.x_thread || []
    const posts = Array.isArray(thread) ? thread : [thread]

    return (
      <div className="space-y-6 max-w-xl mx-auto">
        <div className="space-y-4">
          {posts.length > 0 ? posts.map((tweet: string, i: number) => (
            <div key={i} className="relative pl-6 pb-6 border-l-2 border-slate-200 dark:border-slate-800 last:border-0 last:pb-0">
              <div className="absolute -left-[9px] top-0 w-4 h-4 bg-slate-200 dark:bg-slate-800 rounded-full border-2 border-white dark:border-slate-950" />
              <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-800">
                <p className="whitespace-pre-wrap text-sm text-slate-800 dark:text-slate-200">{tweet}</p>
              </div>
            </div>
          )) : <p className="text-slate-500 text-center p-4">No Twitter content found</p>}
        </div>
        <Button onClick={() => copyToClipboard(posts.join('\n\n'))} className="w-full bg-black hover:bg-gray-800 text-white dark:bg-white dark:text-black">
          <Copy className="w-4 h-4 mr-2" /> Copy Thread
        </Button>
      </div>
    )
  }

  const YouTubeView = () => {
    const data = content.youtube || {}
    // ✅ FIX: Convert object to string safely
    const scriptText = getScriptText(data.script)
    
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full">
        <div className="md:col-span-1 space-y-4">
          <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
            <label className="text-xs font-bold text-slate-500 uppercase">Title</label>
            <p className="font-medium mt-1 text-sm">{data.title || 'Untitled'}</p>
          </div>
          <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
            <label className="text-xs font-bold text-slate-500 uppercase">Description</label>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 whitespace-pre-wrap">
              {data.description || 'No description'}
            </p>
          </div>
        </div>
        <div className="md:col-span-2 flex flex-col h-full">
          <div className="bg-slate-950 text-slate-300 p-6 rounded-xl border border-slate-800 flex-1 overflow-y-auto font-mono text-sm max-h-[500px]">
            <div className="flex items-center gap-2 mb-4 text-slate-500 border-b border-slate-800 pb-2 sticky top-0 bg-slate-950">
              <MonitorPlay className="w-4 h-4" /> Script View
            </div>
            {/* ✅ Now safe to split because scriptText is guaranteed to be a string */}
            {scriptText.split(/(\[.*?\])/).map((part: string, i: number) => 
              part.startsWith('[') && part.endsWith(']') ? 
                <span key={i} className="text-yellow-500 font-bold block my-4">{part}</span> : 
                <span key={i}>{part}</span>
            )}
          </div>
          <Button onClick={() => copyToClipboard(scriptText)} className="w-full mt-4 shrink-0 bg-red-600 hover:bg-red-700 text-white">
            <Copy className="w-4 h-4 mr-2" /> Copy Script
          </Button>
        </div>
      </div>
    )
  }

  const BlogView = () => {
    const data = content.long_blog || {}
    return (
      <div className="space-y-4 h-full flex flex-col max-w-4xl mx-auto">
        <div className="bg-white dark:bg-slate-950 p-8 rounded-xl border border-slate-200 dark:border-slate-800 flex-1 overflow-y-auto max-h-[600px]">
          <h1 className="text-3xl font-bold mb-6">{data.title || 'Untitled Post'}</h1>
          <article className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
            <div dangerouslySetInnerHTML={{ __html: data.html_content || data.html || '<p>No content</p>' }} />
          </article>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button onClick={() => copyToClipboard(data.html_content || data.html || '')} variant="outline" className="flex-1">
            <FileCode className="w-4 h-4 mr-2" /> Copy HTML
          </Button>
          <Button onClick={() => copyToClipboard((data.html_content || data.html || '').replace(/<[^>]*>/g, ''))} className="flex-1">
            <Copy className="w-4 h-4 mr-2" /> Copy Text
          </Button>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    switch(activeTab) {
      case 'linkedin': return <LinkedInView />;
      case 'twitter': return <TwitterView />;
      case 'youtube': return <YouTubeView />;
      case 'blog': return <BlogView />;
      default: return <LinkedInView />;
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-50 dark:bg-slate-950 w-full max-w-6xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-slate-200 dark:border-slate-800">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex justify-between items-center shrink-0">
          <h2 className="text-lg font-bold">Content Preview</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Tabs Navigation */}
        <div className="px-6 pt-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shrink-0">
          <div className="flex gap-2 overflow-x-auto">
             {['linkedin', 'twitter', 'youtube', 'blog'].map((tab) => (
               <button
                 key={tab}
                 onClick={() => setActiveTab(tab)}
                 className={cn(
                   "px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors flex items-center gap-2 whitespace-nowrap",
                   activeTab === tab 
                     ? "border-indigo-500 text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/10" 
                     : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                 )}
               >
                 {tab === 'linkedin' && <Linkedin className="w-4 h-4" />}
                 {tab === 'twitter' && <Twitter className="w-4 h-4" />}
                 {tab === 'youtube' && <Youtube className="w-4 h-4" />}
                 {tab === 'blog' && <FileCode className="w-4 h-4" />}
                 {tab.charAt(0).toUpperCase() + tab.slice(1)}
               </button>
             ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative bg-slate-50 dark:bg-slate-950">
          <div className="absolute inset-0 overflow-y-auto p-6">
             {renderContent()}
          </div>
        </div>

      </div>
    </div>
  )
}