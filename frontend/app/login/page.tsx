'use client'

import { useState, useEffect, Suspense } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

export const dynamic = 'force-dynamic'
import { Loader2, Sparkles, ArrowLeft, Eye, EyeOff, Lock, User, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'
import { motion, AnimatePresence } from 'framer-motion'

function LoginPageInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState({ username: '', password: '' })
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Check for redirect message
    const message = searchParams?.get('message')
    if (message === 'registered') {
      toast.success('Account created successfully! Please sign in.')
    } else if (message === 'session_expired') {
      toast.error('Your session has expired. Please sign in again.')
    }
  }, [searchParams])

  const validateForm = () => {
    const newErrors = { username: '', password: '' }
    let isValid = true

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
      isValid = false
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters'
      isValid = false
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
      isValid = false
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    setErrors({ username: '', password: '' })

    try {
      const callbackUrl = searchParams?.get('callbackUrl') || '/dashboard'
      
      const result = await signIn('credentials', {
        username: formData.username.trim(),
        password: formData.password,
        redirect: false,
      })

      if (result?.error || !result?.ok) {
        toast.error('Invalid username or password')
        setErrors({ username: '', password: 'Invalid credentials' })
        setLoading(false)
      } else {
        toast.success('Login successful!')
        // Immediate redirect without delay
        window.location.href = callbackUrl
      }
    } catch (error) {
      toast.error('Something went wrong. Please try again.')
      setLoading(false)
    }
  }

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, repeat: Infinity, repeatType: 'reverse' }}
          className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-purple-400/20 dark:from-blue-600/10 dark:to-purple-600/10 rounded-full blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.5, delay: 0.5, repeat: Infinity, repeatType: 'reverse' }}
          className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-cyan-400/20 to-blue-400/20 dark:from-cyan-600/10 dark:to-blue-600/10 rounded-full blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 2, delay: 1, repeat: Infinity, repeatType: 'reverse' }}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-purple-400/10 to-pink-400/10 dark:from-purple-600/5 dark:to-pink-600/5 rounded-full blur-3xl"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="mb-6 rounded-xl hover:bg-white/80 dark:hover:bg-slate-800/80 backdrop-blur-sm transition-all"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </motion.div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-slate-800/50 p-8"
        >
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-center mb-8"
          >
            <div className="flex justify-center mb-4">
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
                className="relative"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl blur-lg opacity-50 animate-pulse" />
                <div className="relative w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Sparkles className="w-8 h-8 text-white animate-pulse" />
                </div>
              </motion.div>
            </div>
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent mb-2"
            >
              Welcome Back
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="text-slate-600 dark:text-slate-400"
            >
              Sign in to continue to CONTEXIA
            </motion.p>
          </motion.div>

          {/* Form */}
          <motion.form
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            onSubmit={handleSubmit}
            className="space-y-5"
          >
            {/* Username Field */}
            <div className="mb-6">
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <User className="w-4 h-4" />
                Username
              </label>
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={(e) => {
                    setFormData({ ...formData, username: e.target.value })
                    if (errors.username) setErrors({ ...errors, username: '' })
                  }}
                  className={`h-12 pl-4 pr-4 bg-white/50 dark:bg-slate-800/50 border-2 transition-all ${
                    errors.username
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-slate-200 dark:border-slate-700 focus:border-blue-500'
                  } rounded-xl backdrop-blur-sm`}
                  disabled={loading}
                  autoComplete="username"
                />
                <AnimatePresence>
                  {errors.username && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="flex items-center gap-1 text-red-500 text-xs mt-1"
                    >
                      <AlertCircle className="w-3 h-3" />
                      {errors.username}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Password Field */}
            <div className="mb-6">
              <label className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <Lock className="w-4 h-4" />
                Password
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => {
                    setFormData({ ...formData, password: e.target.value })
                    if (errors.password) setErrors({ ...errors, password: '' })
                  }}
                  className={`h-12 pl-4 pr-12 bg-white/50 dark:bg-slate-800/50 border-2 transition-all ${
                    errors.password
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-slate-200 dark:border-slate-700 focus:border-blue-500'
                  } rounded-xl backdrop-blur-sm`}
                  disabled={loading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
                <AnimatePresence>
                  {errors.password && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="flex items-center gap-1 text-red-500 text-xs mt-1"
                    >
                      <AlertCircle className="w-3 h-3" />
                      {errors.password}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="flex justify-end">
              <Link
                href="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <motion.div
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
            >
              <Button
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <Lock className="mr-2 h-5 w-5" />
                    Sign In
                  </>
                )}
              </Button>
            </motion.div>
          </motion.form>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
            className="mt-8 text-center"
          >
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Don&apos;t have an account?{' '}
              <Link
                href="/register"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-semibold transition-colors"
              >
                Create one
              </Link>
            </p>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin" /></div>}>
      <LoginPageInner />
    </Suspense>
  )
}