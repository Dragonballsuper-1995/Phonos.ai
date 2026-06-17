import { API_BASE_URL } from './constants';
import { Phone, RecommendationResponse } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  getPhones: (params?: Record<string, string>) => {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return fetchApi<{ phones: Phone[], total: number }>(`/phones${queryString}`);
  },

  getPhone: (slug: string) => {
    return fetchApi<Phone>(`/phones/${slug}`);
  },

  searchPhones: (query: string) => {
    return fetchApi<Phone[]>(`/phones/search?q=${encodeURIComponent(query)}`);
  },

  recommendEasy: (data: any) => {
    return fetchApi<RecommendationResponse>('/recommend/easy', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  recommendMedium: (data: any) => {
    return fetchApi<RecommendationResponse>('/recommend/medium', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  comparePhones: (slugs: string[]) => {
    const queryString = slugs.map(slug => `slug=${encodeURIComponent(slug)}`).join('&');
    return fetchApi<Phone[]>(`/phones/compare?${queryString}`);
  },

  getBrands: () => {
    return fetchApi<string[]>('/brands');
  },

  getFilters: () => {
    return fetchApi<any>('/filters');
  }
};
