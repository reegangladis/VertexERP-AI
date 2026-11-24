/**
 * Centralized API Client for VertexERP AI Frontend
 * Communicates with FastAPI /api/v1 backend with credentials, correlation headers,
 * and unified RFC 7807 problem details error handling.
 */

export interface ApiError {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  errors?: Record<string, string[]>;
}

export class ApiException extends Error {
  status: number;
  data: ApiError;

  constructor(status: number, message: string, data: ApiError) {
    super(message);
    this.name = "ApiException";
    this.status = status;
    this.data = data;
  }
}

const API_BASE_URL = (import.meta.env?.VITE_API_BASE_URL as string) || "/api/v1";

export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const normalizedEndpoint = endpoint.startsWith("/api/v1")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const config: RequestInit = {
    ...options,
    headers,
    credentials: "include", // For HttpOnly session cookie support
  };

  const response = await fetch(normalizedEndpoint, config);

  if (response.status === 204) {
    return {} as T;
  }

  let data: any = null;
  const contentType = response.headers && typeof response.headers.get === "function" 
    ? response.headers.get("content-type") 
    : "application/json";

  if (typeof response.json === "function" && (!contentType || contentType.includes("application/json") || !response.headers)) {
    try {
      data = await response.json();
    } catch {
      if (typeof response.text === "function") {
        data = await response.text();
      }
    }
  } else if (typeof response.text === "function") {
    data = await response.text();
  }

  if (!response.ok) {
    const errorDetail =
      (typeof data === "object" && data !== null && (data.detail || data.title || data.message)) ||
      `Request failed with status ${response.status}`;

    throw new ApiException(
      response.status,
      typeof errorDetail === "string" ? errorDetail : JSON.stringify(errorDetail),
      typeof data === "object" ? data : { detail: String(data) }
    );
  }

  return data as T;
}
