import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'react-toastify'
import api from '../utils/api'
import ParticipantCard from './ParticipantCard'
import MemberSelectRow from './MemberSelectRow'
import { confirmDestructive, confirmAction } from '../utils/alerts'
import { Search, Users, Crown, Trash2, Save, Mail, X, Plus, ChevronDown, GripVertical, UserPlus, ArrowLeftRight, ListChecks, ArrowUpDown } from 'lucide-react'
import type { ParticipantRead, FacultyRead, DepartmentRead } from '../types/api'
import './ParticipantsSection.css'

// ── drag-and-drop (native HTML5, no extra lib needed) ──────────────────────
// We keep it simple: dragover reordering via index tracking.
//
// ── Faculty / Department filters + sort ─────────────────────────────────────
// `GET /participants` and `GET /meetings/{id}/participants` (ParticipantRead)
// now join in department/faculty names via back-end/app/api/participants.py's
// participant_to_read(), and `/faculties` + `/departments` list endpoints
// (back-end/app/api/organisation.py) populate the filter dropdowns below.
// Search matches name (content), email, department, and faculty text.

interface ParticipantsSectionProps {
  meetingId: string
  currentPresidentId?: string | null
  currentMembers?: ParticipantRead[]
  allParticipants: ParticipantRead[]
  faculties?: FacultyRead[]
  departments?: DepartmentRead[]
  onPresidentUpdated: (id: string | null) => void
  onMembersUpdated: (ids: string[]) => void
}

export default function ParticipantsSection({
  meetingId,
  currentPresidentId = null,
  currentMembers = [],
  allParticipants,
  faculties = [],
  departments = [],
  onPresidentUpdated,
  onMembersUpdated,
}: ParticipantsSectionProps) {
  // ── President state ────────────────────────────────────────────────────────
  const [searchPresident, setSearchPresident] = useState('')
  const [isPresidentOpen, setIsPresidentOpen] = useState(false)
  const [selectedPresidentId, setSelectedPresidentId] = useState<string | null>(currentPresidentId)

  useEffect(() => setSelectedPresidentId(currentPresidentId), [currentPresidentId])

  const filteredForPresident = (() => {
    const term = searchPresident.toLowerCase().trim()
    if (!term) return allParticipants
    return allParticipants.filter(
      (p) =>
        p.content.toLowerCase().includes(term) ||
        (p.department ?? '').toLowerCase().includes(term) ||
        (p.faculty ?? '').toLowerCase().includes(term),
    )
  })()

  const selectedPresidentCard = allParticipants.find((p) => p.id === selectedPresidentId) || null

  const savePresident = async () => {
    try {
      await api.patch(`/meetings/${meetingId}`, { president_card_id: selectedPresidentId || null })
      onPresidentUpdated(selectedPresidentId)
      toast.success('President updated')
    } catch {
      toast.error('Failed to update president')
    }
  }

  // close dropdown on outside click (working implementation — the Vue
  // version's `v-click-outside` directive was never registered globally
  // and was a silent no-op; see MIGRATION_PLAN.md §4)
  const presidentDropdownRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (presidentDropdownRef.current && !presidentDropdownRef.current.contains(e.target as Node)) {
        setIsPresidentOpen(false)
      }
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  // ── Members state ──────────────────────────────────────────────────────────
  const [selectedMemberIds, setSelectedMemberIds] = useState<string[]>(currentMembers.map((m) => m.id))
  useEffect(() => setSelectedMemberIds(currentMembers.map((m) => m.id)), [currentMembers])

  const orderedMembers = selectedMemberIds
    .map((id) => allParticipants.find((p) => p.id === id))
    .filter((p): p is ParticipantRead => Boolean(p))

  const hasMembers = selectedMemberIds.length > 0

  // ── Modal state ────────────────────────────────────────────────────────────
  const [showModal, setShowModal] = useState(false)
  const [modalSearch, setModalSearch] = useState('')
  const [modalDraftIds, setModalDraftIds] = useState<string[]>([]) // working copy inside modal
  const [modalFacultyId, setModalFacultyId] = useState('')
  const [modalDepartmentId, setModalDepartmentId] = useState('')
  const [sortByFaculty, setSortByFaculty] = useState(false)

  // Departments narrow to the selected faculty (dependent dropdown).
  const departmentOptions = modalFacultyId ? departments.filter((d) => d.faculty_id === modalFacultyId) : departments

  const openModal = () => {
    setModalDraftIds([...selectedMemberIds])
    setModalSearch('')
    setModalFacultyId('')
    setModalDepartmentId('')
    setShowModal(true)
  }

  const closeModal = async () => {
    const dirty = JSON.stringify(modalDraftIds) !== JSON.stringify(selectedMemberIds)
    if (dirty) {
      const ok = await confirmDestructive('Discard changes?', 'Your unsaved member changes will be lost.', 'Yes, Discard')
      if (!ok) return
    }
    setShowModal(false)
  }

  // The available list shows everyone matching the search term + filters —
  // selected participants stay visible (highlighted) rather than
  // disappearing, so multi-selecting across several searches doesn't lose
  // your place.
  const modalAvailable = useMemo(() => {
    const term = modalSearch.toLowerCase().trim()
    let list = allParticipants.filter((p) => {
      if (modalFacultyId && p.faculty_id !== modalFacultyId) return false
      if (modalDepartmentId && p.department_id !== modalDepartmentId) return false
      if (!term) return true
      return (
        p.content.toLowerCase().includes(term) ||
        (p.email ?? '').toLowerCase().includes(term) ||
        (p.department ?? '').toLowerCase().includes(term) ||
        (p.faculty ?? '').toLowerCase().includes(term)
      )
    })
    if (sortByFaculty) {
      list = [...list].sort((a, b) => {
        const fa = a.faculty ?? ''
        const fb = b.faculty ?? ''
        if (fa !== fb) return fa.localeCompare(fb)
        const da = a.department ?? ''
        const db = b.department ?? ''
        if (da !== db) return da.localeCompare(db)
        return a.content.localeCompare(b.content)
      })
    }
    return list
  }, [allParticipants, modalSearch, modalFacultyId, modalDepartmentId, sortByFaculty])

  const modalSelected = modalDraftIds
    .map((id) => allParticipants.find((p) => p.id === id))
    .filter((p): p is ParticipantRead => Boolean(p))

  const modalToggleAdd = (id: string) => {
    setModalDraftIds((prev) => (prev.includes(id) ? prev : [...prev, id]))
  }
  const modalToggleRemove = (id: string) => {
    setModalDraftIds((prev) => prev.filter((i) => i !== id))
  }
  const modalToggle = (id: string) => (modalDraftIds.includes(id) ? modalToggleRemove(id) : modalToggleAdd(id))

  // Select All — only the currently filtered/visible set, never the whole catalogue.
  const allFilteredSelected = modalAvailable.length > 0 && modalAvailable.every((p) => modalDraftIds.includes(p.id))
  const selectAllFiltered = () => {
    setModalDraftIds((prev) => {
      const merged = new Set(prev)
      modalAvailable.forEach((p) => merged.add(p.id))
      return Array.from(merged)
    })
  }
  const clearSelection = () => setModalDraftIds([])

  // ── Save members to API ────────────────────────────────────────────────────
  const saveMembers = async (ids: string[]) => {
    try {
      // NOTE: the body is a bare array, not `{ participant_ids: ids }`.
      // back-end/app/api/meetings.py registers PATCH /{meeting_id}/participants
      // (expecting a raw `list[UUID]` body) BEFORE back-end/app/api/participants.py
      // registers the identical path expecting `{ participant_ids: [...] }` —
      // FastAPI's first-registered-route-wins means meetings.py's handler is the
      // one that actually runs; participants.py's is unreachable dead code. The
      // Vue app sends the `{ participant_ids }` shape and would 422 against the
      // real backend; verified live and fixed here. See PAGES_MIGRATION_REPORT.md.
      await api.patch(`/meetings/${meetingId}/participants`, ids)
      onMembersUpdated([...ids])
      toast.success('Members saved')
    } catch {
      toast.error('Failed to save members')
    }
  }

  const saveModal = async () => {
    const ok = await confirmAction('Save member changes?', `This will update the meeting with ${modalDraftIds.length} member(s).`, 'Save Members')
    if (!ok) return
    setSelectedMemberIds([...modalDraftIds])
    await saveMembers(modalDraftIds)
    setShowModal(false)
  }

  // ── Drag-and-drop reorder inside modal ────────────────────────────────────
  const [dragFromIndex, setDragFromIndex] = useState<number | null>(null)

  const onDragStart = (idx: number) => setDragFromIndex(idx)
  const onDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (dragFromIndex === null || dragFromIndex === idx) return
    const arr = [...modalDraftIds]
    const [moved] = arr.splice(dragFromIndex, 1)
    arr.splice(idx, 0, moved)
    setModalDraftIds(arr)
    setDragFromIndex(idx)
  }
  const onDragEnd = () => setDragFromIndex(null)

  const clearAllMembers = async () => {
    const ok = await confirmDestructive('Clear all members?', 'Every participant will be removed from this meeting.', 'Yes, Clear All')
    if (!ok) return
    setSelectedMemberIds([])
    await saveMembers([])
  }

  const removeMember = async (id: string) => {
    const next = selectedMemberIds.filter((mid) => mid !== id)
    setSelectedMemberIds(next)
    await saveMembers(next)
  }

  const sendEmailPopup = () => {
    toast.info(`Email composer coming soon… (${selectedMemberIds.length} members)`)
  }

  return (
    <div className="space-y-10">
      {/* ══════════════════════════════════════════════
           SECTION HEADER  +  top action button
      ══════════════════════════════════════════════ */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-px bg-slate-300"></div>
          <span className="text-sm font-black uppercase tracking-widest text-slate-500">Participants</span>
        </div>

        {hasMembers ? (
          <button
            onClick={sendEmailPopup}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold
                       bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl
                       transition-all active:scale-95 shadow-sm"
          >
            <Mail size={16} /> Send Email
          </button>
        ) : (
          <button
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold
                       border-2 border-blue-500 text-blue-600 hover:bg-blue-50
                       rounded-xl transition-all active:scale-95"
          >
            <ArrowLeftRight size={16} /> Import from Previous Meeting
          </button>
        )}
      </div>

      {/* ══════════════════════════════════════════════
           PRESIDENT SUB-SECTION
      ══════════════════════════════════════════════ */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-visible">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
          <Crown className="text-amber-500" size={18} />
          <span className="text-sm font-black uppercase tracking-widest text-slate-600">President</span>
        </div>

        <div className="p-6">
          {/* search-integrated dropdown */}
          <div className="relative" ref={presidentDropdownRef}>
            {/* trigger */}
            <button
              onClick={() => setIsPresidentOpen((v) => !v)}
              className="w-full flex items-center justify-between px-5 py-3.5
                         bg-slate-50 border border-slate-200 rounded-xl
                         text-sm font-medium text-slate-700 hover:border-slate-300
                         transition-all"
            >
              <span className="truncate">{selectedPresidentCard ? selectedPresidentCard.content : 'Select President…'}</span>
              <ChevronDown size={16} className={['shrink-0 ml-3 text-slate-400 transition-transform duration-200', isPresidentOpen ? 'rotate-180' : ''].join(' ')} />
            </button>

            {/* dropdown panel */}
            {isPresidentOpen && (
              <div
                className="absolute z-50 mt-2 w-full bg-white border border-slate-200
                           rounded-2xl shadow-2xl overflow-hidden flex flex-col"
                style={{ maxHeight: '22rem' }}
              >
                {/* search inside dropdown */}
                <div className="p-3 border-b border-slate-100 shrink-0">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                    <input
                      value={searchPresident}
                      onChange={(e) => setSearchPresident(e.target.value)}
                      placeholder="Search name…"
                      autoFocus
                      className="w-full pl-9 pr-3 py-2.5 text-sm bg-slate-50
                                 border border-slate-200 rounded-xl outline-none
                                 focus:border-blue-400 transition-colors"
                    />
                  </div>
                </div>

                {/* list */}
                <div className="overflow-y-auto flex-1">
                  {/* none option */}
                  <div
                    onClick={() => {
                      setSelectedPresidentId(null)
                      setIsPresidentOpen(false)
                    }}
                    className={[
                      'flex items-center justify-between px-5 py-3 text-sm',
                      'cursor-pointer hover:bg-slate-50 border-b border-slate-50',
                      selectedPresidentId === null ? 'bg-blue-50 text-blue-700' : 'text-slate-500',
                    ].join(' ')}
                  >
                    <span className="italic">None — no president</span>
                    {selectedPresidentId === null && <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Selected</span>}
                  </div>

                  {filteredForPresident.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => {
                        setSelectedPresidentId(p.id)
                        setIsPresidentOpen(false)
                      }}
                      className={[
                        'flex items-center justify-between px-5 py-3 text-sm',
                        'cursor-pointer hover:bg-slate-50 border-b border-slate-50 last:border-none',
                        selectedPresidentId === p.id ? 'bg-blue-50' : '',
                      ].join(' ')}
                    >
                      <span className="font-medium text-slate-800 truncate pr-4">{p.content}</span>
                      {selectedPresidentId === p.id && (
                        <span className="shrink-0 text-[10px] font-black text-blue-600 uppercase tracking-widest">Selected</span>
                      )}
                    </div>
                  ))}

                  {filteredForPresident.length === 0 && <div className="py-8 text-center text-slate-400 text-sm italic">No results</div>}
                </div>
              </div>
            )}
          </div>

          {/* current president preview */}
          {selectedPresidentCard && (
            <div className="mt-4">
              <ParticipantCard participant={selectedPresidentCard} />
            </div>
          )}

          <button
            onClick={savePresident}
            className="mt-5 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white
                       text-sm font-bold rounded-xl flex items-center justify-center
                       gap-2 transition-all active:scale-95"
          >
            <Save size={16} /> Save President
          </button>
        </div>
      </div>

      {/* ══════════════════════════════════════════════
           MEMBERS SUB-SECTION
      ══════════════════════════════════════════════ */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        {/* members header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="text-blue-500" size={18} />
            <span className="text-sm font-black uppercase tracking-widest text-slate-600">Members</span>
            <span className="ml-1 px-2 py-0.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-full">{selectedMemberIds.length}</span>
          </div>

          <div className="flex items-center gap-3">
            {hasMembers && (
              <button
                onClick={clearAllMembers}
                className="flex items-center gap-1.5 text-xs font-semibold text-red-500
                           hover:text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-50
                           transition-all"
              >
                <Trash2 size={14} /> Clear All
              </button>
            )}

            <button
              onClick={openModal}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold
                         bg-blue-600 hover:bg-blue-700 text-white rounded-xl
                         transition-all active:scale-95 shadow-sm"
            >
              <UserPlus size={15} /> Add Members
            </button>
          </div>
        </div>

        {/* members grid */}
        <div className="p-6">
          {!hasMembers ? (
            <div className="border border-dashed border-slate-200 rounded-xl py-16 flex flex-col items-center gap-3 text-slate-400">
              <Users size={36} className="text-slate-300" />
              <p className="text-sm font-medium">No members added yet</p>
              <button onClick={openModal} className="mt-1 text-xs font-semibold text-blue-500 hover:text-blue-700 underline underline-offset-2">
                Add members
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {orderedMembers.map((m) => (
                <ParticipantCard key={m.id} participant={m} onRemove={() => removeMember(m.id)} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ══════════════════════════════════════════════
           ADD MEMBERS MODAL
      ══════════════════════════════════════════════ */}
      {showModal &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal()
            }}
          >
            <div className="w-full max-w-5xl bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden" style={{ maxHeight: '90vh' }}>
              {/* modal header */}
              <div className="px-7 py-5 border-b border-slate-100 flex items-center justify-between shrink-0">
                <div>
                  <h2 className="text-lg font-black text-slate-800">Manage Meeting Members</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Check members to select them, then Add Selected · drag to reorder</p>
                </div>
                <button onClick={closeModal} className="p-2 rounded-xl hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-all">
                  <X size={20} />
                </button>
              </div>

              {/* modal body: two panels */}
              <div className="flex-1 overflow-hidden flex flex-col lg:flex-row min-h-0">
                {/* LEFT: selected members (draggable) */}
                <div className="flex-1 border-b lg:border-b-0 lg:border-r border-slate-100 flex flex-col overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-100 flex items-center gap-2 shrink-0 bg-slate-50/70">
                    <Users size={15} className="text-blue-500" />
                    <span className="text-xs font-black uppercase tracking-widest text-slate-500">Selected Members</span>
                    <span className="ml-auto px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">{modalSelected.length}</span>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    {modalSelected.length === 0 && (
                      <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2 py-10">
                        <Users size={32} className="text-slate-200" />
                        <p className="text-sm">No members selected yet</p>
                      </div>
                    )}

                    {modalSelected.map((m, idx) => (
                      <div
                        key={m.id}
                        draggable
                        onDragStart={() => onDragStart(idx)}
                        onDragOver={(e) => onDragOver(e, idx)}
                        onDragEnd={onDragEnd}
                        className={['flex items-center gap-2 cursor-grab active:cursor-grabbing', dragFromIndex === idx ? 'opacity-50' : ''].join(' ')}
                      >
                        {/* grip handle */}
                        <GripVertical size={16} className="shrink-0 text-slate-300 hover:text-slate-500 transition-colors" />
                        {/* card */}
                        <div className="flex-1 min-w-0">
                          <ParticipantCard participant={m} onRemove={() => modalToggleRemove(m.id)} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* RIGHT: available members */}
                <div className="flex-1 flex flex-col overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-100 shrink-0 bg-slate-50/70 space-y-2">
                    {/* search */}
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                      <input
                        value={modalSearch}
                        onChange={(e) => setModalSearch(e.target.value)}
                        placeholder="Search by name, email, department, or faculty…"
                        aria-label="Search available members by name, email, department, or faculty"
                        className="w-full pl-9 pr-8 py-2 text-sm bg-white
                                   border border-slate-200 rounded-xl outline-none
                                   focus:border-blue-400 focus-visible:ring-2 focus-visible:ring-blue-200 transition-colors"
                      />
                      {modalSearch && (
                        <button
                          onClick={() => setModalSearch('')}
                          aria-label="Clear search"
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600
                                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 rounded"
                        >
                          <X size={14} />
                        </button>
                      )}
                    </div>

                    {/* faculty / department filters + sort */}
                    <div className="flex flex-wrap items-center gap-2">
                      <select
                        value={modalFacultyId}
                        onChange={(e) => {
                          setModalFacultyId(e.target.value)
                          setModalDepartmentId('') // reset dependent dropdown
                        }}
                        aria-label="Filter by faculty"
                        className="flex-1 min-w-[120px] px-2.5 py-1.5 text-xs font-medium bg-white
                                   border border-slate-200 rounded-lg outline-none text-slate-600
                                   focus:border-blue-400 transition-colors"
                      >
                        <option value="">All Faculties</option>
                        {faculties.map((f) => (
                          <option key={f.id} value={f.id}>
                            {f.name}
                          </option>
                        ))}
                      </select>

                      <select
                        value={modalDepartmentId}
                        onChange={(e) => setModalDepartmentId(e.target.value)}
                        aria-label="Filter by department"
                        className="flex-1 min-w-[120px] px-2.5 py-1.5 text-xs font-medium bg-white
                                   border border-slate-200 rounded-lg outline-none text-slate-600
                                   focus:border-blue-400 transition-colors"
                      >
                        <option value="">All Departments</option>
                        {departmentOptions.map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.name}
                          </option>
                        ))}
                      </select>

                      <button
                        onClick={() => setSortByFaculty((v) => !v)}
                        aria-pressed={sortByFaculty}
                        className={[
                          'flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg transition-all',
                          sortByFaculty ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200 text-slate-500 hover:border-slate-300',
                        ].join(' ')}
                      >
                        <ArrowUpDown size={12} /> Sort by Faculty
                      </button>
                    </div>

                    <div className="flex items-center gap-2">
                      <Plus size={13} className="text-green-500 shrink-0" />
                      <span className="text-xs font-black uppercase tracking-widest text-slate-500">Available</span>
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-full">{modalAvailable.length}</span>

                      <div className="ml-auto flex items-center gap-2">
                        <button
                          onClick={clearSelection}
                          disabled={modalDraftIds.length === 0}
                          className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-red-600
                                     px-2.5 py-1.5 rounded-lg hover:bg-red-50 transition-all
                                     disabled:opacity-40 disabled:pointer-events-none
                                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300"
                        >
                          <X size={12} /> Clear Selection
                        </button>
                        <button
                          onClick={selectAllFiltered}
                          disabled={allFilteredSelected}
                          className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800
                                     px-2.5 py-1.5 rounded-lg hover:bg-blue-50 transition-all
                                     disabled:opacity-40 disabled:pointer-events-none
                                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300"
                        >
                          <ListChecks size={13} /> Select All ({modalAvailable.length})
                        </button>
                      </div>
                    </div>

                    {modalDraftIds.length > 0 && (
                      <p className="text-xs font-bold text-blue-700">
                        Selected ({modalDraftIds.length})
                      </p>
                    )}
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    {modalAvailable.length === 0 && (
                      <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2 py-10">
                        <Users size={32} className="text-slate-200" />
                        <p className="text-sm italic">{modalSearch ? 'No results' : 'No participants found'}</p>
                      </div>
                    )}

                    {modalAvailable.map((p) => (
                      <MemberSelectRow key={p.id} participant={p} selected={modalDraftIds.includes(p.id)} onToggle={modalToggle} />
                    ))}
                  </div>
                </div>
              </div>

              {/* modal footer */}
              <div className="px-7 py-5 border-t border-slate-100 flex items-center justify-end gap-3 shrink-0 bg-slate-50/50">
                <button
                  onClick={closeModal}
                  className="px-6 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={saveModal}
                  disabled={modalDraftIds.length === 0}
                  className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700
                             text-white text-sm font-bold flex items-center gap-2
                             transition-all active:scale-95 shadow-sm
                             disabled:opacity-40 disabled:pointer-events-none disabled:active:scale-100
                             focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2"
                >
                  <Save size={15} />
                  Add Selected ({modalDraftIds.length})
                </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  )
}
