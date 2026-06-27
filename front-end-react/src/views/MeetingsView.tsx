import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import api from '../utils/api'
import { useAuth } from '../auth/AuthContext'
import type { MeetingSummary, PaginatedMeetingResponse } from '../types/api'

interface CreateMeetingForm {
  is_academic: boolean | null
  serial_num: number | null
  meeting_date: string
}

const emptyForm = (): CreateMeetingForm => ({ is_academic: null, serial_num: null, meeting_date: '' })

export default function MeetingsView() {
  const navigate = useNavigate()
  const { userRole } = useAuth()

  // ── list state ─────────────────────────────────────────────────────────────
  const [meetings, setMeetings] = useState<MeetingSummary[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [isAcademic, setIsAcademic] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [sortBy, setSortBy] = useState<keyof MeetingSummary>('meeting_date')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  // ── permissions ────────────────────────────────────────────────────────────
  const canCreate = ['admin', 'staff'].includes(userRole)

  // ── fetch meetings ─────────────────────────────────────────────────────────
  const fetchMeetings = async () => {
    setLoading(true)
    try {
      const response = await api.get<PaginatedMeetingResponse>('/meetings/', {
        params: { is_academic: isAcademic, page: currentPage, limit: 10 },
      })
      setMeetings(response.data.data)
      setTotalCount(response.data.total_count)
    } catch (error) {
      console.error('Failed to fetch meetings', error)
      toast.error('Could not load meetings.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMeetings()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAcademic, currentPage])

  const setTab = (val: boolean) => {
    if (isAcademic === val) return
    setIsAcademic(val)
    setCurrentPage(1)
  }

  const toggleSort = (column: keyof MeetingSummary) => {
    let nextDir: 'asc' | 'desc' = 'asc'
    if (sortBy === column) {
      nextDir = sortDir === 'asc' ? 'desc' : 'asc'
    }
    setSortBy(column)
    setSortDir(nextDir)
    setMeetings((prev) =>
      [...prev].sort((a, b) => {
        const mod = nextDir === 'asc' ? 1 : -1
        const av = a[column] as string | number
        const bv = b[column] as string | number
        if (av < bv) return -1 * mod
        if (av > bv) return 1 * mod
        return 0
      }),
    )
  }

  // ── create meeting modal ───────────────────────────────────────────────────
  const [showModal, setShowModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState<CreateMeetingForm>(emptyForm())

  function openCreateModal() {
    setForm(emptyForm())
    setShowModal(true)
  }

  function closeModal() {
    if (creating) return // don't close mid-request
    setShowModal(false)
  }

  async function submitCreate() {
    // ── client-side validation ──────────────────────────────────────────────
    const errors: string[] = []
    if (form.is_academic === null) errors.push('Please select a council type.')
    if (!form.serial_num || form.serial_num < 1) errors.push('Serial number is required and must be a positive integer.')
    if (!form.meeting_date) errors.push('Meeting date is required.')

    if (errors.length) {
      errors.forEach((e) => toast.warning(e))
      return
    }

    setCreating(true)
    try {
      const payload = {
        is_academic: form.is_academic,
        serial_num: form.serial_num,
        meeting_date: new Date(form.meeting_date + 'T00:00:00Z').toISOString(),
      }

      const res = await api.post('/meetings/', payload)
      const newMeeting = res.data

      toast.success(`Meeting #${newMeeting.serial_num} created — redirecting…`)

      setShowModal(false)

      // Redirect to the newly created meeting's detail page
      navigate(`/meetings/${newMeeting.id}`)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        toast.error(detail)
      } else {
        toast.error('Failed to create meeting. Please try again.')
      }
    } finally {
      setCreating(false)
    }
  }

  return (
    <>
      <div className="container mx-auto py-8 px-4">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="hidden lg:block lg:col-span-1"></div>

          <div className="col-span-1 lg:col-span-10">
            {/* ── HEADER ──────────────────────────────────────────────────── */}
            <header className="mb-8 flex items-start justify-between gap-4 flex-wrap">
              <div>
                <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Council Meetings</h1>
                <p className="text-slate-500 mt-1">Access and manage Academic and Syndicate records</p>
              </div>

              {canCreate && (
                <div className="relative group flex-shrink-0">
                  <button
                    onClick={openCreateModal}
                    className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
                               text-white text-sm font-semibold rounded-xl shadow-sm
                               transition-all active:scale-95 focus:outline-none
                               focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                    title="Create a new meeting record"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                      <line x1="12" y1="5" x2="12" y2="19" />
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    New Meeting
                  </button>
                  <div
                    className="absolute right-0 top-full mt-2 px-3 py-1.5 bg-slate-800 text-white text-xs
                                rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100
                                transition-opacity pointer-events-none z-50 shadow-lg"
                  >
                    Create a new meeting record
                    <div className="absolute -top-1 right-4 w-2 h-2 bg-slate-800 rotate-45"></div>
                  </div>
                </div>
              )}
            </header>

            {/* ── TABS ────────────────────────────────────────────────────── */}
            <div className="flex space-x-1 bg-slate-200/60 p-1 rounded-xl mb-6 w-full sm:w-72 border border-slate-200">
              <button
                onClick={() => setTab(true)}
                className={['flex-1 py-2 text-sm font-semibold rounded-lg transition-all', isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800'].join(
                  ' ',
                )}
              >
                Academic
              </button>
              <button
                onClick={() => setTab(false)}
                className={['flex-1 py-2 text-sm font-semibold rounded-lg transition-all', !isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800'].join(
                  ' ',
                )}
              >
                Syndicate
              </button>
            </div>

            {/* ── TABLE ───────────────────────────────────────────────────── */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <table className="w-full text-left border-collapse table-fixed">
                <thead className="bg-slate-50/80 border-b border-slate-200">
                  <tr>
                    <th onClick={() => toggleSort('serial_num')} className="p-4 w-24 cursor-pointer hover:bg-slate-100 transition">
                      <div className="flex items-center space-x-1">
                        <span className="text-xs uppercase tracking-wider font-bold text-slate-500">Serial</span>
                        {sortBy === 'serial_num' && <span className="text-blue-500 text-xs">{sortDir === 'asc' ? '↑' : '↓'}</span>}
                      </div>
                    </th>
                    <th className="p-4">
                      <span className="text-xs uppercase tracking-wider font-bold text-slate-500">Title</span>
                    </th>
                    <th className="p-4 w-32 text-center">
                      <span className="text-xs uppercase tracking-wider font-bold text-slate-500">Status</span>
                    </th>
                    <th onClick={() => toggleSort('meeting_date')} className="p-4 w-40 cursor-pointer hover:bg-slate-100 transition">
                      <div className="flex items-center justify-end space-x-1">
                        <span className="text-xs uppercase tracking-wider font-bold text-slate-500">Date</span>
                        {sortBy === 'meeting_date' && <span className="text-blue-500 text-xs">{sortDir === 'asc' ? '↑' : '↓'}</span>}
                      </div>
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {meetings.map((meeting) => (
                    <tr key={meeting.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="p-4">
                        <Link to={`/meetings/${meeting.id}`} className="font-mono font-bold text-blue-600 hover:underline">
                          #{meeting.serial_num}
                        </Link>
                      </td>
                      <td className="p-4">
                        <p className="text-slate-700 font-medium truncate" title={meeting.title_plain}>
                          {meeting.title_plain || '—'}
                        </p>
                      </td>
                      <td className="p-4 text-center">
                        {meeting.is_finished ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                            Finished
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">Ongoing</span>
                        )}
                      </td>
                      <td className="p-4 text-right text-slate-500 text-sm font-medium">
                        {meeting.meeting_date &&
                          new Date(meeting.meeting_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}
                      </td>
                    </tr>
                  ))}

                  {loading && (
                    <tr>
                      <td colSpan={4} className="p-12 text-center">
                        <div className="flex flex-col items-center gap-2">
                          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                          <span className="text-sm text-slate-400 font-medium tracking-wide">Fetching meetings…</span>
                        </div>
                      </td>
                    </tr>
                  )}
                  {!loading && meetings.length === 0 && (
                    <tr>
                      <td colSpan={4} className="p-12 text-center text-slate-400 italic">
                        No meeting records found for this category.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* ── PAGINATION ──────────────────────────────────────────────── */}
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-sm text-slate-500 font-medium">
                Showing <span className="text-slate-800">{meetings.length}</span> of <span className="text-slate-800">{totalCount}</span> records
              </p>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage((p) => p - 1)}
                  disabled={currentPage === 1 || loading}
                  className="px-4 py-2 text-sm font-semibold border rounded-xl
                             disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50"
                >
                  Previous
                </button>
                <div className="px-4 py-2 text-sm font-bold bg-white border rounded-xl shadow-sm text-blue-600">{currentPage}</div>
                <button
                  onClick={() => setCurrentPage((p) => p + 1)}
                  disabled={currentPage * 10 >= totalCount || loading}
                  className="px-4 py-2 text-sm font-semibold border rounded-xl
                             disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
          <div className="hidden lg:block lg:col-span-1"></div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════════ */}
      {/* CREATE MEETING MODAL                                                   */}
      {/* ══════════════════════════════════════════════════════════════════════ */}
      {showModal &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal()
            }}
          >
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
              {/* Modal header */}
              <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth={2.5} strokeLinecap="round">
                      <rect x="3" y="4" width="18" height="18" rx="2" />
                      <line x1="16" y1="2" x2="16" y2="6" />
                      <line x1="8" y1="2" x2="8" y2="6" />
                      <line x1="3" y1="10" x2="21" y2="10" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-lg font-black text-slate-800">New Meeting</h2>
                    <p className="text-xs text-slate-400">Fill in the required fields to create a record</p>
                  </div>
                </div>
                <button onClick={closeModal} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>

              {/* Modal body */}
              <div className="px-6 py-6 space-y-5">
                {/* Council Type */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Council Type <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-3">
                    <label
                      className={[
                        'flex-1 flex items-center gap-3 px-4 py-3 rounded-xl border-2 cursor-pointer transition-all',
                        form.is_academic === true ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-slate-300',
                      ].join(' ')}
                    >
                      <input
                        type="radio"
                        checked={form.is_academic === true}
                        onChange={() => setForm((f) => ({ ...f, is_academic: true }))}
                        className="accent-blue-600"
                      />
                      <span className="font-semibold text-sm text-slate-700">Academic Council</span>
                    </label>
                    <label
                      className={[
                        'flex-1 flex items-center gap-3 px-4 py-3 rounded-xl border-2 cursor-pointer transition-all',
                        form.is_academic === false ? 'border-purple-500 bg-purple-50' : 'border-slate-200 hover:border-slate-300',
                      ].join(' ')}
                    >
                      <input
                        type="radio"
                        checked={form.is_academic === false}
                        onChange={() => setForm((f) => ({ ...f, is_academic: false }))}
                        className="accent-purple-600"
                      />
                      <span className="font-semibold text-sm text-slate-700">Syndicate</span>
                    </label>
                  </div>
                </div>

                {/* Serial Number */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Serial Number <span className="text-red-500">*</span>
                  </label>
                  <input
                    value={form.serial_num ?? ''}
                    onChange={(e) => setForm((f) => ({ ...f, serial_num: e.target.value ? Number(e.target.value) : null }))}
                    type="number"
                    min={1}
                    placeholder="e.g. 465"
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-800 font-semibold
                               focus:border-blue-400 focus:ring-3 focus:ring-blue-100 outline-none transition-all
                               placeholder:font-normal placeholder:text-slate-400"
                  />
                </div>

                {/* Meeting Date */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Meeting Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    value={form.meeting_date}
                    onChange={(e) => setForm((f) => ({ ...f, meeting_date: e.target.value }))}
                    type="date"
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-800
                               focus:border-blue-400 focus:ring-3 focus:ring-blue-100 outline-none transition-all"
                  />
                </div>
              </div>

              {/* Modal footer */}
              <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3">
                <p className="text-xs text-slate-400">
                  <span className="text-red-500">*</span> All fields are required
                </p>
                <div className="flex gap-3">
                  <button onClick={closeModal} className="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-white transition-all">
                    Cancel
                  </button>
                  <button
                    onClick={submitCreate}
                    disabled={creating}
                    className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700
                               text-white text-sm font-semibold rounded-xl transition-all
                               disabled:opacity-60 disabled:cursor-not-allowed active:scale-95"
                  >
                    {creating ? (
                      <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="white" strokeWidth={3} strokeDasharray="31.4" strokeDashoffset="10" />
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                        <line x1="12" y1="5" x2="12" y2="19" />
                        <line x1="5" y1="12" x2="19" y2="12" />
                      </svg>
                    )}
                    {creating ? 'Creating…' : 'Create Meeting'}
                  </button>
                </div>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </>
  )
}
