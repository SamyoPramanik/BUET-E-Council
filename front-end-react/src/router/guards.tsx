import { useEffect, type ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../auth/AuthContext'

/**
 * Port of router/index.js's three `meta`-driven guards from the Vue app's
 * global `router.beforeEach`. React Router has no direct equivalent of
 * per-route `meta` + a single global hook, so each guard is its own wrapper
 * component applied per-route — same net effect.
 */

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    if (!isAuthenticated) toast.error('Please sign in to access this page.')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated])

  if (!isAuthenticated) return <Navigate to="/sign-in" replace />
  return <>{children}</>
}

export function GuestOnly({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/profile" replace />
  return <>{children}</>
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { userRole } = useAuth()

  useEffect(() => {
    if (userRole !== 'admin') toast.error('Access Denied: Admin privileges required.')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userRole])

  if (userRole !== 'admin') return <Navigate to="/profile" replace />
  return <>{children}</>
}

/**
 * Port of the `/admin-panel` route's `beforeEnter`, which has no component —
 * it just redirects to the FastAPI-rendered SQLAdmin app. This is a full
 * page navigation out of the SPA (not client routing), matching the
 * original's absolute http://localhost:8000/admin/ URL exactly.
 */
export function AdminPanelRedirect() {
  useEffect(() => {
    window.location.href = 'http://localhost:8000/admin/'
  }, [])
  return null
}
