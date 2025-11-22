import axios, { AxiosInstance } from 'axios';
import { getSession } from 'next-auth/react';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for adding auth token from NextAuth session
apiClient.interceptors.request.use(
  async (config) => {
    // Get token from NextAuth session instead of localStorage
    if (typeof window !== 'undefined') {
      const session = await getSession();
      const token = session?.accessToken;
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login?message=session_expired';
      }
    }
    return Promise.reject(error);
  }
);

export { apiClient };
