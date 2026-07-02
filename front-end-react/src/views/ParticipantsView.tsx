import { useEffect, useState } from 'react'
import { Users, Crown, BookOpen, Search, RefreshCw, Mail, Building2, GraduationCap, AlertCircle } from 'lucide-react'
import BackButton from '../components/BackButton'
import './ParticipantsView.css'

// ── API endpoints ─────────────────────────────────────────────────────────────
// NOTE: relative paths, proxied by nginx in `docker-compose.yml`'s deployment
// (see API_MIGRATION.md §5) — these calls bypass utils/api.ts entirely,
// exactly like the Vue version (no Session-ID header, no withCredentials,
// since this hits BUET's external registry API, not the FastAPI backend).
const USERS_URL = '/buet-api/users/'
const DEAN_HEAD_URL = '/buet-api/department-head/'

// The external API's keys all have trailing colons, e.g. "id:", "name:", etc.
// We normalise them on load. Records otherwise have inconsistent/dynamic keys
// (some with spaces or hyphens), so this is intentionally loosely typed.
interface ExternalPerson {
  id?: string | number
  name?: string
  designation?: string
  email?: string
  [key: string]: unknown
}

type TabId = 'users' | 'deans' | 'heads'

// ── Data normalisation ────────────────────────────────────────────────────────
// Remove trailing colons from every key
function normalise(arr: Record<string, unknown>[]): ExternalPerson[] {
  return arr.map((obj) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k.replace(/:$/, ''), v])))
}

// Clean email: strip </br> tags and trim extra spaces
function cleanEmail(raw?: string): string[] {
  if (!raw) return []
  return raw
    .split(/<\/br>/i)
    .map((e) => e.trim())
    .filter(Boolean)
}

const DESIG_COLOUR: Record<string, string> = {
  Professor: 'bg-blue-100 text-blue-700',
  'Associate Professor': 'bg-violet-100 text-violet-700',
  Dean: 'bg-amber-100 text-amber-700',
  Head: 'bg-emerald-100 text-emerald-700',
}
function designationClass(d?: string): string {
  return (d && DESIG_COLOUR[d]) || 'bg-slate-100 text-slate-600'
}

// ── Avatar initials ───────────────────────────────────────────────────────────
function initials(name?: string): string {
  return (name || '')
    .replace(/^Dr\.?\s*/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('')
}

// ── Avatar hue (deterministic from name) ─────────────────────────────────────
const HUES = [215, 250, 160, 25, 340, 185, 290, 40, 0, 130]
function avatarHue(name?: string): number {
  let h = 0
  for (let i = 0; i < (name || '').length; i++) h += (name as string).charCodeAt(i)
  return HUES[h % HUES.length]
}

const tabs: { id: TabId; label: string; icon: typeof Users; color: string }[] = [
  { id: 'users', label: 'Faculty', icon: Users, color: 'blue' },
  { id: 'deans', label: 'Deans', icon: Crown, color: 'violet' },
  { id: 'heads', label: 'Dept. Heads', icon: BookOpen, color: 'emerald' },
]

export default function ParticipantsView() {
  // ── State ─────────────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<TabId>('users')
  const [searchQuery, setSearchQuery] = useState('')

  const [rawUsers, setRawUsers] = useState<ExternalPerson[]>([])
  const [rawDeanHead, setRawDeanHead] = useState<ExternalPerson[]>([])

  const [loading, setLoading] = useState({ users: false, deanhead: false })
  const [error, setError] = useState<{ users: string | null; deanhead: string | null }>({ users: null, deanhead: null })

  // ── Fetch ─────────────────────────────────────────────────────────────────────
  async function fetchUsers() {
    setLoading((l) => ({ ...l, users: true }))
    setError((e) => ({ ...e, users: null }))
    try {
      const res = await fetch(USERS_URL)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setRawUsers(normalise(await res.json()))
    } catch (e) {
      setError((er) => ({ ...er, users: 'Could not load faculty data. Please try again.' }))
      console.error(e)
    } finally {
      setLoading((l) => ({ ...l, users: false }))
    }
  }

  async function fetchDeanHead() {
    setLoading((l) => ({ ...l, deanhead: true }))
    setError((e) => ({ ...e, deanhead: null }))
    try {
      const res = await fetch(DEAN_HEAD_URL)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setRawDeanHead(normalise(await res.json()))
    } catch (e) {
      setError((er) => ({ ...er, deanhead: 'Could not load Dean/Head data. Please try again.' }))
      console.error(e)
    } finally {
      setLoading((l) => ({ ...l, deanhead: false }))
    }
  }

  useEffect(() => {
    fetchUsers()
    fetchDeanHead()
  }, [])

  // ── Derived lists ─────────────────────────────────────────────────────────────
  const deans = rawDeanHead.filter((p) => p.designation === 'Dean')
  const heads = rawDeanHead.filter((p) => p.designation === 'Head')

  // Search filter
  function matchesSearch(person: ExternalPerson): boolean {
    const q = searchQuery.toLowerCase().trim()
    if (!q) return true
    const name = (person.name || '').toString().toLowerCase()
    const bangla = ((person['Bangla Name'] as string) || '').toLowerCase()
    const dept = (((person['dept_sort'] as string) || (person['In-Charge-Office'] as string)) || '').toLowerCase()
    const desig = (person.designation || '').toLowerCase()
    const email = (person.email || '').toLowerCase()
    return name.includes(q) || bangla.includes(q) || dept.includes(q) || desig.includes(q) || email.includes(q)
  }

  const filteredUsers = rawUsers.filter(matchesSearch)
  const filteredDeans = deans.filter(matchesSearch)
  const filteredHeads = heads.filter(matchesSearch)

  const activeList = activeTab === 'users' ? filteredUsers : activeTab === 'deans' ? filteredDeans : filteredHeads
  const isLoading = activeTab === 'users' ? loading.users : loading.deanhead
  const activeError = activeTab === 'users' ? error.users : error.deanhead

  function retryFetch() {
    if (activeTab === 'users') fetchUsers()
    else fetchDeanHead()
  }

  // Reset search when switching tabs
  function changeTab(id: TabId) {
    setActiveTab(id)
    setSearchQuery('')
  }

  return (
    <div className="participants-page">
      {/* ══ PAGE HEADER ══════════════════════════════════════════════════════ */}
      <div className="page-header">
        <BackButton className="mb-2" />
        <div className="page-header-inner">
          <div className="page-title-block">
            <GraduationCap size={28} className="page-title-icon" />
            <div>
              <h1 className="page-title">BUET Academic Directory</h1>
              <p className="page-subtitle">Faculty, Deans and Department Heads</p>
            </div>
          </div>

          {/* Search */}
          <div className="search-wrap">
            <Search size={16} className="search-icon" />
            <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search by name, dept, email…" className="search-input" />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="search-clear" aria-label="Clear">
                ✕
              </button>
            )}
          </div>
        </div>

        {/* ── Tabs ── */}
        <div className="tab-bar">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => changeTab(tab.id)}
                className={['tab-btn', `tab-btn--${tab.color}`, activeTab === tab.id ? 'tab-btn--active' : ''].join(' ')}
              >
                <Icon size={16} className="tab-icon" />
                {tab.label}
                {!isLoading && (
                  <span className="tab-count">{tab.id === 'users' ? filteredUsers.length : tab.id === 'deans' ? filteredDeans.length : filteredHeads.length}</span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* ══ BODY ═════════════════════════════════════════════════════════════ */}
      <div className="page-body">
        {isLoading ? (
          <div className="state-center">
            <div className="spinner" />
            <p className="state-text">Loading directory…</p>
          </div>
        ) : activeError ? (
          <div className="state-center">
            <div className="error-icon-wrap">
              <AlertCircle size={28} className="text-red-400" />
            </div>
            <p className="state-text state-text--error">{activeError}</p>
            <button onClick={retryFetch} className="retry-btn">
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        ) : activeList.length === 0 && searchQuery ? (
          <div className="state-center">
            <Search size={32} className="text-slate-300 mb-3" />
            <p className="state-text">
              No results for <strong>"{searchQuery}"</strong>
            </p>
            <button onClick={() => setSearchQuery('')} className="retry-btn retry-btn--ghost">
              Clear search
            </button>
          </div>
        ) : activeTab === 'users' ? (
          <>
            <div className="results-meta">
              <span>
                {filteredUsers.length} faculty member{filteredUsers.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="card-grid">
              {filteredUsers.map((person) => (
                <div key={String(person.id)} className="person-card">
                  <div className="avatar" style={{ '--hue': avatarHue(person.name) } as React.CSSProperties}>
                    {initials(person.name)}
                  </div>
                  <div className="person-info">
                    <p className="person-name">{person.name}</p>
                    {!!person['Bangla Name'] && <p className="person-bangla">{person['Bangla Name'] as string}</p>}
                    <div className="badge-row">
                      <span className={['desig-badge', designationClass(person.designation)].join(' ')}>{person.designation}</span>
                      {!!person['dept_sort'] && <span className="dept-badge">{person['dept_sort'] as string}</span>}
                    </div>
                    {!!person['Service Status'] && (
                      <span className={['status-dot', person['Service Status'] === 'Current' ? 'status-dot--on' : 'status-dot--off'].join(' ')}>
                        {person['Service Status'] as string}
                      </span>
                    )}
                    {!!person.email && (
                      <div className="email-list">
                        {cleanEmail(person.email).map((em, i) => (
                          <a key={i} href={`mailto:${em}`} className="email-link">
                            <Mail size={11} />
                            {em}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : activeTab === 'deans' ? (
          <>
            <div className="results-meta">
              <span>
                {filteredDeans.length} Dean{filteredDeans.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="card-grid card-grid--wide">
              {filteredDeans.map((person) => (
                <div key={String(person.id)} className="person-card person-card--featured">
                  <div className="avatar avatar--lg" style={{ '--hue': avatarHue(person.name) } as React.CSSProperties}>
                    {initials(person.name)}
                  </div>
                  <div className="person-info">
                    <p className="person-name">{person.name}</p>
                    {!!person['Bangla Name'] && <p className="person-bangla">{person['Bangla Name'] as string}</p>}
                    <span className="desig-badge bg-amber-100 text-amber-700 mb-1">Dean</span>
                    {!!person['In-Charge-Office'] && (
                      <div className="office-row">
                        <Building2 size={12} className="text-slate-400 shrink-0" />
                        <span className="office-label">{person['In-Charge-Office'] as string}</span>
                      </div>
                    )}
                    {!!person.email && (
                      <div className="email-list mt-2">
                        {cleanEmail(person.email).map((em, i) => (
                          <a key={i} href={`mailto:${em}`} className="email-link">
                            <Mail size={11} />
                            {em}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <div className="results-meta">
              <span>
                {filteredHeads.length} Department Head{filteredHeads.length !== 1 ? 's' : ''}
              </span>
            </div>
            <div className="card-grid">
              {filteredHeads.map((person) => (
                <div key={String(person.id)} className="person-card">
                  <div className="avatar" style={{ '--hue': avatarHue(person.name) } as React.CSSProperties}>
                    {initials(person.name)}
                  </div>
                  <div className="person-info">
                    <p className="person-name">{person.name}</p>
                    {!!person['Bangla Name'] && <p className="person-bangla">{person['Bangla Name'] as string}</p>}
                    <span className="desig-badge bg-emerald-100 text-emerald-700 mb-1">Head</span>
                    {!!person['In-Charge-Office'] && (
                      <div className="office-row">
                        <Building2 size={12} className="text-slate-400 shrink-0" />
                        <span className="office-label">{person['In-Charge-Office'] as string}</span>
                      </div>
                    )}
                    {!!person.email && (
                      <div className="email-list mt-2">
                        {cleanEmail(person.email).map((em, i) => (
                          <a key={i} href={`mailto:${em}`} className="email-link">
                            <Mail size={11} />
                            {em}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
