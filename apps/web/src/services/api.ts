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

// Default to localhost:8000 which is mapped via Docker Compose/Local setup
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/api/v1/health`);
  if (!res.ok) {
    // Attempt to extract response data anyway
    try {
      const data = await res.json();
      if (data.error) {
        return data.error as HealthResponse;
      }
    } catch {
      // Fallback if not JSON
    }
    throw new Error('API Health check failed');
  }
  return res.json();
}

export async function fetchVersion(): Promise<VersionResponse> {
  const res = await fetch(`${API_URL}/api/v1/version`);
  if (!res.ok) {
    throw new Error('API Version check failed');
  }
  return res.json();
}
