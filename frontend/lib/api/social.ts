/**
 * Social Media API Client
 */
import { apiClient } from './client';

export interface SocialAccount {
  id: number;
  platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram';
  account_name: string;
  account_username: string;
  profile_picture_url: string;
  is_active: boolean;
  connected_at: string;
  token_expires_at: string;
  days_until_expiry: number;
}

export interface ScheduledPost {
  id: number;
  social_account: number;
  social_account_details?: SocialAccount;
  content_text: string;
  content_html?: string;
  image_urls?: string[];
  video_url?: string;
  scheduled_time: string;
  status: 'draft' | 'pending' | 'publishing' | 'published' | 'failed' | 'cancelled';
  platform_post_id?: string;
  platform_post_url?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface PostingSchedule {
  id: number;
  social_account: number;
  social_account_details?: SocialAccount;
  weekday: number;
  hour: number;
  minute: number;
  weekday_name: string;
  time_12hour: string;
  confidence_score: number;
  reasoning: string;
  historical_data?: Record<string, any>;
  is_active: boolean;
}

export interface PostAnalytics {
  id: number;
  post: number;
  post_details?: ScheduledPost;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  impressions: number;
  reach: number;
  clicks: number;
  video_views: number;
  engagement_rate: string;
  ctr: string;
  published_at: string;
  last_updated: string;
}

export interface AnalyticsSummary {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_impressions: number;
  total_reach: number;
  avg_engagement_rate: number;
  top_performing_post?: PostAnalytics;
  platform_breakdown: Record<string, {
    count: number;
    total_likes: number;
    avg_engagement: number;
  }>;
}

// Social Accounts API
export const socialAccountsApi = {
  list: () => apiClient.get<SocialAccount[]>('/social/accounts/'),
  
  initiateOAuth: (platform: string, redirectUri: string) =>
    apiClient.post<{ authorization_url: string; state: string }>(
      '/social/accounts/initiate-oauth/',
      { platform, redirect_uri: redirectUri }
    ),
  
  connect: (platform: string, code: string, state: string, codeVerifier?: string) =>
    apiClient.post<SocialAccount>('/social/accounts/connect/', {
      platform,
      code,
      state,
      code_verifier: codeVerifier,
    }),
  
  refreshToken: (id: number) =>
    apiClient.post<SocialAccount>(`/social/accounts/${id}/refresh-token/`),
  
  disconnect: (id: number) =>
    apiClient.post(`/social/accounts/${id}/disconnect/`),
  
  delete: (id: number) =>
    apiClient.delete(`/social/accounts/${id}/`),
};

// Scheduled Posts API
export const scheduledPostsApi = {
  list: (params?: { status?: string; start_date?: string; end_date?: string }) =>
    apiClient.get<ScheduledPost[]>('/social/scheduled-posts/', { params }),
  
  get: (id: number) =>
    apiClient.get<ScheduledPost>(`/social/scheduled-posts/${id}/`),
  
  create: (data: Partial<ScheduledPost>) =>
    apiClient.post<ScheduledPost>('/social/scheduled-posts/', data),
  
  update: (id: number, data: Partial<ScheduledPost>) =>
    apiClient.patch<ScheduledPost>(`/social/scheduled-posts/${id}/`, data),
  
  delete: (id: number) =>
    apiClient.delete(`/social/scheduled-posts/${id}/`),
  
  cancel: (id: number) =>
    apiClient.post<{ message: string }>(`/social/scheduled-posts/${id}/cancel/`),
  
  retry: (id: number) =>
    apiClient.post<{ status: string; task_id: string }>(`/social/scheduled-posts/${id}/retry/`),
  
  publishNow: (data: Partial<ScheduledPost>) =>
    apiClient.post<{ status: string; post_id: number; task_id: string }>(
      '/social/scheduled-posts/publish-now/',
      data
    ),
  
  calendar: (start: string, end: string) =>
    apiClient.get<ScheduledPost[]>('/social/scheduled-posts/calendar/', {
      params: { start, end },
    }),
};

// Posting Schedules API
export const postingSchedulesApi = {
  list: (socialAccountId?: number) =>
    apiClient.get<PostingSchedule[]>('/social/posting-schedules/', {
      params: socialAccountId ? { social_account: socialAccountId } : undefined,
    }),
  
  get: (id: number) =>
    apiClient.get<PostingSchedule>(`/social/posting-schedules/${id}/`),
};

// Analytics API
export const analyticsApi = {
  list: (params?: { start_date?: string; end_date?: string; social_account?: number }) =>
    apiClient.get<PostAnalytics[]>('/social/analytics/', { params }),
  
  get: (id: number) =>
    apiClient.get<PostAnalytics>(`/social/analytics/${id}/`),
  
  summary: (params?: { start_date?: string; end_date?: string }) =>
    apiClient.get<AnalyticsSummary>('/social/analytics/summary/', { params }),
  
  getAnalytics: (params?: { start_date?: string; end_date?: string; platform?: string }) =>
    apiClient.get<any>('/social/analytics/analytics/', { params }),
  
  exportAnalytics: (format: 'csv' | 'pdf', params?: { start_date?: string; end_date?: string }) =>
    apiClient.get(`/social/analytics/export/`, { 
      params: { format, ...params },
      responseType: 'blob',
    }),
};

// Combined social API export
export const socialAPI = {
  ...socialAccountsApi,
  ...scheduledPostsApi,
  ...postingSchedulesApi,
  getAnalytics: analyticsApi.getAnalytics,
  exportAnalytics: analyticsApi.exportAnalytics,
};

