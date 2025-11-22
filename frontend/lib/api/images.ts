

export interface ImageGenerationRequest {
  prompt: string;
  platform?: string;
  quality?: 'standard' | 'hd';
  style?: 'vivid' | 'natural';
  preset?: string;
  size?: '1024x1024' | '1024x1792' | '1792x1024';
}

export interface ImageGenerationResponse {
  success: boolean;
  image_url: string;
  revised_prompt?: string;
  cost?: number;
  provider: 'openai' | 'replicate';
  dimensions: [number, number];
}

export interface ImageVariationRequest {
  image_url: string;
  n?: number;
  size?: string;
}

export interface StockPhotoSearchRequest {
  query: string;
  provider?: 'unsplash' | 'pexels' | 'pixabay';
  per_page?: number;
  page?: number;
  orientation?: 'landscape' | 'portrait' | 'square';
}

export interface StockPhoto {
  id: string;
  url: string;
  thumbnail: string;
  description: string;
  photographer: string;
  photographer_url: string;
  source: string;
  width: number;
  height: number;
}

export interface ImageEditOperation {
  type: 'resize' | 'crop' | 'brightness' | 'contrast' | 'saturation' | 'sharpness' | 'filter' | 'text' | 'watermark' | 'rotate' | 'flip';
  [key: string]: any;
}

export interface ImageEditRequest {
  image_url: string;
  operations: ImageEditOperation[];
}

export interface ImageEditResponse {
  success: boolean;
  url: string;
  dimensions: [number, number];
  operations_applied: number;
}

export interface PlatformOptimizeRequest {
  image_url: string;
  platform: 'instagram' | 'facebook' | 'twitter' | 'linkedin';
  variant?: string;
}

export class ImageAPI {
  private baseUrl: string;

  constructor(baseUrl = '/api/social') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Request failed');
    }

    return response.json();
  }

  // Image Generation
  async generateImage(data: ImageGenerationRequest): Promise<ImageGenerationResponse> {
    return this.request('/image-generation/generate/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createVariations(data: ImageVariationRequest): Promise<ImageGenerationResponse> {
    return this.request('/image-generation/variations/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async optimizePrompt(prompt: string): Promise<{ optimized_prompt: string }> {
    return this.request('/image-generation/optimize-prompt/', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async getStylePresets(): Promise<{ presets: any[] }> {
    return this.request('/image-generation/presets/', {
      method: 'GET',
    });
  }

  // Stock Photos
  async searchStockPhotos(params: StockPhotoSearchRequest): Promise<{ photos: StockPhoto[]; total: number }> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/stock-photos/search/?${query}`, {
      method: 'GET',
    });
  }

  async aiSearchPhotos(query: string): Promise<{ photos: StockPhoto[]; enhanced_query: string }> {
    return this.request('/stock-photos/ai-search/', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  async downloadStockPhoto(url: string, optimize = true): Promise<{ url: string }> {
    return this.request('/stock-photos/download/', {
      method: 'POST',
      body: JSON.stringify({ url, optimize }),
    });
  }

  async getTrendingPhotos(): Promise<{ photos: StockPhoto[] }> {
    return this.request('/stock-photos/trending/', {
      method: 'GET',
    });
  }

  // Image Editor
  async optimizeForPlatform(data: PlatformOptimizeRequest): Promise<ImageEditResponse> {
    return this.request('/image-editor/optimize/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async editImage(data: ImageEditRequest): Promise<ImageEditResponse> {
    return this.request('/image-editor/edit/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPlatformSpecs(): Promise<{ specs: Record<string, Record<string, [number, number]>> }> {
    return this.request('/image-editor/platform-specs/', {
      method: 'GET',
    });
  }

  async getAvailableFilters(): Promise<{ filters: Array<{ name: string; description: string }> }> {
    return this.request('/image-editor/filters/', {
      method: 'GET',
    });
  }
}

export const imageAPI = new ImageAPI();
