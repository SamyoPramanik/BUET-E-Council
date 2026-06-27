/**
 * Shared backend response/request shapes.
 *
 * Source of truth: back-end/app/schemas/*.py and back-end/app/models.py —
 * NOT api.md or README.md, which describe a different, abandoned design
 * (see MIGRATION_PLAN.md §3). Only fields actually consumed by the Vue
 * frontend (and therefore by this port) are typed; relationship fields the
 * UI never reads directly (e.g. Meeting.members) are intentionally omitted.
 */
import type { UserRole } from '../auth/types'

// ── Users (back-end/app/api/users.py) ─────────────────────────────────────

export interface SessionInfo {
  id: string
  ip_address: string | null
  user_agent: string
  created_at: string
  expires_at: string
  is_current: boolean
}

export interface MeResponse {
  user_info: {
    email: string
    role: UserRole
  }
  sessions: SessionInfo[]
}

// ── Participants (back-end/app/schemas/participants.py) ──────────────────

export interface ParticipantRead {
  id: string
  content: string
  email: string | null
}

// ── Meetings (back-end/app/schemas/meetings.py + models.py's Meeting) ────

export interface MeetingSummary {
  id: string
  serial_num: number
  title_plain: string
  meeting_date: string | null
  is_finished: boolean
}

export interface PaginatedMeetingResponse {
  total_count: number
  page: number
  limit: number
  data: MeetingSummary[]
}

/** The bare SQLModel `Meeting` row, as returned by create/get/patch. */
export interface Meeting {
  id: string
  serial_num: number
  is_academic: boolean
  title: string
  description: string | null
  conclusion: string | null
  is_finished: boolean
  created_at: string
  meeting_date: string | null
  president_card_id: string | null
  agenda_pdf: string | null
  resolution_pdf: string | null
}

export interface MeetingCreate {
  is_academic: boolean
  serial_num: number
  meeting_date?: string | null
}

export interface MeetingUpdate {
  serial_num?: number
  is_academic?: boolean
  title?: string
  description?: string | null
  conclusion?: string | null
  is_finished?: boolean
  meeting_date?: string | null
  president_card_id?: string | null
}

export interface MeetingPDFResponse {
  meeting_id: string
  agenda_pdf: string | null
  resolution_pdf: string | null
}

// ── Files (back-end/app/api/files.py) ─────────────────────────────────────

export interface UploadedFile {
  id: string
  original_filename: string
  stored_filename: string
  path: string
  storage_key: string | null
  mime_type: string
  size_bytes: number
  uploaded_at: string
}

export interface AnnexureResponse {
  id: string
  file_id: string
  order: number
  original_filename: string
  mime_type: string
  size_bytes: number
  path: string
}

// ── Resolutions (back-end/app/schemas/resolutions.py) ─────────────────────

export interface InlineResolutionResponse {
  id: string
  body: string | null
  created_at: string
  updated_at: string | null
  attachments: AnnexureResponse[]
}

export interface ResolutionResponse {
  id: string
  body: string | null
  created_at: string
  updated_at: string | null
  agendum_id: string
  attachments: AnnexureResponse[]
}

// ── Agendas (back-end/app/schemas/agendas.py) ─────────────────────────────

export interface AgendumResponse {
  id: string
  serial: number
  body: string | null
  is_supplementary: boolean
  created_at: string
  updated_at: string | null
  meeting_id: string
  annexures: AnnexureResponse[]
  resolution: InlineResolutionResponse | null
}

export interface AgendumCreate {
  meeting_id: string
  serial: number
  is_supplementary?: boolean
}

export interface AgendumUpdate {
  body?: string
  serial?: number
  is_supplementary?: boolean
}

// ── Signature cards (back-end/app/schemas/signature_cards.py) ────────────

export interface SignatureCardResponse {
  id: string
  content: string
  created_at: string
}

export interface PaginatedSignatureCardResponse {
  total_count: number
  page: number
  limit: number
  data: SignatureCardResponse[]
}

// ── Generic Tiptap/ProseMirror document shape ─────────────────────────────
// Agendum.body / Resolution.body are stored as JSON.stringify'd Tiptap docs.
export interface TiptapDoc {
  type: 'doc'
  content?: unknown[]
}
