import { API_BASE_URL } from './constants';
import type {
  PhoneDetails,
  RecommendationResponse,
  EasyRecommendRequest,
  MediumRecommendRequest,
  DeepRecommendRequest,
} from './types';

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
    throw new ApiError(response.status, `API Error: ${response.statusText} (${response.status})`);
  }

  return response.json();
}

export const api = {
  getPhones: (params?: Record<string, string>) => {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return fetchApi<{ phones: PhoneDetails[]; total: number }>(`/phones${queryString}`);
  },

  getPhone: (slug: string) => {
    return fetchApi<PhoneDetails>(`/phones/${encodeURIComponent(slug)}`);
  },

  searchPhones: (query: string) => {
    return fetchApi<PhoneDetails[]>(`/phones/search?q=${encodeURIComponent(query)}`);
  },

  recommendEasy: (data: EasyRecommendRequest) => {
    return fetchApi<RecommendationResponse>('/recommend/easy', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  recommendMedium: (data: MediumRecommendRequest) => {
    return fetchApi<RecommendationResponse>('/recommend/medium', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  recommendDeep: (data: DeepRecommendRequest) => {
    return fetchApi<RecommendationResponse>('/recommend/deep', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  comparePhones: (ids: (string | number)[]) => {
    const idsStr = ids.join(',');
    return fetchApi<{ phones: PhoneDetails[]; differences: Record<string, any> }>(
      `/compare?ids=${encodeURIComponent(idsStr)}`
    );
  },

  getBrands: () => {
    return fetchApi<string[]>('/brands');
  },
};
