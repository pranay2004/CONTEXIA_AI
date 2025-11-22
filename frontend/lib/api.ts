import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { getSession } from 'next-auth/react'
import { handleApiError, retryRequest } from './auth'
import { toast } from 'sonner'
import { log } from './logger'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// Create axios instance with better defaults
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
  validateStatus: (status) => status < 500, // Don't throw on 4xx errors
})

// Request interceptor - add auth token and logging
api.interceptors.request.use(
  async (config) => {
    try {
      const session = await getSession()
      if (session?.accessToken) {
        config.headers.Authorization = `Bearer ${session.accessToken}`
      }
      
      log.debug('API Request', {
        method: config.method?.toUpperCase(),
        url: config.url,
        hasAuth: !!session?.accessToken,
      })
      
      return config
    } catch (error) {
      log.error('Request interceptor error', error as Error)
      return Promise.reject(error)
    }
  },
  (error) => {
    log.error('Request configuration error', error)
    return Promise.reject(error)
  }
)

// Response interceptor with comprehensive error handling
api.interceptors.response.use(
  (response) => {
    log.debug('API Response', {
      status: response.status,
      url: response.config.url,
    })
    return response
  },
  async (error: AxiosError) => {
    const errorMessage = handleApiError(error)
    
    // Log error with context
    log.error('API Error', error, {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: errorMessage,
    })
    
    // Don't show toast for 404s on optional resources
    if (error.response?.status !== 404) {
      // Only show toast for critical errors
      if (error.response?.status && error.response.status >= 500) {
        toast.error('Server error. Please try again later.')
      }
    }
    
    return Promise.reject(error)
  }
)

// Helper function for API calls with automatic retry
async function apiCall<T>(
  request: () => Promise<T>,
  fallbackData?: T
): Promise<T> {
  try {
    return await retryRequest(request, 2) // Retry twice
  } catch (error) {
    if (fallbackData !== undefined) {
      return fallbackData
    }
    throw error
  }
}

// API functions with error handling and logging
export const uploadContent = async (formData: FormData, onProgress?: (progress: number) => void) => {
  try {
    log.info('Starting content upload')
    const response = await api.post('/extract/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      },
    })
    log.info('Content uploaded successfully', { fileId: response.data.id })
    return response.data
  } catch (error) {
    log.error('Content upload failed', error as Error)
    throw error
  }
}

export const generateContent = async (data: {
  uploaded_file_id: number
  platforms?: string[]
  trend_count?: number
}) => {
  try {
    log.info('Starting content generation', { fileId: data.uploaded_file_id })
    const response = await api.post('/generate/', data)
    log.info('Content generation started', { jobId: response.data.id })
    return response.data
  } catch (error) {
    log.error('Content generation failed', error as Error)
    throw error
  }
}

export const getGeneratedContent = async (id: number) => {
  try {
    const response = await api.get(`/generated-content/${id}/`)
    return response.data
  } catch (error) {
    log.error('Failed to fetch generated content', error as Error, { id })
    throw error
  }
}

export const getTrends = async (params?: { source?: string; limit?: number }) => {
  try {
    const response = await api.get('/trends/', { params })
    log.debug('Trends fetched', { count: response.data?.length })
    return response.data
  } catch (error) {
    log.error('Failed to fetch trends', error as Error)
    throw error
  }
}

export const generateHooks = async (data: { topic: string; count?: number }) => {
  try {
    log.info('Generating hooks', { topic: data.topic })
    const response = await api.post('/generate-hooks/', data)
    return response.data
  } catch (error) {
    log.error('Failed to generate hooks', error as Error)
    throw error
  }
}

export const healthCheck = async () => {
  try {
    const response = await api.get('/health/')
    return response.data
  } catch (error) {
    log.warn('Health check failed', error as Error)
    throw error
  }
}

// User stats with automatic retry and fallback
export const getUserStats = async () => {
  return apiCall(
    async () => {
      log.debug('Fetching user stats')
      const response = await api.get('/stats/user/')
      return response.data
    },
    {
      total_uploads: 0,
      total_posts: 0,
      hours_saved: 0
    }
  )
}

// Recent activity with automatic retry and fallback
export const getRecentActivity = async () => {
  return apiCall(
    async () => {
      log.debug('Fetching recent activity')
      const response = await api.get('/activity/recent/')
      return response.data
    },
    []
  )
}

// Upload status
export const getUploadStatus = async (uploadId: string) => {
  try {
    const response = await api.get(`/upload/${uploadId}/status/`)
    return response.data
  } catch (error) {
    log.error('Failed to fetch upload status', error as Error, { uploadId })
    throw error
  }
}

// Generation status
export const getGenerationStatus = async (taskId: string) => {
  try {
    const response = await api.get(`/generate/${taskId}/status/`)
    return response.data
  } catch (error) {
    log.error('Failed to fetch generation status', error as Error, { taskId })
    throw error
  }
}

// Get user's uploads
export const getUploads = async () => {
  try {
    log.debug('Fetching user uploads')
    const response = await api.get('/uploads/')
    return response.data
  } catch (error) {
    log.error('Failed to fetch uploads', error as Error)
    return []
  }
}

// Get user's posts
export const getPosts = async () => {
  try {
    log.debug('Fetching user posts')
    const response = await api.get('/posts/')
    return response.data
  } catch (error) {
    log.error('Failed to fetch posts', error as Error)
    return []
  }
}
