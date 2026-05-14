import type { ApiError } from '@/types/common.types';

const API_BASE_URL = import.meta.env.VITE_BIZFLOW_API_URL ?? 'http://127.0.0.1:8787';

export class ApiClientError extends Error {
  status: number;
  payload?: ApiError;

  constructor(status: number, message: string, payload?: ApiError) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.payload = payload;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...init?.headers
    }
  });

  if (!response.ok) {
    const payload = await safeJson<ApiError>(response);
    throw new ApiClientError(response.status, payload?.message ?? response.statusText, payload);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function safeJson<T>(response: Response): Promise<T | undefined> {
  try {
    return (await response.json()) as T;
  } catch {
    return undefined;
  }
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: body === undefined ? undefined : JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};
