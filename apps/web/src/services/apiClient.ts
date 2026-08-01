/**
 * Enterprise API Client — VertexERP AI
 *
 * Features:
 * - Automatic JWT Bearer token injection
 * - Silent token refresh on 401 (refresh rotation)
 * - Redirect to /auth/session-expired on refresh failure
 * - Proper FastAPI error message extraction
 * - Unique request ID tracing
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// ─────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────

function generateRequestId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function getApiBaseUrl(): string {
  return (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';
}

const BASE_URL = getApiBaseUrl();

// ─────────────────────────────────────────
// Token Storage Helpers
// ─────────────────────────────────────────

const TOKEN_KEY = 'vertex_access_token';
const REFRESH_KEY = 'vertex_refresh_token';

export const tokenStorage = {
  getAccessToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  getRefreshToken: (): string | null => localStorage.getItem(REFRESH_KEY),
  setTokens: (access: string, refresh: string): void => {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clearTokens: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem('vertex_user');
  },
};

// ─────────────────────────────────────────
// Axios Instance
// ─────────────────────────────────────────

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─────────────────────────────────────────
// Request Interceptor
// ─────────────────────────────────────────

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (config.headers) {
      // Inject unique request trace ID
      if (!config.headers['X-Request-ID']) {
        config.headers['X-Request-ID'] = generateRequestId();
      }

      // Inject Bearer token (prefer localStorage, fallback to legacy keys)
      const token =
        tokenStorage.getAccessToken() ||
        localStorage.getItem('token') ||
        localStorage.getItem('access_token');

      if (token && !config.headers['Authorization']) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ─────────────────────────────────────────
// Response Interceptor — Refresh + Error
// ─────────────────────────────────────────

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

apiClient.interceptors.response.use(
  (response) => {
    // Unwrap standard APIResponse envelope
    const payload = response.data;
    if (payload && typeof payload === 'object' && 'success' in payload) {
      if (!payload.success) {
        return Promise.reject(new Error(payload.message || 'Operation failed'));
      }
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // ── Silent refresh on 401 ──
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      originalRequest._retry = true;

      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        tokenStorage.clearTokens();
        window.location.href = '/auth/session-expired';
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue requests until refresh completes
        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken: string) => {
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }

      isRefreshing = true;
      try {
        const res = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const data = res.data?.data || res.data;
        const newAccessToken: string = data.access_token;
        const newRefreshToken: string = data.refresh_token;

        tokenStorage.setTokens(newAccessToken, newRefreshToken);
        onTokenRefreshed(newAccessToken);

        if (originalRequest.headers) {
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        }
        return apiClient(originalRequest);
      } catch (_refreshError) {
        tokenStorage.clearTokens();
        window.location.href = '/auth/session-expired';
        return Promise.reject(_refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // ── Format error message ──
    let friendlyMessage = 'An unexpected error occurred';

    if (error.response) {
      const httpStatus = error.response.status;
      const data = error.response.data as Record<string, unknown>;

      // Extract FastAPI detail (string or list of validation errors)
      let backendMessage: string | undefined;
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          backendMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          backendMessage = (data.detail as Array<{ msg: string }>)
            .map((e) => e.msg)
            .join(', ');
        }
      } else if (data?.message && typeof data.message === 'string') {
        backendMessage = data.message;
      }

      switch (httpStatus) {
        case 400:
          friendlyMessage = backendMessage || 'Bad request — invalid parameters';
          break;
        case 401:
          friendlyMessage = backendMessage || 'Authentication required — please log in';
          break;
        case 403:
          friendlyMessage = backendMessage || 'Access denied — insufficient permissions';
          break;
        case 404:
          friendlyMessage = backendMessage || 'Resource not found';
          break;
        case 409:
          friendlyMessage = backendMessage || 'Conflict — resource already exists';
          break;
        case 422:
          friendlyMessage = backendMessage || 'Validation failed — check your inputs';
          break;
        case 429:
          friendlyMessage = 'Too many requests — please wait before retrying';
          break;
        case 500:
          friendlyMessage = 'Internal server error — please try again later';
          break;
        case 503:
          friendlyMessage = backendMessage || 'Service temporarily unavailable';
          break;
        default:
          friendlyMessage = backendMessage || `Unexpected error (${httpStatus})`;
      }
    } else if (error.request) {
      friendlyMessage =
        'Cannot reach the server — please check your network connection';
    }

    return Promise.reject(new Error(friendlyMessage));
  },
);
