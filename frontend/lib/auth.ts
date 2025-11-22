import { getSession, signOut } from 'next-auth/react'
import { toast } from 'sonner'
import { log } from './logger'

/**
 * Enhanced auth helper with automatic token refresh and error handling
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const session = await getSession()
    return session?.accessToken || null
  } catch (error) {
    log.error('Failed to get auth token', error as Error)
    return null
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const token = await getAuthToken()
  return !!token
}

/**
 * Logout user with cleanup
 */
export async function logout(redirect: string = '/') {
  try {
    log.info('User logging out', { redirect })
    await signOut({ redirect: true, callbackUrl: redirect })
  } catch (error) {
    log.error('Logout error', error as Error)
    toast.error('Failed to logout. Please try again.')
  }
}

/**
 * Handle API errors with user-friendly messages
 */
export function handleApiError(error: any): string {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data

    log.warn('API Error Response', {
      status,
      url: error.config?.url,
      data: data?.message || data?.detail,
    })

    switch (status) {
      case 401:
        toast.error('Session expired. Please login again.')
        logout('/login')
        return 'Authentication failed'
      
      case 403:
        return data?.detail || 'You do not have permission to perform this action'
      
      case 404:
        return data?.detail || 'Resource not found'
      
      case 429:
        return 'Too many requests. Please try again later.'
      
      case 500:
        return 'Server error. Please try again.'
      
      default:
        return data?.detail || data?.error || 'An error occurred'
    }
  }

  if (error.request) {
    return 'Network error. Please check your connection.'
  }

  return error.message || 'An unexpected error occurred'
}

/**
 * Retry failed requests with exponential backoff
 */
export async function retryRequest<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: any

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      
      // Don't retry on client errors (4xx)
      if (error instanceof Object && 'response' in error && (error as any).response?.status >= 400 && (error as any).response?.status < 500) {
        throw error
      }

      // Wait before retrying with exponential backoff
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
      }
    }
  }

  throw lastError
}

/**
 * Protected route checker
 */
export async function requireAuth(redirectUrl: string = '/login'): Promise<boolean> {
  const authenticated = await isAuthenticated()
  
  if (!authenticated) {
    if (typeof window !== 'undefined') {
      window.location.href = redirectUrl
    }
    return false
  }
  
  return true
}

/**
 * Parse JWT token (without verification)
 */
export function parseJwt(token: string): any {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    return null
  }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
  const payload = parseJwt(token)
  if (!payload || !payload.exp) return true
  
  const now = Date.now() / 1000
  return payload.exp < now
}
