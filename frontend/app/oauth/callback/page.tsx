'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { socialApi } from '@/lib/api/social'
import { Loader2, CheckCircle2, XCircle, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function OAuthCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('Verifying authentication...')

  useEffect(() => {
    // Prevent running twice in Strict Mode
    let mounted = true;

    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')

      if (error) {
        if (mounted) {
          setStatus('error')
          setMessage('Authorization was denied by the provider.')
        }
        return
      }

      if (!code || !state) {
        if (mounted) {
          setStatus('error')
          setMessage('Invalid callback parameters received.')
        }
        return
      }

      // Retrieve the platform we started with (stored in Content/Analytics page)
      const pendingPlatform = localStorage.getItem('oauth_pending_platform')

      if (!pendingPlatform) {
        if (mounted) {
          setStatus('error')
          setMessage('Session lost. Please try initiating the connection again.')
        }
        return
      }

      try {
        await socialApi.connectAccount(pendingPlatform, code, state)
        
        if (mounted) {
          setStatus('success')
          setMessage(`Successfully connected to ${pendingPlatform}!`)
          localStorage.removeItem('oauth_pending_platform')
          
          // Auto-redirect after 2 seconds
          setTimeout(() => {
            router.push('/dashboard/analytics')
          }, 2000)
        }
      } catch (err: any) {
        console.error("OAuth Error:", err)
        if (mounted) {
          setStatus('error')
          setMessage(err.response?.data?.error || 'Failed to complete connection.')
        }
      }
    }

    handleCallback()

    return () => { mounted = false }
  }, [searchParams, router])

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-[#020817] text-white p-4">
      {/* Background Effects */}
      <div className="fixed top-0 left-0 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      
      <div className="w-full max-w-md p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl text-center">
        
        {/* Loading State */}
        {status === 'loading' && (
          <div className="space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full" />
              <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mx-auto relative z-10" />
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-2">Connecting Account</h2>
              <p className="text-slate-400">{message}</p>
            </div>
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-emerald-500/20 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 ring-4 ring-emerald-500/10">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Connection Successful!</h2>
              <p className="text-slate-400 mb-6">{message}</p>
              <div className="flex items-center justify-center gap-2 text-sm text-indigo-400">
                <span>Redirecting to dashboard</span>
                <Loader2 className="w-3 h-3 animate-spin" />
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-red-500/20 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 ring-4 ring-red-500/10">
              <XCircle className="w-10 h-10" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Connection Failed</h2>
              <p className="text-red-200/80 bg-red-500/10 p-3 rounded-lg text-sm mb-6 border border-red-500/20">
                {message}
              </p>
              <Button 
                onClick={() => router.push('/dashboard/content')}
                className="w-full bg-white/10 hover:bg-white/20 text-white"
              >
                Return to Dashboard <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}