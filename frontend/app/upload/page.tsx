'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  ArrowRight, 
  X,
  FileType
} from 'lucide-react'
import { useRouter } from 'next/navigation'
// Ensure these files now exist from Step 3
import { Button } from '@/components/ui/button' 
import { cn } from '@/lib/utils'
// Ensure you have this component from the previous turns
import { Navbar } from '@/components/Navbar' 

export default function UploadPage() {
  const router = useRouter()
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [file, setFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selected = acceptedFiles[0]
    if (selected) {
      setFile(selected)
      setUploading(true)
      let p = 0
      const interval = setInterval(() => {
        p += 5
        setProgress(p)
        if (p >= 100) {
          clearInterval(interval)
          setUploading(false)
        }
      }, 100)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  })

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Fixed Navbar Import */}
      <Navbar />

      <main className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
           <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-500/5 rounded-full blur-3xl" />
        </div>

        <div className="max-w-2xl w-full relative z-10">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Feed the Neural Weave</h1>
            <p className="text-gray-400">
              Upload your strategy docs, whitepapers, or brand guidelines. <br />
              We'll extract the context to power your content engine.
            </p>
          </div>

          <div className="glass-panel p-1 rounded-2xl overflow-hidden">
            {!file ? (
              <div 
                {...getRootProps()} 
                className={cn(
                  "h-80 rounded-xl border-2 border-dashed border-white/10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 bg-black/20 hover:bg-black/40 hover:border-indigo-500/30 group",
                  isDragActive && "border-indigo-500 bg-indigo-500/10"
                )}
              >
                <input {...getInputProps()} />
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <UploadCloud className={cn("w-10 h-10 text-gray-400 transition-colors", isDragActive ? "text-indigo-400" : "group-hover:text-indigo-400")} />
                </div>
                <p className="text-lg font-medium mb-2">
                  {isDragActive ? "Drop to inject..." : "Drag & drop source file"}
                </p>
                <p className="text-sm text-gray-500">PDF, DOCX, or TXT (Max 20MB)</p>
              </div>
            ) : (
              <div className="h-80 rounded-xl border border-white/10 bg-black/40 relative flex flex-col items-center justify-center">
                
                {uploading && (
                  <motion.div 
                    initial={{ top: 0 }}
                    animate={{ top: "100%" }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent shadow-[0_0_20px_rgba(99,102,241,0.5)] opacity-50 pointer-events-none"
                  />
                )}

                <div className="w-20 h-20 rounded-2xl bg-indigo-500/20 flex items-center justify-center mb-6 relative">
                   <FileText className="w-10 h-10 text-indigo-400" />
                   {!uploading && (
                      <div className="absolute -right-2 -bottom-2 bg-green-500 text-black rounded-full p-1">
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                   )}
                </div>

                <h3 className="text-xl font-bold mb-2">{file.name}</h3>
                
                {uploading ? (
                  <div className="w-64 space-y-2">
                     <div className="flex justify-between text-xs text-gray-400">
                        <span>Vectorizing...</span>
                        <span>{progress}%</span>
                     </div>
                     <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <motion.div 
                           className="h-full bg-indigo-500" 
                           initial={{ width: 0 }}
                           animate={{ width: `${progress}%` }}
                        />
                     </div>
                  </div>
                ) : (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col items-center gap-4"
                  >
                     <p className="text-green-400 text-sm">Context extracted successfully</p>
                     <div className="flex gap-3 mt-4">
                        <Button variant="outline" onClick={() => setFile(null)} className="border-white/10 hover:bg-white/5">
                           Upload Another
                        </Button>
                        <Button onClick={() => router.push('/dashboard/content')} className="bg-indigo-600 hover:bg-indigo-500 text-white">
                           Generate Content <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                     </div>
                  </motion.div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}