import { apiClient } from './apiClient';

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  services: {
    database: string;
    redis: string;
  };
}

export interface VersionResponse {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  try {
    const response = await apiClient.get('/api/v1/health');
    return response.data.data;
  } catch (error: any) {
    // For 503 Service Unavailable, return parsed sub-service statuses if present
    if (error.response?.data?.data) {
      return error.response.data.data as HealthResponse;
    }
    throw error;
  }
}

export async function fetchVersion(): Promise<VersionResponse> {
  const response = await apiClient.get('/api/v1/version');
  return response.data.data;
}
