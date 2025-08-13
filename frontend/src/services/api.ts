import type { JobSearchRequest, JobSearchResponse, HealthCheckResponse } from '../types';

const API_BASE_URL = '/api';

class ApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    return this.fetchApi<HealthCheckResponse>('/health');
  }

  async searchJobs(request: JobSearchRequest): Promise<JobSearchResponse> {
    return this.fetchApi<JobSearchResponse>('/jobs/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getChatHistory(): Promise<{ messages: any[] }> {
    return this.fetchApi<{ messages: any[] }>('/chat/history');
  }
}

export const apiService = new ApiService();
