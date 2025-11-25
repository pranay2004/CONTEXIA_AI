'use client'

import { useRef, useEffect, useState } from 'react'
import { 
  motion, 
  useScroll, 
  useTransform, 
  useSpring, 
  useMotionValue, 
  useMotionTemplate 
} from 'framer-motion'
import { useRouter } from 'next/navigation'
import { 
  ArrowRight, 
  Sparkles, 
  Layers, 
  Globe, 
  Cpu, 
  BarChart3,
  Command
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Navbar } from '@/components/Navbar' // Import the Navbar

// --- Utility Components ---

function SpotlightCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect()
    mouseX.set(clientX - left)
    mouseY.set(clientY - top)
  }

  return (
    <div
      className={cn(
        "group relative border border-white/10 bg-gray-900/50 overflow-hidden rounded-xl",
        className
      )}
      onMouseMove={handleMouseMove}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              650px circle at ${mouseX}px ${mouseY}px,
              rgba(99, 102, 241, 0.15),
              transparent 80%
            )
          `,
        }}
      />
      <div className="relative h-full">{children}</div>
    </div>
  )
}

function ParallaxText({ children, baseVelocity = 100 }: { children: string; baseVelocity: number }) {
  const baseX = useMotionValue(0)
  const { scrollY } = useScroll()
  const scrollVelocity = useSpring(scrollY, { damping: 50, stiffness: 400 })
  const velocityFactor = useTransform(scrollVelocity, [0, 1000], [0, 5], { clamp: false })
  const x = useTransform(baseX, (v) => `${v}%`) 

  const directionFactor = useRef<number>(1)
  
  useEffect(() => {
    let lastTimestamp = 0
    const animate = (t: number) => {
      if (lastTimestamp !== 0) {
        const delta = t - lastTimestamp
        let moveBy = directionFactor.current * baseVelocity * (delta / 5000)
        
        if (velocityFactor.get() < 0) {
          directionFactor.current = -1
        } else if (velocityFactor.get() > 0) {
          directionFactor.current = 1
        }
        
        moveBy += directionFactor.current * moveBy * velocityFactor.get()
        
        // Infinite loop: wrap around at -100% or 0%
        let newX = baseX.get() + moveBy
        if (newX <= -100) {
          newX = 0
        } else if (newX >= 0) {
          newX = -100
        }
        baseX.set(newX)
      }
      lastTimestamp = t
      requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [baseVelocity, velocityFactor, baseX])

  return (
    <div className="overflow-hidden m-0 whitespace-nowrap flex flex-nowrap">
      <motion.div className="font-black text-6xl md:text-9xl uppercase tracking-tighter text-white/5 flex flex-nowrap" style={{ x }}>
        <span className="block mr-8">{children} </span>
        <span className="block mr-8">{children} </span>
        <span className="block mr-8">{children} </span>
        <span className="block mr-8">{children} </span>
        <span className="block mr-8">{children} </span>
        <span className="block mr-8">{children} </span>
      </motion.div>
    </div>
  )
}

// --- Main Page Component ---

export default function HomePage() {
  const router = useRouter()
  const { scrollYProgress } = useScroll()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  // Hero Animations
  const y = useTransform(scrollYProgress, [0, 0.5], [0, -50])
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.9])

  return (
    <div className="min-h-screen bg-[#030712] text-white selection:bg-indigo-500/30 selection:text-indigo-200 overflow-x-hidden font-sans">
      
      {/* Noise Texture Overlay */}
      <div className="fixed inset-0 z-50 pointer-events-none opacity-[0.03] mix-blend-overlay" 
           style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }} />

      {/* Navigation - Only render after mount to avoid hydration errors */}
      {mounted && <Navbar transparent />}

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center pt-32 pb-20 px-6">
        <motion.div 
          style={{ y, opacity, scale }}
          className="relative z-10 max-w-5xl mx-auto text-center"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-medium mb-8"
          >
            <Sparkles className="w-3 h-3" />
            <span>v2.0 Neural Engine Live</span>
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-6xl md:text-8xl font-black tracking-tighter mb-6 leading-[0.9]"
          >
            Turn Context <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 animate-gradient bg-300%">
              Into Culture.
            </span>
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            The first AI content engine that reads your documents, watches market trends, 
            and weaves them into viral social narratives.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button 
              size="lg" 
              onClick={() => router.push('/register')}
              className="h-14 px-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-lg shadow-xl shadow-indigo-900/20 transition-all hover:scale-105"
            >
              Start Creating
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              className="h-14 px-8 rounded-full border-white/10 hover:bg-white/5 text-lg"
            >
              View Demo
            </Button>
          </motion.div>
        </motion.div>
        
        {/* Hero Visual - The "Brain" */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
           <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-indigo-600/20 rounded-full blur-[120px] opacity-50 mix-blend-screen animate-pulse-slow" />
        </div>
      </section>

      {/* Scroll Velocity Text */}
      <section className="py-10 border-y border-white/5 bg-black/50 backdrop-blur-sm">
        <ParallaxText baseVelocity={-2}>TRENDS • CONTEXT • ANALYTICS • GROWTH •</ParallaxText>
        <ParallaxText baseVelocity={2}>AGENCY • ENTERPRISE • CREATOR • STARTUP •</ParallaxText>
      </section>

      {/* Interactive Dashboard Preview (Bento Grid) */}
      <section id="features" className="py-32 px-6 max-w-7xl mx-auto">
        <div className="mb-20">
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            The Operating System <br /> for <span className="text-indigo-400">Modern Creators</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-auto md:h-[800px]">
          {/* Feature 1: The Ingest Engine */}
          <SpotlightCard className="md:col-span-2 row-span-1 p-8 flex flex-col justify-between bg-gradient-to-br from-gray-900 to-black">
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-6">
                <Layers className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-2xl font-bold mb-2">Context Injection</h3>
              <p className="text-gray-400 max-w-md">
                Drag and drop PDFs, Whitepapers, or URLs. Our vector engine digests your brand voice instantly.
              </p>
            </div>
            {/* Abstract UI Mockup */}
            <div className="mt-8 w-full h-64 bg-gray-950 border border-white/10 rounded-lg overflow-hidden relative p-4">
              <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-2">
                 <div className="w-3 h-3 rounded-full bg-red-500/50" />
                 <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                 <div className="w-3 h-3 rounded-full bg-green-500/50" />
                 <div className="ml-4 h-4 w-40 bg-white/10 rounded-full" />
              </div>
              <div className="space-y-3">
                <motion.div 
                  initial={{ width: 0 }}
                  whileInView={{ width: "80%" }}
                  transition={{ duration: 1, delay: 0.2 }}
                  className="h-8 bg-indigo-500/20 rounded border border-indigo-500/30 flex items-center px-3"
                >
                  <span className="text-xs text-indigo-300">Parsing strategy.pdf...</span>
                </motion.div>
                <motion.div 
                  initial={{ width: 0 }}
                  whileInView={{ width: "60%" }}
                  transition={{ duration: 1, delay: 0.5 }}
                  className="h-8 bg-emerald-500/20 rounded border border-emerald-500/30 flex items-center px-3"
                >
                   <span className="text-xs text-emerald-300">Extracting key entities...</span>
                </motion.div>
              </div>
            </div>
          </SpotlightCard>

          {/* Feature 2: Trend Watcher */}
          <SpotlightCard className="p-8 bg-gray-900">
            <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-6">
              <Globe className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-2xl font-bold mb-2">Global Trend Watch</h3>
            <p className="text-gray-400 text-sm mb-8">
              We scan 50+ marketing sources 24/7. If it's trending, you'll know.
            </p>
            <div className="space-y-4">
               {[1, 2, 3].map((i) => (
                 <div key={i} className="flex items-center gap-3 p-3 rounded bg-white/5 border border-white/5">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    <div className="h-2 w-24 bg-white/20 rounded" />
                 </div>
               ))}
            </div>
          </SpotlightCard>

          {/* Feature 3: Generative AI */}
          <SpotlightCard className="p-8 bg-gray-900">
            <div className="w-12 h-12 rounded-lg bg-pink-500/20 flex items-center justify-center mb-6">
              <Cpu className="w-6 h-6 text-pink-400" />
            </div>
            <h3 className="text-2xl font-bold mb-2">GPT 4o Neural Core</h3>
            <p className="text-gray-400 text-sm">
              Uses OpenAI's gpt-4o to synthesize context + trends into gold.
            </p>
            <div className="mt-8 flex justify-center">
              <div className="w-32 h-32 relative">
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 border-2 border-dashed border-pink-500/30 rounded-full" 
                />
                <div className="absolute inset-4 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full blur-md opacity-50" />
              </div>
            </div>
          </SpotlightCard>

          {/* Feature 4: Analytics */}
          <SpotlightCard className="md:col-span-2 p-8 bg-gradient-to-br from-gray-900 to-gray-800">
            <div className="flex flex-col md:flex-row gap-8 items-start md:items-center h-full">
              <div className="flex-1">
                <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center mb-6">
                  <BarChart3 className="w-6 h-6 text-orange-400" />
                </div>
                <h3 className="text-2xl font-bold mb-2">Predictive Analytics</h3>
                <p className="text-gray-400">
                  Don't just post. Predict performance before you hit publish using our historical data models.
                </p>
              </div>
              <div className="flex-1 w-full h-full min-h-[200px] bg-black/30 rounded-lg border border-white/5 p-4 flex items-end gap-2">
                  {[40, 70, 45, 90, 60, 80, 50].map((h, i) => (
                    <motion.div 
                      key={i}
                      initial={{ height: 0 }}
                      whileInView={{ height: `${h}%` }}
                      transition={{ duration: 0.5, delay: i * 0.1 }}
                      className="flex-1 bg-orange-500/80 rounded-t-sm hover:bg-orange-400 transition-colors"
                    />
                  ))}
              </div>
            </div>
          </SpotlightCard>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-indigo-600/5" />
        <div className="max-w-4xl mx-auto text-center relative z-10 px-6">
          <h2 className="text-5xl md:text-7xl font-black mb-8 tracking-tighter">
            Ready to Weave?
          </h2>
          <p className="text-xl text-gray-400 mb-12">
            Join the new era of context-aware content creation.
          </p>
          <Button 
            onClick={() => router.push('/register')}
            size="lg"
            className="h-16 px-10 text-xl bg-white text-black hover:bg-gray-100 rounded-full font-bold shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)]"
          >
            Start Free Trial
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-[#020617]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
              <Command className="w-3 h-3 text-white" />
            </div>
            <span className="font-bold tracking-tight text-gray-300">CONTEXIA</span>
          </div>
          <div className="text-sm text-gray-500">
            © {new Date().getFullYear()} Contexia Inc. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}