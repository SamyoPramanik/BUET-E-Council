import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'react-toastify'
import api from '../utils/api'
import { isValidEmail } from '../utils/validators'
import { confirmDestructive } from '../utils/alerts'
import BackButton from '../components/BackButton'
import type {
  FacultyRead,
  FacultyCreate,
  FacultyUpdate,
  DepartmentRead,
  DepartmentCreate,
  DepartmentUpdate,
  ParticipantRead,
  ParticipantCreate,
  ParticipantUpdate,
  MemberRole,
} from '../types/api'

type Tab = 'faculties' | 'departments' | 'participants'

const inputClass =
  'w-full px-4 py-3 text-slate-900 bg-slate-50 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all disabled:cursor-not-allowed'

function errorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : fallback
}

// ── edit modal form shapes ───────────────────────────────────────────────

interface FacultyFormState {
  order: string
  name_bangla: string
  name_english: string
}
const emptyFacultyForm = (): FacultyFormState => ({ order: '', name_bangla: '', name_english: '' })

interface DepartmentFormState {
  name_bangla: string
  name_english: string
  alias_bangla: string
  alias_english: string
  faculty_id: string
}
const emptyDepartmentForm = (): DepartmentFormState => ({
  name_bangla: '',
  name_english: '',
  alias_bangla: '',
  alias_english: '',
  faculty_id: '',
})

interface ParticipantFormState {
  content: string
  role: MemberRole
  email: string
  is_external: boolean
  department_id: string
}
const emptyParticipantForm = (): ParticipantFormState => ({
  content: '',
  role: 'Regular',
  email: '',
  is_external: false,
  department_id: '',
})

type EditTarget =
  | { kind: 'faculty'; record: FacultyRead }
  | { kind: 'department'; record: DepartmentRead }
  | { kind: 'participant'; record: ParticipantRead }
  | null

export default function ManageDirectoryView() {
  const [tab, setTab] = useState<Tab>('faculties')

  // ── data ─────────────────────────────────────────────────────────────────
  const [faculties, setFaculties] = useState<FacultyRead[]>([])
  const [departments, setDepartments] = useState<DepartmentRead[]>([])
  const [participants, setParticipants] = useState<ParticipantRead[]>([])
  const [loadingFaculties, setLoadingFaculties] = useState(false)
  const [loadingDepartments, setLoadingDepartments] = useState(false)
  const [loadingParticipants, setLoadingParticipants] = useState(false)

  const facultiesByOrder = useMemo(() => [...faculties].sort((a, b) => a.order - b.order), [faculties])
  const departmentsByName = useMemo(
    () => [...departments].sort((a, b) => a.name.localeCompare(b.name)),
    [departments],
  )

  const fetchFaculties = async () => {
    setLoadingFaculties(true)
    try {
      const { data } = await api.get<FacultyRead[]>('/faculties')
      setFaculties(data)
    } catch {
      toast.error('Failed to load faculties.')
    } finally {
      setLoadingFaculties(false)
    }
  }

  const fetchDepartments = async () => {
    setLoadingDepartments(true)
    try {
      const { data } = await api.get<DepartmentRead[]>('/departments')
      setDepartments(data)
    } catch {
      toast.error('Failed to load departments.')
    } finally {
      setLoadingDepartments(false)
    }
  }

  const fetchParticipants = async () => {
    setLoadingParticipants(true)
    try {
      const { data } = await api.get<ParticipantRead[]>('/participants')
      setParticipants(data)
    } catch {
      toast.error('Failed to load participants.')
    } finally {
      setLoadingParticipants(false)
    }
  }

  useEffect(() => {
    fetchFaculties()
    fetchDepartments()
    fetchParticipants()
  }, [])

  // ── create: faculty ──────────────────────────────────────────────────────
  const [facForm, setFacForm] = useState<FacultyFormState>(emptyFacultyForm())
  const [facSubmitting, setFacSubmitting] = useState(false)

  const handleCreateFaculty = async () => {
    if (facSubmitting) return
    if (!facForm.name_bangla.trim()) {
      toast.error('Bangla name is required.')
      return
    }
    const order = Number(facForm.order)
    if (!facForm.order || !Number.isFinite(order) || order < 1) {
      toast.warning('Please enter a valid display order (positive number).')
      return
    }

    const payload: FacultyCreate = {
      order,
      name_bangla: facForm.name_bangla.trim(),
      name_english: facForm.name_english.trim() || undefined,
    }

    setFacSubmitting(true)
    try {
      await api.post('/faculties', payload)
      toast.success('Faculty created.')
      setFacForm(emptyFacultyForm())
      await fetchFaculties()
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to create faculty.'))
    } finally {
      setFacSubmitting(false)
    }
  }

  const handleDeleteFaculty = async (f: FacultyRead) => {
    const confirmed = await confirmDestructive(
      'Delete this faculty?',
      `"${f.name}" and all of its departments (and their participant cards) will be removed.`,
      'Delete',
    )
    if (!confirmed) return
    try {
      await api.delete(`/faculties/${f.id}`)
      toast.success('Faculty deleted.')
      await Promise.all([fetchFaculties(), fetchDepartments(), fetchParticipants()])
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to delete faculty.'))
    }
  }

  // ── create: department ───────────────────────────────────────────────────
  const [depForm, setDepForm] = useState<DepartmentFormState>(emptyDepartmentForm())
  const [depSubmitting, setDepSubmitting] = useState(false)

  const handleCreateDepartment = async () => {
    if (depSubmitting) return
    if (!depForm.name_bangla.trim() || !depForm.alias_bangla.trim()) {
      toast.error('Bangla name and Bangla alias are required.')
      return
    }
    if (!depForm.faculty_id) {
      toast.warning('Please select a faculty.')
      return
    }

    const payload: DepartmentCreate = {
      name_bangla: depForm.name_bangla.trim(),
      name_english: depForm.name_english.trim() || undefined,
      alias_bangla: depForm.alias_bangla.trim(),
      alias_english: depForm.alias_english.trim() || undefined,
      faculty_id: depForm.faculty_id,
    }

    setDepSubmitting(true)
    try {
      await api.post('/departments', payload)
      toast.success('Department created.')
      setDepForm(emptyDepartmentForm())
      await fetchDepartments()
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to create department.'))
    } finally {
      setDepSubmitting(false)
    }
  }

  const handleDeleteDepartment = async (d: DepartmentRead) => {
    const confirmed = await confirmDestructive(
      'Delete this department?',
      `"${d.name}" and all of its participant cards will be removed.`,
      'Delete',
    )
    if (!confirmed) return
    try {
      await api.delete(`/departments/${d.id}`)
      toast.success('Department deleted.')
      await Promise.all([fetchDepartments(), fetchParticipants()])
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to delete department.'))
    }
  }

  // ── create: participant ──────────────────────────────────────────────────
  const [parForm, setParForm] = useState<ParticipantFormState>(emptyParticipantForm())
  const [parSubmitting, setParSubmitting] = useState(false)
  const [participantSearch, setParticipantSearch] = useState('')

  const handleCreateParticipant = async () => {
    if (parSubmitting) return
    if (!parForm.content.trim()) {
      toast.error('Name / content is required.')
      return
    }
    if (!parForm.department_id) {
      toast.warning('Please select a department.')
      return
    }
    if (parForm.email && !isValidEmail(parForm.email)) {
      toast.warning('Please enter a valid email address.')
      return
    }

    const payload: ParticipantCreate = {
      content: parForm.content.trim(),
      role: parForm.role,
      email: parForm.email.trim() || undefined,
      is_external: parForm.is_external,
      department_id: parForm.department_id,
    }

    setParSubmitting(true)
    try {
      await api.post('/participants', payload)
      toast.success('Participant added.')
      setParForm(emptyParticipantForm())
      await fetchParticipants()
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to add participant.'))
    } finally {
      setParSubmitting(false)
    }
  }

  const handleDeleteParticipant = async (p: ParticipantRead) => {
    const confirmed = await confirmDestructive(
      'Remove this participant?',
      `"${p.content}" will be removed from the directory and from any meetings it's attached to.`,
      'Remove',
    )
    if (!confirmed) return
    try {
      await api.delete(`/participants/${p.id}`)
      toast.success('Participant removed.')
      await fetchParticipants()
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to remove participant.'))
    }
  }

  const filteredParticipants = useMemo(() => {
    const q = participantSearch.trim().toLowerCase()
    if (!q) return participants
    return participants.filter(
      (p) =>
        p.content.toLowerCase().includes(q) ||
        (p.department ?? '').toLowerCase().includes(q) ||
        (p.faculty ?? '').toLowerCase().includes(q) ||
        (p.email ?? '').toLowerCase().includes(q),
    )
  }, [participants, participantSearch])

  // ── edit modal (shared across all three resources) ─────────────────────────
  const [editTarget, setEditTarget] = useState<EditTarget>(null)
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [facEditForm, setFacEditForm] = useState<FacultyFormState>(emptyFacultyForm())
  const [depEditForm, setDepEditForm] = useState<DepartmentFormState>(emptyDepartmentForm())
  const [parEditForm, setParEditForm] = useState<ParticipantFormState>(emptyParticipantForm())

  const openEditFaculty = (f: FacultyRead) => {
    setFacEditForm({ order: String(f.order), name_bangla: f.name_bangla, name_english: f.name_english ?? '' })
    setEditTarget({ kind: 'faculty', record: f })
  }
  const openEditDepartment = (d: DepartmentRead) => {
    setDepEditForm({
      name_bangla: d.name_bangla,
      name_english: d.name_english ?? '',
      alias_bangla: d.alias_bangla,
      alias_english: d.alias_english ?? '',
      faculty_id: d.faculty_id,
    })
    setEditTarget({ kind: 'department', record: d })
  }
  const openEditParticipant = (p: ParticipantRead) => {
    setParEditForm({
      content: p.content,
      role: p.role,
      email: p.email ?? '',
      is_external: p.is_external,
      department_id: p.department_id ?? '',
    })
    setEditTarget({ kind: 'participant', record: p })
  }

  const closeEdit = () => {
    if (editSubmitting) return
    setEditTarget(null)
  }

  const submitEdit = async () => {
    if (!editTarget || editSubmitting) return
    setEditSubmitting(true)
    try {
      if (editTarget.kind === 'faculty') {
        const order = Number(facEditForm.order)
        if (!facEditForm.name_bangla.trim()) throw { response: { data: { detail: 'Bangla name is required.' } } }
        if (!facEditForm.order || !Number.isFinite(order) || order < 1) {
          throw { response: { data: { detail: 'Please enter a valid display order.' } } }
        }
        const payload: FacultyUpdate = {
          order,
          name_bangla: facEditForm.name_bangla.trim(),
          name_english: facEditForm.name_english.trim() || undefined,
        }
        await api.patch(`/faculties/${editTarget.record.id}`, payload)
        toast.success('Faculty updated.')
        await fetchFaculties()
      } else if (editTarget.kind === 'department') {
        if (!depEditForm.name_bangla.trim() || !depEditForm.alias_bangla.trim()) {
          throw { response: { data: { detail: 'Bangla name and Bangla alias are required.' } } }
        }
        const payload: DepartmentUpdate = {
          name_bangla: depEditForm.name_bangla.trim(),
          name_english: depEditForm.name_english.trim() || undefined,
          alias_bangla: depEditForm.alias_bangla.trim(),
          alias_english: depEditForm.alias_english.trim() || undefined,
          faculty_id: depEditForm.faculty_id,
        }
        await api.patch(`/departments/${editTarget.record.id}`, payload)
        toast.success('Department updated.')
        await fetchDepartments()
      } else {
        if (!parEditForm.content.trim()) throw { response: { data: { detail: 'Name / content is required.' } } }
        if (parEditForm.email && !isValidEmail(parEditForm.email)) {
          throw { response: { data: { detail: 'Please enter a valid email address.' } } }
        }
        const payload: ParticipantUpdate = {
          content: parEditForm.content.trim(),
          role: parEditForm.role,
          email: parEditForm.email.trim() || undefined,
          is_external: parEditForm.is_external,
          department_id: parEditForm.department_id,
        }
        await api.patch(`/participants/${editTarget.record.id}`, payload)
        toast.success('Participant updated.')
        await fetchParticipants()
      }
      setEditTarget(null)
    } catch (error) {
      toast.error(errorMessage(error, 'Failed to save changes.'))
    } finally {
      setEditSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      <div className="h-6 mb-4"></div>

      <div className="mx-auto w-full lg:w-4/5 px-4 sm:px-6">
        <BackButton className="mb-3" />

        <div className="mb-2">
          <h1 className="text-2xl font-black text-slate-800">Directory</h1>
          <p className="text-sm text-slate-500 font-medium">Manage faculties, departments, and the participant directory.</p>
        </div>

        {/* ── TABS ─────────────────────────────────────────────────────────── */}
        <div className="flex space-x-1 bg-slate-200/60 p-1 rounded-xl my-6 w-full sm:w-fit border border-slate-200">
          {(
            [
              ['faculties', `Faculties (${faculties.length})`],
              ['departments', `Departments (${departments.length})`],
              ['participants', `Participants (${participants.length})`],
            ] as [Tab, string][]
          ).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={[
                'px-4 py-2 text-sm font-semibold rounded-lg transition-all whitespace-nowrap',
                tab === key ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800',
              ].join(' ')}
            >
              {label}
            </button>
          ))}
        </div>

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* FACULTIES                                                          */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {tab === 'faculties' && (
          <>
            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 p-8 mb-8">
              <h2 className="text-xl font-black text-slate-800 mb-1">Add Faculty</h2>
              <p className="text-sm text-slate-500 font-medium mb-6">Faculties group departments (e.g. যন্ত্রকৌশল অনুষদ).</p>

              <div className="grid sm:grid-cols-4 gap-4 mb-4">
                <input
                  value={facForm.order}
                  onChange={(e) => setFacForm((f) => ({ ...f, order: e.target.value }))}
                  type="number"
                  min={1}
                  placeholder="Display order"
                  disabled={facSubmitting}
                  className={inputClass}
                />
                <input
                  value={facForm.name_bangla}
                  onChange={(e) => setFacForm((f) => ({ ...f, name_bangla: e.target.value }))}
                  placeholder="Name (Bangla)"
                  disabled={facSubmitting}
                  className={`sm:col-span-2 ${inputClass}`}
                />
                <input
                  value={facForm.name_english}
                  onChange={(e) => setFacForm((f) => ({ ...f, name_english: e.target.value }))}
                  placeholder="Name (English, optional)"
                  disabled={facSubmitting}
                  className={inputClass}
                />
              </div>

              <button
                onClick={handleCreateFaculty}
                disabled={facSubmitting}
                className="w-full sm:w-auto px-8 py-3 bg-blue-600 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-blue-700 transition-all active:scale-95 disabled:bg-blue-300 disabled:cursor-not-allowed"
              >
                {facSubmitting ? 'Creating...' : 'Create Faculty'}
              </button>
            </div>

            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
              <div className="p-8 border-b border-gray-50">
                <h2 className="text-xl font-black text-slate-800">All Faculties</h2>
                <p className="text-sm text-slate-500 font-medium">{loadingFaculties ? 'Loading…' : `${faculties.length} total`}</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
                    <tr>
                      <th className="px-8 py-4">Order</th>
                      <th className="px-8 py-4">Bangla Name</th>
                      <th className="px-8 py-4">English Name</th>
                      <th className="px-8 py-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {facultiesByOrder.map((f) => (
                      <tr key={f.id} className="hover:bg-slate-50/30 transition-colors">
                        <td className="px-8 py-6 text-sm font-mono font-bold text-slate-500">{f.order}</td>
                        <td className="px-8 py-6 text-sm font-bold text-slate-700">{f.name_bangla}</td>
                        <td className="px-8 py-6 text-sm font-medium text-slate-500">{f.name_english || '—'}</td>
                        <td className="px-8 py-6 text-right space-x-2 whitespace-nowrap">
                          <button
                            onClick={() => openEditFaculty(f)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteFaculty(f)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {!loadingFaculties && faculties.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-8 py-12 text-center text-slate-400 italic">
                          No faculties yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* DEPARTMENTS                                                        */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {tab === 'departments' && (
          <>
            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 p-8 mb-8">
              <h2 className="text-xl font-black text-slate-800 mb-1">Add Department</h2>
              <p className="text-sm text-slate-500 font-medium mb-6">Departments belong to a faculty and use a short alias for meeting-minutes extraction.</p>

              <div className="grid sm:grid-cols-2 gap-4 mb-4">
                <input
                  value={depForm.name_bangla}
                  onChange={(e) => setDepForm((f) => ({ ...f, name_bangla: e.target.value }))}
                  placeholder="Name (Bangla)"
                  disabled={depSubmitting}
                  className={inputClass}
                />
                <input
                  value={depForm.name_english}
                  onChange={(e) => setDepForm((f) => ({ ...f, name_english: e.target.value }))}
                  placeholder="Name (English, optional)"
                  disabled={depSubmitting}
                  className={inputClass}
                />
                <input
                  value={depForm.alias_bangla}
                  onChange={(e) => setDepForm((f) => ({ ...f, alias_bangla: e.target.value }))}
                  placeholder="Alias (Bangla), e.g. কেমিকৌশল"
                  disabled={depSubmitting}
                  className={inputClass}
                />
                <input
                  value={depForm.alias_english}
                  onChange={(e) => setDepForm((f) => ({ ...f, alias_english: e.target.value }))}
                  placeholder="Alias (English, optional)"
                  disabled={depSubmitting}
                  className={inputClass}
                />
                <select
                  value={depForm.faculty_id}
                  onChange={(e) => setDepForm((f) => ({ ...f, faculty_id: e.target.value }))}
                  disabled={depSubmitting}
                  className={`sm:col-span-2 ${inputClass}`}
                >
                  <option value="">Select faculty…</option>
                  {facultiesByOrder.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleCreateDepartment}
                disabled={depSubmitting}
                className="w-full sm:w-auto px-8 py-3 bg-blue-600 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-blue-700 transition-all active:scale-95 disabled:bg-blue-300 disabled:cursor-not-allowed"
              >
                {depSubmitting ? 'Creating...' : 'Create Department'}
              </button>
            </div>

            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
              <div className="p-8 border-b border-gray-50">
                <h2 className="text-xl font-black text-slate-800">All Departments</h2>
                <p className="text-sm text-slate-500 font-medium">{loadingDepartments ? 'Loading…' : `${departments.length} total`}</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
                    <tr>
                      <th className="px-8 py-4">Name</th>
                      <th className="px-8 py-4">Alias</th>
                      <th className="px-8 py-4">Faculty</th>
                      <th className="px-8 py-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {departmentsByName.map((d) => (
                      <tr key={d.id} className="hover:bg-slate-50/30 transition-colors">
                        <td className="px-8 py-6 text-sm font-bold text-slate-700">{d.name}</td>
                        <td className="px-8 py-6">
                          <span className="px-3 py-1 text-[10px] font-black uppercase rounded-lg tracking-widest bg-slate-50 text-slate-600 border border-slate-100">
                            {d.alias_bangla}
                          </span>
                        </td>
                        <td className="px-8 py-6 text-sm font-medium text-slate-500">
                          {faculties.find((f) => f.id === d.faculty_id)?.name || '—'}
                        </td>
                        <td className="px-8 py-6 text-right space-x-2 whitespace-nowrap">
                          <button
                            onClick={() => openEditDepartment(d)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteDepartment(d)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {!loadingDepartments && departments.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-8 py-12 text-center text-slate-400 italic">
                          No departments yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* PARTICIPANTS                                                       */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {tab === 'participants' && (
          <>
            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 p-8 mb-8">
              <h2 className="text-xl font-black text-slate-800 mb-1">Add Participant</h2>
              <p className="text-sm text-slate-500 font-medium mb-6">
                This directory is the pool meetings draw their attendee list from. Only admins can add, edit, or remove entries here.
              </p>

              <div className="grid sm:grid-cols-2 gap-4 mb-4">
                <input
                  value={parForm.content}
                  onChange={(e) => setParForm((f) => ({ ...f, content: e.target.value }))}
                  placeholder="Full name / title, e.g. অধ্যাপক ডঃ ..."
                  disabled={parSubmitting}
                  className={`sm:col-span-2 ${inputClass}`}
                />
                <select
                  value={parForm.department_id}
                  onChange={(e) => setParForm((f) => ({ ...f, department_id: e.target.value }))}
                  disabled={parSubmitting}
                  className={inputClass}
                >
                  <option value="">Select department…</option>
                  {departmentsByName.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.alias_bangla})
                    </option>
                  ))}
                </select>
                <select
                  value={parForm.role}
                  onChange={(e) => setParForm((f) => ({ ...f, role: e.target.value as MemberRole }))}
                  disabled={parSubmitting}
                  className={inputClass}
                >
                  <option value="Regular">Regular</option>
                  <option value="Head">Head</option>
                  <option value="Dean">Dean</option>
                </select>
                <input
                  value={parForm.email}
                  onChange={(e) => setParForm((f) => ({ ...f, email: e.target.value }))}
                  type="email"
                  placeholder="Email (optional)"
                  disabled={parSubmitting}
                  className={inputClass}
                />
                <label className="flex items-center gap-2 px-4 py-3 text-sm font-semibold text-slate-600">
                  <input
                    type="checkbox"
                    checked={parForm.is_external}
                    onChange={(e) => setParForm((f) => ({ ...f, is_external: e.target.checked }))}
                    disabled={parSubmitting}
                    className="w-4 h-4 accent-blue-600"
                  />
                  External guest (not BUET faculty/staff)
                </label>
              </div>

              <button
                onClick={handleCreateParticipant}
                disabled={parSubmitting}
                className="w-full sm:w-auto px-8 py-3 bg-blue-600 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-blue-700 transition-all active:scale-95 disabled:bg-blue-300 disabled:cursor-not-allowed"
              >
                {parSubmitting ? 'Adding...' : 'Add Participant'}
              </button>
            </div>

            <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
              <div className="p-8 border-b border-gray-50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h2 className="text-xl font-black text-slate-800">All Participants</h2>
                  <p className="text-sm text-slate-500 font-medium">
                    {loadingParticipants ? 'Loading…' : `${filteredParticipants.length} of ${participants.length} shown`}
                  </p>
                </div>
                <input
                  value={participantSearch}
                  onChange={(e) => setParticipantSearch(e.target.value)}
                  placeholder="Search by name, department, email…"
                  className="w-full sm:w-72 px-4 py-2.5 text-sm text-slate-900 bg-slate-50 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                />
              </div>
              <div className="overflow-x-auto max-h-[32rem] overflow-y-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em] sticky top-0">
                    <tr>
                      <th className="px-8 py-4">Name</th>
                      <th className="px-8 py-4">Role</th>
                      <th className="px-8 py-4">Department</th>
                      <th className="px-8 py-4">Email</th>
                      <th className="px-8 py-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filteredParticipants.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-50/30 transition-colors">
                        <td className="px-8 py-6 text-sm font-bold text-slate-700 max-w-xs">
                          <div className="flex items-center gap-2">
                            <span className="truncate" title={p.content}>
                              {p.content}
                            </span>
                            {p.is_external && (
                              <span className="shrink-0 px-2 py-0.5 text-[9px] font-black uppercase rounded-full tracking-widest bg-amber-50 text-amber-700 border border-amber-200">
                                External
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-8 py-6">
                          <span className="px-3 py-1 text-[10px] font-black uppercase rounded-lg tracking-widest bg-slate-50 text-slate-600 border border-slate-100">
                            {p.role}
                          </span>
                        </td>
                        <td className="px-8 py-6 text-sm font-medium text-slate-500">{p.department || '—'}</td>
                        <td className="px-8 py-6 text-sm font-medium text-slate-500">{p.email || '—'}</td>
                        <td className="px-8 py-6 text-right space-x-2 whitespace-nowrap">
                          <button
                            onClick={() => openEditParticipant(p)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-blue-600 hover:border-blue-200"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteParticipant(p)}
                            className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                    {!loadingParticipants && filteredParticipants.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-8 py-12 text-center text-slate-400 italic">
                          {participants.length === 0 ? 'No participants yet.' : 'No participants match your search.'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════════════════ */}
      {/* EDIT MODAL                                                             */}
      {/* ══════════════════════════════════════════════════════════════════════ */}
      {editTarget &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeEdit()
            }}
          >
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
                <h2 className="text-lg font-black text-slate-800">
                  Edit {editTarget.kind === 'faculty' ? 'Faculty' : editTarget.kind === 'department' ? 'Department' : 'Participant'}
                </h2>
                <button onClick={closeEdit} className="p-2 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>

              <div className="px-6 py-6 space-y-4">
                {editTarget.kind === 'faculty' && (
                  <>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Display order</label>
                      <input
                        value={facEditForm.order}
                        onChange={(e) => setFacEditForm((f) => ({ ...f, order: e.target.value }))}
                        type="number"
                        min={1}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Name (Bangla)</label>
                      <input
                        value={facEditForm.name_bangla}
                        onChange={(e) => setFacEditForm((f) => ({ ...f, name_bangla: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Name (English)</label>
                      <input
                        value={facEditForm.name_english}
                        onChange={(e) => setFacEditForm((f) => ({ ...f, name_english: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                  </>
                )}

                {editTarget.kind === 'department' && (
                  <>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Name (Bangla)</label>
                      <input
                        value={depEditForm.name_bangla}
                        onChange={(e) => setDepEditForm((f) => ({ ...f, name_bangla: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Name (English)</label>
                      <input
                        value={depEditForm.name_english}
                        onChange={(e) => setDepEditForm((f) => ({ ...f, name_english: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Alias (Bangla)</label>
                      <input
                        value={depEditForm.alias_bangla}
                        onChange={(e) => setDepEditForm((f) => ({ ...f, alias_bangla: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Alias (English)</label>
                      <input
                        value={depEditForm.alias_english}
                        onChange={(e) => setDepEditForm((f) => ({ ...f, alias_english: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Faculty</label>
                      <select
                        value={depEditForm.faculty_id}
                        onChange={(e) => setDepEditForm((f) => ({ ...f, faculty_id: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      >
                        {facultiesByOrder.map((f) => (
                          <option key={f.id} value={f.id}>
                            {f.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                {editTarget.kind === 'participant' && (
                  <>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Name / content</label>
                      <input
                        value={parEditForm.content}
                        onChange={(e) => setParEditForm((f) => ({ ...f, content: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Department</label>
                      <select
                        value={parEditForm.department_id}
                        onChange={(e) => setParEditForm((f) => ({ ...f, department_id: e.target.value }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      >
                        {departmentsByName.map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.name} ({d.alias_bangla})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Role</label>
                      <select
                        value={parEditForm.role}
                        onChange={(e) => setParEditForm((f) => ({ ...f, role: e.target.value as MemberRole }))}
                        disabled={editSubmitting}
                        className={inputClass}
                      >
                        <option value="Regular">Regular</option>
                        <option value="Head">Head</option>
                        <option value="Dean">Dean</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-2">Email</label>
                      <input
                        value={parEditForm.email}
                        onChange={(e) => setParEditForm((f) => ({ ...f, email: e.target.value }))}
                        type="email"
                        disabled={editSubmitting}
                        className={inputClass}
                      />
                    </div>
                    <label className="flex items-center gap-2 text-sm font-semibold text-slate-600">
                      <input
                        type="checkbox"
                        checked={parEditForm.is_external}
                        onChange={(e) => setParEditForm((f) => ({ ...f, is_external: e.target.checked }))}
                        disabled={editSubmitting}
                        className="w-4 h-4 accent-blue-600"
                      />
                      External guest (not BUET faculty/staff)
                    </label>
                  </>
                )}
              </div>

              <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-3">
                <button onClick={closeEdit} className="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-white transition-all">
                  Cancel
                </button>
                <button
                  onClick={submitEdit}
                  disabled={editSubmitting}
                  className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl transition-all disabled:opacity-60 disabled:cursor-not-allowed active:scale-95"
                >
                  {editSubmitting ? 'Saving…' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  )
}
