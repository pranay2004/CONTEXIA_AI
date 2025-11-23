import { apiClient } from '@/lib/api-client'

export interface UserProfile {
  company_name: string
  target_audience: string
  brand_voice: string
}

export interface User {
  id: number
  username: string
  email: string
  profile: UserProfile
}

export const userApi = {
  getProfile: async () => {
    // FIX: Added trailing slash to match Django convention
    const res = await apiClient.get<User>('/api/users/profile/')
    return res.data
  },

  updateProfile: async (data: Partial<UserProfile>) => {
    const res = await apiClient.put<User>('/api/users/profile/', {
      profile: data 
    })
    return res.data
  }
}