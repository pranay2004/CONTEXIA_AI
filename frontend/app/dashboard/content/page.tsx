'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { 
  Upload, 
  FileText, 
  Image as ImageIcon,
  Sparkles, 
  Loader2,
  CheckCircle2,
  Copy,
  Send,
  Linkedin,
  Twitter,
  Youtube,
  FileCode,
  AlertCircle,
  X,
  MonitorPlay,
  Hash,
  Share2,
  Clock,
  Calendar
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { uploadContent, generateContent, checkTaskStatus, postDirectly } from '@/lib/api-client'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

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
}

export default function ContentLab() {
  const [step, setStep] = useState<'upload' | 'generating' | 'results'>('upload')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadedImages, setUploadedImages] = useState<File[]>([])
  const [textInput, setTextInput] = useState('')
  const [uploadId, setUploadId] = useState<number | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([])
  const [selectedPlatform, setSelectedPlatform] = useState('linkedin')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const docs = acceptedFiles.filter(f => 
      f.type.includes('pdf') || 
      f.type.includes('document') || 
      f.type.includes('presentation') ||
      f.type.includes('text')
    )
    const images = acceptedFiles.filter(f => f.type.includes('image'))

    if (docs.length > 0) setUploadedFile(docs[0])
    if (images.length > 0) setUploadedImages(prev => [...prev, ...images])
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

  const handleUploadAndGenerate = async () => {
    if (!uploadedFile && !textInput) {
      toast.error('Please upload a file or enter text')
      return
    }

    try {
      setGenerating(true)
      setStep('generating')

      let fileId: number
      if (uploadedFile) {
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

      const result = await generateContent({
        uploaded_file_id: fileId,
        platforms: ['linkedin', 'twitter', 'youtube', 'blog'],
        trend_count: 5
      })

      if (result.task_id) {
        let pollCount = 0
        let errorCount = 0
        const maxPolls = 60 
        
        const pollInterval = setInterval(async () => {
          pollCount++
          try {
            const status = await checkTaskStatus(result.task_id!)
            
            if (status.status === 'completed') {
              clearInterval(pollInterval)
              const content = status.result?.content || status.result?.content_json || {}
              
              const transformedContent: GeneratedContent[] = []
              
              if (content.linkedin) {
                const text = content.linkedin.post_text || content.linkedin.text || content.linkedin.content || ''
                transformedContent.push({
                  platform: 'linkedin',
                  content: text,
                  hashtags: content.linkedin.hashtags || [],
                  ...content.linkedin
                })
              }

              if (content.twitter_thread || content.x_thread) {
                const thread = content.twitter_thread || content.x_thread
                transformedContent.push({
                  platform: 'twitter',
                  content: Array.isArray(thread) ? thread.join('\n\n') : (thread || ''),
                  thread: Array.isArray(thread) ? thread : [thread]
                })
              }

              if (content.long_blog) {
                transformedContent.push({
                  platform: 'blog',
                  content: content.long_blog.html_content || content.long_blog.html || '',
                  title: content.long_blog.title || 'Untitled Blog Post'
                })
              }

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
              
              setGeneratedContent(transformedContent)
              setGenerating(false)
              setStep('results')
              toast.success('Content generated successfully!')
            } 
            else if (status.status === 'failed') {
              clearInterval(pollInterval)
              setGenerating(false)
              setStep('upload')
              toast.error(status.error || 'Generation failed')
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
        toast.error('Failed to start generation task. Check console.')
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

  const handlePostNow = async (platform: string, content: string) => {
    toast.info("Direct posting coming soon to this demo!")
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
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
          <p className="text-sm text-slate-400 whitespace-pre-wrap">{item.description}</p>
        </div>
        
        <Button onClick={() => copyToClipboard(item.description || '')} variant="secondary" className="w-full">
          <Copy className="w-4 h-4 mr-2" /> Copy Meta
        </Button>
      </div>

      <div className="lg:col-span-2 bg-white/5 rounded-xl border border-white/10 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
          <h3 className="font-mono text-sm font-bold text-slate-300 flex items-center gap-2">
            <FileText className="w-4 h-4" /> TELEPROMPTER SCRIPT
          </h3>
          <Button size="sm" variant="ghost" onClick={() => copyToClipboard(item.script || '')}>
            <Copy className="w-4 h-4 mr-2" /> Copy Script
          </Button>
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
              <Button size="sm" onClick={() => copyToClipboard(item.content.replace(/<[^>]*>/g, ''))}>
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
                  <p className="text-sm text-gray-500">PDF, DOCX, PPT, TXT</p>
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

            <Button
              onClick={handleUploadAndGenerate}
              disabled={(!uploadedFile && !textInput) || generating}
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="h-[50vh] flex items-center justify-center"
          >
            <div className="text-center">
              <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Generating Content...</h3>
              <p className="text-gray-400">Analyzing trends & drafting posts</p>
            </div>
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
              <TabsList className="grid grid-cols-4 bg-black/20 w-full max-w-2xl mx-auto shrink-0">
                <TabsTrigger value="linkedin"><Linkedin className="w-4 h-4 mr-2" /> LinkedIn</TabsTrigger>
                <TabsTrigger value="twitter"><Twitter className="w-4 h-4 mr-2" /> Twitter</TabsTrigger>
                <TabsTrigger value="youtube"><Youtube className="w-4 h-4 mr-2" /> YouTube</TabsTrigger>
                <TabsTrigger value="blog"><FileCode className="w-4 h-4 mr-2" /> Blog</TabsTrigger>
              </TabsList>

              <div className="mt-6">
                {/* LinkedIn */}
                <TabsContent value="linkedin">
                  {generatedContent.find(c => c.platform === 'linkedin') ? (
                    <div className="space-y-4">
                      <LinkedInPreview item={generatedContent.find(c => c.platform === 'linkedin')!} />
                      <div className="flex justify-center gap-4 max-w-2xl mx-auto">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'linkedin')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Text
                        </Button>
                        <Button onClick={() => handlePostNow('linkedin', '')} className="bg-[#0077b5] hover:bg-[#00669c]">
                          <Send className="w-4 h-4 mr-2" /> Post to LinkedIn
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* Twitter */}
                <TabsContent value="twitter">
                  {generatedContent.find(c => c.platform === 'twitter') ? (
                    <div className="space-y-6 max-w-xl mx-auto pb-10">
                      <TwitterPreview item={generatedContent.find(c => c.platform === 'twitter')!} />
                      <div className="flex justify-center gap-4">
                        <Button variant="secondary" onClick={() => copyToClipboard(generatedContent.find(c => c.platform === 'twitter')?.content || '')}>
                          <Copy className="w-4 h-4 mr-2" /> Copy Thread
                        </Button>
                        <Button onClick={() => handlePostNow('twitter', '')} className="bg-sky-500 hover:bg-sky-600 text-white">
                          <Send className="w-4 h-4 mr-2" /> Tweet Thread
                        </Button>
                      </div>
                    </div>
                  ) : <EmptyState />}
                </TabsContent>

                {/* YouTube */}
                <TabsContent value="youtube">
                  {generatedContent.find(c => c.platform === 'youtube') ? (
                    <YouTubePreview item={generatedContent.find(c => c.platform === 'youtube')!} />
                  ) : <EmptyState />}
                </TabsContent>

                {/* Blog */}
                <TabsContent value="blog">
                  {generatedContent.find(c => c.platform === 'blog') ? (
                    <BlogPreview item={generatedContent.find(c => c.platform === 'blog')!} />
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