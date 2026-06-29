import { useEffect, useRef, useState } from 'react'
import { toast } from 'react-toastify'
import type { JSONContent } from '@tiptap/react'
import api from '../utils/api'
import { confirmDestructive } from '../utils/alerts'
import RichTextEditor from './RichTextEditor'
import type { AgendumResponse, AnnexureResponse } from '../types/api'
import './AgendaBox.css'

/**
 * One agenda card.
 * Changes from the original design (carried over from the Vue version):
 *   - Drag grip removed — reordering is done exclusively from the sidebar
 *   - Resolution edit/save/cancel toolbar is right-aligned
 */
interface AgendaBoxProps {
  agendum: AgendumResponse
  meetingId: string
  canModify?: boolean
  onUpdated: (agendum: AgendumResponse) => void
  onDeleted: (agendumId: string) => void
}

function parseBody(raw: string | null | undefined): JSONContent {
  if (!raw) return {}
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw
  } catch {
    return {}
  }
}

const MEDIA_ROOT = import.meta.env.VITE_MEDIA_URL || ''
const fileUrl = (path: string) => `${MEDIA_ROOT}/${path.replace(/^\/+/, '')}`

function fmtBytes(b: number): string {
  if (!b) return ''
  if (b < 1024) return `${b} B`
  if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`
  return `${(b / 1048576).toFixed(1)} MB`
}

function relTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export default function AgendaBox({ agendum, meetingId, canModify = false, onUpdated, onDeleted }: AgendaBoxProps) {
  // ── local body copies ────────────────────────────────────────────────────────
  const [localBody, setLocalBody] = useState<JSONContent>(() => parseBody(agendum.body))
  const [localResBody, setLocalResBody] = useState<JSONContent>(() => parseBody(agendum.resolution?.body))

  useEffect(() => setLocalBody(parseBody(agendum.body)), [agendum.body])
  useEffect(() => setLocalResBody(parseBody(agendum.resolution?.body)), [agendum.resolution?.body])

  // ── edit state ────────────────────────────────────────────────────────────────
  const [editingBody, setEditingBody] = useState(false)
  const [editingRes, setEditingRes] = useState(false)
  const [savingBody, setSavingBody] = useState(false)
  const [savingRes, setSavingRes] = useState(false)
  const [creatingRes, setCreatingRes] = useState(false)
  const [showResolution, setShowResolution] = useState(false)

  async function refetch() {
    const res = await api.get<AgendumResponse[]>(`/agendas/?meeting_id=${meetingId}`)
    const updated = (res.data || []).find((a) => a.id === agendum.id)
    if (updated) onUpdated(updated)
  }

  // ── Agenda body save / delete ─────────────────────────────────────────────────
  async function saveBody() {
    setSavingBody(true)
    try {
      await api.patch(`/agendas/${agendum.id}`, { body: JSON.stringify(localBody) })
      toast.success('Agenda saved')
      setEditingBody(false)
      await refetch()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Save failed')
    } finally {
      setSavingBody(false)
    }
  }

  async function deleteAgendum() {
    const ok = await confirmDestructive(
      `Delete Ag-${agendum.serial}?`,
      'The agenda, resolution, and all attached files will be permanently deleted.',
      'Yes, Delete',
    )
    if (!ok) return
    try {
      await api.delete(`/agendas/${agendum.id}`)
      toast.success('Agenda deleted')
      onDeleted(agendum.id)
    } catch {
      toast.error('Delete failed')
    }
  }

  // ── Annexure upload / remove / drag-reorder ───────────────────────────────────
  const [annDragIdx, setAnnDragIdx] = useState<number | null>(null)
  const [annOrder, setAnnOrder] = useState<AnnexureResponse[]>(() => [...(agendum.annexures || [])])
  const annDragFrom = useRef<number | null>(null)
  useEffect(() => setAnnOrder([...(agendum.annexures || [])]), [agendum.annexures])

  async function uploadAnnexure(evt: React.ChangeEvent<HTMLInputElement>) {
    const file = evt.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      const up = await api.post('/files/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      await api.post(`/agendas/${agendum.id}/files`, {
        file_id: up.data.id,
        order: (agendum.annexures?.length ?? 0) + 1,
      })
      toast.success('File attached')
      await refetch()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Upload failed')
    }
    evt.target.value = ''
  }

  async function removeAnnexure(annexureId: string) {
    const ok = await confirmDestructive('Remove file?', 'This file will be permanently deleted.', 'Remove')
    if (!ok) return
    try {
      await api.delete(`/agendas/${agendum.id}/files/${annexureId}`)
      toast.success('Removed')
      await refetch()
    } catch {
      toast.error('Failed')
    }
  }

  // ── Resolution attachments ────────────────────────────────────────────────────
  const [resDragIdx, setResDragIdx] = useState<number | null>(null)
  const [resOrder, setResOrder] = useState<AnnexureResponse[]>(() => [...(agendum.resolution?.attachments || [])])
  const resDragFrom = useRef<number | null>(null)
  useEffect(() => setResOrder([...(agendum.resolution?.attachments || [])]), [agendum.resolution?.attachments])

  function fileDragStart(type: 'ann' | 'res', idx: number) {
    if (type === 'ann') annDragFrom.current = idx
    else resDragFrom.current = idx
  }

  function fileDragOver(type: 'ann' | 'res', idx: number) {
    if (type === 'ann') {
      if (annDragFrom.current === null || annDragFrom.current === idx) return
      const arr = [...annOrder]
      const [m] = arr.splice(annDragFrom.current, 1)
      arr.splice(idx, 0, m)
      setAnnOrder(arr)
      setAnnDragIdx(idx)
      annDragFrom.current = idx
    } else {
      if (resDragFrom.current === null || resDragFrom.current === idx) return
      const arr = [...resOrder]
      const [m] = arr.splice(resDragFrom.current, 1)
      arr.splice(idx, 0, m)
      setResOrder(arr)
      setResDragIdx(idx)
      resDragFrom.current = idx
    }
  }

  async function fileDragEnd(type: 'ann' | 'res') {
    if (type === 'ann') {
      setAnnDragIdx(null)
      annDragFrom.current = null
      try {
        await Promise.all(annOrder.map((a, i) => api.patch(`/agendas/${agendum.id}/files/${a.id}`, { order: i + 1 })))
        await refetch()
      } catch {
        toast.error('Reorder failed')
      }
    } else {
      setResDragIdx(null)
      resDragFrom.current = null
      try {
        await Promise.all(
          resOrder.map((a, i) => api.patch(`/resolutions/${agendum.resolution!.id}/files/${a.id}`, { order: i + 1 })),
        )
        await refetch()
      } catch {
        toast.error('Reorder failed')
      }
    }
  }

  // ── Resolution create / save / delete ─────────────────────────────────────────
  async function createResolution() {
    setCreatingRes(true)
    try {
      await api.post('/resolutions/', { agendum_id: agendum.id })
      toast.success('Resolution created')
      setShowResolution(true)
      await refetch()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed')
    } finally {
      setCreatingRes(false)
    }
  }

  async function saveResolution() {
    setSavingRes(true)
    try {
      await api.patch(`/resolutions/${agendum.resolution!.id}`, { body: JSON.stringify(localResBody) })
      toast.success('Resolution saved')
      setEditingRes(false)
      await refetch()
    } catch {
      toast.error('Save failed')
    } finally {
      setSavingRes(false)
    }
  }

  async function deleteResolution() {
    const ok = await confirmDestructive(
      'Delete resolution?',
      'The resolution and its attachments will be permanently deleted.',
      'Delete',
    )
    if (!ok) return
    try {
      await api.delete(`/resolutions/${agendum.resolution!.id}`)
      toast.success('Resolution deleted')
      await refetch()
    } catch {
      toast.error('Failed')
    }
  }

  async function uploadResAttachment(evt: React.ChangeEvent<HTMLInputElement>) {
    const file = evt.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      const up = await api.post('/files/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      await api.post(`/resolutions/${agendum.resolution!.id}/files`, {
        file_id: up.data.id,
        order: (agendum.resolution?.attachments?.length ?? 0) + 1,
      })
      toast.success('Attachment added')
      await refetch()
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Upload failed')
    }
    evt.target.value = ''
  }

  async function removeResAttachment(attachmentId: string) {
    const ok = await confirmDestructive('Remove attachment?', 'This file will be permanently deleted.', 'Remove')
    if (!ok) return
    try {
      await api.delete(`/resolutions/${agendum.resolution!.id}/files/${attachmentId}`)
      toast.success('Removed')
      await refetch()
    } catch {
      toast.error('Failed')
    }
  }

  return (
    <div className={['abox', agendum.is_supplementary ? 'abox--suppl' : ''].join(' ')}>
      {/* ══ HEADER ════════════════════════════════════════════════════════ */}
      <div className="abox-header">
        <div className="abox-header-left">
          <span className="serial-badge">Ag-{agendum.serial}</span>
          {agendum.is_supplementary && <span className="suppl-tag">Supplementary</span>}
          {agendum.updated_at && <span className="meta-hint">edited {relTime(agendum.updated_at)}</span>}
        </div>

        {canModify && (
          <div className="abox-header-right">
            {/* Edit / Cancel toggle */}
            <button className="hbtn" onClick={() => setEditingBody((v) => !v)} title={editingBody ? 'Cancel editing' : 'Edit agenda'}>
              {!editingBody ? (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              )}
              <span className="hbtn-label">{editingBody ? 'Cancel' : 'Edit'}</span>
            </button>

            {/* Save (only when editing) */}
            {editingBody && (
              <button className="hbtn hbtn--primary" onClick={saveBody} disabled={savingBody}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                  <polyline points="17 21 17 13 7 13 7 21" />
                  <polyline points="7 3 7 8 15 8" />
                </svg>
                <span className="hbtn-label">{savingBody ? 'Saving…' : 'Save'}</span>
              </button>
            )}

            {/* Delete */}
            <button className="hbtn hbtn--danger" onClick={deleteAgendum} title="Delete agenda">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6l-1 14H6L5 6" />
                <path d="M10 11v6" />
                <path d="M14 11v6" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* ══ BODY EDITOR ════════════════════════════════════════════════════ */}
      <div className="abox-body">
        <RichTextEditor value={localBody} editable={editingBody && canModify} minHeight="140px" onChange={setLocalBody} />
      </div>

      {/* ══ ANNEXURES ══════════════════════════════════════════════════════ */}
      <div className="abox-section">
        <div className="section-header">
          <span className="section-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
            Annexures
            <span className="count-pill">{agendum.annexures?.length ?? 0}</span>
          </span>
          {canModify && (
            <label className="upload-label" title="Attach file">
              <input type="file" className="sr-only" onChange={uploadAnnexure} />
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              Attach
            </label>
          )}
        </div>

        {!agendum.annexures?.length ? (
          <div className="empty-files">No annexures attached</div>
        ) : (
          <div className="file-list">
            {annOrder.map((ann, idx) => (
              <div
                key={ann.id}
                className={['file-row', annDragIdx === idx ? 'is-dragging' : ''].join(' ')}
                draggable
                onDragStart={() => fileDragStart('ann', idx)}
                onDragOver={(e) => {
                  e.preventDefault()
                  fileDragOver('ann', idx)
                }}
                onDragEnd={() => fileDragEnd('ann')}
              >
                <svg className="drag-pip" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <circle cx="9" cy="7" r="1" fill="currentColor" />
                  <circle cx="9" cy="12" r="1" fill="currentColor" />
                  <circle cx="9" cy="17" r="1" fill="currentColor" />
                  <circle cx="15" cy="7" r="1" fill="currentColor" />
                  <circle cx="15" cy="12" r="1" fill="currentColor" />
                  <circle cx="15" cy="17" r="1" fill="currentColor" />
                </svg>
                <span className="file-order">{idx + 1}</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth={2}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <a href={fileUrl(ann.path)} target="_blank" rel="noreferrer" className="file-name">
                  {ann.original_filename}
                </a>
                <span className="file-size">{fmtBytes(ann.size_bytes)}</span>
                {canModify && (
                  <button className="file-remove" onClick={() => removeAnnexure(ann.id)} title="Remove">
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ══ RESOLUTION ═════════════════════════════════════════════════════ */}
      <div className="abox-section abox-resolution">
        {/* Resolution toggle header */}
        <button className="resolution-toggle" onClick={() => setShowResolution((v) => !v)}>
          <span className="section-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <polyline points="9 11 12 14 22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
            Resolution
            <span className={['res-dot', agendum.resolution ? 'res-dot--yes' : 'res-dot--no'].join(' ')} />
          </span>
          <div className="resolution-toggle-right">
            {canModify && !agendum.resolution && (
              <button
                className="hbtn hbtn--sm"
                onClick={(e) => {
                  e.stopPropagation()
                  createResolution()
                }}
                disabled={creatingRes}
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add
              </button>
            )}
            {canModify && agendum.resolution && (
              <button
                className="hbtn hbtn--danger hbtn--sm"
                onClick={(e) => {
                  e.stopPropagation()
                  deleteResolution()
                }}
                title="Delete resolution"
              >
                ✕
              </button>
            )}
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              className={['chevron', showResolution ? 'chevron--open' : ''].join(' ')}
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        {/* Resolution body (collapsible) */}
        {showResolution && agendum.resolution && (
          <div className="resolution-body">
            {canModify && (
              <div className="res-toolbar">
                <button className="hbtn" onClick={() => setEditingRes((v) => !v)}>
                  {!editingRes ? (
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                  ) : (
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  )}
                  {editingRes ? 'Cancel' : 'Edit'}
                </button>
                {editingRes && (
                  <button className="hbtn hbtn--primary" onClick={saveResolution} disabled={savingRes}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                      <polyline points="17 21 17 13 7 13 7 21" />
                      <polyline points="7 3 7 8 15 8" />
                    </svg>
                    {savingRes ? 'Saving…' : 'Save'}
                  </button>
                )}
              </div>
            )}

            <RichTextEditor value={localResBody} editable={editingRes && canModify} minHeight="110px" onChange={setLocalResBody} />

            {/* Resolution attachments */}
            <div className="section-header mt-3">
              <span className="section-title" style={{ fontSize: '11px' }}>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                </svg>
                Attachments
                <span className="count-pill">{agendum.resolution.attachments?.length ?? 0}</span>
              </span>
              {canModify && (
                <label className="upload-label upload-label--sm" title="Attach file">
                  <input type="file" className="sr-only" onChange={uploadResAttachment} />
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  Attach
                </label>
              )}
            </div>

            {!agendum.resolution.attachments?.length ? (
              <div className="empty-files" style={{ fontSize: '11px' }}>
                No attachments
              </div>
            ) : (
              <div className="file-list">
                {resOrder.map((att, idx) => (
                  <div
                    key={att.id}
                    className={['file-row', resDragIdx === idx ? 'is-dragging' : ''].join(' ')}
                    draggable
                    onDragStart={() => fileDragStart('res', idx)}
                    onDragOver={(e) => {
                      e.preventDefault()
                      fileDragOver('res', idx)
                    }}
                    onDragEnd={() => fileDragEnd('res')}
                  >
                    <svg className="drag-pip" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <circle cx="9" cy="7" r="1" fill="currentColor" />
                      <circle cx="9" cy="12" r="1" fill="currentColor" />
                      <circle cx="9" cy="17" r="1" fill="currentColor" />
                      <circle cx="15" cy="7" r="1" fill="currentColor" />
                      <circle cx="15" cy="12" r="1" fill="currentColor" />
                      <circle cx="15" cy="17" r="1" fill="currentColor" />
                    </svg>
                    <span className="file-order">{idx + 1}</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth={2}>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    <a href={fileUrl(att.path)} target="_blank" rel="noreferrer" className="file-name">
                      {att.original_filename}
                    </a>
                    <span className="file-size">{fmtBytes(att.size_bytes)}</span>
                    {canModify && (
                      <button className="file-remove" onClick={() => removeResAttachment(att.id)}>
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {showResolution && !agendum.resolution && <div className="empty-files">No resolution recorded</div>}
      </div>
    </div>
  )
}
