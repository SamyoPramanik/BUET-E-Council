import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

/**
 * REQUEST INTERCEPTOR
 * Automatically attaches the Session-ID header to every outgoing request
 */
api.interceptors.request.use(
  (config) => {
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
      // Note: We use the hyphenated 'Session-ID' to match your FastAPI alias
      config.headers['Session-ID'] = sessionId;

      if (!document.cookie.includes('session_id')) {
        document.cookie = `session_id=${sessionId}; path=/; samesite=lax;`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * RESPONSE INTERCEPTOR
 * Handles global errors like 401 Unauthorized
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear local storage so the Router Guard doesn't get stuck in a loop
      localStorage.clear();
      // Redirect to sign-in
      window.location.href = '/sign-in';
    }
    return Promise.reject(error);
  }
);

export default api;