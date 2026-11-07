const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || "";

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");

export function getApiUrl(path) {
  if (!path) return API_BASE_URL;
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}
