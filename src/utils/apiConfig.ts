import { Capacitor } from '@capacitor/core';

/**
 * Returns the environment-aware base URL for the backend API.
 * 
 * Resolution Order:
 * 1. import.meta.env.VITE_API_BASE_URL (explicit environment variable override)
 * 2. Capacitor Native Context:
 *    - Android: Defaults to 10.0.2.2:8000 (Android emulator alias to host localhost)
 *    - iOS / Native: Defaults to localhost:8000
 * 3. Desktop Web Browser:
 *    - Defaults to http://localhost:8000/api
 */
export function getApiBaseUrl(): string {
  // 1. Explicit environment variable override
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    return envUrl.trim().replace(/\/$/, '');
  }

  // 2. Capacitor Native platform check
  if (Capacitor.isNativePlatform()) {
    const platform = Capacitor.getPlatform();
    if (platform === 'android') {
      return 'http://10.0.2.2:8000/api';
    }
    return 'http://localhost:8000/api';
  }

  // 3. Desktop Web Browser default
  return 'http://localhost:8000/api';
}

/**
 * Returns a fully qualified API endpoint URL for a given relative path.
 * e.g., getApiEndpoint('health') -> 'http://localhost:8000/api/health'
 *       getApiEndpoint('/scan') -> 'http://localhost:8000/api/scan'
 */
export function getApiEndpoint(path: string): string {
  const baseUrl = getApiBaseUrl();
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  // If the path already begins with /api/, strip /api from baseUrl to prevent duplication
  if (cleanPath.startsWith('/api/')) {
    const baseWithoutApi = baseUrl.replace(/\/api$/, '');
    return `${baseWithoutApi}${cleanPath}`;
  }
  
  return `${baseUrl}${cleanPath}`;
}
