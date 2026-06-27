# API Integration Migration Notes

Companion to [MIGRATION_PLAN.md](MIGRATION_PLAN.md). The backend, database, and
every endpoint are **unchanged** by this migration — this document exists so
the React data-fetching layer is built against the *real* contracts
(`back-end/app/schemas/*.py`, `back-end/app/models.py`, `back-end/app/api/*.py`)
instead of the stale `api.md`/`README.md`.

## 1. There is no response envelope

`api.md` claims every response looks like
`{ success, message, data: {...} }`. **That is not what the code does.**
Responses are bespoke Pydantic models returned directly, e.g.:

- `GET /meetings/` → `PaginatedMeetingResponse`: `{ total_count, page, limit, data: MeetingSummary[] }`
- `GET /meetings/{id}` → a bare `Meeting` row (the SQLModel object), not wrapped
- `GET /agendas/?meeting_id=...` → a bare `AgendumResponse[]` array
- `POST /agendas/` → a bare `AgendumResponse`

Build the React data layer to unwrap exactly what each endpoint actually
returns — check the `response_model=` on the specific route in
`back-end/app/api/*.py` before assuming a shape, don't generalize from one
endpoint to another.

## 2. Real route inventory (verified against `main.py`'s `include_router` calls)

| Router file | Mount prefix | Notes |
|---|---|---|
| `api/auth.py` | `/auth` | `request-otp`, `verify-otp`, `sign-out` — see [AUTH_MIGRATION.md](AUTH_MIGRATION.md) |
| `api/users.py` | `/users` | `GET /users/me`, `DELETE /users/sessions/{id}`, `DELETE /users/sessions` |
| `api/meetings.py` | `/meetings` | Meeting CRUD **and** meeting-level participants, PDFs, and signature-cards — see §3 below |
| `api/participants.py` | *(no prefix — paths are explicit)* | `GET /participants`, `GET /meetings/{id}/participants`, `PATCH /meetings/{id}/participants` |
| `api/agendas.py` | `/agendas` | Agenda CRUD + per-agendum files + PDF |
| `api/resolutions.py` | `/resolutions` | Resolution CRUD + per-resolution files + PDF |
| `api/files.py` | `/files` | Generic binary upload/delete, used by both agendas and resolutions |
| `api/signature_cards.py` | `/signature-cards` | Global signature-card catalogue CRUD only |
| `api/health.py` | *(none)* | `GET /health` |

⚠️ **Dead code warning**: `api/signature_cards.py` also defines a
`meetings_router = APIRouter(prefix="/meetings", ...)` with a docstring
describing `GET/POST/PATCH/DELETE /meetings/{id}/signature-cards`. **This
router is never registered in `main.py`** — only `signature_cards.router` is.
The real, live implementation of those meeting-level signature-card routes is
in `api/meetings.py` (lines ~479–641, using `meetings.py`'s own `router`). If
you go looking for "how does attaching a signature card to a meeting work,"
read `meetings.py`, not the docstring in `signature_cards.py`.

## 3. Full endpoint reference (grouped by resource, as actually called by the current frontend)

### Auth — see [AUTH_MIGRATION.md](AUTH_MIGRATION.md) for full detail
- `POST /auth/request-otp` `{ email }`
- `POST /auth/verify-otp` `{ email, code }` → `{ status, data: { session_id, user_role, expires_at } }`
- `DELETE /auth/sign-out` (header `Session-ID`)

### Users
- `GET /users/me` → `{ user_info: { email, role, ... }, sessions: [...] }`
- `DELETE /users/sessions/{session_id}`
- `DELETE /users/sessions` (revoke all)

### Meetings
- `POST /meetings/` `{ is_academic, serial_num, meeting_date }` → `Meeting`
- `GET /meetings/?is_academic=&page=&limit=` → `PaginatedMeetingResponse`
- `GET /meetings/{id}` → `Meeting`
- `PATCH /meetings/{id}` (partial — `MeetingUpdate` fields) → `Meeting`
- `GET /meetings/{id}/participants`
- `PATCH /meetings/{id}/participants` `{ participant_ids: [uuid] }`
- `POST /meetings/{id}/files/agenda` (multipart) / `GET` (streams) / `DELETE`
- `POST /meetings/{id}/files/resolution` (multipart) / `GET` (streams) / `DELETE`
- `GET /meetings/{id}/signature-cards` → `SignatureCardResponse[]`
- `POST /meetings/{id}/signature-cards` `{ signature_card_id, order }`
- `PATCH /meetings/{id}/signature-cards/{sig_id}` `{ order }`
- `DELETE /meetings/{id}/signature-cards/{sig_id}`
- `DELETE /meetings/{id}/signature-cards` (detach all)

### Participants
- `GET /participants` → `ParticipantRead[]` (global catalogue: `{ id, content, email }`)
- `GET /meetings/{id}/participants` → `ParticipantRead[]` (members of one meeting)
- `PATCH /meetings/{id}/participants` `{ participant_ids: [uuid] }` (same endpoint shape exists in both `participants.py` and `meetings.py` — the frontend currently calls the `meetings.py` one for writes and the bare `/participants` one for the global list)

### Agendas
- `GET /agendas/?meeting_id=` → `AgendumResponse[]`
- `POST /agendas/` `{ meeting_id, serial, is_supplementary }` → `AgendumResponse`
- `PATCH /agendas/{id}` (partial: `body` as a **JSON-stringified** Tiptap doc, `serial`, `is_supplementary`)
- `DELETE /agendas/{id}` (cascades resolution + files)
- `DELETE /agendas/` (delete all for a meeting — used by "Delete all regular/supplementary")
- `POST /agendas/{id}/files` `{ file_id, order }`
- `PATCH /agendas/{id}/files/{annexure_id}` `{ order }`
- `DELETE /agendas/{id}/files/{annexure_id}`
- `DELETE /agendas/{id}/files` (clear all)
- `GET /agendas/{id}/pdf` / `DELETE /agendas/{id}/pdf`

### Resolutions
- `POST /resolutions/` `{ agendum_id }` → `ResolutionResponse` (creates a blank resolution)
- `PATCH /resolutions/{id}` `{ body }` (JSON-stringified Tiptap doc)
- `DELETE /resolutions/{id}`
- `POST /resolutions/{id}/files` `{ file_id, order }`
- `PATCH /resolutions/{id}/files/{attachment_id}` `{ order }`
- `DELETE /resolutions/{id}/files/{attachment_id}`
- `DELETE /resolutions/{id}/files` (clear all)
- `GET /resolutions/{id}/pdf` / `DELETE /resolutions/{id}/pdf`

### Files (generic binary store)
- `POST /files/upload` — multipart `file` field → `UploadedFile` (`{ id, original_filename, mime_type, size_bytes, path, ... }`). Always called *before* the resource-specific "attach" call (two-step: upload, then `POST /agendas/{id}/files` or `POST /resolutions/{id}/files` with the returned `file_id`).
- `DELETE /files/{id}`

### Signature cards (global catalogue)
- `GET /signature-cards/?page=&limit=&search=` → `PaginatedSignatureCardResponse`
- `POST /signature-cards/` `{ content }` → `SignatureCardResponse`
- `PATCH /signature-cards/{id}` `{ content }`
- `DELETE /signature-cards/{id}` (removes globally — detaches from every meeting too)

### Health
- `GET /health` → `{ status: "ok" }`

## 4. Data-shape gotchas to preserve exactly

1. **Rich text bodies are JSON-as-text.** `Agendum.body` / `Resolution.body`
   are stored as a `TEXT` column containing a `JSON.stringify`'d Tiptap
   ProseMirror document. Every `PATCH` that touches `body` must
   `JSON.stringify()` the editor's `getJSON()` output before sending; every
   read must `JSON.parse()` it before feeding it back into the editor (and
   tolerate `null`/`"{}"`/invalid JSON → fall back to an empty doc, exactly
   like `parseBody()` in the current `AgendaBox.vue`).
2. **File attach is two HTTP calls, not one.** `POST /files/upload`
   (multipart) first, then `POST /agendas/{id}/files` or
   `POST /resolutions/{id}/files` with the returned `file_id` + an `order`.
   There is no single "upload and attach" endpoint.
3. **Reordering is N sequential/parallel `PATCH` calls, not a bulk endpoint.**
   Every drag-reorder feature (agenda annexures, resolution attachments,
   meeting signature-cards, meeting members-modal) persists by `PATCH`ing each
   item's `order`/`serial` field individually (`Promise.all(...)` or a `for`
   loop with sequential `await`). Don't build a bulk-reorder request — the
   backend doesn't have one, and adding one would violate "API endpoints
   remain unchanged."
4. **Agenda serial renumbering uses a two-pass offset trick.** When
   inserting/reordering agenda items, `MeetingDetailsView.vue` first
   `PATCH`es the affected items to `serial = OFFSET + i` (where
   `OFFSET = 10000`) to avoid transient unique/ordering collisions, then
   `PATCH`es them again to their real final `serial`. Port this exact two-pass
   algorithm (`shiftToOffset` / `assignFinalSerials` in the source) — it's
   working around real backend constraints, not incidental complexity.
5. **PDF download is a blob dance.** `GET .../pdf` (or `.../files/agenda`,
   `.../files/resolution`) is called with `responseType: 'blob'`, turned into
   an object URL, clicked via a manufactured `<a download>`, then
   `URL.revokeObjectURL`'d. Worth extracting into one
   `downloadBlob(blob, filename)` helper shared by all four PDF-download call
   sites (currently duplicated 1:1 in the Vue code).
6. **The "global participants list" vs. "meeting members" are different
   endpoints returning the same shape.** `GET /participants` (everyone) and
   `GET /meetings/{id}/participants` (this meeting's members) both return
   `ParticipantRead[]` — don't conflate the caching of one with the other.

## 5. External (non-FastAPI) integration — `ParticipantsView.vue`

This view bypasses `utils/api.js` and the FastAPI backend entirely, calling:
- `GET /buet-api/users/`
- `GET /buet-api/department-head/`

via raw `fetch()`. These relative paths only resolve correctly because
`nginx/nginx.conf` proxies `/buet-api/users/` and
`/buet-api/department-head/` straight through to BUET's real registry-office
PHP API (`regoffice.buet.ac.bd`). **This only works behind nginx**
(`docker-compose.yml`'s path) — under raw `vite dev` /
`podman-compose.yaml` (no nginx), these calls 404, because `vite.config.js`'s
dev proxy rewrites a *different* prefix (`/api/buet/*`, not `/buet-api/*`).

Decide explicitly when porting this view:
- **Reproduce as-is** (recommended for a pure migration): keep calling
  `/buet-api/...`, accept that it only works under the nginx-fronted compose
  path, exactly like today.
- **Fix the mismatch**: either change `vite.config.js`'s dev proxy to match
  `/buet-api`, or change the fetch calls to `/api/buet`. This is a real
  behavior change beyond a like-for-like migration — flag it to the team
  rather than silently changing it while porting.

Either way, this data does **not** go through `utils/api.js` (no
`Session-ID` header, no `withCredentials`) — don't accidentally route it
through the authenticated axios instance when porting; it must stay a plain
unauthenticated `fetch()` to keep matching the live PHP API's expectations.
Also note the response keys from that external API have trailing colons
(e.g. `"id:"`, `"name:"`) that the Vue code strips in a `normalise()` step —
preserve that normalization.

## 6. Recommended React data-layer shape

The Vue app has **no service/repository layer** — every component calls
`api.get(...)`/`api.post(...)` inline. Match that level of abstraction; don't
introduce a generated client, GraphQL layer, or repository pattern "while
we're at it" (see [MIGRATION_PLAN.md §6](MIGRATION_PLAN.md)). A reasonable,
equivalently-thin React structure:

- Keep one `api.js` (ported verbatim from `utils/api.js`) as the single axios instance.
- Either call `api.get/post/patch/delete(...)` directly inside components/hooks
  (closest match to current behavior), or wrap each call in a one-line custom
  hook (`useMeetings()`, `useAgendas(meetingId)`, etc.) **only** where a
  component would otherwise duplicate the same fetch — e.g. `MeetingDetailsView`
  and its children share meeting/agenda data today via props, not via a shared
  fetch hook, so don't introduce one unless restructuring data flow is an
  explicit goal.

## 7. CORS / credentials contract (do not change backend, but verify)

`back-end/app/main.py` allows origins `settings.FRONTEND_URL` (env-configurable,
default `http://localhost:5173`), `http://frontend:3000`, and `*.github.dev`,
with `allow_credentials=True` and `allow_headers=["*"]`. The React app must
keep sending `withCredentials: true` (already in `utils/api.js`) and the
`Session-ID` header on every authenticated request — both already satisfied by
porting `utils/api.js` verbatim. No backend changes needed as long as the React
dev server keeps running on the same ports (5173 dev / 3000 built) that
`FRONTEND_URL` and the hardcoded `http://frontend:3000` already cover.
