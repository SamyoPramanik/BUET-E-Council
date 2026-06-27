import axios from 'axios'

/**
 * Ported verbatim (logic-for-logic) from the Vue app's src/utils/api.js.
 * baseURL is intentionally a relative '/api' — this only resolves correctly
 * behind nginx's `location /api/ { proxy_pass http://backend:8000/; }` rule
 * (see nginx/nginx.conf and INFRA_COMPATIBILITY.md). It is NOT wired to
 * VITE_API_BASE_URL, matching the existing Vue app's behavior exactly.
 */
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * REQUEST INTERCEPTOR
 * Automatically attaches the Session-ID header to every outgoing request.
 */
api.interceptors.request.use(
  (config) => {
    const sessionId = localStorage.getItem('session_id')
    if (sessionId) {
      // Hyphenated 'Session-ID' to match the FastAPI header alias.
      config.headers.set('Session-ID', sessionId)

      if (!document.cookie.includes('session_id')) {
        document.cookie = `session_id=${sessionId}; path=/; samesite=lax;`
      }
    }
    return config
  },
  (error) => Promise.reject(error),
)

/**
 * RESPONSE INTERCEPTOR
 * Handles global errors like 401 Unauthorized.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear local storage so no stale state survives a forced logout.
      localStorage.clear()
      window.location.href = '/sign-in'
    }
    return Promise.reject(error)
  },
)

export default api
