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
  X,
  Download,
  Share2,
  Eye,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Hash,
  AtSign,
  Mail,
  Send,
  ExternalLink
} from "lucide-react"
import { toast } from "sonner"
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { format } from 'date-fns'

interface ContentDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  content: any
}

export function ContentDetailsModal({ isOpen, onClose, content }: ContentDetailsModalProps) {
  const [activeTab, setActiveTab] = useState('linkedin')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (isOpen) setActiveTab('linkedin')
  }, [isOpen])

  if (!isOpen || !content) return null

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    toast.success('Copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadAsFile = (text: string, filename: string) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Downloaded successfully!')
  }

  const postToLinkedIn = (text: string) => {
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`
    window.open(linkedinUrl, '_blank', 'width=600,height=600')
    toast.success('Opening LinkedIn...')
  }

  const postToTwitter = (text: string) => {
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`
    window.open(twitterUrl, '_blank', 'width=600,height=600')
    toast.success('Opening Twitter...')
  }

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-emerald-500" />
      case 'processing': return <Clock className="w-4 h-4 text-amber-500" />
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-500" />
      default: return <Clock className="w-4 h-4 text-slate-400" />
    }
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
    const wordCount = text.split(/\s+/).length
    const charCount = text.length
    
    return (
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 max-w-2xl mx-auto"
      >
        {/* Stats Bar */}
        <div className="flex items-center justify-between gap-4 p-4 bg-blue-50 dark:bg-blue-900/10 rounded-xl border border-blue-100 dark:border-blue-900/30">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-blue-600" />
              <span className="text-slate-600 dark:text-slate-400">{wordCount} words</span>
            </div>
            <div className="flex items-center gap-2">
              <AtSign className="w-4 h-4 text-blue-600" />
              <span className="text-slate-600 dark:text-slate-400">{charCount} chars</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400 font-medium">
            <Sparkles className="w-3 h-3" />
            AI Generated
          </div>
        </div>

        {/* LinkedIn Post Card */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg">
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-md">
              <Linkedin className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-base">LinkedIn Post</div>
              <div className="text-xs text-slate-500 flex items-center gap-2">
                <Eye className="w-3 h-3" />
                Professional Format • Ready to Share
              </div>
            </div>
          </div>
          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-lg">
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800 dark:text-slate-200 font-sans">
              {text}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button 
            onClick={() => postToLinkedIn(text)} 
            className="flex-1 bg-[#0077b5] hover:bg-[#00669c] text-white shadow-md hover:shadow-lg transition-all"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Post to LinkedIn
          </Button>
          <Button 
            onClick={() => copyToClipboard(text)} 
            variant="outline"
            className="border-[#0077b5] text-[#0077b5] hover:bg-blue-50 dark:hover:bg-blue-950/20"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
            {copied ? 'Copied!' : 'Copy'}
          </Button>
          <Button 
            onClick={() => downloadAsFile(text, 'linkedin-post.txt')} 
            variant="outline"
            className="border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </motion.div>
    )
  }

  const TwitterView = () => {
    const thread = content.twitter_thread || content.x_thread || []
    const posts = Array.isArray(thread) ? thread : [thread]
    const totalChars = posts.reduce((acc: number, tweet: string) => acc + tweet.length, 0)

    return (
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 max-w-xl mx-auto"
      >
        {/* Stats Bar */}
        <div className="flex items-center justify-between gap-4 p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Twitter className="w-4 h-4 text-slate-700 dark:text-slate-300" />
              <span className="text-slate-600 dark:text-slate-400">{posts.length} {posts.length === 1 ? 'tweet' : 'tweets'}</span>
            </div>
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-slate-700 dark:text-slate-300" />
              <span className="text-slate-600 dark:text-slate-400">{totalChars} chars total</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 font-medium">
            <Sparkles className="w-3 h-3" />
            Thread
          </div>
        </div>

        {/* Thread */}
        <div className="space-y-4">
          {posts.length > 0 ? posts.map((tweet: string, i: number) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="relative pl-6 pb-6 border-l-2 border-slate-300 dark:border-slate-700 last:border-0 last:pb-0"
            >
              <div className="absolute -left-[9px] top-0 w-4 h-4 bg-slate-700 dark:bg-slate-300 rounded-full border-2 border-white dark:border-slate-950 shadow-sm" />
              <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-md hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-2 mb-3 text-xs text-slate-500">
                  <span className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-full font-medium">
                    Tweet {i + 1}/{posts.length}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span>{tweet.length}/280 chars</span>
                </div>
                <p className="whitespace-pre-wrap text-sm text-slate-800 dark:text-slate-200 leading-relaxed">{tweet}</p>
              </div>
            </motion.div>
          )) : (
            <div className="text-center p-8 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
              <Twitter className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500">No Twitter content found</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button 
            onClick={() => postToTwitter(posts.join('\n\n'))} 
            className="flex-1 bg-black hover:bg-gray-800 text-white dark:bg-white dark:text-black dark:hover:bg-slate-200 shadow-md hover:shadow-lg transition-all"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Post to Twitter
          </Button>
          <Button 
            onClick={() => copyToClipboard(posts.join('\n\n'))} 
            variant="outline"
            className="border-slate-700 dark:border-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
            {copied ? 'Copied!' : 'Copy'}
          </Button>
          <Button 
            onClick={() => downloadAsFile(posts.join('\n\n'), 'twitter-thread.txt')} 
            variant="outline"
            className="border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </motion.div>
    )
  }

  const YouTubeView = () => {
    const data = content.youtube || {}
    const scriptText = getScriptText(data.script)
    const wordCount = scriptText.split(/\s+/).length
    const estimatedDuration = Math.ceil(wordCount / 150) // Approx 150 words per minute
    
    return (
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full"
      >
        {/* Metadata Panel */}
        <div className="md:col-span-1 space-y-4">
          <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-950/30 dark:to-red-900/20 p-5 rounded-xl border border-red-200 dark:border-red-900/30 shadow-md">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center shadow-md">
                <Youtube className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-semibold text-sm">YouTube Video</div>
                <div className="text-xs text-red-700 dark:text-red-400">Script Ready</div>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                <Clock className="w-4 h-4" />
                <span>~{estimatedDuration} min read</span>
              </div>
              <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                <Hash className="w-4 h-4" />
                <span>{wordCount} words</span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-md">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2 mb-2">
              <Sparkles className="w-3 h-3" /> Title
            </label>
            <p className="font-semibold text-sm leading-relaxed">{data.title || 'Untitled Video'}</p>
          </div>

          <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-md">
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2 mb-2">
              <FileCode className="w-3 h-3" /> Description
            </label>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-wrap">
              {data.description || 'No description available'}
            </p>
          </div>
        </div>

        {/* Script Panel */}
        <div className="md:col-span-2 flex flex-col h-full">
          <div className="bg-slate-950 text-slate-300 p-6 rounded-xl border border-slate-800 flex-1 overflow-y-auto font-mono text-sm max-h-[500px] shadow-2xl">
            <div className="flex items-center gap-2 mb-6 text-slate-400 border-b border-slate-800 pb-3 sticky top-0 bg-slate-950 z-10">
              <MonitorPlay className="w-5 h-5 text-red-500" />
              <span className="font-bold">Video Script</span>
              <span className="ml-auto text-xs bg-slate-800 px-2 py-1 rounded">AI Generated</span>
            </div>
            <div className="space-y-1">
              {scriptText.split(/(\[.*?\])/).map((part: string, i: number) => 
                part.startsWith('[') && part.endsWith(']') ? 
                  <div key={i} className="text-amber-400 font-bold text-base my-6 flex items-center gap-2">
                    <div className="w-1 h-6 bg-amber-400 rounded-full" />
                    {part}
                  </div> : 
                  <span key={i} className="text-slate-300 leading-relaxed block">{part}</span>
              )}
            </div>
          </div>
          <div className="flex gap-3 mt-4 shrink-0">
            <Button 
              onClick={() => copyToClipboard(scriptText)} 
              className="flex-1 bg-red-600 hover:bg-red-700 text-white shadow-md hover:shadow-lg transition-all"
            >
              {copied ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
              {copied ? 'Copied!' : 'Copy Script'}
            </Button>
            <Button 
              onClick={() => downloadAsFile(scriptText, 'youtube-script.txt')} 
              variant="outline"
              className="border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>
        </div>
      </motion.div>
    )
  }

  const BlogView = () => {
    const data = content.long_blog || {}
    const htmlContent = data.html_content || data.html || '<p>No content</p>'
    const plainText = htmlContent.replace(/<[^>]*>/g, '')
    const wordCount = plainText.split(/\s+/).length
    const readTime = Math.ceil(wordCount / 200) // 200 words per minute
    
    return (
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 h-full flex flex-col max-w-4xl mx-auto"
      >
        {/* Stats Bar */}
        <div className="flex items-center justify-between gap-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/20 rounded-xl border border-purple-200 dark:border-purple-900/30 shadow-md">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="text-slate-700 dark:text-slate-300 font-medium">Blog Post</span>
            </div>
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="text-slate-600 dark:text-slate-400">{wordCount} words</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="text-slate-600 dark:text-slate-400">{readTime} min read</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-purple-600 dark:text-purple-400 font-medium">
            <Sparkles className="w-3 h-3" />
            Long Form
          </div>
        </div>

        {/* Blog Content */}
        <div className="bg-white dark:bg-slate-950 p-8 md:p-10 rounded-xl border border-slate-200 dark:border-slate-800 flex-1 overflow-y-auto max-h-[600px] shadow-lg">
          <div className="mb-8 pb-6 border-b border-slate-200 dark:border-slate-800">
            <h1 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {data.title || 'Untitled Post'}
            </h1>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                <span>{format(new Date(), 'MMM dd, yyyy')}</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4" />
                <span>Professional Format</span>
              </div>
            </div>
          </div>
          <article className="prose prose-sm md:prose-base dark:prose-invert max-w-none prose-headings:font-bold prose-a:text-purple-600 dark:prose-a:text-purple-400 prose-img:rounded-lg prose-img:shadow-md">
            <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
          </article>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 shrink-0">
          <Button 
            onClick={() => copyToClipboard(htmlContent)} 
            variant="outline" 
            className="flex-1 border-purple-300 dark:border-purple-700 hover:bg-purple-50 dark:hover:bg-purple-900/20"
          >
            <FileCode className="w-4 h-4 mr-2" /> Copy HTML
          </Button>
          <Button 
            onClick={() => copyToClipboard(plainText)} 
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-md hover:shadow-lg transition-all"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
            {copied ? 'Copied!' : 'Copy Text'}
          </Button>
          <Button 
            onClick={() => downloadAsFile(htmlContent, 'blog-post.html')} 
            variant="outline"
            className="border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </Button>
        </div>
      </motion.div>
    )
  }

  const EmailView = () => {
    const data = content.email || {}
    const subject = data.subject || 'No subject available'
    const body = data.body || data.content || 'No content available'
    const wordCount = body.split(/\s+/).length
    const readTime = Math.ceil(wordCount / 200)
    
    return (
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 max-w-3xl mx-auto"
      >
        {/* Stats Bar */}
        <div className="flex items-center justify-between gap-4 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/20 rounded-xl border border-emerald-200 dark:border-emerald-900/30 shadow-md">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span className="text-slate-700 dark:text-slate-300 font-medium">Email Campaign</span>
            </div>
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span className="text-slate-600 dark:text-slate-400">{wordCount} words</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span className="text-slate-600 dark:text-slate-400">{readTime} min read</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            <Sparkles className="w-3 h-3" />
            Professional
          </div>
        </div>

        {/* Email Card */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg overflow-hidden">
          {/* Email Header */}
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center shadow-md">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="font-semibold text-sm opacity-90">Professional Email</div>
                <div className="text-xs opacity-75">Ready to Send</div>
              </div>
            </div>
          </div>

          {/* Email Content */}
          <div className="p-6 space-y-6">
            {/* Subject Line */}
            <div className="pb-4 border-b border-slate-200 dark:border-slate-800">
              <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2 mb-2">
                <Send className="w-3 h-3" /> Subject Line
              </label>
              <p className="font-semibold text-lg text-slate-800 dark:text-slate-200">
                {subject}
              </p>
            </div>

            {/* Email Body */}
            <div className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-lg">
              <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2 mb-3">
                <FileCode className="w-3 h-3" /> Email Body
              </label>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                  {body}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button 
            onClick={() => {
              const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
              window.location.href = mailtoLink
              toast.success('Opening email client...')
            }}
            className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all"
          >
            <Send className="w-4 h-4 mr-2" />
            Open in Email Client
          </Button>
          <Button 
            onClick={() => copyToClipboard(`Subject: ${subject}\n\n${body}`)} 
            variant="outline"
            className="border-emerald-300 dark:border-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/20"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
            {copied ? 'Copied!' : 'Copy'}
          </Button>
          <Button 
            onClick={() => downloadAsFile(`Subject: ${subject}\n\n${body}`, 'email-campaign.txt')} 
            variant="outline"
            className="border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </motion.div>
    )
  }

  const renderContent = () => {
    switch(activeTab) {
      case 'linkedin': return <LinkedInView />;
      case 'twitter': return <TwitterView />;
      case 'youtube': return <YouTubeView />;
      case 'blog': return <BlogView />;
      case 'email': return <EmailView />;
      default: return <LinkedInView />;
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md"
          onClick={onClose}
        >
          <motion.div 
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ type: "spring", duration: 0.5 }}
            className="bg-slate-50 dark:bg-slate-950 w-full max-w-6xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-slate-200 dark:border-slate-800"
            onClick={(e) => e.stopPropagation()}
          >
            
            {/* Enhanced Header */}
            <div className="p-5 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-r from-white to-slate-50 dark:from-slate-900 dark:to-slate-900/80 flex justify-between items-center shrink-0 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                  <Eye className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold flex items-center gap-2">
                    Content Preview
                    {content.status && (
                      <span className="ml-2">{getStatusIcon(content.status)}</span>
                    )}
                  </h2>
                  <p className="text-xs text-slate-500 flex items-center gap-2">
                    {content.created_at && (
                      <>
                        <Calendar className="w-3 h-3" />
                        {format(new Date(content.created_at), 'MMM dd, yyyy • h:mm a')}
                      </>
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="ghost" 
                  size="icon"
                  className="hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full"
                  onClick={onClose}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </div>

            {/* Enhanced Tabs Navigation */}
            <div className="px-6 pt-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shrink-0">
              <div className="flex gap-2 overflow-x-auto pb-px scrollbar-hide">
                 {['linkedin', 'twitter', 'youtube', 'blog', 'email'].map((tab) => (
                   <button
                     key={tab}
                     onClick={() => setActiveTab(tab)}
                     className={cn(
                       "px-5 py-3 text-sm font-medium rounded-t-xl transition-all flex items-center gap-2 whitespace-nowrap border-b-2 relative overflow-hidden",
                       activeTab === tab 
                         ? "border-indigo-500 text-indigo-600 dark:text-indigo-400 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/20 shadow-sm" 
                         : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                     )}
                   >
                     {activeTab === tab && (
                       <motion.div
                         layoutId="activeTab"
                         className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/20 -z-10"
                         transition={{ type: "spring", duration: 0.5 }}
                       />
                     )}
                     {tab === 'linkedin' && <Linkedin className="w-4 h-4" />}
                     {tab === 'twitter' && <Twitter className="w-4 h-4" />}
                     {tab === 'youtube' && <Youtube className="w-4 h-4" />}
                     {tab === 'blog' && <FileCode className="w-4 h-4" />}
                     {tab === 'email' && <Mail className="w-4 h-4" />}
                     {tab.charAt(0).toUpperCase() + tab.slice(1)}
                   </button>
                 ))}
              </div>
            </div>

            {/* Content Area with Animation */}
            <div className="flex-1 overflow-hidden relative bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
              <div className="absolute inset-0 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700 scrollbar-track-transparent">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderContent()}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}