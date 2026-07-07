import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Fetch (or return cached) user info from the backend.
 * Triggers a Codeforces API call if the cache is stale.
 */
export async function fetchUser(handle) {
  const response = await api.get(`/api/cf/user/${encodeURIComponent(handle)}`);
  return response.data;
}

/**
 * Compute and return analytics for a handle that has already been fetched.
 */
export async function fetchAnalytics(handle) {
  const response = await api.get(`/api/analytics/${encodeURIComponent(handle)}`);
  return response.data;
}

/**
 * Run NLP sentiment analysis on the most recent contest blog comments.
 */
export async function fetchSentiment(handle) {
  const response = await api.get(`/api/sentiment/${encodeURIComponent(handle)}`);
  return response.data;
}

/**
 * Delete the cached data for a handle and re-fetch fresh data.
 */
export async function refreshUser(handle) {
  await api.delete(`/api/cf/user/${encodeURIComponent(handle)}`);
  return fetchUser(handle);
}

export default api;
