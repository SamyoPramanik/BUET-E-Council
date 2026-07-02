import { useCallback, useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { toast } from 'react-toastify'
import Swal from 'sweetalert2'
import {
  Menu,
  X,
  Info,
  Layout,
  FileText,
  CheckCircle,
  Hash,
  Calendar,
  Edit3,
  Save,
  Users,
  ListOrdered,
  FileDown,
  Trash2,
  Plus,
  GripVertical,
  UploadCloud,
  Download,
  File as FileIcon,
  PenLine,
  Printer,
  type LucideIcon,
} from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../auth/AuthContext'
import { confirmDestructive } from '../utils/alerts'

import ParticipantsSection from '../components/ParticipantsSection'
import ParticipantCard from '../components/ParticipantCard'
import AgendaBox from '../components/AgendaBox'
import InsertStrip from '../components/InsertStrip'
import SignatureCardsSection from '../components/SignatureCardsSection'
import PrintableMeeting from '../components/PrintableMeeting'
import type { Meeting, ParticipantRead, AgendumResponse, SignatureCardResponse } from '../types/api'
import './MeetingDetailsView.css'

const OFFSET = 10000

const staticSections: { id: string; label: string; icon: LucideIcon; suppl: boolean }[] = [
  { id: 'info', label: 'Basic Info', icon: Info, suppl: false },
  { id: 'title', label: 'Meeting Title', icon: Layout, suppl: false },
  { id: 'description', label: 'Discussion & Minutes', icon: FileText, suppl: false },
  { id: 'participants', label: 'Participants', icon: Users, suppl: false },
  { id: 'agendas', label: 'Agendas', icon: ListOrdered, suppl: false },
  { id: 'suppl-agendas', label: 'Supplementary Agendas', icon: ListOrdered, suppl: true },
  { id: 'materials', label: 'Materials', icon: FileDown, suppl: false },
  { id: 'conclusion', label: 'Final Conclusion', icon: CheckCircle, suppl: false },
  { id: 'signatures', label: 'Signature Cards', icon: PenLine, suppl: false },
]

export default function MeetingDetailsView() {
  const { id: meetingId } = useParams<{ id: string }>()
  const { userRole } = useAuth()
  const canModify = ['admin', 'staff'].includes(userRole)

  // ── layout ────────────────────────────────────────────────────────────────────
  const [showSections, setShowSections] = useState(false)

  // ── data ──────────────────────────────────────────────────────────────────────
  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [loading, setLoading] = useState(true)
  const [allParticipants, setAllParticipants] = useState<ParticipantRead[]>([])
  const [meetingMembers, setMeetingMembers] = useState<ParticipantRead[]>([])
  const [agendas, setAgendas] = useState<AgendumResponse[]>([])
  const [signatureCards, setSignatureCards] = useState<SignatureCardResponse[]>([])

  const currentPresident = meeting?.president_card_id ? allParticipants.find((p) => p.id === meeting.president_card_id) ?? null : null

  // Split agendas into two independent lists
  const regularAgendas = [...agendas].filter((a) => !a.is_supplementary).sort((a, b) => a.serial - b.serial)
  const supplAgendas = [...agendas].filter((a) => a.is_supplementary).sort((a, b) => a.serial - b.serial)

  // ── sidebar sections ──────────────────────────────────────────────────────────
  const [activeSection, setActiveSection] = useState('info')
  const observersRef = useRef<IntersectionObserver[]>([])

  const setupObservers = useCallback(() => {
    observersRef.current.forEach((o) => o.disconnect())
    observersRef.current = []
    const ids = [...staticSections.map((s) => s.id), ...agendas.map((a) => `agenda-${a.id}`)]
    ids.forEach((id) => {
      const el = document.getElementById(id)
      if (!el) return
      const obs = new IntersectionObserver(
        ([e]) => {
          if (e.isIntersecting) setActiveSection(id)
        },
        { rootMargin: '-15% 0px -65% 0px', threshold: 0 },
      )
      obs.observe(el)
      observersRef.current.push(obs)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agendas])

  useEffect(() => {
    return () => observersRef.current.forEach((o) => o.disconnect())
  }, [])

  // ── fetch ─────────────────────────────────────────────────────────────────────
  const fetchAllData = useCallback(async () => {
    setLoading(true)
    try {
      const [mRes, pRes, mbRes, agRes, sigRes] = await Promise.all([
        api.get<Meeting>(`/meetings/${meetingId}`),
        api.get<ParticipantRead[]>('/participants'),
        api.get<ParticipantRead[]>(`/meetings/${meetingId}/participants`),
        api.get<AgendumResponse[]>(`/agendas/?meeting_id=${meetingId}`),
        api.get<SignatureCardResponse[]>(`/meetings/${meetingId}/signature-cards`),
      ])
      setMeeting(mRes.data)
      setAllParticipants(pRes.data || [])
      setMeetingMembers(mbRes.data || [])
      setAgendas(agRes.data || [])
      setSignatureCards(sigRes.data || [])
    } catch (e) {
      console.error(e)
      toast.error('Could not load meeting data.')
    } finally {
      setLoading(false)
      setTimeout(setupObservers, 120)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meetingId])

  useEffect(() => {
    fetchAllData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meetingId])

  // ── navigation ────────────────────────────────────────────────────────────────
  const navTo = (id: string) => {
    setShowSections(false)
    setTimeout(() => {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 0)
  }

  // ── edit state ────────────────────────────────────────────────────────────────
  const [isEditingBasic, setIsEditingBasic] = useState(false)
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [isEditingDescription, setIsEditingDescription] = useState(false)
  const [isEditingConclusion, setIsEditingConclusion] = useState(false)

  const confirmSave = async (name: string): Promise<boolean> => {
    const r = await Swal.fire({
      title: `Save ${name}?`,
      text: 'This will permanently update the meeting record.',
      icon: 'info',
      iconColor: '#3b82f6',
      showCancelButton: true,
      confirmButtonText: 'Yes, Save',
      cancelButtonText: 'Cancel',
      reverseButtons: true,
      background: '#fff',
      buttonsStyling: false,
      customClass: {
        popup: 'rounded-[2rem] shadow-2xl p-8',
        title: 'text-2xl font-black text-slate-800 pt-4',
        htmlContainer: 'text-slate-500 font-medium pb-2',
        confirmButton: 'bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest mx-2 shadow-lg',
        cancelButton: 'bg-slate-100 hover:bg-slate-200 text-slate-600 px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest mx-2',
      },
    })
    return r.isConfirmed
  }

  const patch = async (payload: Partial<Meeting>) => api.patch(`/meetings/${meetingId}`, payload)

  const saveBasic = async () => {
    if (!meeting || !(await confirmSave('Basic Information'))) return
    try {
      await patch({ serial_num: meeting.serial_num, is_academic: meeting.is_academic, meeting_date: meeting.meeting_date, is_finished: meeting.is_finished })
      toast.success('Basic info saved.')
      setIsEditingBasic(false)
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed.')
    }
  }
  const cancelBasic = async () => {
    setIsEditingBasic(false)
    await fetchAllData()
  }

  const saveTitle = async () => {
    if (!meeting || !(await confirmSave('Title'))) return
    try {
      await patch({ title: meeting.title })
      toast.success('Title saved.')
      setIsEditingTitle(false)
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed.')
    }
  }
  const cancelTitle = async () => {
    setIsEditingTitle(false)
    await fetchAllData()
  }

  const saveDescription = async () => {
    if (!meeting || !(await confirmSave('Discussion & Minutes'))) return
    try {
      await patch({ description: meeting.description })
      toast.success('Minutes saved.')
      setIsEditingDescription(false)
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed.')
    }
  }
  const cancelDescription = async () => {
    setIsEditingDescription(false)
    await fetchAllData()
  }

  const saveConclusion = async () => {
    if (!meeting || !(await confirmSave('Final Conclusion'))) return
    try {
      await patch({ conclusion: meeting.conclusion })
      toast.success('Conclusion saved.')
      setIsEditingConclusion(false)
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed.')
    }
  }
  const cancelConclusion = async () => {
    setIsEditingConclusion(false)
    await fetchAllData()
  }

  // ── participants ───────────────────────────────────────────────────────────────
  const handlePresidentUpdate = (presidentId: string | null) => {
    setMeeting((m) => (m ? { ...m, president_card_id: presidentId } : m))
  }
  const handleMembersUpdate = (ids: string[]) => {
    setMeetingMembers(allParticipants.filter((p) => ids.includes(p.id)))
  }

  // ── agendas shared ─────────────────────────────────────────────────────────────
  const [creatingAgenda, setCreatingAgenda] = useState(false)
  const [creatingSupplAgenda, setCreatingSupplAgenda] = useState(false)

  const refreshAgendas = async () => {
    const res = await api.get<AgendumResponse[]>(`/agendas/?meeting_id=${meetingId}`)
    setAgendas(res.data || [])
    setTimeout(setupObservers, 80)
  }

  const handleAgendumUpdated = (updated: AgendumResponse) => {
    setAgendas((prev) => {
      const idx = prev.findIndex((a) => a.id === updated.id)
      if (idx !== -1) {
        const next = [...prev]
        next[idx] = updated
        return next
      }
      return [...prev, updated]
    })
  }
  const handleAgendumDeleted = (deletedId: string) => {
    setAgendas((prev) => prev.filter((a) => a.id !== deletedId))
    setTimeout(setupObservers, 80)
  }

  // Offset helpers — avoid serial collision on backend
  async function shiftToOffset(items: AgendumResponse[]) {
    await Promise.all(items.map((ag, i) => api.patch(`/agendas/${ag.id}`, { serial: OFFSET + i + 1 })))
  }
  async function assignFinalSerials(items: AgendumResponse[]) {
    for (let i = 0; i < items.length; i++) {
      await api.patch(`/agendas/${items[i].id}`, { serial: i + 1 })
    }
  }

  // ── REGULAR agendas ────────────────────────────────────────────────────────────
  async function addAgendum(insertIdx: number | null = null) {
    setCreatingAgenda(true)
    try {
      const sorted = regularAgendas
      let targetSerial: number
      if (insertIdx === null) {
        targetSerial = sorted.length + 1
      } else {
        targetSerial = insertIdx + 1
        const toShift = sorted.slice(insertIdx)
        await Promise.all(toShift.map((ag, i) => api.patch(`/agendas/${ag.id}`, { serial: OFFSET + insertIdx! + 2 + i })))
        for (let i = 0; i < toShift.length; i++) await api.patch(`/agendas/${toShift[i].id}`, { serial: insertIdx! + 2 + i })
      }
      await api.post('/agendas/', { meeting_id: meetingId, serial: targetSerial, is_supplementary: false })
      toast.success('Agenda item added')
      await refreshAgendas()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to add agenda')
    } finally {
      setCreatingAgenda(false)
    }
  }

  async function deleteAllAgendas() {
    const ok = await confirmDestructive(
      'Delete all regular agenda items?',
      'Every regular agenda, its resolution, and all attached files will be permanently deleted.',
      'Yes, Delete All',
    )
    if (!ok) return
    try {
      await Promise.all(regularAgendas.map((ag) => api.delete(`/agendas/${ag.id}`)))
      toast.success('All regular agendas deleted')
      setAgendas((prev) => prev.filter((a) => a.is_supplementary))
      setTimeout(setupObservers, 80)
    } catch {
      toast.error('Failed to delete agendas')
      await refreshAgendas()
    }
  }

  // Sidebar drag — regular
  const [dragFromIdxReg, setDragFromIdxReg] = useState<number | null>(null)
  const [sidebarOrderReg, setSidebarOrderReg] = useState<AgendumResponse[]>([])

  const onSidebarDragStartReg = (idx: number) => {
    setSidebarOrderReg([...regularAgendas])
    setDragFromIdxReg(idx)
  }
  const onSidebarDragOverReg = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (dragFromIdxReg === null || dragFromIdxReg === idx) return
    const arr = [...sidebarOrderReg]
    const [m] = arr.splice(dragFromIdxReg, 1)
    arr.splice(idx, 0, m)
    setSidebarOrderReg(arr)
    setDragFromIdxReg(idx)
  }
  const onSidebarDragEndReg = async () => {
    const newOrder = [...sidebarOrderReg]
    setDragFromIdxReg(null)
    setAgendas((prev) => [...newOrder.map((ag, i) => ({ ...ag, serial: i + 1 })), ...prev.filter((a) => a.is_supplementary)])
    try {
      await shiftToOffset(newOrder)
      await assignFinalSerials(newOrder)
      toast.success('Order saved')
      await refreshAgendas()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to save order')
      await refreshAgendas()
    }
  }

  // ── SUPPLEMENTARY agendas ──────────────────────────────────────────────────────
  async function addSupplAgendum(insertIdx: number | null = null) {
    setCreatingSupplAgenda(true)
    try {
      const sorted = supplAgendas
      let targetSerial: number
      if (insertIdx === null) {
        targetSerial = sorted.length + 1
      } else {
        targetSerial = insertIdx + 1
        const toShift = sorted.slice(insertIdx)
        await Promise.all(toShift.map((ag, i) => api.patch(`/agendas/${ag.id}`, { serial: OFFSET + insertIdx! + 2 + i })))
        for (let i = 0; i < toShift.length; i++) await api.patch(`/agendas/${toShift[i].id}`, { serial: insertIdx! + 2 + i })
      }
      await api.post('/agendas/', { meeting_id: meetingId, serial: targetSerial, is_supplementary: true })
      toast.success('Supplementary agenda item added')
      await refreshAgendas()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to add supplementary agenda')
    } finally {
      setCreatingSupplAgenda(false)
    }
  }

  async function deleteAllSupplAgendas() {
    const ok = await confirmDestructive(
      'Delete all supplementary agenda items?',
      'Every supplementary agenda, its resolution, and all attached files will be permanently deleted.',
      'Yes, Delete All',
    )
    if (!ok) return
    try {
      await Promise.all(supplAgendas.map((ag) => api.delete(`/agendas/${ag.id}`)))
      toast.success('All supplementary agendas deleted')
      setAgendas((prev) => prev.filter((a) => !a.is_supplementary))
      setTimeout(setupObservers, 80)
    } catch {
      toast.error('Failed to delete supplementary agendas')
      await refreshAgendas()
    }
  }

  // Sidebar drag — supplementary
  const [dragFromIdxSuppl, setDragFromIdxSuppl] = useState<number | null>(null)
  const [sidebarOrderSuppl, setSidebarOrderSuppl] = useState<AgendumResponse[]>([])

  const onSidebarDragStartSuppl = (idx: number) => {
    setSidebarOrderSuppl([...supplAgendas])
    setDragFromIdxSuppl(idx)
  }
  const onSidebarDragOverSuppl = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (dragFromIdxSuppl === null || dragFromIdxSuppl === idx) return
    const arr = [...sidebarOrderSuppl]
    const [m] = arr.splice(dragFromIdxSuppl, 1)
    arr.splice(idx, 0, m)
    setSidebarOrderSuppl(arr)
    setDragFromIdxSuppl(idx)
  }
  const onSidebarDragEndSuppl = async () => {
    const newOrder = [...sidebarOrderSuppl]
    setDragFromIdxSuppl(null)
    setAgendas((prev) => [...prev.filter((a) => !a.is_supplementary), ...newOrder.map((ag, i) => ({ ...ag, serial: i + 1 }))])
    try {
      await shiftToOffset(newOrder)
      await assignFinalSerials(newOrder)
      toast.success('Order saved')
      await refreshAgendas()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to save order')
      await refreshAgendas()
    }
  }

  const displayedRegular = dragFromIdxReg !== null ? sidebarOrderReg : regularAgendas
  const displayedSuppl = dragFromIdxSuppl !== null ? sidebarOrderSuppl : supplAgendas

  // ── materials: upload / download / delete ─────────────────────────────────────
  const [pdfUploading, setPdfUploading] = useState({ agenda: false, resolution: false })

  async function uploadPdf(event: React.ChangeEvent<HTMLInputElement>, type: 'agenda' | 'resolution') {
    const file = event.target.files?.[0]
    event.target.value = '' // reset so same file can be re-selected if needed
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are allowed')
      return
    }
    setPdfUploading((p) => ({ ...p, [type]: true }))
    try {
      const fd = new FormData()
      fd.append('file', file)
      await api.post(`/meetings/${meetingId}/files/${type}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      toast.success(`${type === 'agenda' ? 'Agenda' : 'Resolution'} PDF uploaded`)
      await fetchAllData()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Upload failed')
    } finally {
      setPdfUploading((p) => ({ ...p, [type]: false }))
    }
  }

  async function downloadPdf(type: 'agenda' | 'resolution') {
    try {
      const res = await api.get(`/meetings/${meetingId}/files/${type}`, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${type}_meeting_${meeting?.serial_num}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('Download started')
    } catch {
      toast.error('Download failed')
    }
  }

  async function deletePdf(type: 'agenda' | 'resolution') {
    const ok = await confirmDestructive(`Delete ${type === 'agenda' ? 'Agenda' : 'Resolution'} PDF?`, 'The uploaded file will be permanently removed.', 'Yes, Delete')
    if (!ok) return
    try {
      await api.delete(`/meetings/${meetingId}/files/${type}`)
      toast.success('PDF deleted')
      await fetchAllData()
    } catch {
      toast.error('Delete failed')
    }
  }

  return (
    <>
    <div className="screen-only h-screen flex flex-col bg-slate-50 overflow-hidden">
      {/* ══ HEADER ══════════════════════════════════════════════════════════ */}
      <header className="h-16 shrink-0 bg-white border-b border-slate-200 shadow-sm px-4 sm:px-6 flex items-center gap-3 z-50">
        <button onClick={() => setShowSections((v) => !v)} className="lg:hidden p-2.5 -ml-1 rounded-xl hover:bg-slate-100 text-slate-600 transition-colors shrink-0">
          {showSections ? <X size={22} /> : <Menu size={22} />}
        </button>
        {meeting && (
          <div className="flex items-center gap-3 sm:gap-4 min-w-0">
            <span
              className={['px-3 sm:px-4 py-1 text-xs font-black uppercase tracking-widest rounded-xl shrink-0', meeting.is_academic ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'].join(
                ' ',
              )}
            >
              {meeting.is_academic ? 'Academic' : 'Syndicate'}
            </span>
            <span className="h-4 w-px bg-slate-200 shrink-0 hidden sm:block" />
            <span className="font-black text-2xl tracking-tighter text-slate-800 shrink-0">#{meeting.serial_num}</span>
          </div>
        )}
        <div className="flex-1 min-w-0" />
        {meeting && (
          <button
            onClick={() => window.print()}
            className="shrink-0 flex items-center gap-2 px-3 sm:px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all text-slate-600"
            title="Print or save this meeting as a PDF"
          >
            <Printer size={16} />
            <span className="hidden sm:inline">Print / Save PDF</span>
          </button>
        )}
        {meeting && (
          <div className="shrink-0">
            <span
              className={['px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5', meeting.is_finished ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'].join(' ')}
            >
              {meeting.is_finished && <CheckCircle size={13} />}
              {meeting.is_finished ? 'Finished' : 'Ongoing'}
            </span>
          </div>
        )}
      </header>

      {/* ══ BODY ═══════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex overflow-hidden relative">
        {showSections && <div onClick={() => setShowSections(false)} className="lg:hidden absolute inset-0 bg-black/40 z-30" />}

        {/* ── SIDEBAR ──────────────────────────────────────────────────── */}
        <aside
          className={[
            'absolute lg:relative z-40 h-full bg-white border-r border-slate-200',
            'transition-transform duration-300 ease-in-out shadow-xl lg:shadow-none',
            showSections ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0 lg:w-64 xl:w-72',
          ].join(' ')}
        >
          <div className="p-4 h-full flex flex-col overflow-hidden">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 px-2">Sections</p>
            <nav className="flex-1 overflow-y-auto space-y-0.5 pr-1">
              {staticSections.map((s) => {
                const Icon = s.icon
                return (
                  <div key={s.id}>
                    <button
                      onClick={() => navTo(s.id)}
                      className={[
                        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all text-left',
                        activeSection === s.id ? (s.suppl ? 'bg-amber-50 text-amber-700' : 'bg-blue-50 text-blue-700') : 'text-slate-600 hover:bg-slate-50',
                      ].join(' ')}
                    >
                      <span
                        className={['w-1 h-4 rounded-full shrink-0 transition-all', activeSection === s.id ? (s.suppl ? 'bg-amber-400' : 'bg-blue-500') : 'bg-transparent'].join(' ')}
                      />
                      <Icon size={16} className={activeSection === s.id ? (s.suppl ? 'text-amber-500' : 'text-blue-600') : s.suppl ? 'text-amber-400' : 'text-slate-400'} />
                      <span className={s.suppl && activeSection !== s.id ? 'text-amber-600' : ''}>{s.label}</span>
                    </button>

                    {/* Sub-items: regular agendas */}
                    {s.id === 'agendas' && regularAgendas.length > 0 && (
                      <div className="ml-4 pl-3 border-l-2 border-slate-100 space-y-0.5 py-0.5">
                        {displayedRegular.map((ag, idx) => (
                          <div
                            key={ag.id}
                            className={[
                              'sidebar-agenda-item group flex items-center gap-1.5 rounded-lg transition-all',
                              activeSection === `agenda-${ag.id}` ? 'bg-blue-50' : 'hover:bg-slate-50',
                              dragFromIdxReg === idx ? 'sidebar-dragging' : '',
                            ].join(' ')}
                            draggable={canModify}
                            onDragStart={() => canModify && onSidebarDragStartReg(idx)}
                            onDragOver={(e) => canModify && onSidebarDragOverReg(e, idx)}
                            onDragEnd={() => canModify && onSidebarDragEndReg()}
                          >
                            {canModify && (
                              <span className="drag-grip-sidebar shrink-0 pl-1 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing">
                                <GripVertical size={12} className="text-slate-400" />
                              </span>
                            )}
                            <button onClick={() => navTo(`agenda-${ag.id}`)} className="flex-1 flex items-center gap-1.5 px-1.5 py-1.5 text-left min-w-0">
                              <span className={['shrink-0 font-bold text-[11px]', activeSection === `agenda-${ag.id}` ? 'text-blue-700' : 'text-slate-500'].join(' ')}>
                                Ag-{idx + 1}
                              </span>
                              {(!ag.body || ag.body === '{}') && <span className="truncate text-slate-400 italic text-[10px]">Empty</span>}
                            </button>
                          </div>
                        ))}
                        {dragFromIdxReg !== null && canModify && <div className="text-[10px] text-slate-400 italic px-2 py-1 text-center">Drop to reorder</div>}
                      </div>
                    )}

                    {/* Sub-items: supplementary agendas */}
                    {s.id === 'suppl-agendas' && supplAgendas.length > 0 && (
                      <div className="ml-4 pl-3 border-l-2 border-amber-200 space-y-0.5 py-0.5">
                        {displayedSuppl.map((ag, idx) => (
                          <div
                            key={ag.id}
                            className={[
                              'sidebar-agenda-item group flex items-center gap-1.5 rounded-lg transition-all',
                              activeSection === `agenda-${ag.id}` ? 'bg-amber-50' : 'hover:bg-slate-50',
                              dragFromIdxSuppl === idx ? 'sidebar-dragging-suppl' : '',
                            ].join(' ')}
                            draggable={canModify}
                            onDragStart={() => canModify && onSidebarDragStartSuppl(idx)}
                            onDragOver={(e) => canModify && onSidebarDragOverSuppl(e, idx)}
                            onDragEnd={() => canModify && onSidebarDragEndSuppl()}
                          >
                            {canModify && (
                              <span className="drag-grip-sidebar shrink-0 pl-1 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing">
                                <GripVertical size={12} className="text-amber-400" />
                              </span>
                            )}
                            <button onClick={() => navTo(`agenda-${ag.id}`)} className="flex-1 flex items-center gap-1.5 px-1.5 py-1.5 text-left min-w-0">
                              <span className={['shrink-0 font-bold text-[11px]', activeSection === `agenda-${ag.id}` ? 'text-amber-700' : 'text-amber-600'].join(' ')}>
                                SA-{idx + 1}
                              </span>
                              {(!ag.body || ag.body === '{}') && <span className="truncate text-slate-400 italic text-[10px]">Empty</span>}
                            </button>
                          </div>
                        ))}
                        {dragFromIdxSuppl !== null && canModify && <div className="text-[10px] text-amber-400 italic px-2 py-1 text-center">Drop to reorder</div>}
                      </div>
                    )}
                  </div>
                )
              })}
            </nav>
          </div>
        </aside>

        {/* ── MAIN ─────────────────────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-7 lg:p-10">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-96 gap-4">
              <div className="w-8 h-8 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
              <p className="text-sm font-medium text-slate-400">Loading meeting…</p>
            </div>
          ) : meeting ? (
            <div className="max-w-4xl mx-auto space-y-14 pb-28">
              {/* ── BASIC INFO ──────────────────────────────────────────── */}
              <section id="info" className="scroll-mt-20">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-px bg-slate-300" />
                    <span className="text-sm font-black uppercase tracking-widest text-slate-500">Basic Information</span>
                  </div>
                  {canModify && !isEditingBasic && (
                    <button onClick={() => setIsEditingBasic(true)} className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                      <Edit3 size={14} /> Edit
                    </button>
                  )}
                </div>
                {!isEditingBasic ? (
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      { icon: Hash, color: 'text-blue-500', label: 'Serial No.', value: `#${meeting.serial_num}`, big: true, status: false },
                      {
                        icon: Calendar,
                        color: 'text-violet-500',
                        label: 'Date',
                        value: meeting.meeting_date
                          ? new Date(meeting.meeting_date).toLocaleDateString('en-US', { weekday: 'short', month: 'long', day: 'numeric', year: 'numeric' })
                          : 'Not set',
                        big: false,
                        status: false,
                      },
                      { icon: CheckCircle, color: 'text-emerald-500', label: 'Status', value: meeting.is_finished ? 'Completed' : 'In Progress', big: false, status: true },
                    ].map((card) => {
                      const Icon = card.icon
                      return (
                        <div key={card.label} className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                          <div className="flex items-center gap-2 mb-2">
                            <Icon className={card.color} size={16} />
                            <p className="text-xs text-slate-500 font-medium">{card.label}</p>
                          </div>
                          <p
                            className={[
                              card.big ? 'text-3xl font-black text-slate-800' : 'text-sm font-semibold text-slate-700',
                              card.status ? (meeting.is_finished ? 'text-emerald-700 text-lg' : 'text-amber-700 text-lg') : '',
                            ].join(' ')}
                          >
                            {card.value}
                          </p>
                        </div>
                      )
                    })}
                    <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="w-4 h-4 rounded bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-500">T</span>
                        <p className="text-xs text-slate-500 font-medium">Type</p>
                      </div>
                      <p className="text-lg font-semibold text-slate-700">{meeting.is_academic ? 'Academic' : 'Syndicate'}</p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-7">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-slate-600 mb-2">Serial Number</label>
                        <input
                          type="number"
                          value={meeting.serial_num}
                          onChange={(e) => setMeeting((m) => (m ? { ...m, serial_num: Number(e.target.value) } : m))}
                          className="w-full px-4 py-3 text-xl font-semibold rounded-xl border border-slate-200 focus:border-blue-400 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-600 mb-2">Meeting Date</label>
                        <input
                          type="date"
                          value={meeting.meeting_date ? new Date(meeting.meeting_date).toISOString().split('T')[0] : ''}
                          onChange={(e) =>
                            setMeeting((m) => (m ? { ...m, meeting_date: e.target.value ? new Date(e.target.value + 'T00:00:00Z').toISOString() : null } : m))
                          }
                          className="w-full px-4 py-3 text-base rounded-xl border border-slate-200 focus:border-blue-400 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-600 mb-2">Status</label>
                        <label className="flex items-center gap-3 cursor-pointer mt-1">
                          <input
                            type="checkbox"
                            checked={meeting.is_finished}
                            onChange={(e) => setMeeting((m) => (m ? { ...m, is_finished: e.target.checked } : m))}
                            className="w-5 h-5 accent-blue-600"
                          />
                          <span className="text-base font-medium">Finished / Completed</span>
                        </label>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-600 mb-2">Council Type</label>
                        <select
                          value={String(meeting.is_academic)}
                          onChange={(e) => setMeeting((m) => (m ? { ...m, is_academic: e.target.value === 'true' } : m))}
                          className="w-full px-4 py-3 text-base font-medium rounded-xl border border-slate-200 focus:border-blue-400 outline-none"
                        >
                          <option value="true">Academic Council</option>
                          <option value="false">Syndicate</option>
                        </select>
                      </div>
                    </div>
                    <div className="flex gap-3 mt-8 justify-end">
                      <button onClick={cancelBasic} className="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">
                        Cancel
                      </button>
                      <button onClick={saveBasic} className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                        <Save size={14} /> Save
                      </button>
                    </div>
                  </div>
                )}
              </section>

              {/* ── MEETING TITLE ───────────────────────────────────────── */}
              <section id="title" className="scroll-mt-20">
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                    <div className="flex items-center gap-3">
                      <Layout className="text-violet-500" size={18} />
                      <h3 className="text-xl font-black text-slate-800">Meeting Title</h3>
                    </div>
                    {canModify && !isEditingTitle && (
                      <button onClick={() => setIsEditingTitle(true)} className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                        <Edit3 size={14} /> Edit
                      </button>
                    )}
                  </div>
                  {!isEditingTitle ? (
                    <div className="px-7 py-8">
                      <h2 className="text-xl font-semibold leading-relaxed text-slate-800">{meeting.title || 'No title set'}</h2>
                    </div>
                  ) : (
                    <div className="p-7">
                      <input
                        value={meeting.title}
                        onChange={(e) => setMeeting((m) => (m ? { ...m, title: e.target.value } : m))}
                        className="w-full bg-slate-50 border border-slate-200 focus:border-violet-300 rounded-xl px-5 py-4 text-xl font-semibold outline-none"
                        placeholder="Enter meeting title…"
                      />
                      <div className="flex gap-3 mt-6 justify-end">
                        <button onClick={cancelTitle} className="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">
                          Cancel
                        </button>
                        <button onClick={saveTitle} className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                          <Save size={14} /> Save Title
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </section>

              {/* ── DISCUSSION & MINUTES ────────────────────────────────── */}
              <section id="description" className="scroll-mt-20">
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                    <div className="flex items-center gap-3">
                      <FileText className="text-emerald-500" size={18} />
                      <h3 className="text-xl font-black text-slate-800">Discussion & Minutes</h3>
                    </div>
                    {canModify && !isEditingDescription && (
                      <button onClick={() => setIsEditingDescription(true)} className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                        <Edit3 size={14} /> Edit
                      </button>
                    )}
                  </div>
                  {!isEditingDescription ? (
                    <div className="px-7 py-8 prose prose-slate max-w-none">
                      {meeting.description ? (
                        <div className="text-[15px] leading-relaxed text-slate-700" dangerouslySetInnerHTML={{ __html: meeting.description }} />
                      ) : (
                        <p className="text-slate-400 italic">No discussion minutes recorded yet.</p>
                      )}
                    </div>
                  ) : (
                    <div className="p-7">
                      <textarea
                        value={meeting.description ?? ''}
                        onChange={(e) => setMeeting((m) => (m ? { ...m, description: e.target.value } : m))}
                        rows={12}
                        className="w-full resize-y bg-slate-50 border border-slate-200 focus:border-emerald-300 rounded-2xl px-5 py-4 text-[15px] leading-relaxed outline-none font-medium"
                        placeholder="Write detailed minutes here…"
                      />
                      <div className="flex gap-3 mt-6 justify-end">
                        <button onClick={cancelDescription} className="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">
                          Cancel
                        </button>
                        <button onClick={saveDescription} className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                          <Save size={14} /> Save Minutes
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </section>

              {/* ── PARTICIPANTS ────────────────────────────────────────── */}
              <section id="participants" className="scroll-mt-20">
                {canModify ? (
                  <ParticipantsSection
                    meetingId={meetingId!}
                    currentPresidentId={meeting.president_card_id}
                    currentMembers={meetingMembers}
                    allParticipants={allParticipants}
                    onPresidentUpdated={handlePresidentUpdate}
                    onMembersUpdated={handleMembersUpdate}
                  />
                ) : (
                  <div className="space-y-8">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-px bg-slate-300" />
                      <span className="text-sm font-black uppercase tracking-widest text-slate-500">Participants</span>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-widest font-black text-slate-400 mb-3">President</p>
                      {currentPresident ? (
                        <div className="max-w-sm">
                          <ParticipantCard participant={currentPresident} />
                        </div>
                      ) : (
                        <div className="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-10 text-center text-sm text-slate-400">No president assigned</div>
                      )}
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-widest font-black text-slate-400 mb-3">Members ({meetingMembers.length})</p>
                      {meetingMembers.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                          {meetingMembers.map((m) => (
                            <ParticipantCard key={m.id} participant={m} />
                          ))}
                        </div>
                      ) : (
                        <div className="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-12 text-center">
                          <Users className="mx-auto mb-2 text-slate-300" size={32} />
                          <p className="text-slate-400 text-sm font-medium">No members added yet</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </section>

              {/* ── REGULAR AGENDAS ─────────────────────────────────────── */}
              <section id="agendas" className="scroll-mt-20">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-px bg-slate-300" />
                    <span className="text-sm font-black uppercase tracking-widest text-slate-500">Agendas</span>
                    <span className="text-xs font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">{regularAgendas.length}</span>
                  </div>
                  {canModify && (
                    <div className="flex items-center gap-2 flex-wrap justify-end">
                      {regularAgendas.length > 0 && (
                        <button onClick={deleteAllAgendas} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all">
                          <Trash2 size={11} /> Delete All
                        </button>
                      )}
                      <button onClick={() => addAgendum(null)} disabled={creatingAgenda} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50">
                        <Plus size={11} /> Add Agenda
                      </button>
                    </div>
                  )}
                </div>

                {canModify && regularAgendas.length > 1 && (
                  <div className="flex items-center gap-2 mb-4 px-3 py-2 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-600 font-medium">
                    <GripVertical size={13} /> Drag items in the sidebar to reorder agendas
                  </div>
                )}

                {regularAgendas.length === 0 ? (
                  <div className="ag-empty">
                    <div className="ag-empty-icon">
                      <ListOrdered size={30} className="text-slate-300" />
                    </div>
                    <p className="ag-empty-title">No agenda items yet</p>
                    <p className="ag-empty-sub">Use the button above or the strip below to add an agenda item</p>
                    {canModify && (
                      <div className="mt-4">
                        <InsertStrip disabled={creatingAgenda} onAddRegular={() => addAgendum(0)} />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="ag-list">
                    {canModify && <InsertStrip disabled={creatingAgenda} onAddRegular={() => addAgendum(0)} />}
                    {regularAgendas.map((ag, idx) => (
                      <div key={ag.id}>
                        <div id={`agenda-${ag.id}`} className="scroll-mt-20 ag-card-wrap">
                          <AgendaBox agendum={{ ...ag, serial: idx + 1 }} meetingId={meetingId!} canModify={canModify} onUpdated={handleAgendumUpdated} onDeleted={handleAgendumDeleted} />
                        </div>
                        {canModify && <InsertStrip disabled={creatingAgenda} onAddRegular={() => addAgendum(idx + 1)} />}
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {/* ── SUPPLEMENTARY AGENDAS ──────────────────────────────── */}
              <section id="suppl-agendas" className="scroll-mt-20">
                <div className="rounded-2xl border border-amber-200 bg-amber-50/50 overflow-hidden">
                  <div className="flex items-center justify-between px-6 py-5 border-b border-amber-100 bg-amber-50">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-px bg-amber-300" />
                      <span className="text-sm font-black uppercase tracking-widest text-amber-700">Supplementary Agendas</span>
                      <span className="text-xs font-bold text-amber-700 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full">{supplAgendas.length}</span>
                    </div>
                    {canModify && (
                      <div className="flex items-center gap-2 flex-wrap justify-end">
                        {supplAgendas.length > 0 && (
                          <button onClick={deleteAllSupplAgendas} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all">
                            <Trash2 size={11} /> Delete All
                          </button>
                        )}
                        <button
                          onClick={() => addSupplAgendum(null)}
                          disabled={creatingSupplAgenda}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-all disabled:opacity-50"
                        >
                          <Plus size={11} /> Add Supplementary
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="p-6">
                    {canModify && supplAgendas.length > 1 && (
                      <div className="flex items-center gap-2 mb-4 px-3 py-2 bg-amber-100 border border-amber-200 rounded-xl text-xs text-amber-700 font-medium">
                        <GripVertical size={13} /> Drag items in the sidebar to reorder supplementary agendas
                      </div>
                    )}

                    {supplAgendas.length === 0 ? (
                      <div className="ag-empty ag-empty--suppl">
                        <div className="ag-empty-icon ag-empty-icon--suppl">
                          <ListOrdered size={30} className="text-amber-300" />
                        </div>
                        <p className="ag-empty-title">No supplementary agenda items yet</p>
                        <p className="ag-empty-sub">Items added mid-meeting go here</p>
                        {canModify && (
                          <div className="mt-4">
                            <InsertStrip disabled={creatingSupplAgenda} onAddRegular={() => addSupplAgendum(0)} />
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="ag-list">
                        {canModify && <InsertStrip disabled={creatingSupplAgenda} onAddRegular={() => addSupplAgendum(0)} />}
                        {supplAgendas.map((ag, idx) => (
                          <div key={ag.id}>
                            <div id={`agenda-${ag.id}`} className="scroll-mt-20 ag-card-wrap">
                              <AgendaBox agendum={{ ...ag, serial: idx + 1 }} meetingId={meetingId!} canModify={canModify} onUpdated={handleAgendumUpdated} onDeleted={handleAgendumDeleted} />
                            </div>
                            {canModify && <InsertStrip disabled={creatingSupplAgenda} onAddRegular={() => addSupplAgendum(idx + 1)} />}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </section>

              {/* ── MATERIALS ──────────────────────────────────────────── */}
              <section id="materials" className="scroll-mt-20">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-px bg-slate-300" />
                  <span className="text-sm font-black uppercase tracking-widest text-slate-500">Materials</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {/* ══ Agenda PDF ══ */}
                  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
                    <div className="px-5 pt-5 pb-4 border-b border-slate-100 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
                        <FileDown className="text-blue-600" size={18} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-black text-slate-800">Agenda PDF</p>
                        <p className="text-xs text-slate-400">Full meeting agenda document</p>
                      </div>
                    </div>

                    <div className="px-5 py-4 flex-1 flex flex-col gap-3">
                      {meeting.agenda_pdf ? (
                        <>
                          <button
                            onClick={() => downloadPdf('agenda')}
                            className="flex items-center gap-3 px-4 py-3 bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 rounded-xl transition-all group w-full text-left"
                          >
                            <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                              <FileIcon size={15} className="text-red-500" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-slate-700 group-hover:text-blue-700 truncate leading-tight">agenda_meeting_{meeting.serial_num}.pdf</p>
                              <p className="text-xs text-slate-400 mt-0.5">Click to download</p>
                            </div>
                            <Download size={14} className="text-slate-400 group-hover:text-blue-500 shrink-0" />
                          </button>

                          {canModify && (
                            <button
                              onClick={() => deletePdf('agenda')}
                              className="flex items-center justify-center gap-1.5 py-2 text-xs font-semibold text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition-all w-full"
                            >
                              <Trash2 size={12} /> Remove PDF
                            </button>
                          )}
                        </>
                      ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-3 py-4">
                          <span className="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1 rounded-full">No file uploaded yet</span>
                          {canModify && (
                            <label
                              className={[
                                'flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-semibold',
                                'bg-blue-600 hover:bg-blue-700 text-white rounded-xl cursor-pointer transition-all w-full',
                                pdfUploading.agenda ? 'opacity-60 pointer-events-none' : '',
                              ].join(' ')}
                            >
                              <input type="file" accept=".pdf,application/pdf" onChange={(e) => uploadPdf(e, 'agenda')} className="hidden" />
                              <UploadCloud size={15} />
                              {pdfUploading.agenda ? 'Uploading…' : 'Upload Agenda PDF'}
                            </label>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* ══ Resolution PDF ══ */}
                  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
                    <div className="px-5 pt-5 pb-4 border-b border-slate-100 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
                        <FileDown className="text-emerald-600" size={18} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-black text-slate-800">Resolution PDF</p>
                        <p className="text-xs text-slate-400">All decisions and resolutions</p>
                      </div>
                    </div>

                    <div className="px-5 py-4 flex-1 flex flex-col gap-3">
                      {meeting.resolution_pdf ? (
                        <>
                          <button
                            onClick={() => downloadPdf('resolution')}
                            className="flex items-center gap-3 px-4 py-3 bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-xl transition-all group w-full text-left"
                          >
                            <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                              <FileIcon size={15} className="text-red-500" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-slate-700 group-hover:text-emerald-700 truncate leading-tight">resolution_meeting_{meeting.serial_num}.pdf</p>
                              <p className="text-xs text-slate-400 mt-0.5">Click to download</p>
                            </div>
                            <Download size={14} className="text-slate-400 group-hover:text-emerald-500 shrink-0" />
                          </button>

                          {canModify && (
                            <button
                              onClick={() => deletePdf('resolution')}
                              className="flex items-center justify-center gap-1.5 py-2 text-xs font-semibold text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition-all w-full"
                            >
                              <Trash2 size={12} /> Remove PDF
                            </button>
                          )}
                        </>
                      ) : (
                        <div className="flex-1 flex flex-col items-center justify-center gap-3 py-4">
                          <span className="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1 rounded-full">No file uploaded yet</span>
                          {canModify && (
                            <label
                              className={[
                                'flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-semibold',
                                'bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl cursor-pointer transition-all w-full',
                                pdfUploading.resolution ? 'opacity-60 pointer-events-none' : '',
                              ].join(' ')}
                            >
                              <input type="file" accept=".pdf,application/pdf" onChange={(e) => uploadPdf(e, 'resolution')} className="hidden" />
                              <UploadCloud size={15} />
                              {pdfUploading.resolution ? 'Uploading…' : 'Upload Resolution PDF'}
                            </label>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </section>

              {/* ── FINAL CONCLUSION ───────────────────────────────────── */}
              <section id="conclusion" className="scroll-mt-20">
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="text-rose-500" size={18} />
                      <h3 className="text-xl font-black text-slate-800">Final Conclusion</h3>
                    </div>
                    {canModify && !isEditingConclusion && (
                      <button onClick={() => setIsEditingConclusion(true)} className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                        <Edit3 size={14} /> Edit
                      </button>
                    )}
                  </div>
                  {!isEditingConclusion ? (
                    <div className="px-7 py-8 prose prose-slate max-w-none">
                      {meeting.conclusion ? (
                        <div className="text-[15px] leading-relaxed text-slate-700" dangerouslySetInnerHTML={{ __html: meeting.conclusion }} />
                      ) : (
                        <p className="text-slate-400 italic">No conclusion recorded yet.</p>
                      )}
                    </div>
                  ) : (
                    <div className="p-7">
                      <textarea
                        value={meeting.conclusion ?? ''}
                        onChange={(e) => setMeeting((m) => (m ? { ...m, conclusion: e.target.value } : m))}
                        rows={9}
                        className="w-full resize-y bg-slate-50 border border-slate-200 focus:border-rose-300 rounded-2xl px-5 py-4 text-[15px] leading-relaxed outline-none font-medium"
                        placeholder="Write final decisions and closing remarks…"
                      />
                      <div className="flex gap-3 mt-6 justify-end">
                        <button onClick={cancelConclusion} className="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">
                          Cancel
                        </button>
                        <button onClick={saveConclusion} className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                          <Save size={14} /> Save Conclusion
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </section>

              {/* ── SIGNATURE CARDS ────────────────────────────────────── */}
              <section id="signatures" className="scroll-mt-20">
                <SignatureCardsSection meetingId={meetingId!} canModify={canModify} />
              </section>
            </div>
          ) : (
            <div className="flex items-center justify-center h-96 text-slate-400">Meeting not found or has been deleted.</div>
          )}
        </main>
      </div>
    </div>

    {meeting && (
      <PrintableMeeting
        meeting={meeting}
        president={currentPresident}
        members={meetingMembers}
        regularAgendas={regularAgendas}
        supplAgendas={supplAgendas}
        signatureCards={signatureCards}
      />
    )}
    </>
  )
}
