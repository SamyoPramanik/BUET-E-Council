# Auth Migration Report

Scope of this change: **the authentication layer only**, in
`front-end-react/`. No Vue pages were migrated, `App.tsx` still renders the
default Vite scaffold content, and no Vue or backend source files were
modified. This report documents exactly what was added, how it was verified,
and what is intentionally still missing (because it belongs to a page, not
the auth layer).

## 1. Files added

```
front-end-react/src/utils/api.ts        — axios instance + interceptors
front-end-react/src/auth/types.ts       — UserRole / response shape types
front-end-react/src/auth/authApi.ts     — requestOtp / verifyOtp / signOut
front-end-react/src/auth/AuthContext.tsx — AuthProvider + useAuth() hook
```

**Files modified:**

```
front-end-react/src/main.tsx  — wraps <App/> in <AuthProvider>
front-end-react/package.json  — added `axios` as a real dependency
```

`App.tsx` itself was **not touched** — it still renders the unmodified Vite
scaffold. `<AuthProvider>` wraps it so the context is mountable and testable,
without pulling any auth UI into a page yet.

## 2. What was ported, and from where

| New file | Ported from (Vue) | Change |
|---|---|---|
| `src/utils/api.ts` | `front-end/src/utils/api.js` | Logic ported 1:1 (axios instance, `Session-ID` header attach, cookie mirror, 401 → `localStorage.clear()` + hard redirect). Typed; header mutation uses `config.headers.set(...)` (axios v1's `AxiosHeaders` API) instead of bracket assignment, for TS correctness — behavior is identical. |
| `src/auth/AuthContext.tsx` | `front-end/src/store/auth.js` | Vue's `reactive()` singleton replaced with a React `Context` + `useState`/`useCallback`/`useMemo`, exposing the same shape: `isAuthenticated`, `userEmail`, `userRole`, `refresh()`, `clear()`. **Same `localStorage` keys** (`session_id`, `user_email`, `user_role`) and the **same cookie-expiry line** in `clear()` — this is load-bearing: the FastAPI `/admin` (SQLAdmin) panel reads `session_id` from a cookie, not the header (see `back-end/app/admin.py`), so `clear()` must keep expiring it exactly as before. |
| `src/auth/authApi.ts` | Inlined in `SignInView.vue` / `VerificationView.vue` | New file — these calls didn't exist as standalone functions in Vue (they were inline `axios.post(...)` calls inside components). Extracted into typed functions (`requestOtp`, `verifyOtp`, `signOut`) since there is no page yet to inline them into. |
| `src/auth/types.ts` | — | New — `UserRole` matches `back-end/app/models.py`'s actual enum (`staff \| viewer \| admin`), **not** the README's `admin/moderator/member`. |

## 3. Scope boundary (why these endpoints and not others)

Only the 3 endpoints in `back-end/app/api/auth.py` were wrapped:
`POST /auth/request-otp`, `POST /auth/verify-otp`, `DELETE /auth/sign-out`.

**Deliberately excluded** (belong to a page, not the auth layer, per
[AUTH_MIGRATION.md](AUTH_MIGRATION.md) and
[COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md)):
- `GET /users/me`, `DELETE /users/sessions/{id}`, `DELETE /users/sessions` —
  these are `users.py` endpoints consumed by `ProfileView.vue`'s session-management
  UI, not by the sign-in flow. Out of scope until `ProfileView` is migrated.
- Route guards (`RequireAuth`/`GuestOnly`/`RequireAdmin`) — not added yet,
  since there's no router and no pages to guard. `react-router-dom` was
  **not** installed in this change for the same reason.
- A toast/alert library — the Vue auth flow's 401 handling doesn't use toasts
  (it just clears storage and redirects); toasts are only used by the *pages*
  (`SignInView`, `VerificationView`), which are out of scope here.

## 4. A real finding made during verification (not a bug I introduced)

While live-testing `signOut()` called twice in a row with the same session, I
initially expected the second call to 404 (`back-end/app/api/auth.py`'s
`sign_out` has an explicit `if not session_record: raise 404` branch). It
actually returns **401**, not 404. Reason: `sign_out`'s `current_user: User =
Depends(get_current_user)` dependency runs first and independently re-validates
the same `Session-ID` header against the `UserSession` table; since the first
call already deleted that row, the dependency itself fails with 401 *before*
the endpoint body's own 404 check ever runs. That 404 branch is effectively
unreachable in practice (both reads come from the identical header). This is
a pre-existing backend characteristic, not something this change touched —
documented here because it shaped the test's expected status code, and
because it means a 401 from a "second sign-out" is correctly handled by the
existing 401 interceptor in `api.ts` (clears storage, redirects) — which is
actually the desirable outcome anyway.

## 5. Verification

### 5.1 `npx tsc -b --force` — TypeScript passes

```
(no output — success)
```

### 5.2 `npm run build` — succeeds

```
> front-end-react@0.0.0 build
> tsc -b && vite build

vite v8.1.0 building client environment for production...
✓ 21 modules transformed.   (was 20 before this change — +1 for the new auth modules graph)
dist/index.html                   0.46 kB
dist/assets/index-BSTdr-tk.js   193.91 kB │ gzip: 60.91 kB
✓ built in 124ms
```

### 5.3 `npm run dev` — boots cleanly

Started the dev server, confirmed `GET http://localhost:5173/` returns `HTTP
200` and that `main.tsx`'s transformed output correctly resolves the new
`AuthProvider` import with no console/compile errors:

```
GET / -> HTTP 200
...
import { AuthProvider } from "/src/auth/AuthContext.tsx";
  VITE v8.1.0  ready in 140 ms
```

### 5.4 Existing backend endpoints remain compatible — verified live, end-to-end

Static contract review isn't enough to claim "compatible," so a real,
throwaway instance of the **actual, unmodified** FastAPI backend was started
locally (isolated Postgres 16 cluster on a private port, the backend's real
`pyproject.toml` dependencies installed into a scratch venv, `app.main:app`
run via `uvicorn` — no Docker required, since the daemon wasn't reachable in
this sandbox; see [INFRA_COMPATIBILITY.md](INFRA_COMPATIBILITY.md) for that
constraint). One real `User` row was seeded directly via `app.models.User`
(the backend's own model class, not a fixture reimplementation). The new
`authApi.ts`/`api.ts` modules were then imported and exercised with the
browser globals they depend on (`localStorage`, `document.cookie`,
`window.location`) shimmed, via `npx tsx`, against the live backend:

```
PASS  requestOtp(known email) resolves
PASS  requestOtp(unknown email) still resolves 200
PASS  verifyOtp(wrong code) rejects with backend detail message
PASS  verifyOtp(correct code) returns session_id + user_role
PASS  signOut() succeeds using the interceptor-attached Session-ID header
PASS  second signOut() correctly 401s — session was really deleted server-side
PASS  protected call with invalid session returns 401
PASS  401 interceptor cleared localStorage
PASS  401 interceptor redirected to /sign-in

9 passed, 0 failed
```

This confirms, against the real backend (not a mock):
- Request shapes match (`{ email }`, `{ email, code }` JSON bodies).
- The `Session-ID` header is correctly attached by the request interceptor
  and accepted by `get_current_user`.
- Response shapes match the TS types exactly (`{ status, data: { session_id,
  user_role, expires_at } }`).
- Error responses are surfaced in the shape the future sign-in UI will need
  (`error.response.data.detail`).
- The 401 interceptor's side effects (clear `localStorage`, redirect to
  `/sign-in`) actually fire on a real 401 from the real backend.

The test script and the temporary isolated Postgres/venv were both deleted
after the run — `front-end-react/src/` contains only the 4 files listed in §1
plus the pre-existing scaffold; `git status` shows no other changes anywhere
in the repo (including no stray modifications to `back-end/`'s tracked
`__pycache__` files, which running the backend locally incidentally touched
and which were reverted with `git checkout --`).

## 6. What's intentionally still missing

- No UI. There is no sign-in form, no OTP-entry screen, and no way to trigger
  this code from the running app yet — by design, per "do not migrate any
  pages yet."
- No router, no route guards — nothing to guard without pages.
- No toast/alert library — not needed by the auth layer itself.
- `vite.config.ts` still has no dev-proxy rule — not needed yet since nothing
  calls the live backend from the browser at this stage; required before any
  page that calls the backend in dev mode is migrated (see
  [INFRA_COMPATIBILITY.md §6](INFRA_COMPATIBILITY.md)).

Next step per [COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md)
would be Wave 4 (`SignInView`, `VerificationView`) — the first actual pages,
which would consume `authApi.ts` and `useAuth()` from this change.
