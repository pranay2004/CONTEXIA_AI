'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Linkedin, 
  Twitter, 
  Youtube, 
  FileCode, 
  Copy, 
  MonitorPlay
} from "lucide-react"
import { toast } from "sonner"

interface ContentDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  content: any // The full content_json from the database
}

export function ContentDetailsModal({ isOpen, onClose, content }: ContentDetailsModalProps) {
  const [activeTab, setActiveTab] = useState('linkedin')

  if (!content) return null

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  // --- Views ---

  const LinkedInView = () => {
    const data = content.linkedin || {}
    const text = data.post_text || data.text || data.content || "No content available"
    const hashtags = data.hashtags || []

    return (
      <div className="space-y-4">
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
          {hashtags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {hashtags.map((tag: string, i: number) => (
                <span key={i} className="text-blue-500 text-sm">#{tag.replace('#', '')}</span>
              ))}
            </div>
          )}
        </div>
        <Button onClick={() => copyToClipboard(text)} className="w-full">
          <Copy className="w-4 h-4 mr-2" /> Copy Post
        </Button>
      </div>
    )
  }

  const TwitterView = () => {
    const thread = content.twitter_thread || content.x_thread || []
    const posts = Array.isArray(thread) ? thread : [thread]

    return (
      <div className="space-y-6">
        <div className="space-y-4">
          {posts.map((tweet: string, i: number) => (
            <div key={i} className="relative pl-6 pb-6 border-l-2 border-slate-200 dark:border-slate-800 last:border-0 last:pb-0">
              <div className="absolute -left-[9px] top-0 w-4 h-4 bg-slate-200 dark:bg-slate-800 rounded-full border-2 border-white dark:border-slate-950" />
              <div className="bg-white dark:bg-slate-900 p-4 rounded-lg border border-slate-200 dark:border-slate-800">
                <p className="whitespace-pre-wrap text-sm text-slate-800 dark:text-slate-200">{tweet}</p>
              </div>
            </div>
          ))}
        </div>
        <Button onClick={() => copyToClipboard(posts.join('\n\n'))} className="w-full">
          <Copy className="w-4 h-4 mr-2" /> Copy Thread
        </Button>
      </div>
    )
  }

  const YouTubeView = () => {
    const data = content.youtube || {}
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
          <div className="bg-slate-950 text-slate-300 p-6 rounded-xl border border-slate-800 flex-1 overflow-y-auto font-mono text-sm custom-scrollbar">
            <div className="flex items-center gap-2 mb-4 text-slate-500 border-b border-slate-800 pb-2 sticky top-0 bg-slate-950">
              <MonitorPlay className="w-4 h-4" /> Script View
            </div>
            {(data.script || '').split(/(\[.*?\])/).map((part: string, i: number) => 
              part.startsWith('[') && part.endsWith(']') ? 
                <span key={i} className="text-yellow-500 font-bold block my-4">{part}</span> : 
                <span key={i}>{part}</span>
            )}
          </div>
          <Button onClick={() => copyToClipboard(data.script)} className="w-full mt-4">
            <Copy className="w-4 h-4 mr-2" /> Copy Script
          </Button>
        </div>
      </div>
    )
  }

  const BlogView = () => {
    const data = content.long_blog || {}
    return (
      <div className="space-y-4 h-full flex flex-col">
        <div className="bg-white dark:bg-slate-950 p-8 rounded-xl border border-slate-200 dark:border-slate-800 flex-1 overflow-y-auto">
          <h1 className="text-3xl font-bold mb-6">{data.title || 'Untitled Post'}</h1>
          <article className="prose prose-sm md:prose-base dark:prose-invert max-w-none">
            <div dangerouslySetInnerHTML={{ __html: data.html_content || data.html || '' }} />
          </article>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button onClick={() => copyToClipboard(data.html_content || data.html)} variant="outline" className="flex-1">
            <FileCode className="w-4 h-4 mr-2" /> Copy HTML
          </Button>
          <Button onClick={() => copyToClipboard((data.html_content || data.html || '').replace(/<[^>]*>/g, ''))} className="flex-1">
            <Copy className="w-4 h-4 mr-2" /> Copy Text
          </Button>
        </div>
      </div>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-6xl h-[90vh] flex flex-col p-0 gap-0 bg-slate-50 dark:bg-slate-950 overflow-hidden">
        <DialogHeader className="p-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
          <DialogTitle>Content Preview</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col min-h-0">
          <div className="px-6 pt-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shrink-0">
            <TabsList className="grid grid-cols-4 w-full max-w-md">
              <TabsTrigger value="linkedin"><Linkedin className="w-4 h-4 mr-2" /> LinkedIn</TabsTrigger>
              <TabsTrigger value="twitter"><Twitter className="w-4 h-4 mr-2" /> Twitter</TabsTrigger>
              <TabsTrigger value="youtube"><Youtube className="w-4 h-4 mr-2" /> YouTube</TabsTrigger>
              <TabsTrigger value="blog"><FileCode className="w-4 h-4 mr-2" /> Blog</TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-hidden relative bg-slate-50 dark:bg-slate-950">
            <div className="absolute inset-0 overflow-y-auto p-6">
              <TabsContent value="linkedin" className="m-0 max-w-2xl mx-auto h-full">
                <LinkedInView />
              </TabsContent>
              <TabsContent value="twitter" className="m-0 max-w-xl mx-auto h-full">
                <TwitterView />
              </TabsContent>
              <TabsContent value="youtube" className="m-0 h-full">
                <YouTubeView />
              </TabsContent>
              <TabsContent value="blog" className="m-0 max-w-4xl mx-auto h-full">
                <BlogView />
              </TabsContent>
            </div>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}