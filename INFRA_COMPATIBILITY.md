# Infra Compatibility — `front-end-react/` vs. existing infrastructure

Companion to [MIGRATION_PLAN.md](MIGRATION_PLAN.md). Verifies that the new
`front-end-react/` scaffold (Vite 8 + React 19 + TypeScript, created via
`npm create vite@latest -- --template react-ts`) can slot into the *existing*
`docker-compose.yml`, `podman-compose.yaml`, Dockerfiles, and nginx config with
**zero edits to those files**, before any Vue page is ported.

**Method**: rather than reasoning about this in the abstract, each claim below
was actually executed against the real scaffold (dev server, production build,
the `serve` static server, env-var inlining) and is marked accordingly. One
item (a literal `docker build`) could not be executed because no Docker daemon
is reachable in this analysis sandbox (`docker` CLI present, but
`/var/run/docker.sock` / Docker Desktop socket not available) — that gap is
called out explicitly in §3 rather than glossed over. No files in the repo
were modified by this verification; a temporary probe added to `App.tsx` for
the env-var test was reverted immediately (`git status` confirms `front-end-react/`
is still a single untracked, unmodified directory).

## 1. `docker-compose.yml` compatibility

```yaml
frontend:
  build:
    context: ./front-end
    dockerfile: Dockerfile
    args:
      VITE_API_BASE_URL: ${BACKEND_URL}/api
      VITE_API_INTERNAL_URL: http://backend:8000
  healthcheck:
    test: ["CMD-SHELL", "wget --spider -q http://localhost:3000 || exit 1"]
```

**Compatible, with one required change at cutover time**: `context: ./front-end`
must become `context: ./front-end-react` (and the `frontend` Dockerfile must
exist there — see §3). Nothing else in this block needs to change:

- The two build `args` are plain `VITE_*`-prefixed strings — **verified**
  these get inlined into the production bundle by Vite 8 exactly like Vite 7
  did for the Vue app (built with `VITE_INFRA_PROBE=infra_probe_value_12345
  npm run build` and confirmed the literal value appears in
  `dist/assets/*.js`).
- The healthcheck (`wget --spider -q http://localhost:3000`) — **verified**
  against the real build output: `npm run build` → `npx serve -s dist -l 3000`
  → `wget --spider -q http://localhost:3000` exits `0`.
- No port is published for `frontend` here (commented out) — nginx reaches it
  over the compose network on 3000, which `serve -s dist -l 3000` satisfies
  unchanged.
- `depends_on: backend: condition: service_healthy` — unaffected, no change needed.

## 2. `podman-compose.yaml` compatibility

```yaml
frontend:
  image: node:22-alpine
  working_dir: /app
  volumes:
    - ./front-end:/app
    - /app/node_modules
  ports:
    - "5173:5173"
  environment:
    - VITE_API_BASE_URL=http://localhost:8000
  command: sh -c "npm install && npm run dev -- --host"
```

**Compatible, with one required change at cutover time**: the two `./front-end`
volume mounts become `./front-end-react`. Nothing else changes:

- This service **never builds an image** — it bind-mounts source into a stock
  `node:22-alpine` and runs `npm install && npm run dev -- --host` directly.
  That command is framework-agnostic; it doesn't care whether `package.json`
  describes a Vue or React app.
- **Verified** `npm run dev -- --host` works against the new scaffold exactly
  as it does today: ran it, confirmed Vite reports `Local: http://localhost:5173/`
  and `Network: http://10.18.100.208:5173/` (i.e. bound to `0.0.0.0`, not just
  loopback) — required for the container's published port mapping to work.
- The anonymous `/app/node_modules` volume trick (to avoid host/container
  `node_modules` collisions) is unaffected by the app's framework.
- `VITE_API_BASE_URL` env var — same `VITE_` prefix convention, picked up the
  same way (see §5).

## 3. Existing Dockerfile/Containerfile requirements

### `front-end/Dockerfile` (the one actually used by `docker-compose.yml`)

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ARG VITE_API_INTERNAL_URL
ENV VITE_API_INTERNAL_URL=$VITE_API_INTERNAL_URL
RUN npm run build
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

**Fully compatible, copy-paste reusable as-is** for `front-end-react/` — every
step was independently verified outside the container:
- `npm install` then `npm run build` → confirmed `tsc -b && vite build`
  succeeds and writes to `dist/` (the directory `serve -s dist` expects — same
  output directory name as the Vue app, no path change needed).
- `npm install -g serve` + `serve -s dist -l 3000` → confirmed serves with
  HTTP 200 and passes the `wget --spider` healthcheck (§1).
- **musl/Alpine compatibility** (the one thing that *could* differ between the
  Vue and React toolchains): Vite 8's new native-binary dependencies
  (`rolldown` replaces esbuild; `lightningcss` replaces postcss-for-CSS-minify)
  and `oxlint` all publish `linux-x64-musl` / `linux-arm64-musl` prebuilt
  binaries on npm (confirmed via `npm view <pkg> optionalDependencies`) — so
  `npm install` inside `node:22-alpine` (musl libc) will resolve correctly,
  same as it already does for the Vue app's Vite 7 + esbuild stack today.
- **Not independently verified**: an actual `docker build` of this Dockerfile
  against the `front-end-react` context, because no Docker daemon is reachable
  in this sandbox. Every individual step it performs was verified outside the
  container; recommend the team run one real `docker build -f front-end/Dockerfile
  front-end-react` (or just flip the compose `context:` at cutover and run
  `docker compose build frontend`) as the final confirmation once Docker is
  available.

**One gap to close before cutover**: `front-end-react/` has no `.dockerignore`
yet (the Vite scaffolder doesn't generate one). `front-end/.dockerignore`
excludes `node_modules`, `dist`, `.vite`, `.cache`, logs — copy that same file
into `front-end-react/` before pointing the Docker build context at it,
otherwise a local `npm install`/`npm run build` run before the Docker build
will bloat the build context unnecessarily (functionally harmless since `COPY
package*.json` + `RUN npm install` still wins, but slow and wasteful).

### `front-end/Containerfile` (nginx multi-stage build)

```dockerfile
FROM docker.io/library/node:20-alpine AS build-stage
...
FROM docker.io/library/nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Not relevant to this migration — confirmed dead and confirmed broken**:
neither `docker-compose.yml` nor `podman-compose.yaml` references this file at
all (re-confirmed: `grep -rn "Containerfile" docker-compose.yml
podman-compose.yaml` matches nothing in `docker-compose.yml` and only the
*backend's* `Containerfile` in `podman-compose.yaml`). It is also **not even
buildable as written**: it does `COPY nginx.conf /etc/nginx/conf.d/default.conf`,
but there is no `nginx.conf` file anywhere inside `front-end/` (only
`./nginx/nginx.conf` at the repo root, a different file, in a different
directory, not in this build's context). Leave this file alone; it requires no
action for the React migration to proceed.

## 4. Nginx routing requirements

```nginx
location / {
    proxy_pass http://frontend:3000;
}
location /api/ {
    proxy_pass http://backend:8000/;
}
location /admin/ {
    proxy_pass http://backend:8000/admin/;
}
location /buet-api/department-head/ { proxy_pass https://regoffice.buet.ac.bd/...; }
location /buet-api/users/           { proxy_pass https://regoffice.buet.ac.bd/...; }
```

**Zero changes required, by construction** — nginx only knows the `frontend`
service by its compose network alias and port (3000), which `serve -s dist -l
3000` continues to provide unchanged (§1, §3). Nginx has no awareness of what
framework built the static files it's proxying to. The `/api/`, `/admin/`, and
`/buet-api/*` rules proxy to the *backend* and to BUET's external API
respectively — both completely independent of the frontend framework choice.

One **forward-looking note**, not a compatibility issue today: when
`ParticipantsView` is eventually ported (Wave 6 per
[COMPONENT_MIGRATION_ORDER.md](COMPONENT_MIGRATION_ORDER.md)), its `fetch()`
calls to `/buet-api/users/` and `/buet-api/department-head/` will only resolve
correctly behind this nginx config (i.e. under `docker-compose`, not under
`podman-compose`'s raw `vite dev`) — same caveat that exists for the Vue app
today, documented in [API_MIGRATION.md §5](API_MIGRATION.md). Not something to
address now, since no pages are migrated yet.

## 5. Environment variables

| Variable | Where it's set | Consumed by | Verified |
|---|---|---|---|
| `VITE_API_BASE_URL` | `docker-compose.yml` build arg (`${BACKEND_URL}/api`); `podman-compose.yaml` plain env (`http://localhost:8000`) | Vite inlines into the client bundle at build/dev time via `import.meta.env.VITE_API_BASE_URL` | ✅ build-time inlining proven with a temporary probe (`VITE_INFRA_PROBE=infra_probe_value_12345 npm run build` → value found in `dist/assets/*.js`); no app code references real `VITE_*` vars yet since no pages are migrated |
| `VITE_API_INTERNAL_URL` | `docker-compose.yml` build arg (`http://backend:8000`) | Same mechanism | Same as above — not yet referenced by any component (no pages ported) |
| `BACKEND_URL`, `FRONTEND_URL` | Injected into `.env` on the Azure VM by `.github/workflows/deploy.yml` from GitHub Actions vars | Read by `docker-compose.yml`'s `${BACKEND_URL}` interpolation and by the **backend's** `FRONTEND_URL` setting (CORS) — not frontend code directly | No change needed; backend is untouched and these are compose/deploy-level, not framework-level |

Mechanism is identical to the Vue app: only variables prefixed `VITE_` are
exposed to client code via `import.meta.env`, and only ones actually
*referenced* by source code survive dead-code elimination into the bundle —
this is a Vite behavior, not a Vue or React one, so nothing here changes by
switching frameworks. No backend env vars need touching.

## 6. Development workflow

| Step | Vue (today) | React (`front-end-react/`) | Status |
|---|---|---|---|
| Local dev (no Docker) | `cd front-end && npm install && npm run dev` → `http://localhost:5173` | `cd front-end-react && npm install && npm run dev` → `http://localhost:5173` | ✅ verified, identical |
| Containerized dev (`podman-compose up`) | bind-mount + `npm run dev -- --host`, port 5173 | same command, same port | ✅ verified (`--host` binds `0.0.0.0`, matches container port-mapping needs) |
| Hot reload | Vite HMR via `@vitejs/plugin-vue` | Vite HMR via `@vitejs/plugin-react` (Fast Refresh) | Same dev-server architecture, different plugin — no config or workflow change for the developer |
| API proxy during dev | `vite.config.js` has a `/api/buet` dev-proxy rule to the live BUET API | `vite.config.ts` currently has **no proxy rules** (bare scaffold, no pages ported yet) | **Action needed before Wave 6** (`ParticipantsView`) lands: port the proxy rule into `vite.config.ts`. Not needed yet — no page calls it |

## 7. Production build workflow

| Step | Vue (today) | React (`front-end-react/`) | Status |
|---|---|---|---|
| Build command | `npm run build` → `vite build` → `dist/` | `npm run build` → `tsc -b && vite build` → `dist/` | ✅ verified — same output directory name, same artifact shape (`index.html` + `assets/`) |
| Type checking | none (plain JS) | `tsc -b` runs **before** `vite build` and will fail the whole build on type errors | New: this is a stricter gate than the Vue app had. Confirmed it doesn't break the Docker flow (devDependencies, including `typescript`, are installed by the Dockerfile's `RUN npm install` since no `--omit=dev` flag is used) |
| Static serving | `npm install -g serve` + `serve -s dist -l 3000` | identical | ✅ verified |
| Build-time env injection | `ARG`/`ENV` → `vite build` reads `process.env` | identical mechanism | ✅ verified |

## 8. CI/CD workflow

`.github/workflows/ci.yml` today:
```yaml
- run: docker compose build
- run: docker compose up -d --wait
- run: curl --fail http://localhost:9001/api/health
- run: curl --fail http://localhost:9001/   # step name: "Test Next.js Frontend Delivery"
- run: docker compose down
```

**No impact today**: `front-end-react/` is not referenced by `docker-compose.yml`
yet (per "do not migrate any pages yet"), so this pipeline currently builds
and tests the *Vue* app exactly as before — adding the new directory changes
nothing about CI's current behavior (confirmed: `front-end-react/` doesn't
appear anywhere in `.github/workflows/*.yml`).

**At cutover** (once pages are migrated and `docker-compose.yml`'s `frontend.build.context`
is flipped to `./front-end-react`), this pipeline requires **no edits** to
keep working, because:
- `docker compose build` will simply build the new Dockerfile/context instead — same command.
- The healthchecks (`/api/health`, `/`) are framework-agnostic HTTP checks against nginx (port 9001) — they don't care what's behind `frontend:3000`.
- `docker compose up -d --wait` already waits on the `frontend` healthcheck (§1) before the curl steps run, so a slower TS build (`tsc -b` adds real but small overhead — builds in ~150–200ms locally on this scaffold) won't introduce flakiness.

**Cosmetic cleanup recommended, not required**: the step name `"Test Next.js
Frontend Delivery"` and the branch name `nextjs-migration` are both leftovers
from an earlier (abandoned) Next.js plan — rename them to avoid misleading
future readers, per [MIGRATION_PLAN.md §2](MIGRATION_PLAN.md). Functionally
harmless either way.

`.github/workflows/deploy.yml` (Azure VM deploy) needs **zero changes** — it
operates purely at the `docker compose up -d --build` level and has no
framework-specific logic.

## Summary

| # | Area | Compatible as-is? | Action required before cutover |
|---|---|---|---|
| 1 | `docker-compose.yml` | Yes | Flip `frontend.build.context` to `./front-end-react` |
| 2 | `podman-compose.yaml` | Yes | Flip both `./front-end` volume mounts to `./front-end-react` |
| 3 | `front-end/Dockerfile` | Yes, reusable verbatim | Copy/move it into `front-end-react/`; add a `.dockerignore` (copy the existing one) |
| 3b | `front-end/Containerfile` | N/A — already dead & already broken | None — out of scope |
| 4 | nginx routing | Yes, zero changes | None |
| 5 | Environment variables | Yes, same `VITE_*` mechanism | None now; just remember to *use* `VITE_API_BASE_URL`/`VITE_API_INTERNAL_URL` when API calls are ported |
| 6 | Dev workflow | Yes | Port the `/api/buet` Vite dev-proxy rule into `vite.config.ts` before Wave 6 (`ParticipantsView`) |
| 7 | Prod build workflow | Yes | None — `tsc -b` adds a stricter (good) gate, not a blocker |
| 8 | CI/CD | Yes, no pipeline edits needed at cutover | Optional: rename the stale "Next.js" step name |
