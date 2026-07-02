# Auth Migration Notes

> **Update (2026-07-01):** The OTP flow described below has been **replaced**
> with email + password login. `POST /auth/request-otp` and
> `POST /auth/verify-otp` no longer exist. See the current flow in section 1
> below (updated in place) and [README.md](README.md#authentication) for the
> user-facing summary. Sections 2–3 are kept as historical record of the
> Vue → React port and are otherwise still accurate (session header/cookie
> handling, route guards, HTTP client) — only the login step itself changed.

Companion to [MIGRATION_PLAN.md](MIGRATION_PLAN.md). Documents the **real**
authentication flow (as implemented in code today, not as described in
older revisions of `README.md`) and how it's wired up in React.

## 1. What the backend actually does

The real flow, read from [back-end/app/api/auth.py](back-end/app/api/auth.py),
[back-end/app/dependencies.py](back-end/app/dependencies.py), and
[back-end/app/admin.py](back-end/app/admin.py):

1. `POST /auth/login` — body `{ email, password }`. Looks up the user and
   checks the password against `User.hashed_password` with bcrypt
   (`utils.verify_password`). On success it creates a `UserSession` row (UUID
   primary key, 7-day `expires_at`, captures `ip_address`/`user_agent`) and
   returns:
   ```json
   { "status": "success", "data": { "session_id": "<uuid>", "user_role": "admin|staff|viewer", "expires_at": "..." } }
   ```
   On failure it returns `401` with `{ "detail": "Invalid email or password." }`.
   There is no self-service sign-up — accounts only come from an admin via
   `POST /users` (see [API_MIGRATION.md](API_MIGRATION.md)), which generates or
   accepts a password and emails it via `utils.send_credentials_email`.
2. `POST /auth/change-password` — body `{ current_password, new_password }`,
   requires a valid session. Lets a logged-in user rotate their own password.
3. Every protected endpoint requires a `Session-ID` header (a raw UUID, not a
   signed token) — validated in `get_current_user` against the `UserSession`
   table's `expires_at`. `get_admin_user` layers a `role == "admin"` check.
4. `DELETE /auth/sign-out` — requires both the `Session-ID` header (to identify
   the caller) **and** a `Session-Id` header again as the literal session row to
   delete (`session_id: UUID = Header(...)` — same header read twice under the
   hood by FastAPI, not a bug to fix, just how it's wired).
5. The SQLAdmin panel at `/admin` (mounted in `admin.py`) authenticates
   **differently**: it reads `request.cookies.get("session_id")` — a **cookie**,
   not the header — and separately checks `role == "admin"`. This is why the
   SPA must keep a cookie in sync, not just `localStorage`.

CORS (`main.py`) allows `settings.FRONTEND_URL` (default
`http://localhost:5173`), a hardcoded `http://frontend:3000`, and any
`*.github.dev` origin, with `allow_credentials=True`. **Do not** change these —
they're backend config, not yours to touch — but the new frontend's origin must
keep matching one of them (it will, since React+Vite keeps the same ports).

## 2. What the current Vue app does (the contract to replicate)

[front-end/src/store/auth.js](front-end/src/store/auth.js) — a `reactive()`
singleton, **not Pinia**, holding `isAuthenticated`/`userEmail`/`userRole`
derived from `localStorage`, with `refresh()` (re-read from storage) and
`clear()` (wipe storage + expire the cookie) methods.

[front-end/src/utils/api.js](front-end/src/utils/api.js) — one `axios`
instance:
- Request interceptor: if `localStorage.session_id` exists, attach it as the
  `Session-ID` request header, **and** if `document.cookie` doesn't already
  contain `session_id`, write it there too (`session_id=<id>; path=/; samesite=lax`).
- Response interceptor: on any `401`, `localStorage.clear()` and hard
  `window.location.href = '/sign-in'` (a full page reload, not a router push —
  intentional, to guarantee a clean state reset).

[front-end/src/views/VerificationView.vue](front-end/src/views/VerificationView.vue)
— on successful `verify-otp`, writes `session_id`/`user_role`/`user_email` to
`localStorage`, **and separately** sets the `session_id` cookie itself
(`document.cookie = `session_id=${session_id}; path=/; samesite=lax;``), then
calls `authState.refresh()` so the Navbar updates without a reload.

[front-end/src/router/index.js](front-end/src/router/index.js) — a global
`router.beforeEach` implementing three guards read from route `meta`:
- `requiresAuth` + not authenticated → toast error, redirect to `SignIn`.
- `guestOnly` + authenticated → redirect to `profile`.
- `requiresAdmin` + `userRole !== 'admin'` → toast error, redirect to `profile`.

The `admin-panel` route has no component — its `beforeEnter` does
`window.location.href = 'http://localhost:8000/admin/'`, a **full page
navigation out of the SPA** to the FastAPI-rendered SQLAdmin app. This is
intentional: `/admin` is a separate server-rendered app, not part of the bundle.

## 3. React target design

### 3.1 Auth state

Replace the `reactive()` singleton with a small context + hook, preserving the
**exact same `localStorage` keys** (`session_id`, `user_role`, `user_email`,
`pending_email`) so nothing else (the axios client, the admin-panel link) needs
to change in lockstep:

```
AuthContext: { isAuthenticated, userEmail, userRole, refresh(), clear() }
```

`refresh()` and `clear()` keep doing exactly what they do today, including the
cookie write/expiry in `clear()`. Don't reach for Redux/Zustand unless the team
already wants it elsewhere — a `useReducer` + `localStorage` sync is enough; the
Vue app didn't need more than this either.

### 3.2 Route guards

`react-router-dom` has no built-in `meta` + global `beforeEach`. Two options,
pick one and apply consistently:

- **Wrapper components** (closest 1:1 mapping): `<RequireAuth>`,
  `<GuestOnly>`, `<RequireAdmin>` that read the auth context and either render
  `<Outlet/>` or `<Navigate to="/sign-in"/>` (with the same toast call before
  navigating, to match the current UX).
- **Loader-based** (React Router v6.4+ data APIs): a `requireAuth()` loader
  helper attached per-route. More idiomatic for the newer router APIs but a
  bigger structural change from the current file.

Either way, keep the `admin-panel` route's behavior as a **plain anchor /
`window.location.href`**, not a `<Link>` — it must leave the SPA entirely so the
browser sends the `session_id` cookie as a normal cross-document navigation,
matching what `admin.py`'s `AuthenticationBackend` expects.

### 3.3 HTTP client

Port `utils/api.js` verbatim — it's plain `axios`, no Vue dependency. Keep the
401-interceptor's hard `window.location.href` redirect (not a router
`navigate()`) — it's deliberately a full reload to guarantee no stale component
state survives a forced logout.

## 4. Things the frontend must **not** try to fix

- The frontend should just submit whatever email/password the user types and
  display whatever error the backend returns — don't validate password
  strength/format client-side beyond basic non-empty checks, since the backend
  is the source of truth.
- Don't switch to a JWT/Bearer pattern because older `README.md` revisions
  described one — the real backend has no token signing at all. Header-based
  opaque session IDs are the actual contract.
- Don't centralize session revocation differently than today — `ProfileView`'s
  "Revoke" (single session) and "Sign out from all devices" map to
  `DELETE /users/sessions/{id}` and `DELETE /users/sessions` respectively
  (see [API_MIGRATION.md](API_MIGRATION.md)); keep both.

## 5. Manual test checklist (run against the live `docker-compose` stack)

- [ ] Sign in with a registered email + correct password → lands on `/meetings`.
- [ ] Sign in with a wrong password → error toast, stays on `/sign-in`.
- [ ] Refresh the page while signed in → still authenticated (localStorage survives).
- [ ] Visit a `requiresAuth` route while signed out → toast + redirect to `/sign-in`.
- [ ] Visit `/sign-in` while already signed in → redirect to `/profile`.
- [ ] Visit `/admin-panel` as a non-admin → toast "Access Denied" + redirect to `/profile`.
- [ ] Visit `/admin-panel` as an admin → full-page navigation to `http://<host>:8000/admin/`, SQLAdmin loads without a second login prompt (cookie carried over).
- [ ] Visit `/staff` as a non-admin → toast "Access Denied" + redirect to `/profile`.
- [ ] Visit `/staff` as an admin → create an account, receive a toast confirming the email was sent, new account appears in the list and can log in with the emailed password.
- [ ] Sign out from the Navbar dropdown → localStorage cleared, cookie expired, redirected to `/sign-in`.
- [ ] In Profile, revoke a *different* session → toast success, list refreshes, you stay logged in.
- [ ] In Profile, revoke your *current* session (or "Sign out from all devices") → redirected to `/sign-in`, fully logged out.
- [ ] Force a `401` (e.g. manually clear `localStorage.session_id` then trigger an API call) → hard redirect to `/sign-in`, no stale UI flashes.
