# Auth Migration Notes

Companion to [MIGRATION_PLAN.md](MIGRATION_PLAN.md). Documents the **real**
authentication flow (as implemented in code today, not as described in
`README.md`) and how to reproduce it in React without touching the backend.

## 1. What the backend actually does

There is **no JWT, no Pinia, no Bearer token** despite what `README.md` claims.
The real flow, read from [back-end/app/api/auth.py](back-end/app/api/auth.py),
[back-end/app/dependencies.py](back-end/app/dependencies.py), and
[back-end/app/admin.py](back-end/app/admin.py):

1. `POST /auth/request-otp` — body `{ email }`. Looks up the user, lazily
   creates a `pyotp` secret if missing, and **prints** the OTP to server logs
   (`print(f"--- DEBUG OTP: {otp_code} for {email} ---")`). Real email sending
   via `fastapi-mail` exists in `utils.py` but is commented out. Always returns
   `200` regardless of whether the email exists (anti-harvesting).
2. `POST /auth/verify-otp` — body `{ email, code }`. **The real TOTP check is
   commented out**; the endpoint currently hardcodes `if not code == "123456"`.
   On success it creates a `UserSession` row (UUID primary key, 7-day
   `expires_at`, captures `ip_address`/`user_agent`) and returns:
   ```json
   { "status": "success", "data": { "session_id": "<uuid>", "user_role": "admin|staff|viewer", "expires_at": "..." } }
   ```
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

- The hardcoded `"123456"` OTP check and disabled email sending are backend
  behavior. The React app should just submit whatever the user types and
  display whatever error the backend returns — don't hardcode `"123456"` into
  the frontend or special-case it.
- Don't switch to a JWT/Bearer pattern because `README.md` describes one — the
  real backend has no token signing at all. Header-based opaque session IDs are
  the actual contract.
- Don't centralize session revocation differently than today — `ProfileView`'s
  "Revoke" (single session) and "Sign out from all devices" map to
  `DELETE /users/sessions/{id}` and `DELETE /users/sessions` respectively
  (see [API_MIGRATION.md](API_MIGRATION.md)); keep both.

## 5. Manual test checklist (run against the live `docker-compose` stack)

- [ ] Sign in with a registered email → OTP screen → enter `123456` → lands on `/meetings`.
- [ ] Refresh the page while signed in → still authenticated (localStorage survives).
- [ ] Visit a `requiresAuth` route while signed out → toast + redirect to `/sign-in`.
- [ ] Visit `/sign-in` while already signed in → redirect to `/profile`.
- [ ] Visit `/admin-panel` as a non-admin → toast "Access Denied" + redirect to `/profile`.
- [ ] Visit `/admin-panel` as an admin → full-page navigation to `http://<host>:8000/admin/`, SQLAdmin loads without a second login prompt (cookie carried over).
- [ ] Sign out from the Navbar dropdown → localStorage cleared, cookie expired, redirected to `/sign-in`.
- [ ] In Profile, revoke a *different* session → toast success, list refreshes, you stay logged in.
- [ ] In Profile, revoke your *current* session (or "Sign out from all devices") → redirected to `/sign-in`, fully logged out.
- [ ] Force a `401` (e.g. manually clear `localStorage.session_id` then trigger an API call) → hard redirect to `/sign-in`, no stale UI flashes.
- [ ] Visit `/verify` directly without a `pending_email` in `localStorage` → redirected to `/sign-in` (the route's `beforeEnter` guard, ported to a loader/wrapper check).
