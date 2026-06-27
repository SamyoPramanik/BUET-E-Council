# Component & Page Migration Order

Companion to [MIGRATION_PLAN.md](MIGRATION_PLAN.md). Lists every `.vue` file in
`front-end/src/` plus the supporting (non-component) JS modules, in the order
they should be ported, with complexity, dependencies, the recommended React
approach, and an effort estimate. Ordering is **dependency-driven**: a
component is never scheduled before the things it imports.

Effort tiers used below: **Trivial** (<1h) · **Low** (1–3h) · **Medium** (4–6h)
· **High** (8–12h) · **Very High** (12–20h).

---

## Wave 0 — Foundation (not components, but block everything else)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/utils/validators.js](front-end/src/utils/validators.js) | Trivial (4 lines) | none | Port verbatim — plain JS, no Vue API used | Trivial |
| [src/utils/api.js](front-end/src/utils/api.js) | Low | `axios` | Port verbatim — the axios instance + interceptors (Session-ID header attach, cookie mirror, 401 hard-redirect) are framework-agnostic | Trivial |
| [src/utils/alerts.js](front-end/src/utils/alerts.js) | Low | `sweetalert2` | Port verbatim — `Swal` is vanilla JS | Trivial |
| [src/store/auth.js](front-end/src/store/auth.js) | Low | `vue` (`reactive`) | Replace with a small `AuthContext` + `useReducer`, or a `useSyncExternalStore` hook over the same `localStorage` keys (`session_id`, `user_role`, `user_email`). Must keep mirroring `session_id` into a cookie too — the FastAPI `/admin` panel reads it from there, not the header. See [AUTH_MIGRATION.md](AUTH_MIGRATION.md) | Low |
| [src/main.js](front-end/src/main.js) | Trivial | `vue`, `vue-toastification` | `ReactDOM.createRoot(...).render(<App/>)`; move toast plugin options into a `<ToastContainer position="bottom-right" .../>` (react-toastify) mounted once at the root | Trivial |

---

## Wave 1 — Leaf presentational components

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/views/UnauthorizedView.vue](front-end/src/views/UnauthorizedView.vue) | Trivial (9 lines) | `vue-router` (`router-link`) | Static JSX, `<Link to="/profile">` | Trivial |
| [App.vue](front-end/src/App.vue) | Trivial (4 lines) | `vue-router` (`router-view`) | `<Outlet/>` from `react-router-dom`, or just `<RouterProvider>` at the root | Trivial |
| [src/components/ParticipantCard.vue](front-end/src/components/ParticipantCard.vue) | Low (98 lines) | `lucide-vue-next` (`Mail`,`Check`), `navigator.clipboard` | Pure presentational function component; `computed` → inline derivations or `useMemo`; the `<component :is="copied ? Check : Mail">` dynamic-icon swap becomes `{copied ? <Check/> : <Mail/>}` | Low |
| [src/components/SignatureCardItem.vue](front-end/src/components/SignatureCardItem.vue) | Low (179 lines, mostly scoped CSS) | `lucide-vue-next` (`GripVertical`,`X`) | Function component + props; scoped `<style>` → CSS Modules or a plain `.css` import (class names are already unique/prefixed `sig-card__*`) | Low |
| [src/components/InsertStrip.vue](front-end/src/components/InsertStrip.vue) | Low (149 lines) | `vue-toastification` | `hovered` state → `useState`; `<Transition>` → CSS transition classes driven by the same state, or `framer-motion` if the team wants real exit animations (not required — current Vue version is enter/leave CSS classes only) | Low |
| [src/components/Navbar.vue](front-end/src/components/Navbar.vue) | Low (125 lines) | `vue-router`, `vue-toastification`, auth store | Manual click-outside via `useRef` + `useEffect(() => document.addEventListener('click', handler))` — this is the **working** pattern in the codebase (see [MIGRATION_PLAN.md §4](MIGRATION_PLAN.md)); `window.open('/admin/', ...)` stays a plain DOM call, not router navigation | Low |
| [src/components/Sidebar.vue](front-end/src/components/Sidebar.vue) | Low (160 lines, ~110 of which are scoped CSS) | `vue-router`, `lucide-vue-next`, auth store | `isExpanded` → `useState`; CSS ports almost unchanged (it's plain CSS with BEM-ish class names, not Vue-specific) | Low |
| [src/layouts/MainLayout.vue](front-end/src/layouts/MainLayout.vue) | Trivial (28 lines) | `Navbar`, `Sidebar`, auth store | Composes the two above + `<Outlet/>`; one computed → one boolean from context | Trivial |

---

## Wave 2 — Rich text core (everything else funnels through this)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/components/RichTextEditor.vue](front-end/src/components/RichTextEditor.vue) | **Very High** (517 lines) | `@tiptap/vue-3`, `@tiptap/starter-kit`, `@tiptap/extension-{underline,text-align,text-style,font-family,table,table-row,table-cell,table-header}`, `@tiptap/core` | Swap to `@tiptap/react`'s `useEditor`/`EditorContent` — the extension list, the hand-rolled `FontSize` custom `Extension.create()`, and the ProseMirror-JSON `v-model` content contract all port near 1:1 (Tiptap's extension API is framework-agnostic; only the Vue *binding* changes). The trickiest part is **not** Tiptap — it's the hand-built floating dropdowns (bullet/order/table-grid pickers) positioned via `getBoundingClientRect()` and rendered through `<Teleport to="body">`; in React use `createPortal(..., document.body)` + the same rect math in a `useLayoutEffect`. `v-bind(minHeight)` (dynamic CSS var) → inline `style={{ '--min-height': minHeight }}` or a CSS-in-JS equivalent | Very High |

---

## Wave 3 — Composite components (consume Wave 1 + Wave 2)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/components/MeetingSection.vue](front-end/src/components/MeetingSection.vue) | Medium (125 lines) | `RichTextEditor`, `lucide-vue-next`, `vue-toastification` | Generic "label + edit/save/cancel + dirty-check" wrapper around the editor. `props`/`emit('update:modelValue')` (Vue's `v-model` contract) → a controlled component with `value`/`onChange` props. Deep-clone-for-draft pattern (`JSON.parse(JSON.stringify(...))`) is plain JS, ports unchanged | Medium |
| [src/components/AgendaBox.vue](front-end/src/components/AgendaBox.vue) | **Very High** (625 lines) | `RichTextEditor` (×2 instances), `axios` (`utils/api.js`), `utils/alerts.js`, `vue-toastification` | The single most behavior-dense component: per-agendum edit/save/delete, two independent file lists (annexures + resolution attachments) each with upload (`FormData` multipart), remove, and native HTML5 drag-reorder (`onDragStart`/`onDragOver`/`onDragEnd` index-swapping — no library, ports directly to React drag handlers), inline resolution create/delete, and a `refetch()`-after-every-mutation pattern. Recommend porting the `watch(() => props.agendum.body, ...)` sync logic as a `useEffect` keyed on `agendum.id` to avoid stale local state when the parent list re-fetches | Very High |
| [src/components/SignatureCardsSection.vue](front-end/src/components/SignatureCardsSection.vue) | High (510 lines) | `SignatureCardItem`, `axios`, `utils/alerts.js`, `vue-toastification`, `lucide-vue-next` | Two independent drag-reorder lists (main grid + modal draft list), a paginated/debounced-search/infinite-scroll catalogue (`onScroll` near-bottom check), and a "create new card and attach in one action" flow. `<Teleport to="body">` for the modal → `createPortal`. Reorder persistence does **N sequential `PATCH` calls** (no bulk-reorder endpoint exists on the backend) — keep that exact pattern, don't invent a bulk endpoint | High |
| [src/components/ParticipantsSection.vue](front-end/src/components/ParticipantsSection.vue) | High (610 lines) | `ParticipantCard`, `axios`, `utils/alerts.js`, `vue-toastification`, `lucide-vue-next` | President picker (searchable dropdown, click-outside — same caveat as Navbar, the `v-click-outside` directive here is currently broken/unregistered, so just implement a working click-outside hook) + a members-management modal (search/add/remove + drag-reorder of a working draft list before "Save"). Two `defineEmits` (`president-updated`, `members-updated`) → two callback props from the parent (`MeetingDetailsView`) | High |

---

## Wave 4 — Auth views (need Wave 0's store/api, nothing else)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/views/SignInView.vue](front-end/src/views/SignInView.vue) | Low (105 lines) | `vue-router`, `vue-toastification`, `utils/validators.js`, auth store, `utils/api.js` | Plain controlled form + `onSubmit` calling `POST /auth/request-otp`; redirect via `useNavigate()` | Low |
| [src/views/VerificationView.vue](front-end/src/views/VerificationView.vue) | Medium (194 lines) | `vue-router`, `vue-toastification`, auth store, `utils/api.js` | 6-box OTP input with auto-advance-on-input, backspace-to-previous, and paste-splitting across boxes — port the `id="otp-{i}"` + `document.getElementById(...).focus()` pattern to `useRef` array; the `setInterval` countdown timer → `useEffect` with cleanup | Medium |

---

## Wave 5 — Router + guards (needs Waves 1 & 4 to exist as route targets)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/router/index.js](front-end/src/router/index.js) | Medium (104 lines) | `vue-router`, `vue-toastification`, auth store | `react-router-dom`'s `createBrowserRouter` with the same route tree (note the odd nesting in the source — `/sign-in` and `/verify` are declared as *children* of `MainLayout` in the array literal but have no `MainLayout` shell visually since they don't render `Navbar`/`Sidebar` content; verify intent before flattening). Re-implement the 3 guards (`requiresAuth`, `guestOnly`, `requiresAdmin`) as a `<RequireAuth>`/`<GuestOnly>`/`<RequireAdmin>` wrapper component each, or one parametrized `<ProtectedRoute>`. The `admin-panel` route's `beforeEnter` that does `window.location.href = '.../admin/'` stays a plain redirect (full page nav out of the SPA, not client routing — see [AUTH_MIGRATION.md](AUTH_MIGRATION.md)) | Medium |

---

## Wave 6 — Standalone views (independent of MeetingDetails)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/views/ProfileView.vue](front-end/src/views/ProfileView.vue) | Low–Medium (193 lines) | `vue-router`, `vue-toastification`, auth store, `utils/api.js`, `utils/alerts.js` | Session list table + revoke/revoke-all; straightforward data-fetch-and-render, no exotic Vue features | Medium |
| [src/views/MeetingsView.vue](front-end/src/views/MeetingsView.vue) | Medium (456 lines) | `vue-router`, `vue-toastification`, `utils/api.js`, auth store | Paginated/sortable/tabbed table + a "create meeting" modal with client-side validation. Client-side `.sort()` of the already-fetched page (not server-side) — port that as-is, it's a known simplification in the current app, not a bug to fix | Medium |
| [src/views/ParticipantsView.vue](front-end/src/views/ParticipantsView.vue) | Medium–High (741 lines, but ~360 of those are scoped CSS) | `lucide-vue-next`, raw `fetch()` (bypasses `utils/api.js` entirely) | Two parallel external-data tabs (BUET registry "users" + "dean/head"), client-side search-filter across normalized objects (keys with trailing colons stripped), deterministic avatar-hue-from-name hashing. **Decision needed before porting**: fix the `/buet-api` vs `/api/buet` dev-proxy prefix mismatch (see [MIGRATION_PLAN.md §4](MIGRATION_PLAN.md)) or reproduce it as-is | High |

---

## Wave 7 — Flagship view (depends on Waves 2, 3 being complete)

| File | Complexity | Dependencies | React approach | Effort |
|---|---|---|---|---|
| [src/views/MeetingDetailsView.vue](front-end/src/views/MeetingDetailsView.vue) | **Very High** (1004 lines) | `vue-router`, `vue-toastification`, `sweetalert2`, `lucide-vue-next`, auth store, `utils/alerts.js`, `ParticipantsSection`, `ParticipantCard`, `AgendaBox`, `InsertStrip`, `SignatureCardsSection` | The largest single unit. Distinct sub-problems to port separately and test separately: (1) **scrollspy** — `IntersectionObserver` per section + per agenda anchor, re-run on data changes (`nextTick(() => setTimeout(setupObservers, ...))`) → a `useEffect` that rebuilds observers on `agendas` change, cleaned up in the effect's return; (2) **4 inline-editable sections** (basic info / title / description / conclusion) each with its own edit-flag, a SweetAlert2 "confirm before save" gate, and a cancel-then-refetch; (3) **dual agenda lists** (regular vs. supplementary) with native drag-reorder *and* an offset-based renumbering algorithm (`shiftToOffset`/`assignFinalSerials`, using `OFFSET = 10000` to dodge serial collisions during reorder) — port this exact two-pass algorithm, it's load-bearing business logic, not incidental; (4) **PDF upload/download/delete** for both agenda and resolution packets, including the `responseType: 'blob'` + manufactured `<a download>` + `URL.revokeObjectURL` dance — a small `downloadBlob(blob, filename)` helper is worth extracting; (5) mobile sidebar overlay (`showSections` boolean + backdrop). Recommend splitting this single Vue file into several React components/hooks (e.g. `useScrollspy`, `useAgendaReorder`, `useMeetingPdf`) rather than one 1000-line component, but that's a structural improvement, not a requirement | Very High |

---

## Wave 8 — Integration

Not a file — a checklist:

- [ ] `docker-compose up --build` boots the React app on port 3000 behind nginx (9001) exactly like the Vue app did.
- [ ] `podman-compose up` runs the React app's dev server on 5173 via the same `npm run dev -- --host` command (no Containerfile build).
- [ ] CORS still works (`FRONTEND_URL` env var unchanged, `Session-ID` header + credentialed cookie still accepted).
- [ ] `/admin` (SQLAdmin) still reachable and authenticates via the mirrored cookie.
- [ ] Full manual pass through [AUTH_MIGRATION.md](AUTH_MIGRATION.md)'s test checklist.
- [ ] Full manual pass exercising every endpoint in [API_MIGRATION.md](API_MIGRATION.md)'s reference table from the actual UI.

---

## Summary table (quick reference)

| # | File | Wave | Complexity | Effort |
|---|---|---|---|---|
| 1 | utils/validators.js | 0 | Trivial | Trivial |
| 2 | utils/api.js | 0 | Low | Trivial |
| 3 | utils/alerts.js | 0 | Low | Trivial |
| 4 | store/auth.js | 0 | Low | Low |
| 5 | main.js | 0 | Trivial | Trivial |
| 6 | UnauthorizedView.vue | 1 | Trivial | Trivial |
| 7 | App.vue | 1 | Trivial | Trivial |
| 8 | ParticipantCard.vue | 1 | Low | Low |
| 9 | SignatureCardItem.vue | 1 | Low | Low |
| 10 | InsertStrip.vue | 1 | Low | Low |
| 11 | Navbar.vue | 1 | Low | Low |
| 12 | Sidebar.vue | 1 | Low | Low |
| 13 | MainLayout.vue | 1 | Trivial | Trivial |
| 14 | RichTextEditor.vue | 2 | Very High | Very High |
| 15 | MeetingSection.vue | 3 | Medium | Medium |
| 16 | AgendaBox.vue | 3 | Very High | Very High |
| 17 | SignatureCardsSection.vue | 3 | High | High |
| 18 | ParticipantsSection.vue | 3 | High | High |
| 19 | SignInView.vue | 4 | Low | Low |
| 20 | VerificationView.vue | 4 | Medium | Medium |
| 21 | router/index.js | 5 | Medium | Medium |
| 22 | ProfileView.vue | 6 | Low–Medium | Medium |
| 23 | MeetingsView.vue | 6 | Medium | Medium |
| 24 | ParticipantsView.vue | 6 | Medium–High | High |
| 25 | MeetingDetailsView.vue | 7 | Very High | Very High |

(25 rows = 19 `.vue` files + 6 supporting JS modules, matching the full inventory in `front-end/src/`.)
