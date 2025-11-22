import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { toast } from 'sonner'
import { log } from './logger'

/**
 * Global React Query client configuration
 * Implements caching, retry logic, and error handling
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache for 5 minutes
      staleTime: 5 * 60 * 1000,
      // Keep unused data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests twice with exponential backoff
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus for fresh data
      refetchOnWindowFocus: true,
      // Don't refetch on mount if data is fresh
      refetchOnMount: false,
    },
    mutations: {
      // Retry mutations once
      retry: 1,
    },
  },
})

/**
 * Query keys for type-safe cache management
 */
export const queryKeys = {
  // User data
  userProfile: ['user', 'profile'] as const,
  userStats: ['user', 'stats'] as const,
  
  // Content
  uploads: ['uploads'] as const,
  posts: ['posts'] as const,
  recentActivity: ['activity', 'recent'] as const,
  generatedContent: (id: number) => ['content', 'generated', id] as const,
  
  // Trends
  trends: (params?: { source?: string; limit?: number }) => 
    ['trends', params] as const,
  
  // Analytics
  analytics: ['analytics'] as const,
  dashboard: ['dashboard'] as const,
}

/**
 * Invalidate queries helper
 */
export const invalidateQueries = {
  userProfile: () => queryClient.invalidateQueries({ queryKey: queryKeys.userProfile }),
  userStats: () => queryClient.invalidateQueries({ queryKey: queryKeys.userStats }),
  uploads: () => queryClient.invalidateQueries({ queryKey: queryKeys.uploads }),
  posts: () => queryClient.invalidateQueries({ queryKey: queryKeys.posts }),
  recentActivity: () => queryClient.invalidateQueries({ queryKey: queryKeys.recentActivity }),
  analytics: () => queryClient.invalidateQueries({ queryKey: queryKeys.analytics }),
  dashboard: () => queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
  all: () => queryClient.invalidateQueries(),
}

/**
 * Prefetch helpers for optimistic loading
 */
export const prefetchQueries = {
  userProfile: async () => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.userProfile,
      queryFn: async () => {
        const { api } = await import('./api')
        const response = await api.get('/profile/')
        return response.data
      },
    })
  },
  
  userStats: async () => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.userStats,
      queryFn: async () => {
        const { getUserStats } = await import('./api')
        return await getUserStats()
      },
    })
  },
  
  dashboard: async () => {
    await Promise.all([
      prefetchQueries.userStats(),
      prefetchQueries.userProfile(),
    ])
  },
}
