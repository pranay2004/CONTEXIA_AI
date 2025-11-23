/**
 * CONTEXIA API Client
 * Comprehensive API integration with Django backend
 */

import axios, { AxiosError, AxiosProgressEvent } from 'axios'
import { getSession } from 'next-auth/react'
import { toast } from 'sonner'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with optimized settings
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes (300 seconds) for long-running tasks
  maxRedirects: 5,
  withCredentials: true,
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const session = await getSession()
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<any>) => {
    const data: any = error.response?.data || {}
    
    console.error("API Request Failed:", {
      url: error.config?.url,
      status: error.response?.status,
      data: data
    })

    const status = error.response?.status
    // Only show toast for critical errors, not 500s on every request
    if (status === 401) {
      toast.error('Session expired. Please login again.')
    } else if (status === 403) {
      toast.error('Access denied')
    }
    // Remove the 500 error toast - let individual pages handle it
    
    return Promise.reject(error)
  }
)

// ==================== CONTENT UPLOAD & EXTRACTION ====================

export interface UploadResponse {
  id: number
  filename: string
  file_type: string
  extracted_text?: string
  status: string
  created_at: string
}

export const uploadContent = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UploadResponse>('/api/extract/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    },
  })

  return response.data
}

// ==================== CONTENT GENERATION ====================

export interface GenerateContentRequest {
  uploaded_file_id?: number
  platforms?: string[]
  trend_count?: number
  custom_context?: string
  tone?: string
  has_images?: boolean  // Indicates if manual images were uploaded
  generate_images?: boolean  // Explicitly request AI image generation
}

// Interface for the response from the generation API
export interface GenerateContentResponse {
  task_id?: string
  image_task_id?: string  // Task ID for background image generation
  status?: string
  message?: string
  generated_content?: any
}

export const generateContent = async (
  data: GenerateContentRequest
): Promise<GenerateContentResponse> => {
  // Use the synchronous task-starter endpoint
  const response = await apiClient.post<GenerateContentResponse>(
    '/api/generate/', 
    data
  )
  return response.data
}

export const checkTaskStatus = async (taskId: string) => {
  const response = await apiClient.get(`/api/jobs/${taskId}/`)
  return response.data
}

export const getGeneratedContent = async (contentId: number) => {
  const response = await apiClient.get(`/api/generated-content/${contentId}/`)
  return response.data
}

// ==================== VOICE ANALYSIS ====================

export interface VoiceAnalysisResponse {
  system_instruction: string
  tone_profile: {
    formality: string
    emotion: string
    vocabulary_level: string
  }
  writing_patterns: string[]
  sample_sentences: string[]
  voice_name?: string
  metrics?: Record<string, any>
  keywords?: string[]
}

export const uploadVoiceSample = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<VoiceAnalysisResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<VoiceAnalysisResponse>(
    '/api/analyze-my-voice-file/',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      },
    }
  )

  return response.data
}

export const analyzeVoiceUrl = async (url: string): Promise<VoiceAnalysisResponse> => {
  const response = await apiClient.post<VoiceAnalysisResponse>(
    '/api/analyze-my-voice-file/',
    { url }
  )
  return response.data
}

// ==================== TRENDS ====================

export interface TrendArticle {
  id: number
  title: string
  description: string
  url: string
  source: string
  trending_score: number
  published_date: string
  keywords: string[]
  category: string
}

export const getTrends = async (params?: {
  source?: string
  category?: string
  limit?: number
}): Promise<TrendArticle[]> => {
  const response = await apiClient.get<TrendArticle[]>('/api/trends/', { params })
  return response.data
}

export const generateViralHooks = async (data: {
  topic: string
  count?: number
  tone?: string
}): Promise<{ hooks: string[] }> => {
  const response = await apiClient.post('/api/hooks/generate/', data)
  return response.data
}

// ==================== USER ANALYTICS ====================

export interface UserStats {
  total_uploads: number
  total_posts: number
  total_scheduled: number
  engagement_rate: number
  hours_saved: number
  trending_score: number
}

export const getUserAnalytics = async (): Promise<UserStats> => {
  const response = await apiClient.get<UserStats>('/api/analytics/')
  return response.data
}

export const getRecentActivity = async () => {
  const response = await apiClient.get('/api/stats/recent-activity/')
  return response.data
}

export const getUserUploads = async () => {
  const response = await apiClient.get('/api/stats/uploads/')
  return response.data
}

export const getUserPosts = async () => {
  const response = await apiClient.get('/api/stats/posts/')
  return response.data
}

// ==================== SOCIAL MEDIA ACCOUNTS ====================

export interface SocialAccount {
  id: number
  platform: 'twitter' | 'linkedin' | 'instagram' | 'facebook' | 'tiktok'
  username: string
  is_active: boolean
  last_sync: string
  followers_count?: number
}

export const getSocialAccounts = async (): Promise<SocialAccount[]> => {
  const response = await apiClient.get<SocialAccount[]>('/api/social/accounts/')
  return response.data
}

export const initiateSocialOAuth = async (platform: string) => {
  const response = await apiClient.post(`/api/social/accounts/initiate_oauth/`, { platform })
  return response.data
}

export const connectSocialAccount = async (platform: string, code: string) => {
  const response = await apiClient.post('/api/social/accounts/connect_account/', {
    platform,
    code,
  })
  return response.data
}

export const disconnectSocialAccount = async (accountId: number) => {
  const response = await apiClient.post(`/api/social/accounts/${accountId}/disconnect_account/`)
  return response.data
}

// ==================== SCHEDULED POSTS ====================

export interface ScheduledPost {
  id: number
  content: string
  platform: string
  scheduled_time: string
  status: 'pending' | 'published' | 'failed' | 'cancelled'
  media_urls?: string[]
  hashtags?: string[]
}

export const getScheduledPosts = async (params?: {
  start_date?: string
  end_date?: string
  platform?: string
}): Promise<ScheduledPost[]> => {
  const response = await apiClient.get<ScheduledPost[]>('/api/social/scheduled-posts/', {
    params,
  })
  return response.data
}

export const createScheduledPost = async (data: {
  content: string
  platform: string
  scheduled_time: string
  media_urls?: string[]
  hashtags?: string[]
}): Promise<ScheduledPost> => {
  const response = await apiClient.post<ScheduledPost>('/api/social/scheduled-posts/', data)
  return response.data
}

export const updateScheduledPost = async (
  postId: number,
  data: Partial<ScheduledPost>
): Promise<ScheduledPost> => {
  const response = await apiClient.patch<ScheduledPost>(
    `/api/social/scheduled-posts/${postId}/`,
    data
  )
  return response.data
}

export const cancelScheduledPost = async (postId: number) => {
  const response = await apiClient.post(`/api/social/scheduled-posts/${postId}/cancel_post/`)
  return response.data
}

export const publishPostNow = async (postId: number) => {
  const response = await apiClient.post(`/api/social/scheduled-posts/${postId}/publish_now/`)
  return response.data
}

export const postDirectly = async (data: {
  content: string
  platform: string
  media_urls?: string[]
  hashtags?: string[]
}) => {
  const response = await apiClient.post('/api/social/posts/direct-post/', data)
  return response.data
}

export const getCalendarView = async (params: { month: number; year: number }) => {
  const response = await apiClient.get('/api/social/scheduled-posts/calendar_view/', { params })
  return response.data
}

// ==================== POST ANALYTICS ====================

export interface PostAnalytics {
  id: number
  post_id: number
  impressions: number
  likes: number
  comments: number
  shares: number
  engagement_rate: number
  reach: number
  clicks: number
  last_updated: string
}

export interface PlatformBreakdown {
  count: number
  total_likes: number
  avg_engagement: number
}

export interface AnalyticsSummaryResponse {
  total_posts: number
  total_likes: number
  total_comments: number
  total_shares: number
  total_impressions: number
  total_reach: number
  avg_engagement_rate: number
  top_performing_post?: PostAnalytics
  platform_breakdown: Record<string, PlatformBreakdown>
}

export const getPostAnalytics = async (postId?: number): Promise<PostAnalytics[]> => {
  const url = postId ? `/api/social/analytics/${postId}/` : '/api/social/analytics/'
  const response = await apiClient.get<PostAnalytics[]>(url)
  return response.data
}

export const getAnalyticsSummary = async (params?: {
  start_date?: string
  end_date?: string
}) => {
  const response = await apiClient.get<AnalyticsSummaryResponse>('/api/social/analytics/summary/', {
    params,
  })
  return response.data
}

export const getDashboardAnalytics = async (params?: {
  start_date?: string
  end_date?: string
  platform?: string
}) => {
  const response = await apiClient.get('/api/social/analytics/analytics/', { params })
  return response.data
}

export const exportAnalytics = async (format: 'csv' | 'json' = 'csv') => {
  const response = await apiClient.get('/api/social/analytics/export_analytics/', {
    params: { format },
    responseType: 'blob',
  })
  return response.data
}

// ==================== IMAGE GENERATION ====================

export interface ImageGenerationRequest {
  prompt: string
  style?: string
  aspect_ratio?: '1:1' | '16:9' | '9:16' | '4:5'
  enhance_prompt?: boolean
}

export const generateImage = async (data: ImageGenerationRequest) => {
  const response = await apiClient.post('/api/social/image-generation/generate/', data)
  return response.data
}

export const generateImageVariations = async (imageUrl: string, count: number = 3) => {
  const response = await apiClient.post('/api/social/image-generation/variations/', {
    image_url: imageUrl,
    count,
  })
  return response.data
}

export const getImageStylePresets = async () => {
  const response = await apiClient.get('/api/social/image-generation/style_presets/')
  return response.data
}

export const optimizeImagePrompt = async (prompt: string) => {
  const response = await apiClient.post('/api/social/image-generation/optimize_prompt/', {
    prompt,
  })
  return response.data
}

// ==================== STOCK PHOTOS ====================

export const searchStockPhotos = async (params: {
  query: string
  page?: number
  per_page?: number
  orientation?: 'landscape' | 'portrait' | 'square'
  color?: string
}) => {
  const response = await apiClient.get('/api/social/stock-photos/search/', { params })
  return response.data
}

export const aiSearchStockPhotos = async (description: string) => {
  const response = await apiClient.post('/api/social/stock-photos/ai_search/', { description })
  return response.data
}

export const downloadStockPhoto = async (photoId: string, download_location?: string) => {
  const response = await apiClient.post('/api/social/stock-photos/download/', {
    photo_id: photoId,
    download_location,
  })
  return response.data
}

export const getTrendingPhotos = async () => {
  const response = await apiClient.get('/api/social/stock-photos/trending/')
  return response.data
}

// ==================== IMAGE EDITING ====================

export const optimizeImageForPlatform = async (data: {
  image_url: string
  platform: string
  post_type?: string
}) => {
  const response = await apiClient.post('/api/social/image-editor/optimize_for_platform/', data)
  return response.data
}

export const editImage = async (data: {
  image_url: string
  operations: Array<{
    type: string
    params: any
  }>
}) => {
  const response = await apiClient.post('/api/social/image-editor/edit/', data)
  return response.data
}

export const getPlatformImageSpecs = async () => {
  const response = await apiClient.get('/api/social/image-editor/platform_specs/')
  return response.data
}

export const getAvailableFilters = async () => {
  const response = await apiClient.get('/api/social/image-editor/available_filters/')
  return response.data
}

// ==================== PHOTO PROCESSING ====================

export const processPhoto = async (formData: FormData) => {
  const response = await apiClient.post('/api/photos/process/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const createCollage = async (data: {
  image_urls: string[]
  template: string
  output_size?: string
}) => {
  const response = await apiClient.post('/api/photos/collage/', data)
  return response.data
}

export const batchProcessPhotos = async (data: {
  image_urls: string[]
  operations: any[]
}) => {
  const response = await apiClient.post('/api/photos/batch/', data)
  return response.data
}

export const getPhotoTemplates = async () => {
  const response = await apiClient.get('/api/photos/templates/')
  return response.data
}

export const getPhotoFilters = async () => {
  const response = await apiClient.get('/api/photos/filters/')
  return response.data
}

// ==================== HEALTH CHECKS ====================

export const healthCheck = async () => {
  const response = await apiClient.get('/api/health/')
  return response.data
}

export const readinessCheck = async () => {
  const response = await apiClient.get('/api/health/ready/')
  return response.data
}

// ==================== ERROR HANDLING ====================

export const isApiError = (error: any): error is AxiosError => {
  return axios.isAxiosError(error)
}

export const getErrorMessage = (error: any): string => {
  if (isApiError(error)) {
    const data: any = error.response?.data
    return (
      data?.detail ||
      data?.error ||
      data?.message ||
      error.message
    )
  }
  return error?.message || 'An unexpected error occurred'
}