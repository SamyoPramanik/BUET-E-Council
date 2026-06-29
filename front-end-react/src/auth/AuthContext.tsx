import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { UserRole } from './types'

/**
 * React port of the Vue app's src/store/auth.js reactive() singleton.
 * Same localStorage keys (session_id, user_email, user_role), same
 * refresh()/clear() semantics — including clearing the session_id cookie
 * in clear(), which the FastAPI /admin (SQLAdmin) panel depends on.
 */
interface AuthState {
  isAuthenticated: boolean
  userEmail: string
  userRole: UserRole | ''
}

interface AuthContextValue extends AuthState {
  /** Re-read auth state from localStorage (call after login/verify). */
  refresh: () => void
  /** Wipe localStorage + expire the session_id cookie (call on logout). */
  clear: () => void
  /**
   * Update the in-memory email/role only — does NOT touch localStorage.
   * Mirrors the Vue app's ProfileView.vue directly mutating
   * `authState.userEmail`/`authState.userRole` after a `/users/me` refetch
   * (a live UI sync, intentionally not persisted until the next real login).
   */
  setUserInfo: (info: { email: string; role: UserRole }) => void
}

function readAuthState(): AuthState {
  return {
    isAuthenticated: !!localStorage.getItem('session_id'),
    userEmail: localStorage.getItem('user_email') ?? '',
    userRole: (localStorage.getItem('user_role') as UserRole | null) ?? '',
  }
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => readAuthState())

  const refresh = useCallback(() => {
    setState(readAuthState())
  }, [])

  const clear = useCallback(() => {
    localStorage.clear()
    document.cookie = 'session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    setState(readAuthState())
  }, [])

  const setUserInfo = useCallback(({ email, role }: { email: string; role: UserRole }) => {
    setState((prev) => ({ ...prev, userEmail: email, userRole: role }))
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ ...state, refresh, clear, setUserInfo }),
    [state, refresh, clear, setUserInfo],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>')
  }
  return ctx
}
