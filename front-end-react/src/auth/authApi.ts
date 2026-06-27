import api from '../utils/api'
import type { RequestOtpResponse, VerifyOtpResponse } from './types'

/**
 * Typed wrappers around the 3 endpoints in back-end/app/api/auth.py.
 * These did not exist as standalone functions in the Vue app (the calls
 * were inlined in SignInView.vue / VerificationView.vue) — extracted here
 * because there is no page yet to inline them into.
 */

/** POST /auth/request-otp — always resolves 200, even for unknown emails. */
export async function requestOtp(email: string): Promise<RequestOtpResponse> {
  const { data } = await api.post<RequestOtpResponse>('/auth/request-otp', { email })
  return data
}

/** POST /auth/verify-otp — resolves with a new session on success. */
export async function verifyOtp(email: string, code: string): Promise<VerifyOtpResponse> {
  const { data } = await api.post<VerifyOtpResponse>('/auth/verify-otp', { email, code })
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
