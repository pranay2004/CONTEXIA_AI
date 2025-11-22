'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Zap, User, Mail, Lock, Loader2, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'

export default function RegisterPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match")
      return
    }

    setIsLoading(true)

    try {
      // FIX: Ensure we don't double up on /api if the client base URL already has it
      // The apiClient base URL is http://localhost:8000, so we need '/api/auth/register/'
      // We strip any accidental double slashes just in case
      await apiClient.post('/api/auth/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      })

      toast.success('Account initialized successfully.')
      router.push('/login?message=registered')
    } catch (error: any) {
      console.error("Registration error:", error)
      const msg = error.response?.data?.detail || 
                  Object.values(error.response?.data || {}).flat().join(', ') || 
                  'Registration failed. Please try again.'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden p-4">
      {/* Background FX */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-purple-600/20 rounded-full blur-[120px] opacity-50 animate-pulse-slow" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md glass-panel p-8 rounded-2xl border border-white/10 shadow-2xl relative z-10"
      >
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Initialize Access</h1>
          <p className="text-gray-400 text-sm mt-2">Join the Neural Weave ecosystem.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-300 uppercase tracking-wide">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
              <Input 
                placeholder="alexchen" 
                className="pl-10 bg-black/20 border-white/10 h-11"
                value={formData.username}
                onChange={e => setFormData({...formData, username: e.target.value})}
                required
                autoComplete="name" 
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-300 uppercase tracking-wide">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-500" />
              <Input 
                type="email"
                placeholder="name@company.com" 
                className="pl-10 bg-black/20 border-white/10 h-11"
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-300 uppercase tracking-wide">Password</label>
              <Input 
                type="password"
                placeholder="••••••••" 
                className="bg-black/20 border-white/10 h-11"
                value={formData.password}
                onChange={e => setFormData({...formData, password: e.target.value})}
                required
                autoComplete="new-password"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-300 uppercase tracking-wide">Confirm</label>
              <Input 
                type="password"
                placeholder="••••••••" 
                className="bg-black/20 border-white/10 h-11"
                value={formData.confirmPassword}
                onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
                required
                autoComplete="new-password"
              />
            </div>
          </div>

          <Button 
            type="submit" 
            disabled={isLoading}
            className="w-full h-11 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold shadow-lg shadow-indigo-500/25 mt-4"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 pt-6 border-t border-white/5 text-center text-sm text-gray-400">
          Already have an account?{' '}
          <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
            Log in here
          </Link>
        </div>
      </motion.div>
    </div>
  )
}