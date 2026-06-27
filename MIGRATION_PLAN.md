# BUET E-Council — Vue → React Migration Plan

> Status: **planning document only**. No application code has been changed. This
> file, together with [COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md),
> [AUTH_MIGRATION.md](AUTH_MIGRATION.md), and [API_MIGRATION.md](API_MIGRATION.md),
> records the analysis and plan for migrating `front-end/` from Vue 3 to React.
> Companion document: see chat history for the full repo analysis this plan was
> derived from (architecture/frontend/backend/dependency review).

## 1. Goals & constraints (as given)

| Constraint | Implication |
|---|---|
| FastAPI backend remains unchanged | No edits anywhere under `back-end/` |
| API endpoints remain unchanged | The new frontend must speak the *exact* contracts in `back-end/app/schemas/*.py` and `back-end/app/models.py` — not the aspirational ones in `README.md`/`api.md` |
| Database remains unchanged | No migrations, no schema work |
| Podman/Docker setup remains unchanged | `docker-compose.yml`, `podman-compose.yaml`, `nginx/nginx.conf`, ports (5173 dev / 3000 build / 9001 nginx / 8000 api) must keep working with zero edits |
| Target framework | **React + Vite** (decided over Next.js — see §2) |

## 2. Why React + Vite, not Next.js

The current branch is named `nextjs-migration` and `.github/workflows/ci.yml` has
a step literally called *"Test Next.js Frontend Delivery"*. That is a leftover
naming choice, not a hard requirement — confirmed with the project owner.
**React + Vite was chosen** because it is a drop-in swap:

- `@vitejs/plugin-vue` → `@vitejs/plugin-react`, same dev port (5173), same
  `VITE_*` env-var prefix, same `dist/` build output, same `serve -s dist -l 3000`
  runtime.
- **Zero edits** to `front-end/Dockerfile`, `docker-compose.yml`, or
  `podman-compose.yaml` are required.
- Next.js would require `NEXT_PUBLIC_*` env vars, a different dev/start command
  and port-binding flags, and a different build output directory — all of which
  would force edits to the Dockerfile/compose files, conflicting with the
  "infra unchanged" constraint.

Action item: rename/remove the stale `nextjs-migration` branch name and the
`ci.yml` step name once the React app lands, to stop misleading future readers.

## 3. Ground truth vs. stale docs (read this before touching anything)

Three artifacts in this repo describe a **different, abandoned design** and must
**not** be used as a reference for the migration:

- `README.md` — describes JWT auth, Pinia, Alembic migrations, a `frontend/`
  (not `front-end/`) layout, and endpoints like `/api/auth/send-otp` that don't exist.
- `api.md` — describes a `{success, data, message}` response envelope, Bearer
  tokens, `/auth/signin`, `/members`, `/templates` — none of which exist in the code.
- `auth_service/`, `db/init.sql`, `db/init1.sql`, `test/auth_test.http` — a third,
  even older design (username/password, `moderator`/`member` roles). **Not wired
  into either compose file** — dead code, ignore entirely.

**The only source of truth is the code itself**: `back-end/app/models.py`,
`back-end/app/schemas/*.py`, `back-end/app/api/*.py`, and the current
`front-end/src/**` files. See [API_MIGRATION.md](API_MIGRATION.md) for the real
contract reference and [AUTH_MIGRATION.md](AUTH_MIGRATION.md) for the real auth flow.

## 4. Known pre-existing issues to carry forward as-is (not to "fix" silently)

These are quirks in the *current* Vue app. The migration should reproduce the
same observable behavior unless the team explicitly decides to fix them as a
separate change:

1. `v-click-outside` directive used in `ParticipantsSection.vue` is never
   registered globally (`main.js` has no `app.directive(...)`/`app.use(...)` for
   it) — it likely silently no-ops today. `Navbar.vue`'s manual
   `window.addEventListener('click', …)` pattern is the one that actually works.
2. `ParticipantsView.vue` calls `/buet-api/users/` and `/buet-api/department-head/`
   directly via `fetch()`. `vite.config.js`'s dev proxy only rewrites
   `/api/buet/*` — a different prefix — so these calls already 404 under raw
   `vite dev` / `podman-compose` (no nginx in front). Only nginx's
   `docker-compose.yml` path makes them work today.
2. `back-end/app/api/signature_cards.py` defines a `meetings_router` (with a
   docstring describing `GET/POST/PATCH/DELETE /meetings/{id}/signature-cards`)
   that is **never registered** in `main.py`. The real implementation of those
   routes lives in `back-end/app/api/meetings.py`'s own `router`. Don't be misled
   by the docstring — verified the actual route table in
   [API_MIGRATION.md](API_MIGRATION.md).
3. OTP verification in `back-end/app/api/auth.py` currently hardcodes acceptance
   of the literal code `"123456"` (real TOTP check is commented out), and OTP
   "sending" just prints to server logs. This is a backend behavior the frontend
   must simply tolerate — don't build any frontend logic that assumes real email
   delivery or real OTP validation.
4. `front-end/Containerfile` is orphaned (not referenced by either compose file).
   Leave it alone unless asked to clean it up.

## 5. Phased plan

| Phase | Scope | Depends on |
|---|---|---|
| 0 — Scaffold | New Vite+React app skeleton in `front-end/` (or a parallel dir, see §6), Tailwind v4 config ported, `vite.config.js` proxy rule ported | — |
| 1 — Foundation | Port `utils/api.js`, `utils/alerts.js`, `utils/validators.js`, build the auth store/context | Phase 0 |
| 2 — Leaf components | `ParticipantCard`, `SignatureCardItem`, `InsertStrip`, shell (`MainLayout`, `Navbar`, `Sidebar`) | Phase 1 |
| 3 — Rich text core | `RichTextEditor` via `@tiptap/react` | Phase 1 |
| 4 — Composite components | `MeetingSection`, `AgendaBox`, `SignatureCardsSection`, `ParticipantsSection` | Phases 2–3 |
| 5 — Auth views + router | `SignInView`, `VerificationView`, `UnauthorizedView`, route guards | Phase 1 |
| 6 — Standalone views | `ProfileView`, `MeetingsView`, `ParticipantsView` | Phases 2, 5 |
| 7 — Flagship view | `MeetingDetailsView` | Phases 3, 4 |
| 8 — Integration & QA | Manual pass against the live FastAPI backend (`docker-compose up`), verify both the build path (port 3000 via `serve`) and the dev path (port 5173 via `vite --host`, as used by `podman-compose.yaml`) | All above |

Full per-file detail (complexity / dependencies / React approach / effort) is in
[COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md).

## 6. Suggested working method

- Build the React app in a new sibling directory (e.g. `front-end-react/`) so the
  Vue app keeps running in `docker-compose`/`podman-compose` until the React app
  is feature-complete, then swap the compose `build.context` over in one commit.
  This avoids a half-migrated `front-end/` blocking the team's ability to demo or
  deploy mid-migration.
- Port one vertical slice at a time (e.g. "sign-in → OTP → profile" end-to-end)
  rather than all components of one type, so each slice can be manually verified
  against the real backend immediately.
- Do not introduce a new state-management library, API envelope, or response
  wrapper "while we're at it" — match the existing Vue app's level of abstraction
  (it has none beyond the single axios instance and one reactive auth singleton).

## 7. Dependency swap reference

| Vue package | Status | React replacement |
|---|---|---|
| `vue`, `vue-router` | replace | `react`, `react-dom`, `react-router-dom` |
| `@tiptap/vue-3` + the 8 extension packages actually imported in `RichTextEditor.vue` (`starter-kit`, `underline`, `text-align`, `text-style`, `font-family`, `table`, `table-row`, `table-cell`, `table-header`, `core`, `pm`) | replace | `@tiptap/react` + identical extension packages |
| `vue-toastification` | replace | `react-toastify` or `sonner` |
| `lucide-vue-next` | replace | `lucide-react` |
| `axios`, `sweetalert2` | keep | framework-agnostic, port files verbatim |
| `@vueuse/core` | **drop** | unused anywhere in `src/` |
| `vue-pdf-embed` | **drop** | unused anywhere in `src/` |
| `@tiptap/extension-bullet-list`, `-ordered-list`, `-list-item` | **drop** | redundant — `StarterKit` already bundles these |
| `@tiptap/extension-color` | **drop** | unused |
| `@tiptap/extension-font-size`, `tiptap-extension-font-size` | **drop** | unused — font-size is hand-rolled as a custom Tiptap `Extension` inside `RichTextEditor.vue`; port that custom extension's logic (it's framework-agnostic Tiptap code), not the npm packages |

## 8. Effort summary

See the per-file breakdown in [COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md).
Rolling up all 19 `.vue` files plus the 6 supporting JS modules (router, store,
api client, alerts, validators, entry point) gives **≈110–115 raw developer-hours**.
Adding ~30% buffer for integration testing, Tiptap/drag-and-drop edge cases, and
visual polish: **≈145–150 hours**, i.e. roughly **3.5–4 weeks for one developer**,
or **~2 weeks for two developers** splitting the component tree (one takes the
editor/agenda/signature stack, the other takes auth/views/router) along the
phase boundaries in §5.

These are rough planning numbers based on file size, prop/emit surface, and
third-party library complexity observed in the current Vue code — not a
formal estimate. Re-validate after Phase 0–1 land, since editor/drag-and-drop
porting time is the biggest source of estimate risk.
