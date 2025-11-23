'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/navigation'
import { 
  Upload, FileText, Sparkles, Loader2, Copy, Send,
  Linkedin, Twitter, Youtube, FileCode, AlertCircle,
  X, MonitorPlay, Clock, Calendar as CalendarIcon, Mail, Image as ImageIcon
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { uploadContent, generateContent, checkTaskStatus } from '@/lib/api-client'
import { socialApi, SocialAccount } from '@/lib/api/social'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'

export const dynamic = 'force-dynamic'

// Enhanced Interface for Rich Content
interface GeneratedContent {
  platform: string
  content: string
  images?: string[]
  hashtags?: string[]
  title?: string
  thread?: string[]
  description?: string
  script?: string
  plainText?: string  // For email plain text version
}

export default function ContentLab() {
  const router = useRouter()
  const [step, setStep] = useState<'upload' | 'generating' | 'results'>('upload')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadedImages, setUploadedImages] = useState<File[]>([])
  const [textInput, setTextInput] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [uploadId, setUploadId] = useState<number | null>(null)
  
  // Generation States
  const [generating, setGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([])
  const [selectedPlatform, setSelectedPlatform] = useState('linkedin')

  // Social Connection States
  const [connectedAccounts, setConnectedAccounts] = useState<SocialAccount[]>([])
  const [isPosting, setIsPosting] = useState(false)

  // Scheduling States
  const [date, setDate] = useState<Date>()
  const [isScheduling, setIsScheduling] = useState(false)

  // Image Processing States
  const [processedImages, setProcessedImages] = useState<{
    collage: { url: string; width: number; height: number } | null
    framed: Array<{ url: string; width: number; height: number }>
  }>({ collage: null, framed: [] })

  // --- 1. Load Connected Accounts on Mount ---
  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    try {
      const accounts = await socialApi.getAccounts()
      // Ensure it's always an array, no matter what the API returns
      if (Array.isArray(accounts)) {
        setConnectedAccounts(accounts)
      } else if (accounts && typeof accounts === 'object') {
        // In case API returns an object with data property
        setConnectedAccounts(Array.isArray((accounts as any).data) ? (accounts as any).data : [])
      } else {
        setConnectedAccounts([])
      }
    } catch (error) {
      // Silently fail - just means no accounts connected yet
      console.debug("No social accounts connected")
      setConnectedAccounts([]) // Always set to empty array on error
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const docs = acceptedFiles.filter(f => 
      f.type.includes('pdf') || 
      f.type.includes('document') || 
      f.type.includes('presentation') ||
      f.type.includes('text')
    )
    const images = acceptedFiles.filter(f => f.type.includes('image'))

    if (docs.length > 0) setUploadedFile(docs[0])
    if (images.length > 0) {
      setUploadedImages(prev => {
        const newImages = [...prev, ...images]
        if (newImages.length > 4) {
          toast.error('Maximum 4 images allowed')
          return newImages.slice(0, 4)
        }
        return newImages
      })
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    }
  })

  // Helper to convert object script to string if necessary
  const formatScript = (script: any): string => {
    if (!script) return '';
    if (typeof script === 'string') return script;
    
    let formatted = '';
    if (script.intro) formatted += `[INTRO]\n${script.intro}\n\n`;
    if (script.story_problem) formatted += `[STORY & PROBLEM]\n${script.story_problem}\n\n`;
    if (script.main_content) formatted += `[MAIN CONTENT]\n${script.main_content}\n\n`;
    if (script.key_takeaways) formatted += `[TAKEAWAYS]\n${script.key_takeaways}\n\n`;
    if (script.cta) formatted += `[CTA]\n${script.cta}\n\n`;
    if (script.outro) formatted += `[OUTRO]\n${script.outro}`;
    
    if (!formatted) {
        return Object.entries(script)
            .map(([key, val]) => `[${key.toUpperCase().replace(/_/g, ' ')}]\n${val}`)
            .join('\n\n');
    }
    return formatted;
  }

  // --- Process Images Function with AI-Powered Design ---
  const processImages = async (contentText?: string) => {
    if (uploadedImages.length === 0) return

    try {
      const formData = new FormData()
      uploadedImages.forEach((img, idx) => {
        formData.append(`image_${idx + 1}`, img)
      })
      
      // Add content text for AI-powered design analysis
      if (contentText) {
        formData.append('content_text', contentText)
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/process-images/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })

      if (!response.ok) throw new Error('Image processing failed')
      const result = await response.json()
      
      setProcessedImages({
        collage: result.collage,
        framed: result.framed_images
      })
      
      toast.success('Images processed with AI-powered design!')
    } catch (error) {
      console.error('Image processing error:', error)
      toast.error('Failed to process images')
    }
  }

  // --- Poll Image Generation Function ---
  const pollImageGeneration = (taskId: string) => {
    let pollCount = 0
    const maxPolls = 40 // 2 minutes with 3 second intervals
    
    const pollInterval = setInterval(async () => {
      pollCount++
      
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/image-task/${taskId}/`, {
          credentials: 'include',
        })
        
        if (!response.ok) {
          clearInterval(pollInterval)
          return
        }
        
        const statusData = await response.json()
        
        if (statusData.status === 'completed') {
          clearInterval(pollInterval)
          
          if (statusData.result) {
            setProcessedImages({
              collage: statusData.result.collage || null,
              framed: statusData.result.framed_images?.map((img: any) => ({
                url: img.url,
                width: img.width || 0,
                height: img.height || 0
              })) || []
            })
            toast.success('AI images generated!', { duration: 3000 })
          }
        } else if (statusData.status === 'failed') {
          clearInterval(pollInterval)
          console.error('Image generation failed:', statusData.error)
          toast.error('Image generation failed', { duration: 3000 })
        } else if (pollCount >= maxPolls) {
          clearInterval(pollInterval)
          toast.warning('Image generation is taking longer than expected', { duration: 3000 })
        }
      } catch (error) {
        console.error('Image polling error:', error)
        // Don't show error toast for every polling failure
      }
    }, 3000) // Poll every 3 seconds
  }

  // --- Generate AI Images Function ---
  const generateAIImages = async (textContent: string) => {
    try {
      toast.info('Generating AI images... This may take a minute.')
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate-ai-images/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text_content: textContent,
          num_images: 4
        }),
        credentials: 'include',
      })

      if (!response.ok) throw new Error('AI image generation failed')
      const result = await response.json()
      
      // Poll for task completion
      if (result.task_id) {
        const pollInterval = setInterval(async () => {
          try {
            const statusResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/${result.task_id}/`, {
              credentials: 'include',
            })
            
            if (!statusResponse.ok) {
              clearInterval(pollInterval)
              return
            }
            
            const statusData = await statusResponse.json()
            
            if (statusData.status === 'completed') {
              clearInterval(pollInterval)
              
              if (statusData.result) {
                setProcessedImages({
                  collage: statusData.result.collage,
                  framed: statusData.result.framed_images.map((img: any) => ({
                    url: img.url,
                    width: 0,
                    height: 0
                  }))
                })
                toast.success('AI images generated successfully!')
              }
            } else if (statusData.status === 'failed') {
              clearInterval(pollInterval)
              toast.error('AI image generation failed')
            }
          } catch (error) {
            console.error('Polling error:', error)
          }
        }, 3000) // Poll every 3 seconds
        
        // Stop polling after 2 minutes
        setTimeout(() => clearInterval(pollInterval), 120000)
      }
      
    } catch (error) {
      console.error('AI image generation error:', error)
      toast.error('Failed to generate AI images')
    }
  }

  // --- 2. Handle Content Generation ---
  const handleUploadAndGenerate = async () => {
    if (!uploadedFile && !textInput && !urlInput) {
      toast.error('Please upload a file, enter text, or provide a URL')
      return
    }

    // Validate URL if provided
    if (urlInput) {
      try {
        new URL(urlInput)
      } catch {
        toast.error('Please enter a valid URL')
        return
      }
    }

    try {
      setGenerating(true)
      setStep('generating')

      // 1. Upload content
      let fileId: number
      if (urlInput) {
        // URL input - backend already supports this
        const formData = new FormData()
        formData.append('url', urlInput)
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/extract/`, {
          method: 'POST',
          body: formData,
          credentials: 'include',
        })
        
        if (!response.ok) throw new Error('URL extraction failed')
        const uploadResult = await response.json()
        fileId = uploadResult.id
      } else if (uploadedFile) {
        const uploadResult = await uploadContent(uploadedFile, (progress) => {
          console.log('Upload progress:', progress)
        })
        fileId = uploadResult.id
      } else {
        const textBlob = new Blob([textInput], { type: 'text/plain' })
        const textFile = new File([textBlob], 'input.txt', { type: 'text/plain' })
        const uploadResult = await uploadContent(textFile)
        fileId = uploadResult.id
      }

      setUploadId(fileId)

      // 1.5. Process images with AI-powered design if any (pass content for analysis)
      if (uploadedImages.length > 0) {
        const contentForDesign = textInput || urlInput || uploadedFile?.name || ''
        await processImages(contentForDesign)
      }

      // 2. Start Generation Task (automatically detect if AI images needed)
      const hasManualImages = uploadedImages.length > 0
      const shouldGenerateAIImages = !hasManualImages  // Only generate AI images if no manual images uploaded
      
      const result = await generateContent({
        uploaded_file_id: fileId,
        platforms: ['linkedin', 'twitter', 'youtube', 'blog', 'email'],
        trend_count: 5,
        has_images: hasManualImages,  // Tell backend we have manual images
        generate_images: shouldGenerateAIImages  // Auto-enable AI images only when no manual images
      })

      // 3. Start polling for image generation if task was started (only when AI images requested)
      if (result.image_task_id && shouldGenerateAIImages) {
        toast.info('Generating AI images in the background...', { duration: 3000 })
        pollImageGeneration(result.image_task_id)
      }

      // 4. Robust Polling Logic for Content with Progressive Updates
      if (result.task_id) {
        let pollCount = 0
        let errorCount = 0
        const maxPolls = 60 
        
        const pollInterval = setInterval(async () => {
          pollCount++
          try {
            const status = await checkTaskStatus(result.task_id!)
            
            // Process content on each poll to show progressive updates
            const content = status.result?.content || status.result?.content_json || {}
            const transformedContent: GeneratedContent[] = []
            
            // LinkedIn Mapping
            if (content.linkedin) {
              const text = content.linkedin.post_text || content.linkedin.text || content.linkedin.content || ''
              transformedContent.push({
                platform: 'linkedin',
                content: text,
                hashtags: content.linkedin.hashtags || [],
                ...content.linkedin
              })
            }

            // Twitter Mapping
            if (content.twitter_thread || content.x_thread) {
              const thread = content.twitter_thread || content.x_thread
              transformedContent.push({
                platform: 'twitter',
                content: Array.isArray(thread) ? thread.join('\n\n') : (thread || ''),
                thread: Array.isArray(thread) ? thread : [thread]
              })
            }

            // Blog Mapping
            if (content.long_blog) {
              transformedContent.push({
                platform: 'blog',
                content: content.long_blog.html_content || content.long_blog.html || '',
                title: content.long_blog.title || 'Untitled Blog Post'
              })
            }

            // YouTube Mapping
            if (content.youtube) {
               const scriptText = formatScript(content.youtube.script);
               transformedContent.push({
                platform: 'youtube',
                content: scriptText, 
                script: scriptText,
                description: content.youtube.description,
                title: content.youtube.title
              })
            }
            
            // Email Newsletter Mapping
            if (content.email_newsletter) {
              transformedContent.push({
                platform: 'email',
                content: content.email_newsletter.html_body || '',
                title: content.email_newsletter.subject || 'Newsletter',
                description: content.email_newsletter.preheader || '',
                plainText: content.email_newsletter.plain_text || ''
              })
            }
            
            // Update content state progressively
            if (transformedContent.length > 0) {
              setGeneratedContent(transformedContent)
            }
            
            if (status.status === 'completed') {
              clearInterval(pollInterval)
              setGenerating(false)
              setStep('results')
              
              // Check if there's an image task running in background
              if (result.image_task_id) {
                toast.success('Content generated! AI images are being generated in the background.', { duration: 4000 })
              } else {
                toast.success('Content generated successfully!')
              }
            } 
            else if (status.status === 'failed') {
              clearInterval(pollInterval)
              setGenerating(false)
              setStep('upload')
              
              // Show more helpful error message
              const errorMsg = status.error || 'Generation failed'
              if (errorMsg.includes('AI image') || errorMsg.includes('provider')) {
                toast.error('Content generated, but AI image generation failed. Upload manual images or check API credentials.', { duration: 6000 })
              } else {
                toast.error(errorMsg)
              }
            }
            else if (pollCount >= maxPolls) {
              clearInterval(pollInterval)
              setGenerating(false)
              setStep('upload')
              toast.error('Generation timed out.')
            }
          } catch (err) {
            errorCount++
            if (errorCount > 5) {
              clearInterval(pollInterval)
              setGenerating(false)
              setStep('upload')
              toast.error('Network connection lost')
            }
          }
        }, 2000)
      } else if (result.generated_content) {
        setGeneratedContent(result.generated_content)
        setStep('results')
      } else {
        toast.error('Failed to start generation task.')
        setGenerating(false)
        setStep('upload')
      }
    } catch (error: any) {
      console.error('Detailed Error:', error)
      toast.error(error.message || 'Failed to generate content')
      setGenerating(false)
      setStep('upload')
    }
  }

  // --- 3. Unified Auth & Post Handler ---
  const handleAuthOrPost = async (platform: string, content: string) => {
    // Determine if the user has an active connection for this platform
    const isConnected = Array.isArray(connectedAccounts) && connectedAccounts.some(
      acc => acc.platform === platform && acc.is_active
    )

    if (!isConnected) {
      // -- Path A: Not Connected -> Start OAuth --
      try {
        // Save pending platform to localStorage so callback page knows what to verify
        localStorage.setItem('oauth_pending_platform', platform)
        
        // Get the redirect URL from backend
        const { authorization_url } = await socialApi.getAuthUrl(platform)
        
        if (authorization_url) {
          window.location.href = authorization_url 
        } else {
          toast.error(`Could not initiate ${platform} connection`)
        }
      } catch (error) {
        console.error('Auth Init Error:', error)
        toast.error('Connection failed. Please try again.')
      }
      return
    }

    // -- Path B: Connected -> Post Content --
    try {
      setIsPosting(true)
      await socialApi.directPost(platform, content)
      toast.success(`Posted successfully to ${platform}!`)
    } catch (error: any) {
      console.error('Posting Error:', error)
      toast.error(error.response?.data?.error || 'Failed to post content')
    } finally {
      setIsPosting(false)
    }
  }

  // --- 4. Schedule Handler ---
  const handleSchedule = async (platform: string, content: string) => {
    if (!date) {
      toast.error("Please pick a date and time first")
      return
    }

    const account = Array.isArray(connectedAccounts) ? connectedAccounts.find(
      acc => acc.platform === platform && acc.is_active
    ) : null

    if (!account) {
      toast.error(`Please connect your ${platform} account first`)
      return
    }

    try {
      setIsScheduling(true)
      await socialApi.schedulePost(account.id, content, date)
      toast.success(`Scheduled for ${format(date, 'PPP p')}`)
      setDate(undefined) // Close popover/reset date
    } catch (error: any) {
      console.error("Scheduling Error:", error)
      toast.error("Failed to schedule post")
    } finally {
      setIsScheduling(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const downloadImage = async (url: string, filename: string) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
      toast.success('Download started!')
    } catch (error) {
      console.error('Download failed:', error)
      toast.error('Failed to download image')
    }
  }

  const resetForm = () => {
    setStep('upload')
    setUploadedFile(null)
    setUploadedImages([])
    setTextInput('')
    setGeneratedContent([])
    setUploadId(null)
  }

  // --- Render Components ---

  const LinkedInPreview = ({ item }: { item: GeneratedContent }) => (
    <div className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden max-w-2xl mx-auto shadow-sm">
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex gap-3">
        <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">
          You
        </div>
        <div>
          <div className="font-semibold text-sm">Your Name</div>
          <div className="text-xs text-slate-500">Industry Leader • 1h • <span className="inline-block transform rotate-90">🌐</span></div>
        </div>
      </div>
      <div className="p-4">
        <p className="whitespace-pre-wrap text-sm leading-relaxed font-sans">
          {item.content}
        </p>
        {item.hashtags && item.hashtags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {item.hashtags.map(tag => (
              <span key={tag} className="text-blue-600 dark:text-blue-400 text-sm font-medium hover:underline cursor-pointer">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )

  const TwitterPreview = ({ item }: { item: GeneratedContent }) => (
    <div className="max-w-xl mx-auto space-y-0">
      {(item.thread || [item.content]).map((tweet, i) => (
        <div key={i} className="relative pb-8 last:pb-0">
          {i < (item.thread?.length || 1) - 1 && (
            <div className="absolute top-12 left-6 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700" />
          )}
          <div className="flex gap-4">
            <div className="flex-shrink-0 relative z-10">
              <div className="w-12 h-12 bg-slate-200 dark:bg-slate-800 rounded-full border-4 border-white dark:border-slate-950" />
            </div>
            <div className="flex-1 pt-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-bold text-slate-900 dark:text-white">You</span>
                <span className="text-slate-500 text-sm">@handle · 1m</span>
              </div>
              <p className="text-slate-800 dark:text-slate-200 whitespace-pre-wrap text-[15px] leading-normal">
                {tweet}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  const YouTubePreview = ({ item }: { item: GeneratedContent }) => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <div className="aspect-video bg-slate-800 rounded-lg mb-3 flex items-center justify-center text-slate-600">
            <MonitorPlay className="w-10 h-10" />
          </div>
          <label className="text-xs uppercase text-slate-500 font-bold tracking-wider mb-1 block">Title</label>
          <h3 className="font-bold text-lg leading-tight mb-4 text-white">{item.title}</h3>
          
          <label className="text-xs uppercase text-slate-500 font-bold tracking-wider mb-1 block">Description</label>
          <p className="text-sm text-slate-400 whitespace-pre-wrap mb-4">{item.description}</p>
          
          <Button onClick={() => copyToClipboard(item.script || '')} variant="secondary" className="w-full">
            <Copy className="w-4 h-4 mr-2" /> Copy Script
          </Button>
        </div>
      </div>

      <div className="lg:col-span-2 bg-white/5 rounded-xl border border-white/10 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
          <h3 className="font-mono text-sm font-bold text-slate-300 flex items-center gap-2">
            <FileText className="w-4 h-4" /> TELEPROMPTER SCRIPT
          </h3>
        </div>
        <div className="flex-1 p-6 bg-slate-950 font-mono text-sm leading-relaxed text-slate-300">
          {(item.script || '').split(/(\[.*?\])/).map((part, i) => 
            part.startsWith('[') && part.endsWith(']') ? 
              <span key={i} className="text-yellow-500 font-bold block my-4">{part}</span> : 
              <span key={i}>{part}</span>
          )}
        </div>
      </div>
    </div>
  )

  const BlogPreview = ({ item }: { item: GeneratedContent }) => {
    const words = item.content.replace(/<[^>]*>/g, '').split(/\s+/).length
    const readTime = Math.ceil(words / 200)

    return (
      <div className="relative max-w-4xl mx-auto bg-white dark:bg-slate-950 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="sticky top-0 z-10 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 p-4 flex justify-between items-center">
           <div className="flex items-center gap-3 text-sm text-slate-500">
              <span className="bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 px-2 py-1 rounded-md font-medium text-xs">Blog Post</span>
              <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {readTime} min read</span>
           </div>
           <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.content)}>
                <FileCode className="w-4 h-4 mr-2" /> Copy HTML
              </Button>
              <Button variant="secondary" size="sm" onClick={() => copyToClipboard(item.content.replace(/<[^>]*>/g, ''))}>
                <Copy className="w-4 h-4 mr-2" /> Copy Text
              </Button>
           </div>
        </div>

        <div className="p-8 md:p-16">
          <div className="mb-10 border-b border-slate-100 dark:border-slate-800 pb-10">
            <h1 className="text-3xl md:text-5xl font-extrabold text-slate-900 dark:text-white leading-tight mb-6 tracking-tight">
              {item.title}
            </h1>
            <div className="flex items-center gap-4">
               <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                 AI
               </div>
               <div>
                 <p className="text-sm font-bold text-slate-900 dark:text-slate-100">TrendMaster AI</p>
                 <div className="flex items-center gap-2 text-xs text-slate-500">
                    <span>Published just now</span>
                    <span>•</span>
                    <span>Neural Generated</span>
                 </div>
               </div>
            </div>
          </div>

          <article className="prose prose-lg dark:prose-invert max-w-none 
            prose-headings:font-bold prose-headings:text-slate-900 dark:prose-headings:text-slate-100 prose-headings:leading-tight
            prose-p:text-slate-700 dark:prose-p:text-slate-300 prose-p:leading-relaxed prose-p:mb-6
            prose-li:text-slate-700 dark:prose-li:text-slate-300
            prose-strong:text-slate-900 dark:prose-strong:text-white prose-strong:font-bold
            prose-blockquote:border-l-4 prose-blockquote:border-indigo-500 prose-blockquote:pl-4 prose-blockquote:italic
            prose-img:rounded-xl prose-img:shadow-lg">
            <div dangerouslySetInnerHTML={{ __html: item.content }} />
          </article>
        </div>
      </div>
    )
  }

  const EmailPreview = ({ item }: { item: GeneratedContent }) => {
    return (
      <div className="relative max-w-4xl mx-auto space-y-4">
        {/* Email Header Info */}
        <div className="glass-panel p-6 rounded-xl border border-white/10">
          <div className="space-y-4">
            <div>
              <label className="text-xs uppercase text-slate-500 font-bold tracking-wider mb-2 block">Subject Line</label>
              <div className="flex items-center gap-2">
                <p className="flex-1 text-lg font-semibold text-white bg-white/5 p-3 rounded-lg">{item.title}</p>
                <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.title || '')}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
            {item.description && (
              <div>
                <label className="text-xs uppercase text-slate-500 font-bold tracking-wider mb-2 block">Preheader Text</label>
                <div className="flex items-center gap-2">
                  <p className="flex-1 text-sm text-slate-300 bg-white/5 p-3 rounded-lg">{item.description}</p>
                  <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.description || '')}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* HTML Preview */}
        <div className="glass-panel rounded-xl border border-white/10 overflow-hidden">
          <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
            <h3 className="font-mono text-sm font-bold text-slate-300 flex items-center gap-2">
              <Mail className="w-4 h-4" /> EMAIL PREVIEW
            </h3>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.content)}>
                <FileCode className="w-4 h-4 mr-2" /> Copy HTML
              </Button>
              {item.plainText && (
                <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.plainText || '')}>
                  <FileText className="w-4 h-4 mr-2" /> Copy Plain Text
                </Button>
              )}
            </div>
          </div>
          
          {/* Email Preview in Iframe */}
          <div className="bg-slate-100 dark:bg-slate-900 p-6">
            <div className="max-w-[600px] mx-auto bg-white shadow-xl rounded-lg overflow-hidden">
              <iframe
                srcDoc={item.content}
                className="w-full h-[600px] border-0"
                title="Email Preview"
                sandbox="allow-same-origin"
              />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-full">
      <AnimatePresence mode="wait">
        {step === 'upload' && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-6"
          >
            <div>
              <h1 className="text-3xl font-bold mb-2">Content Lab</h1>
              <p className="text-gray-400">Upload your content and let AI generate platform-ready posts</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* File Upload Section */}
              <div className="glass-panel p-6 rounded-2xl flex flex-col">
                <h3 className="text-lg font-semibold mb-4">Upload Content</h3>
                <div
                  {...getRootProps()}
                  className={cn(
                    "h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all",
                    isDragActive ? "border-indigo-500 bg-indigo-500/10" : "border-gray-700 hover:border-gray-600"
                  )}
                >
                  <input {...getInputProps()} />
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <p className="text-gray-300 mb-2">Drag & drop or click to upload</p>
                  <p className="text-sm text-gray-500">PDF, DOCX, PPT, TXT + up to 4 images</p>
                </div>
                {uploadedFile && (
                  <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-green-400" />
                      <span className="text-sm text-green-400">{uploadedFile.name}</span>
                    </div>
                    <button onClick={() => setUploadedFile(null)}>
                      <X className="w-4 h-4 text-gray-400 hover:text-white" />
                    </button>
                  </div>
                )}
                
                {/* Uploaded Images Display */}
                {uploadedImages.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-400">Uploaded Images ({uploadedImages.length}/4)</p>
                      <span className="text-xs px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded-full flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        AI Design
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {uploadedImages.map((img, idx) => (
                        <div key={idx} className="relative group">
                          <div className="aspect-video bg-slate-800 rounded-lg overflow-hidden border border-white/10">
                            <img 
                              src={URL.createObjectURL(img)} 
                              alt={`Upload ${idx + 1}`}
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <button
                            onClick={() => setUploadedImages(prev => prev.filter((_, i) => i !== idx))}
                            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="w-4 h-4 text-white" />
                          </button>
                          <p className="text-xs text-gray-500 mt-1 truncate">{img.name}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Text Input Section */}
              <div className="glass-panel p-6 rounded-2xl flex flex-col">
                <h3 className="text-lg font-semibold mb-4">Or Paste Text</h3>
                <Textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste your content here..."
                  className="h-64 bg-black/20 border-gray-700 resize-none"
                />
              </div>
            </div>

            {/* URL Input Section - New */}
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="text-lg font-semibold mb-4">Or Enter Website URL</h3>
              <div className="flex gap-3">
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com/article"
                  className="flex-1 h-12 px-4 bg-black/20 border border-gray-700 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none text-white placeholder-gray-500"
                />
                {urlInput && (
                  <button 
                    onClick={() => setUrlInput('')}
                    className="px-4 h-12 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 hover:bg-red-500/20 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">AI will automatically scan and extract content from the webpage</p>
            </div>

            <Button
              onClick={handleUploadAndGenerate}
              disabled={(!uploadedFile && !textInput && !urlInput) || generating}
              className="w-full h-14 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-lg font-semibold"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Generate Content for All Platforms
            </Button>
          </motion.div>
        )}

        {step === 'generating' && (
          <motion.div
            key="generating"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-6"
          >
            <div className="flex items-center justify-between shrink-0">
              <div>
                <h1 className="text-2xl font-bold mb-1 flex items-center gap-3">
                  <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
                  Generating Content...
                </h1>
                <p className="text-gray-400 text-sm">Content will appear below as it's generated</p>
              </div>
            </div>

            <Tabs value={selectedPlatform} onValueChange={setSelectedPlatform} className="flex-1 flex flex-col">
              <TabsList className="grid grid-cols-6 bg-black/20 w-full max-w-4xl mx-auto shrink-0">
                <TabsTrigger value="linkedin"><Linkedin className="w-4 h-4 mr-2" /> LinkedIn</TabsTrigger>
                <TabsTrigger value="twitter"><Twitter className="w-4 h-4 mr-2" /> Twitter</TabsTrigger>
                <TabsTrigger value="youtube"><Youtube className="w-4 h-4 mr-2" /> YouTube</TabsTrigger>
                <TabsTrigger value="blog"><FileCode className="w-4 h-4 mr-2" /> Blog</TabsTrigger>
                <TabsTrigger value="email"><Mail className="w-4 h-4 mr-2" /> Email</TabsTrigger>
                <TabsTrigger value="images" disabled={!processedImages.collage && processedImages.framed.length === 0}><ImageIcon className="w-4 h-4 mr-2" /> Images</TabsTrigger>
              </TabsList>

              <div className="mt-6">
                {/* LinkedIn Content */}
                <TabsContent value="linkedin">
                  {generatedContent.find(c => c.platform === 'linkedin') ? (
                    <div className="space-y-4">
                      <LinkedInPreview item={generatedContent.find(c => c.platform === 'linkedin')!} />
                      <div className="flex justify-center gap-4 max-w-2xl mx-auto">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'linkedin')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Text
                        </Button>
                        
                        {/* SCHEDULE / POST ACTIONS */}
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="gap-2">
                              <CalendarIcon className="w-4 h-4" />
                              {date ? format(date, 'MMM d, HH:mm') : 'Schedule'}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="end">
                            <div className="p-4 bg-slate-950 border border-white/10 rounded-lg">
                              <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                initialFocus
                                className="rounded-md border border-white/10"
                              />
                              <div className="p-3 border-t border-white/10 mt-3">
                                <label className="text-xs text-gray-400 block mb-2">Time (24h)</label>
                                <input 
                                  type="time" 
                                  className="w-full bg-black/20 border border-white/10 rounded p-2 text-sm text-white"
                                  onChange={(e) => {
                                    if (date && e.target.value) {
                                      const [h, m] = e.target.value.split(':')
                                      const newDate = new Date(date)
                                      newDate.setHours(parseInt(h))
                                      newDate.setMinutes(parseInt(m))
                                      setDate(newDate)
                                    }
                                  }}
                                />
                                <Button 
                                  size="sm" 
                                  className="w-full mt-4 bg-indigo-600"
                                  onClick={() => handleSchedule('linkedin', generatedContent.find(c => c.platform === 'linkedin')?.content || '')}
                                  disabled={isScheduling || !date}
                                >
                                  {isScheduling ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Confirm Schedule'}
                                </Button>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>

                        <Button 
                          onClick={() => handleAuthOrPost('linkedin', generatedContent.find(c => c.platform === 'linkedin')?.content || '')} 
                          className="bg-[#0077b5] hover:bg-[#00669c]"
                          disabled={isPosting}
                        >
                          {isPosting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                          {Array.isArray(connectedAccounts) && connectedAccounts.some(a => a.platform === 'linkedin' && a.is_active) ? 'Post Now' : 'Connect & Post'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating LinkedIn post...</p>
                    </div>
                  )}
                </TabsContent>

                {/* Twitter Content */}
                <TabsContent value="twitter">
                  {generatedContent.find(c => c.platform === 'twitter') ? (
                    <div className="space-y-6 max-w-xl mx-auto pb-10">
                      <TwitterPreview item={generatedContent.find(c => c.platform === 'twitter')!} />
                      <div className="flex justify-center gap-4">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'twitter')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Thread
                        </Button>

                        {/* SCHEDULE / POST ACTIONS */}
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="gap-2">
                              <CalendarIcon className="w-4 h-4" />
                              {date ? format(date, 'MMM d, HH:mm') : 'Schedule'}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="end">
                            <div className="p-4 bg-slate-950 border border-white/10 rounded-lg">
                              <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                initialFocus
                                className="rounded-md border border-white/10"
                              />
                              <div className="p-3 border-t border-white/10 mt-3">
                                <label className="text-xs text-gray-400 block mb-2">Time (24h)</label>
                                <input 
                                  type="time" 
                                  className="w-full bg-black/20 border border-white/10 rounded p-2 text-sm text-white"
                                  onChange={(e) => {
                                    if (date && e.target.value) {
                                      const [h, m] = e.target.value.split(':')
                                      const newDate = new Date(date)
                                      newDate.setHours(parseInt(h))
                                      newDate.setMinutes(parseInt(m))
                                      setDate(newDate)
                                    }
                                  }}
                                />
                                <Button 
                                  size="sm" 
                                  className="w-full mt-4 bg-indigo-600"
                                  onClick={() => handleSchedule('twitter', generatedContent.find(c => c.platform === 'twitter')?.content || '')}
                                  disabled={isScheduling || !date}
                                >
                                  {isScheduling ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Confirm Schedule'}
                                </Button>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>

                        <Button 
                          onClick={() => handleAuthOrPost('twitter', generatedContent.find(c => c.platform === 'twitter')?.content || '')} 
                          className="bg-sky-500 hover:bg-sky-600 text-white"
                          disabled={isPosting}
                        >
                          {isPosting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                          {Array.isArray(connectedAccounts) && connectedAccounts.some(a => a.platform === 'twitter' && a.is_active) ? 'Tweet Thread' : 'Connect & Tweet'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating Twitter thread...</p>
                    </div>
                  )}
                </TabsContent>

                {/* YouTube Content */}
                <TabsContent value="youtube">
                  {generatedContent.find(c => c.platform === 'youtube') ? (
                    <div className="space-y-6">
                      <YouTubePreview item={generatedContent.find(c => c.platform === 'youtube')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => {
                            const item = generatedContent.find(c => c.platform === 'youtube')
                            if (item) {
                              const fullText = `${item.title}\n\n${item.description}\n\n---SCRIPT---\n${item.script}`
                              copyToClipboard(fullText)
                            }
                          }}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy All
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating YouTube script...</p>
                    </div>
                  )}
                </TabsContent>

                {/* Blog Content */}
                <TabsContent value="blog">
                  {generatedContent.find(c => c.platform === 'blog') ? (
                    <div className="space-y-6">
                      <BlogPreview item={generatedContent.find(c => c.platform === 'blog')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'blog')?.content.replace(/<[^>]*>/g, '') || '')}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy as Text
                        </Button>
                        <Button 
                          variant="secondary" 
                          onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'blog')?.content || '')}
                        >
                          <FileCode className="w-4 h-4 mr-2" /> Copy as HTML
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating blog article...</p>
                    </div>
                  )}
                </TabsContent>

                {/* Email Newsletter Content */}
                <TabsContent value="email">
                  {generatedContent.find(c => c.platform === 'email') ? (
                    <div className="space-y-6">
                      <EmailPreview item={generatedContent.find(c => c.platform === 'email')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => {
                            const item = generatedContent.find(c => c.platform === 'email')
                            if (item) {
                              const fullText = `Subject: ${item.title}\n\nPreheader: ${item.description}\n\n${item.plainText || item.content.replace(/<[^>]*>/g, '')}`
                              copyToClipboard(fullText)
                            }
                          }}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy All
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating email newsletter...</p>
                    </div>
                  )}
                </TabsContent>

                {/* Images Content */}
                <TabsContent value="images">
                  {processedImages.collage ? (
                    <div className="space-y-6 max-w-6xl mx-auto">
                      {/* Collage Display */}
                      <div className="glass-panel p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                          <ImageIcon className="w-5 h-5 text-indigo-400" />
                          Professional Collage
                        </h3>
                        <div className="bg-slate-900 rounded-lg p-4 flex justify-center">
                          <img 
                            src={processedImages.collage.url} 
                            alt="Image Collage"
                            className="max-w-full h-auto rounded-lg shadow-xl border border-white/10"
                          />
                        </div>
                        <div className="mt-4 flex justify-center gap-3">
                          <Button 
                            variant="secondary" 
                            onClick={() => downloadImage(processedImages.collage!.url, 'collage.png')}
                          >
                            <Copy className="w-4 h-4 mr-2" /> Download Collage
                          </Button>
                        </div>
                      </div>

                      {/* Framed Images Display */}
                      {processedImages.framed.length > 0 && (
                        <div className="glass-panel p-6 rounded-2xl border border-white/10">
                          <h3 className="text-lg font-semibold mb-4">Framed Images ({processedImages.framed.length})</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {processedImages.framed.map((img, idx) => (
                              <div key={idx} className="space-y-3">
                                <div className="bg-slate-900 rounded-lg p-4 flex justify-center">
                                  <img 
                                    src={img.url} 
                                    alt={`Framed ${idx + 1}`}
                                    className="max-w-full h-auto rounded-lg shadow-lg border border-white/10"
                                  />
                                </div>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="w-full"
                                  onClick={() => downloadImage(img.url, `framed-${idx + 1}.png`)}
                                >
                                  <Copy className="w-4 h-4 mr-2" /> Download Image {idx + 1}
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
                      <Loader2 className="w-12 h-12 mb-4 opacity-40 animate-spin text-indigo-500" />
                      <p>Generating images...</p>
                    </div>
                  )}
                </TabsContent>
              </div>
            </Tabs>
          </motion.div>
        )}

        {step === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col gap-6"
          >
            <div className="flex items-center justify-between shrink-0">
              <div>
                <h1 className="text-2xl font-bold mb-1">Generated Assets</h1>
                <p className="text-gray-400 text-sm">Ready to publish</p>
              </div>
              <Button onClick={resetForm} variant="outline">Create New</Button>
            </div>

            <Tabs value={selectedPlatform} onValueChange={setSelectedPlatform} className="flex-1 flex flex-col">
              <TabsList className="grid grid-cols-6 bg-black/20 w-full max-w-4xl mx-auto shrink-0">
                <TabsTrigger value="linkedin"><Linkedin className="w-4 h-4 mr-2" /> LinkedIn</TabsTrigger>
                <TabsTrigger value="twitter"><Twitter className="w-4 h-4 mr-2" /> Twitter</TabsTrigger>
                <TabsTrigger value="youtube"><Youtube className="w-4 h-4 mr-2" /> YouTube</TabsTrigger>
                <TabsTrigger value="blog"><FileCode className="w-4 h-4 mr-2" /> Blog</TabsTrigger>
                <TabsTrigger value="email"><Mail className="w-4 h-4 mr-2" /> Email</TabsTrigger>
                <TabsTrigger value="images" disabled={!processedImages.collage && processedImages.framed.length === 0}><ImageIcon className="w-4 h-4 mr-2" /> Images</TabsTrigger>
              </TabsList>

              <div className="mt-6">
                {/* LinkedIn Content */}
                <TabsContent value="linkedin">
                  {generatedContent.find(c => c.platform === 'linkedin') ? (
                    <div className="space-y-4">
                      <LinkedInPreview item={generatedContent.find(c => c.platform === 'linkedin')!} />
                      <div className="flex justify-center gap-4 max-w-2xl mx-auto">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'linkedin')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Text
                        </Button>
                        
                        {/* SCHEDULE / POST ACTIONS */}
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="gap-2">
                              <CalendarIcon className="w-4 h-4" />
                              {date ? format(date, 'MMM d, HH:mm') : 'Schedule'}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="end">
                            <div className="p-4 bg-slate-950 border border-white/10 rounded-lg">
                              <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                initialFocus
                                className="rounded-md border border-white/10"
                              />
                              <div className="p-3 border-t border-white/10 mt-3">
                                <label className="text-xs text-gray-400 block mb-2">Time (24h)</label>
                                <input 
                                  type="time" 
                                  className="w-full bg-black/20 border border-white/10 rounded p-2 text-sm text-white"
                                  onChange={(e) => {
                                    if (date && e.target.value) {
                                      const [h, m] = e.target.value.split(':')
                                      const newDate = new Date(date)
                                      newDate.setHours(parseInt(h))
                                      newDate.setMinutes(parseInt(m))
                                      setDate(newDate)
                                    }
                                  }}
                                />
                                <Button 
                                  size="sm" 
                                  className="w-full mt-4 bg-indigo-600"
                                  onClick={() => handleSchedule('linkedin', generatedContent.find(c => c.platform === 'linkedin')?.content || '')}
                                  disabled={isScheduling || !date}
                                >
                                  {isScheduling ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Confirm Schedule'}
                                </Button>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>

                        <Button 
                          onClick={() => handleAuthOrPost('linkedin', generatedContent.find(c => c.platform === 'linkedin')?.content || '')} 
                          className="bg-[#0077b5] hover:bg-[#00669c]"
                          disabled={isPosting}
                        >
                          {isPosting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                          {Array.isArray(connectedAccounts) && connectedAccounts.some(a => a.platform === 'linkedin' && a.is_active) ? 'Post Now' : 'Connect & Post'}
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* Twitter Content */}
                <TabsContent value="twitter">
                  {generatedContent.find(c => c.platform === 'twitter') ? (
                    <div className="space-y-6 max-w-xl mx-auto pb-10">
                      <TwitterPreview item={generatedContent.find(c => c.platform === 'twitter')!} />
                      <div className="flex justify-center gap-4">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'twitter')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Thread
                        </Button>

                        {/* SCHEDULE / POST ACTIONS */}
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button variant="outline" className="gap-2">
                              <CalendarIcon className="w-4 h-4" />
                              {date ? format(date, 'MMM d, HH:mm') : 'Schedule'}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0" align="end">
                            <div className="p-4 bg-slate-950 border border-white/10 rounded-lg">
                              <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                initialFocus
                                className="rounded-md border border-white/10"
                              />
                              <div className="p-3 border-t border-white/10 mt-3">
                                <label className="text-xs text-gray-400 block mb-2">Time (24h)</label>
                                <input 
                                  type="time" 
                                  className="w-full bg-black/20 border border-white/10 rounded p-2 text-sm text-white"
                                  onChange={(e) => {
                                    if (date && e.target.value) {
                                      const [h, m] = e.target.value.split(':')
                                      const newDate = new Date(date)
                                      newDate.setHours(parseInt(h))
                                      newDate.setMinutes(parseInt(m))
                                      setDate(newDate)
                                    }
                                  }}
                                />
                                <Button 
                                  size="sm" 
                                  className="w-full mt-4 bg-indigo-600"
                                  onClick={() => handleSchedule('twitter', generatedContent.find(c => c.platform === 'twitter')?.content || '')}
                                  disabled={isScheduling || !date}
                                >
                                  {isScheduling ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Confirm Schedule'}
                                </Button>
                              </div>
                            </div>
                          </PopoverContent>
                        </Popover>

                        <Button 
                          onClick={() => handleAuthOrPost('twitter', generatedContent.find(c => c.platform === 'twitter')?.content || '')} 
                          className="bg-sky-500 hover:bg-sky-600 text-white"
                          disabled={isPosting}
                        >
                          {isPosting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                          {Array.isArray(connectedAccounts) && connectedAccounts.some(a => a.platform === 'twitter' && a.is_active) ? 'Tweet Thread' : 'Connect & Tweet'}
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* YouTube Content */}
                <TabsContent value="youtube">
                  {generatedContent.find(c => c.platform === 'youtube') ? (
                    <div className="space-y-6">
                      <YouTubePreview item={generatedContent.find(c => c.platform === 'youtube')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => {
                            const item = generatedContent.find(c => c.platform === 'youtube')
                            if (item) {
                              const fullText = `${item.title}\n\n${item.description}\n\n---SCRIPT---\n${item.script}`
                              copyToClipboard(fullText)
                            }
                          }}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy All
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* Blog Content */}
                <TabsContent value="blog">
                  {generatedContent.find(c => c.platform === 'blog') ? (
                    <div className="space-y-6">
                      <BlogPreview item={generatedContent.find(c => c.platform === 'blog')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'blog')?.content.replace(/<[^>]*>/g, '') || '')}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy as Text
                        </Button>
                        <Button 
                          variant="secondary" 
                          onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'blog')?.content || '')}
                        >
                          <FileCode className="w-4 h-4 mr-2" /> Copy as HTML
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* Email Newsletter Content */}
                <TabsContent value="email">
                  {generatedContent.find(c => c.platform === 'email') ? (
                    <div className="space-y-6">
                      <EmailPreview item={generatedContent.find(c => c.platform === 'email')!} />
                      <div className="flex justify-center gap-4 max-w-4xl mx-auto">
                        <Button 
                          variant="secondary" 
                          onClick={() => {
                            const item = generatedContent.find(c => c.platform === 'email')
                            if (item) {
                              const fullText = `Subject: ${item.title}\n\nPreheader: ${item.description}\n\n${item.plainText || item.content.replace(/<[^>]*>/g, '')}`
                              copyToClipboard(fullText)
                            }
                          }}
                        >
                          <Copy className="w-4 h-4 mr-2" /> Copy All
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* Images Content */}
                <TabsContent value="images">
                  {processedImages.collage ? (
                    <div className="space-y-6 max-w-6xl mx-auto">
                      {/* Collage Display */}
                      <div className="glass-panel p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                          <ImageIcon className="w-5 h-5 text-indigo-400" />
                          Professional Collage
                        </h3>
                        <div className="bg-slate-900 rounded-lg p-4 flex justify-center">
                          <img 
                            src={processedImages.collage.url} 
                            alt="Image Collage"
                            className="max-w-full h-auto rounded-lg shadow-xl border border-white/10"
                          />
                        </div>
                        <div className="mt-4 flex justify-center gap-3">
                          <Button 
                            variant="secondary" 
                            onClick={() => {
                              const link = document.createElement('a')
                              link.href = processedImages.collage!.url
                              link.download = 'collage.jpg'
                              link.click()
                            }}
                          >
                            <Copy className="w-4 h-4 mr-2" /> Download Collage
                          </Button>
                        </div>
                      </div>

                      {/* Framed Images Display */}
                      {processedImages.framed.length > 0 && (
                        <div className="glass-panel p-6 rounded-2xl border border-white/10">
                          <h3 className="text-lg font-semibold mb-4">Framed Images ({processedImages.framed.length})</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {processedImages.framed.map((img, idx) => (
                              <div key={idx} className="space-y-3">
                                <div className="bg-slate-900 rounded-lg p-4 flex justify-center">
                                  <img 
                                    src={img.url} 
                                    alt={`Framed ${idx + 1}`}
                                    className="max-w-full h-auto rounded-lg shadow-lg border border-white/10"
                                  />
                                </div>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="w-full"
                                  onClick={() => {
                                    const link = document.createElement('a')
                                    link.href = img.url
                                    link.download = `framed-${idx + 1}.jpg`
                                    link.click()
                                  }}
                                >
                                  <Copy className="w-4 h-4 mr-2" /> Download Image {idx + 1}
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : <EmptyState />}
                </TabsContent>
              </div>
            </Tabs>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center text-gray-500 p-12 border border-dashed border-white/10 rounded-xl">
      <AlertCircle className="w-12 h-12 mb-4 opacity-20" />
      <p>No content generated for this platform</p>
    </div>
  )
}
