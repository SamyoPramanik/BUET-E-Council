import api from '../utils/api'
import type { LoginResponse } from './types'

/** POST /auth/login — resolves with a new session on success. */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', { email, password })
  return data
}

/**
 * DELETE /auth/sign-out — deletes the current session server-side.
 * Relies on the axios interceptor in utils/api.ts to attach the
 * Session-ID header automatically from localStorage.
 */
export async function signOut(): Promise<void> {
  await api.delete('/auth/sign-out')
}
