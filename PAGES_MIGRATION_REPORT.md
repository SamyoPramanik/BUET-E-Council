# Pages Migration Report

Scope: **all remaining Vue pages and components**, completing the migration
started in [AUTH_MIGRATION_REPORT.md](AUTH_MIGRATION_REPORT.md). The Vue app
in `front-end/` was left untouched; `back-end/` was left untouched; only
`front-end-react/` was changed. This report documents what was ported, the
deliberate fixes made to actually satisfy "all pages must work perfectly,"
and exactly how that claim was verified.

## 1. What was added

```
front-end-react/src/
  types/api.ts                         shared backend response/request types
  utils/{alerts,validators}.ts         ported verbatim from Vue
  components/
    ParticipantCard.tsx
    SignatureCardItem.tsx(+.css)
    InsertStrip.tsx(+.css)
    Navbar.tsx
    Sidebar.tsx(+.css)
    RichTextEditor.tsx(+.css)          Tiptap editor (@tiptap/react)
    MeetingSection.tsx(+.css)
    AgendaBox.tsx(+.css)
    SignatureCardsSection.tsx(+.css)
    ParticipantsSection.tsx(+.css)
  layouts/MainLayout.tsx(+.css)
  views/
    UnauthorizedView.tsx
    SignInView.tsx / VerificationView.tsx   (wired to the existing auth layer)
    ProfileView.tsx
    MeetingsView.tsx
    ParticipantsView.tsx
    MeetingDetailsView.tsx(+.css)       the flagship view
  router/{index,guards}.tsx
```

Plus: `main.tsx` now mounts `<AuthProvider>` + `<App>` + a `<ToastContainer>`;
`App.tsx` is now `<RouterProvider router={router}/>`; `vite.config.ts` got the
`/api/buet` dev-proxy rule ported from the Vue app's `vite.config.js`; the
unused Vite demo scaffolding (`App.css`, demo SVGs/PNG, `icons.svg`) was
deleted since nothing references it anymore. New runtime dependencies:
`react-router-dom`, `react-toastify`, `sweetalert2`, `lucide-react`,
`@tiptap/react` + the same 8 extension packages the Vue app used, plus the
Tailwind v4 dev toolchain (`tailwindcss`, `@tailwindcss/postcss`,
`autoprefixer`, `postcss`).

## 2. Real bugs found and fixed during this migration

Porting line-for-line surfaced concrete defects that only show up when you
actually run the integration, not when reading the Vue source. All three were
confirmed by hitting a **real, unmodified FastAPI backend** (see §4) — not
guessed.

### 2.1 `PATCH /meetings/{id}/participants` — route shadowing (fixed in the frontend)

`back-end/app/api/meetings.py` registers `PATCH /{meeting_id}/participants`
(expecting a **bare JSON array** body: `[uuid, uuid, ...]`).
`back-end/app/api/participants.py` registers the **identical full path**
`PATCH /meetings/{meeting_id}/participants` expecting `{ "participant_ids":
[...] }`. `main.py` includes `meetings.router` before `participants.router`,
so FastAPI's first-match routing means **meetings.py's handler is the one
that actually runs** — `participants.py`'s is dead, unreachable code.

The Vue app's `ParticipantsSection.vue` sends `{ participant_ids: [...] }` —
the shape the *unreachable* handler expects. Verified live: this 422s against
the real backend. **Fixed** in `components/ParticipantsSection.tsx` to send
the bare array, matching the handler that actually executes. This is the one
substantive behavior change in this migration, made because "must work
perfectly" requires it and because backend changes were out of scope — full
detail and rationale is inline as a comment at the fix site.

### 2.2 `DELETE /meetings/{id}/files/{agenda|resolution}` — unfixable backend bug (documented, not patched)

`delete_agenda_pdf` (and the symmetric resolution handler) in
`back-end/app/api/meetings.py` calls `delete_file()` to remove the
`UploadedFile` row **before** nulling out `meeting.agenda_pdf` and
committing. Since the FK is still in place, `delete_file`'s own commit fails
with a `ForeignKeyViolation`; the handler's `except Exception: pass` swallows
that error but leaves the SQLAlchemy session in a poisoned state, so the very
next `session.commit()` two lines later raises `PendingRollbackError`, which
surfaces to the client as an unhandled `500`.

Confirmed live, with a full traceback (reproduced twice). This is a **backend
defect** — it cannot be fixed from the frontend, and the backend is out of
scope for this migration. `MeetingDetailsView.tsx`'s `deletePdf()` already
has a `try/catch` around this call (ported from the Vue app), so the UI
degrades gracefully — a toast error, not a crash — but the underlying
"Remove PDF" action will not actually remove the file while this backend bug
exists. A secondary symptom was also isolated and ruled out as unrelated: in
Node, axios's keep-alive HTTP agent hangs reusing the same TCP socket
immediately after that malformed 500 ("socket hang up"); forcing a fresh
connection for the next request resolved it instantly, proving it's an
artifact of one specific test client's connection reuse, not a second
backend bug or anything the React app's browser-based fetches would
necessarily inherit the same way.

### 2.3 Dead/unreachable component confirmed: `MeetingSection`

`MeetingSection.vue` (and therefore `MeetingSection.tsx`) is a real component
file in the Vue app, fully implemented, but **never imported or rendered
anywhere** — `MeetingDetailsView.vue`'s title/description/conclusion sections
are hand-rolled inline (plain `<textarea>` + `v-html`, not Tiptap JSON) and
never reach for this component. It was ported faithfully anyway, per
"convert all Vue components," and is available for future use, but is
currently unused by any page — exactly mirroring its status in the Vue app.

### 2.4 Other small, deliberate fixes (all additive, none narrow existing behavior)
- `ParticipantsSection`'s president-picker dropdown now actually
  closes on outside-click (the Vue app's `v-click-outside` directive was
  never registered and was a silent no-op — see `AUTH_MIGRATION.md`).
- `RichTextEditor`'s `applyBulletStyle`/`applyOrderStyle` walk up to the
  nearest **element** ancestor before looking for `<ul>`/`<ol>`; the Vue
  version's `node.closest?.()` silently no-ops when the selection resolves to
  a text node (the common case), so the bullet/number style picker likely
  rarely worked in the original.
- `Sidebar`'s two nav links now both use a real, working active-state
  mechanism (`NavLink`'s `isActive`) — but the *visual* outcome is
  preserved exactly: the Participants link's active class
  (`nav-item--active`) still has no CSS rule behind it, matching the Vue
  app's actual (inconsistent) rendered appearance today.

None of these touch the backend, the database, or any Docker/Podman file.

## 3. Routing — one structural fix vs. the literal Vue source

`router/index.js` nests `/sign-in`, `/verify`, and `/meetings/:id` as **array
children** of the `/` → `MainLayout` route, even though their own `path`
strings start with `/` and the file's own comments label them "Auth routes
(no shell)" / "Full-screen routes (no shell)". Because they're still
children of the `MainLayout` route record, vue-router renders MainLayout's
Sidebar+Navbar around them regardless of the comment's intent — for
`MeetingDetailsView`, which renders its own full-viewport header and sidebar
internally, that produces a visibly broken double-shell.

This port makes those three routes **siblings** of `/` instead — matching
the documented intent, and the only arrangement that doesn't double up
chrome around `MeetingDetailsView`. Full reasoning is inline as a comment in
`router/index.tsx`.

## 4. Verification

### 4.1 TypeScript — clean

```
npx tsc -b --force
(no output — success)
```

### 4.2 Production build — succeeds

```
> tsc -b && vite build
✓ 214 modules transformed
dist/assets/index-*.css     80.28 kB │ gzip:  15.47 kB
dist/assets/index-*.js   1,054.16 kB │ gzip: 315.78 kB
✓ built in 910ms
```

(One advisory-only warning about a >500kB chunk — `vite`/`rolldown`
suggesting code-splitting. Not an error; not addressed here since splitting
is an optimization decision, not a correctness one, and out of scope for a
migration task.)

### 4.3 Dev server — boots cleanly

`npm run dev -- --host` → `GET http://localhost:5173/` → `HTTP 200`, every
new module (router, all views, `RichTextEditor`) resolves with no console or
compile errors.

### 4.4 Backend integration — verified live, end-to-end, for every page

Static review isn't sufficient for "works perfectly," so — exactly as in the
auth-layer migration — a real, **unmodified** FastAPI backend was started
locally (isolated Postgres 16 cluster on a private port, the backend's own
`pyproject.toml` dependencies in a scratch venv, `uvicorn app.main:app`; no
Docker needed). A `User` (admin), `Faculty`, `Department`, and
`ParticipantCard` were seeded directly via the backend's own SQLModel
classes. A throwaway script then drove the project's real `utils/api.ts` /
`auth/authApi.ts` against it (browser globals shimmed, same technique as the
auth-layer report), exercising **every endpoint every migrated page calls**:

```
PASS  login as admin succeeds
PASS  GET /users/me returns user_info + sessions                       (ProfileView)
PASS  GET /participants returns array with seeded participant          (ParticipantsSection)
PASS  POST /meetings/ creates a meeting                                 (MeetingsView)
PASS  GET /meetings/ returns PaginatedMeetingResponse shape             (MeetingsView)
PASS  GET /meetings/{id} returns the created meeting                    (MeetingDetailsView)
PASS  PATCH /meetings/{id} updates title/description/conclusion         (MeetingDetailsView)
PASS  GET /meetings/{id}/participants starts empty                      (ParticipantsSection)
PASS  PATCH then GET /meetings/{id}/participants reflects the new member (fix #2.1)
PASS  PATCH /meetings/{id} sets president_card_id                       (ParticipantsSection)
PASS  POST /agendas/ creates an agendum                                  (MeetingDetailsView)
PASS  PATCH /agendas/{id} body round-trips as the same Tiptap JSON       (AgendaBox + RichTextEditor)
PASS  POST /resolutions/ creates a resolution                            (AgendaBox)
PASS  PATCH /resolutions/{id} body is reflected in the inline resolution (AgendaBox + RichTextEditor)
PASS  POST /files/upload stores the file                                (AgendaBox)
PASS  POST /agendas/{id}/files attaches the annexure                    (AgendaBox)
PASS  PATCH /agendas/{id}/files/{annexureId} reorder succeeds            (AgendaBox drag-reorder)
PASS  DELETE /agendas/{id}/files/{annexureId} removes the annexure       (AgendaBox)
PASS  DELETE /resolutions/{id} succeeds                                  (AgendaBox)
PASS  POST /signature-cards/ creates a card                             (SignatureCardsSection)
PASS  GET /signature-cards/ returns paginated catalogue                 (SignatureCardsSection)
PASS  PATCH /signature-cards/{id} updates content                       (SignatureCardsSection)
PASS  POST + GET /meetings/{id}/signature-cards attaches the card       (SignatureCardsSection)
PASS  PATCH /meetings/{id}/signature-cards/{id} reorder succeeds        (SignatureCardsSection drag-reorder)
PASS  DELETE /meetings/{id}/signature-cards/{id} detaches the card      (SignatureCardsSection)
PASS  DELETE /signature-cards/{id} (global delete) succeeds            (SignatureCardsSection)
PASS  POST /meetings/{id}/files/agenda attaches a PDF                   (MeetingDetailsView Materials)
PASS  GET /meetings/{id}/files/agenda streams the PDF back              (MeetingDetailsView Materials)
KNOWN BUG  DELETE /meetings/{id}/files/agenda 500s server-side — backend bug, see §2.2
PASS  DELETE /agendas/{id} succeeds                                     (MeetingDetailsView)
PASS  DELETE /users/sessions (revoke all) succeeds                      (ProfileView)

29 passed, 0 failed, 1 confirmed pre-existing backend bug (documented, not fixable from the frontend)
```

This confirms, against the real backend: request shapes match for every
endpoint; response shapes match the TS types in `types/api.ts` exactly;
the Tiptap JSON body round-trips byte-for-byte through `JSON.stringify`/
`JSON.parse`; file upload → attach → reorder → remove works end-to-end;
drag-reorder's N-sequential-PATCH pattern (no bulk endpoint exists) works;
and the one real bug that exists is in the backend, not in this port.

All test infrastructure (temp Postgres, venv, smoke-test script) was deleted
afterward. An incidental modification to tracked backend `.pyc` cache files
(from running the backend locally) was reverted both times. `git status`
confirms only the intended new files exist anywhere in the repo.

## 5. What "works perfectly" does **not** cover here

Be precise about the verification's actual ceiling, not just its floor:

- **No real browser was driven.** Everything above proves the network
  contract between this React app's code and the real backend is correct.
  It does not prove pixel-perfect visual fidelity, that every Tailwind class
  renders identically, or that interactive behaviors (drag-and-drop reorder
  *in a browser*, Tiptap's toolbar dropdown positioning, modal animations)
  feel right — there is no browser automation tool available in this
  environment. `npm run dev` was confirmed to boot and serve without error;
  manual click-through in an actual browser is the recommended next step
  before considering this production-ready.
- Visual transitions (`<Transition>` enter/leave animations in the Vue app's
  modals, the `InsertStrip` hover-reveal) were simplified to plain
  conditional rendering, or a CSS-only enter animation without an animated
  *exit* — functionally equivalent, marginally less polished on dismiss.
  Not addressed with an animation library since none was requested and the
  Vue app's effect was subtle.
- The known backend bug in §2.2 means "Remove PDF" does not actually work
  end-to-end yet — through no fault of this migration, and not fixable
  without backend changes that are explicitly out of scope.
