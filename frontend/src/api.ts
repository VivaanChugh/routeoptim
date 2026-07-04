/**
 * API Service for communicating with the backend
 */

import axios, { AxiosInstance } from 'axios';
import {
  RouteOptimizationRequest,
  RouteOptimizationResponse,
  HealthResponse,
  ApiConfig,
  SampleScenario,
} from './types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2 minutes for optimization
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // Server responded with error
          throw new Error(error.response.data.detail || error.response.data.error || 'API Error');
        } else if (error.request) {
          // Request made but no response
          throw new Error('No response from server. Check if backend is running.');
        } else {
          // Error in request setup
          throw new Error(error.message);
        }
      }
    );
  }

  /**
   * Check API health status
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Get API configuration
   */
  async getConfig(): Promise<ApiConfig> {
    const response = await this.client.get<ApiConfig>('/config');
    return response.data;
  }

  /**
   * Optimize a delivery route
   */
  async optimizeRoute(request: RouteOptimizationRequest): Promise<RouteOptimizationResponse> {
    const response = await this.client.post<RouteOptimizationResponse>('/optimize', request);
    return response.data;
  }

  /**
   * Get sample scenarios
   */
  async getSampleScenarios(): Promise<Record<string, SampleScenario>> {
    const response = await this.client.get<Record<string, SampleScenario>>('/sample-scenarios');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
