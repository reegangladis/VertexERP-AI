import axios, { AxiosError } from 'axios';

// Helper to generate a unique request ID tracer
function generateRequestId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// Read API base URL from environments dynamically
export function getApiBaseUrl(): string {
  return (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';
}

const baseURL = getApiBaseUrl();

export const apiClient = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Inject unique Request IDs for tracing and Authorization token
apiClient.interceptors.request.use(
  (config) => {
    if (config.headers) {
      if (!config.headers['X-Request-ID']) {
        config.headers['X-Request-ID'] = generateRequestId();
      }
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      if (token && !config.headers['Authorization']) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Parse generic APIResponse envelope and format errors
apiClient.interceptors.response.use(
  (response) => {
    // If response matches standard APIResponse wrapper, extract data
    const payload = response.data;
    if (payload && typeof payload === 'object' && 'success' in payload) {
      if (!payload.success) {
        return Promise.reject(new Error(payload.message || 'Operation failed'));
      }
      return response;
    }
    return response;
  },
  (error: AxiosError) => {
    let friendlyMessage = 'An unexpected connection error occurred';
    
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;
      
      // Attempt to read custom backend error message
      const backendMessage = data?.message || data?.error?.message;
      
      switch (status) {
        case 400:
          friendlyMessage = backendMessage || 'Bad Request: The server could not parse your parameters';
          break;
        case 401:
          friendlyMessage = backendMessage || 'Unauthorized: Access credentials invalid';
          break;
        case 403:
          friendlyMessage = backendMessage || 'Forbidden: You do not have privilege to run this task';
          break;
        case 404:
          friendlyMessage = backendMessage || 'Not Found: The resource could not be located';
          break;
        case 409:
          friendlyMessage = backendMessage || 'Conflict: Logical state collision on database';
          break;
        case 422:
          friendlyMessage = backendMessage || 'Validation Failed: Input parameters failed constraints';
          break;
        case 500:
          friendlyMessage = 'Internal Server Error: Something went wrong on the server';
          break;
        case 503:
          friendlyMessage = backendMessage || 'Service Unavailable: Gateway timeout or system is under maintenance';
          break;
      }
    } else if (error.request) {
      friendlyMessage = 'Unable to connect to the backend server. Please verify your connection status.';
    }
    
    return Promise.reject(new Error(friendlyMessage));
  }
);
