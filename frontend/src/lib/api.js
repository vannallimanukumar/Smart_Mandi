import { getAccessToken } from "./supabase";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export async function api(path, options = {}) {
  const token = options.auth ? await getAccessToken() : null;
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${BASE}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return payload;
}
