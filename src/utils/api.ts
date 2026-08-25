/// <reference types="vite/client" />

// API base URL configuration
// For local development: empty string (uses localhost:3000)
// For production: uses VITE_BACKEND_URL from environment variable
export const API_BASE = (import.meta.env.VITE_BACKEND_URL as string | undefined) || '';

export const apiCall = (endpoint: string, options?: RequestInit) => {
  const url = API_BASE + endpoint;
  return fetch(url, options);
};
