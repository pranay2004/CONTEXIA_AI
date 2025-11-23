import { apiClient } from '@/lib/api-client';

// --- Types ---

export interface SocialAccount {
  id: number;
  platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram';
  account_name: string;
  account_username: string;
  profile_picture_url: string;
  is_active: boolean;
  days_until_expiry?: number;
}

export interface ScheduledPost {
  id: number;
  content_text: string;
  social_account_platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram';
  scheduled_time: string;
  status: 'pending' | 'published' | 'failed' | 'cancelled';
}

export interface AnalyticsSummary {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_impressions: number;
  avg_engagement_rate: number;
  platform_breakdown: Array<{
    scheduled_post__social_account__platform: string;
    count: number;
    engagement: number;
  }>;
}

export interface DashboardData {
  engagement_trend: Array<{
    date: string;
    impressions: number;
    likes: number;
  }>;
  top_posts: Array<{
    post_content: string;
    post_platform: string;
    engagement_rate: number;
    likes: number;
    published_at: string;
  }>;
}

// --- API Client ---

export const socialApi = {
  // 1. Auth & Accounts
  getAuthUrl: async (platform: string) => {
    const res = await apiClient.post('/api/social/accounts/initiate-oauth/', { platform });
    return res.data; // Returns { authorization_url, state }
  },

  connectAccount: async (platform: string, code: string, state: string) => {
    const res = await apiClient.post('/api/social/accounts/connect/', { platform, code, state });
    return res.data;
  },

  getAccounts: async () => {
    const res = await apiClient.get<SocialAccount[]>('/api/social/accounts/');
    return res.data;
  },

  disconnectAccount: async (id: number) => {
    await apiClient.post(`/api/social/accounts/${id}/disconnect/`);
  },

  // 2. Posting & Scheduling
  directPost: async (platform: string, content: string) => {
    const res = await apiClient.post('/api/social/posts/direct-post/', { platform, content });
    return res.data;
  },

  schedulePost: async (accountId: number, content: string, scheduledTime: Date) => {
    const res = await apiClient.post('/api/social/scheduled-posts/', {
      social_account: accountId,
      content_text: content,
      scheduled_time: scheduledTime.toISOString(),
      status: 'pending'
    });
    return res.data;
  },

  getScheduledPosts: async () => {
    const res = await apiClient.get<ScheduledPost[]>('/api/social/scheduled-posts/');
    return res.data;
  },

  cancelScheduledPost: async (id: number) => {
    await apiClient.post(`/api/social/scheduled-posts/${id}/cancel_post/`);
  },

  // 3. Analytics
  getAnalyticsSummary: async () => {
    const res = await apiClient.get<AnalyticsSummary>('/api/social/analytics/summary/');
    return res.data;
  },

  getDashboardData: async () => {
    const res = await apiClient.get<DashboardData>('/api/social/analytics/dashboard-data/');
    return res.data;
  }
};