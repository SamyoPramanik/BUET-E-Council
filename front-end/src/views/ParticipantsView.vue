<!-- views/ParticipantsView.vue -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  Users, Crown, BookOpen, Search, RefreshCw,
  Mail, Building2, ChevronDown, ChevronUp, GraduationCap,
  AlertCircle, User
} from 'lucide-vue-next'

// ── API endpoints ─────────────────────────────────────────────────────────────
const USERS_URL     = 'https://regoffice.buet.ac.bd/filetracker/my-php-api/api/users.php'
const DEAN_HEAD_URL = 'https://regoffice.buet.ac.bd/filetracker/my-php-api/api/Dean_Head.php'

// ── NOTE: The API keys all have trailing colons, e.g. "id:", "name:", etc.
// We normalise them on load.

// ── State ─────────────────────────────────────────────────────────────────────
const activeTab   = ref('users')   // 'users' | 'deans' | 'heads'
const searchQuery = ref('')

const rawUsers    = ref([])
const rawDeanHead = ref([])

const loading = ref({ users: false, deanhead: false })
const error   = ref({ users: null,  deanhead: null  })

// ── Data normalisation ────────────────────────────────────────────────────────
// Remove trailing colons from every key
function normalise(arr) {
  return arr.map(obj =>
    Object.fromEntries(
      Object.entries(obj).map(([k, v]) => [k.replace(/:$/, ''), v])
    )
  )
}

// Clean email: strip </br> tags and trim extra spaces
function cleanEmail(raw) {
  if (!raw) return []
  return raw
    .split(/<\/br>/i)
    .map(e => e.trim())
    .filter(Boolean)
}

// ── Fetch ─────────────────────────────────────────────────────────────────────
async function fetchUsers() {
  loading.value.users = true
  error.value.users   = null
  try {
    const res = await fetch(USERS_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    rawUsers.value = normalise(await res.json())
  } catch (e) {
    error.value.users = 'Could not load faculty data. Please try again.'
    console.error(e)
  } finally {
    loading.value.users = false
  }
}

async function fetchDeanHead() {
  loading.value.deanhead = true
  error.value.deanhead   = null
  try {
    const res = await fetch(DEAN_HEAD_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    rawDeanHead.value = normalise(await res.json())
  } catch (e) {
    error.value.deanhead = 'Could not load Dean/Head data. Please try again.'
    console.error(e)
  } finally {
    loading.value.deanhead = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchDeanHead()
})

// ── Derived lists ─────────────────────────────────────────────────────────────
const deans = computed(() => rawDeanHead.value.filter(p => p.designation === 'Dean'))
const heads  = computed(() => rawDeanHead.value.filter(p => p.designation === 'Head'))

// Search filter
function matchesSearch(person) {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return true
  const name      = (person.name        || '').toLowerCase()
  const bangla    = (person['Bangla Name'] || '').toLowerCase()
  const dept      = (person['dept_sort'] || person['In-Charge-Office'] || '').toLowerCase()
  const desig     = (person.designation || '').toLowerCase()
  const email     = (person.email        || '').toLowerCase()
  return name.includes(q) || bangla.includes(q) || dept.includes(q) || desig.includes(q) || email.includes(q)
}

const filteredUsers  = computed(() => rawUsers.value.filter(matchesSearch))
const filteredDeans  = computed(() => deans.value.filter(matchesSearch))
const filteredHeads  = computed(() => heads.value.filter(matchesSearch))

// Active list
const activeList = computed(() => {
  if (activeTab.value === 'users') return filteredUsers.value
  if (activeTab.value === 'deans') return filteredDeans.value
  return filteredHeads.value
})

const isLoading = computed(() => {
  if (activeTab.value === 'users') return loading.value.users
  return loading.value.deanhead
})

const activeError = computed(() => {
  if (activeTab.value === 'users') return error.value.users
  return error.value.deanhead
})

function retryFetch() {
  if (activeTab.value === 'users') fetchUsers()
  else fetchDeanHead()
}

// Reset search when switching tabs
watch(activeTab, () => { searchQuery.value = '' })

// ── Tab config ────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'users', label: 'Faculty',      icon: Users,      color: 'blue'   },
  { id: 'deans', label: 'Deans',        icon: Crown,      color: 'violet' },
  { id: 'heads', label: 'Dept. Heads',  icon: BookOpen,   color: 'emerald'},
]

// ── Designation badge colour ──────────────────────────────────────────────────
const DESIG_COLOUR = {
  'Professor':           'bg-blue-100 text-blue-700',
  'Associate Professor': 'bg-violet-100 text-violet-700',
  'Dean':                'bg-amber-100 text-amber-700',
  'Head':                'bg-emerald-100 text-emerald-700',
}
function designationClass(d) {
  return DESIG_COLOUR[d] || 'bg-slate-100 text-slate-600'
}

// ── Avatar initials ───────────────────────────────────────────────────────────
function initials(name) {
  return (name || '')
    .replace(/^Dr\.?\s*/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(w => w[0].toUpperCase())
    .join('')
}

// ── Avatar hue (deterministic from name) ─────────────────────────────────────
const HUES = [215, 250, 160, 25, 340, 185, 290, 40, 0, 130]
function avatarHue(name) {
  let h = 0
  for (let i = 0; i < (name || '').length; i++) h += name.charCodeAt(i)
  return HUES[h % HUES.length]
}
</script>

<template>
  <div class="participants-page">

    <!-- ══ PAGE HEADER ══════════════════════════════════════════════════════ -->
    <div class="page-header">
      <div class="page-header-inner">
        <div class="page-title-block">
          <GraduationCap :size="28" class="page-title-icon" />
          <div>
            <h1 class="page-title">BUET Academic Directory</h1>
            <p class="page-subtitle">Faculty, Deans and Department Heads</p>
          </div>
        </div>

        <!-- Search -->
        <div class="search-wrap">
          <Search :size="16" class="search-icon" />
          <input
            v-model="searchQuery"
            placeholder="Search by name, dept, email…"
            class="search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="search-clear" aria-label="Clear">✕</button>
        </div>
      </div>

      <!-- ── Tabs ── -->
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab-btn', `tab-btn--${tab.color}`, activeTab === tab.id ? 'tab-btn--active' : '']"
        >
          <component :is="tab.icon" :size="16" class="tab-icon" />
          {{ tab.label }}
          <span v-if="!isLoading" class="tab-count">
            {{
              tab.id === 'users' ? filteredUsers.length
              : tab.id === 'deans' ? filteredDeans.length
              : filteredHeads.length
            }}
          </span>
        </button>
      </div>
    </div>

    <!-- ══ BODY ═════════════════════════════════════════════════════════════ -->
    <div class="page-body">

      <!-- Loading -->
      <div v-if="isLoading" class="state-center">
        <div class="spinner" />
        <p class="state-text">Loading directory…</p>
      </div>

      <!-- Error -->
      <div v-else-if="activeError" class="state-center">
        <div class="error-icon-wrap">
          <AlertCircle :size="28" class="text-red-400" />
        </div>
        <p class="state-text state-text--error">{{ activeError }}</p>
        <button @click="retryFetch" class="retry-btn">
          <RefreshCw :size="14" /> Retry
        </button>
      </div>

      <!-- Empty search -->
      <div v-else-if="activeList.length === 0 && searchQuery" class="state-center">
        <Search :size="32" class="text-slate-300 mb-3" />
        <p class="state-text">No results for <strong>"{{ searchQuery }}"</strong></p>
        <button @click="searchQuery = ''" class="retry-btn retry-btn--ghost">Clear search</button>
      </div>

      <!-- ── USERS TAB ─────────────────────────────────────────────────── -->
      <template v-else-if="activeTab === 'users'">
        <div class="results-meta">
          <span>{{ filteredUsers.length }} faculty member{{ filteredUsers.length !== 1 ? 's' : '' }}</span>
        </div>
        <div class="card-grid">
          <div
            v-for="person in filteredUsers"
            :key="person.id"
            class="person-card"
          >
            <!-- Avatar -->
            <div
              class="avatar"
              :style="`--hue: ${avatarHue(person.name)}`"
            >
              {{ initials(person.name) }}
            </div>

            <!-- Info -->
            <div class="person-info">
              <p class="person-name">{{ person.name }}</p>
              <p class="person-bangla" v-if="person['Bangla Name']">{{ person['Bangla Name'] }}</p>

              <div class="badge-row">
                <span :class="['desig-badge', designationClass(person.designation)]">
                  {{ person.designation }}
                </span>
                <span v-if="person['dept_sort']" class="dept-badge">
                  {{ person['dept_sort'] }}
                </span>
              </div>

              <!-- Service status -->
              <span v-if="person['Service Status']"
                :class="['status-dot', person['Service Status'] === 'Current' ? 'status-dot--on' : 'status-dot--off']">
                {{ person['Service Status'] }}
              </span>

              <!-- Emails -->
              <div v-if="person.email" class="email-list">
                <a
                  v-for="(em, i) in cleanEmail(person.email)"
                  :key="i"
                  :href="`mailto:${em}`"
                  class="email-link"
                >
                  <Mail :size="11" />{{ em }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ── DEANS TAB ─────────────────────────────────────────────────── -->
      <template v-else-if="activeTab === 'deans'">
        <div class="results-meta">
          <span>{{ filteredDeans.length }} Dean{{ filteredDeans.length !== 1 ? 's' : '' }}</span>
        </div>
        <div class="card-grid card-grid--wide">
          <div
            v-for="person in filteredDeans"
            :key="person.id"
            class="person-card person-card--featured"
          >
            <div class="avatar avatar--lg" :style="`--hue: ${avatarHue(person.name)}`">
              {{ initials(person.name) }}
            </div>
            <div class="person-info">
              <p class="person-name">{{ person.name }}</p>
              <p class="person-bangla" v-if="person['Bangla Name']">{{ person['Bangla Name'] }}</p>

              <span class="desig-badge bg-amber-100 text-amber-700 mb-1">Dean</span>

              <div v-if="person['In-Charge-Office']" class="office-row">
                <Building2 :size="12" class="text-slate-400 shrink-0" />
                <span class="office-label">{{ person['In-Charge-Office'] }}</span>
              </div>

              <div v-if="person.email" class="email-list mt-2">
                <a
                  v-for="(em, i) in cleanEmail(person.email)"
                  :key="i"
                  :href="`mailto:${em}`"
                  class="email-link"
                >
                  <Mail :size="11" />{{ em }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ── HEADS TAB ─────────────────────────────────────────────────── -->
      <template v-else>
        <div class="results-meta">
          <span>{{ filteredHeads.length }} Department Head{{ filteredHeads.length !== 1 ? 's' : '' }}</span>
        </div>
        <div class="card-grid">
          <div
            v-for="person in filteredHeads"
            :key="person.id"
            class="person-card"
          >
            <div class="avatar" :style="`--hue: ${avatarHue(person.name)}`">
              {{ initials(person.name) }}
            </div>
            <div class="person-info">
              <p class="person-name">{{ person.name }}</p>
              <p class="person-bangla" v-if="person['Bangla Name']">{{ person['Bangla Name'] }}</p>

              <span class="desig-badge bg-emerald-100 text-emerald-700 mb-1">Head</span>

              <div v-if="person['In-Charge-Office']" class="office-row">
                <Building2 :size="12" class="text-slate-400 shrink-0" />
                <span class="office-label">{{ person['In-Charge-Office'] }}</span>
              </div>

              <div v-if="person.email" class="email-list mt-2">
                <a
                  v-for="(em, i) in cleanEmail(person.email)"
                  :key="i"
                  :href="`mailto:${em}`"
                  class="email-link"
                >
                  <Mail :size="11" />{{ em }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
/* ── Page shell ──────────────────────────────────────────────────────────── */
.participants-page {
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 30;
  box-shadow: 0 1px 8px rgba(0,0,0,.05);
}
.page-header-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 16px 24px 12px;
}

.page-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}
.page-title-icon { color: #3b82f6; flex-shrink: 0; }
.page-title {
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -.02em;
  white-space: nowrap;
}
.page-subtitle {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
  margin-top: 1px;
}

/* ── Search ──────────────────────────────────────────────────────────────── */
.search-wrap {
  position: relative;
  flex-shrink: 0;
  width: min(100%, 280px);
}
.search-icon {
  position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  color: #94a3b8; pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 8px 32px 8px 34px;
  font-size: 13px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  outline: none;
  transition: border-color .15s;
  color: #1e293b;
}
.search-input:focus { border-color: #93c5fd; background: #fff; }
.search-clear {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  font-size: 11px; color: #94a3b8; cursor: pointer; background: none; border: none;
  padding: 2px 4px; border-radius: 4px;
}
.search-clear:hover { color: #475569; }

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.tab-bar {
  display: flex;
  gap: 2px;
  padding: 0 20px;
  overflow-x: auto;
  scrollbar-width: none;
}
.tab-bar::-webkit-scrollbar { display: none; }

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 10px 16px 11px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #64748b;
  border-bottom: 2px solid transparent;
  transition: color .15s, border-color .15s;
  white-space: nowrap;
  margin-bottom: -1px;
}
.tab-btn:hover { color: #1e293b; }

.tab-btn--blue.tab-btn--active   { color: #2563eb; border-color: #2563eb; }
.tab-btn--violet.tab-btn--active  { color: #7c3aed; border-color: #7c3aed; }
.tab-btn--emerald.tab-btn--active { color: #059669; border-color: #059669; }

.tab-icon { opacity: .7; }
.tab-btn--active .tab-icon { opacity: 1; }

.tab-count {
  font-size: 11px;
  font-weight: 700;
  background: #f1f5f9;
  color: #64748b;
  padding: 1px 6px;
  border-radius: 20px;
  min-width: 22px;
  text-align: center;
}
.tab-btn--blue.tab-btn--active   .tab-count { background: #dbeafe; color: #1d4ed8; }
.tab-btn--violet.tab-btn--active  .tab-count { background: #ede9fe; color: #6d28d9; }
.tab-btn--emerald.tab-btn--active .tab-count { background: #d1fae5; color: #065f46; }

/* ── Page body ───────────────────────────────────────────────────────────── */
.page-body {
  flex: 1;
  padding: 28px 24px 48px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* ── States (loading / error / empty) ───────────────────────────────────── */
.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  text-align: center;
}
.spinner {
  width: 36px; height: 36px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.state-text { font-size: 14px; color: #64748b; font-weight: 500; }
.state-text--error { color: #ef4444; }
.error-icon-wrap {
  width: 56px; height: 56px; border-radius: 16px;
  background: #fee2e2; display: flex; align-items: center; justify-content: center;
}
.retry-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 18px; font-size: 13px; font-weight: 600;
  background: #2563eb; color: #fff;
  border: none; border-radius: 10px; cursor: pointer;
  transition: background .12s;
}
.retry-btn:hover { background: #1d4ed8; }
.retry-btn--ghost { background: #f1f5f9; color: #475569; }
.retry-btn--ghost:hover { background: #e2e8f0; }

/* ── Results meta ────────────────────────────────────────────────────────── */
.results-meta {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-bottom: 16px;
}

/* ── Card grid ───────────────────────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.card-grid--wide {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

/* ── Person card ─────────────────────────────────────────────────────────── */
.person-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 18px 16px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  transition: box-shadow .18s, transform .18s;
}
.person-card:hover {
  box-shadow: 0 6px 24px rgba(0,0,0,.08);
  transform: translateY(-2px);
}
.person-card--featured {
  border-color: #fde68a;
  background: linear-gradient(160deg, #fff 70%, #fffbeb);
}

/* ── Avatar ──────────────────────────────────────────────────────────────── */
.avatar {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: hsl(var(--hue, 215), 60%, 92%);
  color: hsl(var(--hue, 215), 60%, 35%);
  font-size: 16px;
  font-weight: 900;
  letter-spacing: -.02em;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid hsl(var(--hue, 215), 40%, 85%);
}
.avatar--lg {
  width: 64px;
  height: 64px;
  font-size: 20px;
  border-radius: 18px;
}

/* ── Person info ─────────────────────────────────────────────────────────── */
.person-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  min-width: 0;
}
.person-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}
.person-bangla {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

/* ── Badges ──────────────────────────────────────────────────────────────── */
.badge-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 4px;
}
.desig-badge {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: .02em;
  text-transform: uppercase;
}
.dept-badge {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
  letter-spacing: .04em;
  text-transform: uppercase;
}

/* ── Status dot ──────────────────────────────────────────────────────────── */
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
  font-weight: 600;
  margin-top: 2px;
}
.status-dot::before {
  content: '';
  width: 6px; height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.status-dot--on  { color: #059669; }
.status-dot--on::before  { background: #10b981; }
.status-dot--off { color: #94a3b8; }
.status-dot--off::before { background: #cbd5e1; }

/* ── Office row ──────────────────────────────────────────────────────────── */
.office-row {
  display: flex;
  align-items: flex-start;
  gap: 5px;
  margin-top: 4px;
}
.office-label {
  font-size: 11.5px;
  color: #475569;
  line-height: 1.45;
  text-align: left;
}

/* ── Email list ──────────────────────────────────────────────────────────── */
.email-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: center;
  width: 100%;
}
.email-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #2563eb;
  text-decoration: none;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color .1s;
}
.email-link:hover { color: #1d4ed8; text-decoration: underline; }

.mt-2 { margin-top: 8px; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .page-header-inner  { flex-direction: column; align-items: stretch; padding: 14px 16px 10px; }
  .search-wrap        { width: 100%; }
  .page-title         { font-size: 16px; }
  .page-body          { padding: 16px 12px 40px; }
  .card-grid          { grid-template-columns: 1fr 1fr; gap: 10px; }
  .card-grid--wide    { grid-template-columns: 1fr; }
  .person-card        { padding: 14px 12px 12px; }
  .avatar             { width: 44px; height: 44px; font-size: 14px; border-radius: 12px; }
  .person-name        { font-size: 12.5px; }
  .person-bangla      { font-size: 11px; }
}

@media (max-width: 380px) {
  .card-grid { grid-template-columns: 1fr; }
}
</style>
