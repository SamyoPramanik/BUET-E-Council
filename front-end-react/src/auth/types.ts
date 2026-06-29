/**
 * Mirrors back-end/app/models.py's UserRole enum exactly
 * (staff | viewer | admin) — not the README's admin/moderator/member.
 */
export type UserRole = 'staff' | 'viewer' | 'admin'

/** Response body of POST /auth/request-otp (back-end/app/api/auth.py). */
export interface RequestOtpResponse {
  message: string
}

/** Response body of POST /auth/verify-otp on success. */
export interface VerifyOtpResponse {
  status: 'success'
  data: {
    session_id: string
    user_role: UserRole
    expires_at: string
  }
}

/** Shape of the FastAPI error body, e.g. { "detail": "Invalid or expired OTP code." } */
export interface ApiErrorBody {
  detail?: string
}
