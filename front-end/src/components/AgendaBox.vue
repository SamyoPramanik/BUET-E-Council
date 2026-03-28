<!-- components/AgendaBox.vue -->
<!--
  One agenda card.
  Props : agendum (AgendumResponse), meetingId, canModify
  Emits : updated(agendum), deleted(agendumId)

  Changes:
    • Drag grip removed — reordering is done exclusively from the sidebar
    • Resolution edit/save/cancel toolbar moved to the right (flex justify-end)
-->
<template>
  <div class="abox" :class="{ 'abox--suppl': agendum.is_supplementary }">

    <!-- ══ HEADER ════════════════════════════════════════════════════════ -->
    <div class="abox-header">
      <div class="abox-header-left">
        <span class="serial-badge">Ag-{{ agendum.serial }}</span>
        <span v-if="agendum.is_supplementary" class="suppl-tag">Supplementary</span>
        <span v-if="agendum.updated_at" class="meta-hint">
          edited {{ relTime(agendum.updated_at) }}
        </span>
      </div>

      <div v-if="canModify" class="abox-header-right">
        <!-- Edit / Cancel toggle -->
        <button class="hbtn" @click="editingBody = !editingBody"
          :title="editingBody ? 'Cancel editing' : 'Edit agenda'">
          <svg v-if="!editingBody" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          <span class="hbtn-label">{{ editingBody ? 'Cancel' : 'Edit' }}</span>
        </button>

        <!-- Save (only when editing) -->
        <button v-if="editingBody" class="hbtn hbtn--primary" @click="saveBody" :disabled="savingBody">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <span class="hbtn-label">{{ savingBody ? 'Saving…' : 'Save' }}</span>
        </button>

        <!-- Delete -->
        <button class="hbtn hbtn--danger" @click="deleteAgendum" title="Delete agenda">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14H6L5 6"/>
            <path d="M10 11v6"/><path d="M14 11v6"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ══ BODY EDITOR ════════════════════════════════════════════════════ -->
    <div class="abox-body">
      <RichTextEditor
        v-model="localBody"
        :editable="editingBody && canModify"
        minHeight="140px"
      />
    </div>

    <!-- ══ ANNEXURES ══════════════════════════════════════════════════════ -->
    <div class="abox-section">
      <div class="section-header">
        <span class="section-title">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
          </svg>
          Annexures
          <span class="count-pill">{{ agendum.annexures?.length ?? 0 }}</span>
        </span>
        <label v-if="canModify" class="upload-label" title="Attach file">
          <input type="file" class="sr-only" @change="uploadAnnexure" />
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Attach
        </label>
      </div>

      <div v-if="!agendum.annexures?.length" class="empty-files">
        No annexures attached
      </div>

      <!-- Drag-to-reorder file list -->
      <div v-else class="file-list">
        <div
          v-for="(ann, idx) in agendum.annexures"
          :key="ann.id"
          class="file-row"
          draggable="true"
          @dragstart="fileDragStart('ann', idx)"
          @dragover.prevent="fileDragOver('ann', idx)"
          @dragend="fileDragEnd('ann')"
          :class="{ 'is-dragging': annDragIdx === idx }"
        >
          <svg class="drag-pip" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="9" cy="7" r="1" fill="currentColor"/><circle cx="9" cy="12" r="1" fill="currentColor"/>
            <circle cx="9" cy="17" r="1" fill="currentColor"/><circle cx="15" cy="7" r="1" fill="currentColor"/>
            <circle cx="15" cy="12" r="1" fill="currentColor"/><circle cx="15" cy="17" r="1" fill="currentColor"/>
          </svg>
          <span class="file-order">{{ idx + 1 }}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <a :href="fileUrl(ann.path)" target="_blank" class="file-name">{{ ann.original_filename }}</a>
          <span class="file-size">{{ fmtBytes(ann.size_bytes) }}</span>
          <button v-if="canModify" class="file-remove" @click="removeAnnexure(ann.id)" title="Remove">✕</button>
        </div>
      </div>
    </div>

    <!-- ══ RESOLUTION ═════════════════════════════════════════════════════ -->
    <div class="abox-section abox-resolution">
      <!-- Resolution toggle header -->
      <button class="resolution-toggle" @click="showResolution = !showResolution">
        <span class="section-title">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 11 12 14 22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
          Resolution
          <span :class="['res-dot', agendum.resolution ? 'res-dot--yes' : 'res-dot--no']" />
        </span>
        <div class="resolution-toggle-right">
          <!-- Create resolution button (only if none exists) -->
          <button v-if="canModify && !agendum.resolution"
            class="hbtn hbtn--sm"
            @click.stop="createResolution"
            :disabled="creatingRes">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add
          </button>
          <!-- Delete resolution -->
          <button v-if="canModify && agendum.resolution"
            class="hbtn hbtn--danger hbtn--sm"
            @click.stop="deleteResolution"
            title="Delete resolution">✕</button>
          <!-- Chevron -->
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            :class="['chevron', { 'chevron--open': showResolution }]">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </button>

      <!-- Resolution body (collapsible) -->
      <div v-if="showResolution && agendum.resolution" class="resolution-body">

        <!-- ── Resolution edit toolbar — RIGHT-aligned ── -->
        <div v-if="canModify" class="res-toolbar">
          <button class="hbtn" @click="editingRes = !editingRes">
            <svg v-if="!editingRes" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            {{ editingRes ? 'Cancel' : 'Edit' }}
          </button>
          <button v-if="editingRes" class="hbtn hbtn--primary" @click="saveResolution" :disabled="savingRes">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            {{ savingRes ? 'Saving…' : 'Save' }}
          </button>
        </div>

        <RichTextEditor
          v-model="localResBody"
          :editable="editingRes && canModify"
          minHeight="110px"
        />

        <!-- Resolution attachments -->
        <div class="section-header mt-3">
          <span class="section-title" style="font-size:11px">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
            Attachments
            <span class="count-pill">{{ agendum.resolution.attachments?.length ?? 0 }}</span>
          </span>
          <label v-if="canModify" class="upload-label upload-label--sm" title="Attach file">
            <input type="file" class="sr-only" @change="uploadResAttachment" />
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Attach
          </label>
        </div>

        <div v-if="!agendum.resolution.attachments?.length" class="empty-files" style="font-size:11px">
          No attachments
        </div>

        <div v-else class="file-list">
          <div
            v-for="(att, idx) in agendum.resolution.attachments"
            :key="att.id"
            class="file-row"
            draggable="true"
            @dragstart="fileDragStart('res', idx)"
            @dragover.prevent="fileDragOver('res', idx)"
            @dragend="fileDragEnd('res')"
            :class="{ 'is-dragging': resDragIdx === idx }"
          >
            <svg class="drag-pip" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="9" cy="7" r="1" fill="currentColor"/><circle cx="9" cy="12" r="1" fill="currentColor"/>
              <circle cx="9" cy="17" r="1" fill="currentColor"/><circle cx="15" cy="7" r="1" fill="currentColor"/>
              <circle cx="15" cy="12" r="1" fill="currentColor"/><circle cx="15" cy="17" r="1" fill="currentColor"/>
            </svg>
            <span class="file-order">{{ idx + 1 }}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <a :href="fileUrl(att.path)" target="_blank" class="file-name">{{ att.original_filename }}</a>
            <span class="file-size">{{ fmtBytes(att.size_bytes) }}</span>
            <button v-if="canModify" class="file-remove" @click="removeResAttachment(att.id)">✕</button>
          </div>
        </div>
      </div>

      <div v-if="showResolution && !agendum.resolution" class="empty-files">
        No resolution recorded
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import api from '../utils/api'
import { confirmDestructive } from '../utils/alerts'
import RichTextEditor from './RichTextEditor.vue'

const props = defineProps({
  agendum:   { type: Object,  required: true },
  meetingId: { type: String,  required: true },
  canModify: { type: Boolean, default: false },
})
const emit = defineEmits(['updated', 'deleted'])

const toast = useToast()

// ── local body copies ────────────────────────────────────────────────────────
const localBody    = ref(parseBody(props.agendum.body))
const localResBody = ref(parseBody(props.agendum.resolution?.body))

watch(() => props.agendum.body,              v => { localBody.value    = parseBody(v) })
watch(() => props.agendum.resolution?.body,  v => { localResBody.value = parseBody(v) })

function parseBody(raw) {
  if (!raw) return {}
  try { return typeof raw === 'string' ? JSON.parse(raw) : raw }
  catch { return {} }
}

// ── edit state ────────────────────────────────────────────────────────────────
const editingBody    = ref(false)
const editingRes     = ref(false)
const savingBody     = ref(false)
const savingRes      = ref(false)
const creatingRes    = ref(false)
const showResolution = ref(false)

// ── helpers ──────────────────────────────────────────────────────────────────
const MEDIA_ROOT = import.meta.env.VITE_MEDIA_URL || ''
const fileUrl    = path => `${MEDIA_ROOT}/${path.replace(/^\/+/, '')}`

function fmtBytes(b) {
  if (!b) return ''
  if (b < 1024)    return `${b} B`
  if (b < 1048576) return `${(b/1024).toFixed(1)} KB`
  return `${(b/1048576).toFixed(1)} MB`
}

function relTime(iso) {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h/24)}d ago`
}

async function refetch() {
  const res = await api.get(`/agendas/?meeting_id=${props.meetingId}`)
  const updated = (res.data || []).find(a => a.id === props.agendum.id)
  if (updated) emit('updated', updated)
}

// ── Agenda body save / delete ─────────────────────────────────────────────────
async function saveBody() {
  savingBody.value = true
  try {
    await api.patch(`/agendas/${props.agendum.id}`, { body: JSON.stringify(localBody.value) })
    toast.success('Agenda saved')
    editingBody.value = false
    await refetch()
  } catch (e) { toast.error(e.response?.data?.detail ?? 'Save failed') }
  finally { savingBody.value = false }
}

async function deleteAgendum() {
  const ok = await confirmDestructive(
    `Delete Ag-${props.agendum.serial}?`,
    'The agenda, resolution, and all attached files will be permanently deleted.',
    'Yes, Delete'
  )
  if (!ok) return
  try {
    await api.delete(`/agendas/${props.agendum.id}`)
    toast.success('Agenda deleted')
    emit('deleted', props.agendum.id)
  } catch { toast.error('Delete failed') }
}

// ── Annexure upload / remove / drag-reorder ───────────────────────────────────
const annDragIdx = ref(null)
const annOrder   = ref([...(props.agendum.annexures || [])])
watch(() => props.agendum.annexures, v => { annOrder.value = [...(v || [])] })

async function uploadAnnexure(evt) {
  const file = evt.target.files?.[0]; if (!file) return
  const fd   = new FormData(); fd.append('file', file)
  try {
    const up  = await api.post('/files/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    await api.post(`/agendas/${props.agendum.id}/files`, {
      file_id: up.data.id,
      order:   (props.agendum.annexures?.length ?? 0) + 1
    })
    toast.success('File attached')
    await refetch()
  } catch (e) {
    toast.error(e.response?.data?.detail ?? 'Upload failed')
  }
  evt.target.value = ''
}

async function removeAnnexure(annexureId) {
  const ok = await confirmDestructive('Remove file?', 'This file will be permanently deleted.', 'Remove')
  if (!ok) return
  try {
    await api.delete(`/agendas/${props.agendum.id}/files/${annexureId}`)
    toast.success('Removed')
    await refetch()
  } catch { toast.error('Failed') }
}

let annDragFrom = null
let resDragFrom = null

function fileDragStart(type, idx) {
  if (type === 'ann') annDragFrom = idx
  else resDragFrom = idx
}

function fileDragOver(type, idx) {
  if (type === 'ann') {
    if (annDragFrom === null || annDragFrom === idx) return
    const arr = [...annOrder.value]
    const [m] = arr.splice(annDragFrom, 1); arr.splice(idx, 0, m)
    annOrder.value = arr; annDragIdx.value = idx; annDragFrom = idx
  } else {
    if (resDragFrom === null || resDragFrom === idx) return
    const arr = [...resOrder.value]
    const [m] = arr.splice(resDragFrom, 1); arr.splice(idx, 0, m)
    resOrder.value = arr; resDragIdx.value = idx; resDragFrom = idx
  }
}

async function fileDragEnd(type) {
  if (type === 'ann') {
    annDragIdx.value = null; annDragFrom = null
    try {
      await Promise.all(annOrder.value.map((a, i) =>
        api.patch(`/agendas/${props.agendum.id}/files/${a.id}`, { order: i + 1 })
      ))
      await refetch()
    } catch { toast.error('Reorder failed') }
  } else {
    resDragIdx.value = null; resDragFrom = null
    try {
      await Promise.all(resOrder.value.map((a, i) =>
        api.patch(`/resolutions/${props.agendum.resolution.id}/files/${a.id}`, { order: i + 1 })
      ))
      await refetch()
    } catch { toast.error('Reorder failed') }
  }
}

// ── Resolution create / save / delete ─────────────────────────────────────────
async function createResolution() {
  creatingRes.value = true
  try {
    await api.post('/resolutions/', { agendum_id: props.agendum.id })
    toast.success('Resolution created')
    showResolution.value = true
    await refetch()
  } catch (e) { toast.error(e.response?.data?.detail ?? 'Failed') }
  finally { creatingRes.value = false }
}

async function saveResolution() {
  savingRes.value = true
  try {
    await api.patch(`/resolutions/${props.agendum.resolution.id}`, {
      body: JSON.stringify(localResBody.value)
    })
    toast.success('Resolution saved')
    editingRes.value = false
    await refetch()
  } catch { toast.error('Save failed') }
  finally { savingRes.value = false }
}

async function deleteResolution() {
  const ok = await confirmDestructive(
    'Delete resolution?',
    'The resolution and its attachments will be permanently deleted.',
    'Delete'
  )
  if (!ok) return
  try {
    await api.delete(`/resolutions/${props.agendum.resolution.id}`)
    toast.success('Resolution deleted')
    await refetch()
  } catch { toast.error('Failed') }
}

// ── Resolution attachments ────────────────────────────────────────────────────
const resDragIdx = ref(null)
const resOrder   = ref([...(props.agendum.resolution?.attachments || [])])
watch(() => props.agendum.resolution?.attachments, v => { resOrder.value = [...(v || [])] })

async function uploadResAttachment(evt) {
  const file = evt.target.files?.[0]; if (!file) return
  const fd   = new FormData(); fd.append('file', file)
  try {
    const up = await api.post('/files/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    await api.post(`/resolutions/${props.agendum.resolution.id}/files`, {
      file_id: up.data.id,
      order:   (props.agendum.resolution.attachments?.length ?? 0) + 1
    })
    toast.success('Attachment added')
    await refetch()
  } catch (e) {
    toast.error(e.response?.data?.detail ?? 'Upload failed')
  }
  evt.target.value = ''
}

async function removeResAttachment(attachmentId) {
  const ok = await confirmDestructive('Remove attachment?', 'This file will be permanently deleted.', 'Remove')
  if (!ok) return
  try {
    await api.delete(`/resolutions/${props.agendum.resolution.id}/files/${attachmentId}`)
    toast.success('Removed')
    await refetch()
  } catch { toast.error('Failed') }
}
</script>

<style scoped>
/* ── Box ── */
.abox {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  transition: box-shadow .2s;
}
.abox:hover { box-shadow: 0 4px 16px rgba(0,0,0,.06); }
.abox--suppl { border-left: 3px solid #f59e0b; }

/* ── Header ── */
.abox-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.abox-header-left  { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }
.abox-header-right { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }

.serial-badge {
  font-size: 11px; font-weight: 800; color: #1d4ed8;
  background: #dbeafe; padding: 2px 9px; border-radius: 20px; flex-shrink: 0;
}
.suppl-tag {
  font-size: 10px; font-weight: 700; color: #92400e;
  background: #fef3c7; padding: 2px 8px; border-radius: 20px;
  text-transform: uppercase; letter-spacing: .04em;
}
.meta-hint { font-size: 11px; color: #94a3b8; }

/* ── Header buttons ── */
.hbtn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; font-size: 12px; font-weight: 600;
  border: 1px solid #e2e8f0; border-radius: 8px;
  background: #fff; cursor: pointer; color: #374151;
  transition: background .12s; white-space: nowrap;
}
.hbtn:hover         { background: #f1f5f9; }
.hbtn:disabled      { opacity: .5; cursor: not-allowed; }
.hbtn--primary      { background: #2563eb; color: #fff; border-color: #2563eb; }
.hbtn--primary:hover{ background: #1d4ed8; }
.hbtn--danger       { color: #dc2626; border-color: #fecaca; }
.hbtn--danger:hover { background: #fee2e2; }
.hbtn--sm           { padding: 2px 8px; font-size: 11px; }
.hbtn-label         { display: none; }
@media (min-width: 480px) { .hbtn-label { display: inline; } }

/* ── Body ── */
.abox-body { padding: 14px; }

/* ── Sections (annexures + resolution) ── */
.abox-section {
  border-top: 1px solid #f1f5f9;
  padding: 10px 14px;
}
.abox-resolution { background: #fafafa; }

.section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
}
.section-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: .06em;
}
.count-pill {
  background: #e2e8f0; color: #475569; font-size: 10px;
  font-weight: 700; padding: 1px 6px; border-radius: 20px;
}

/* ── Upload label ── */
.upload-label {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; font-size: 11px; font-weight: 600;
  border: 1px dashed #94a3b8; border-radius: 6px;
  cursor: pointer; color: #475569;
  transition: background .1s, border-color .1s;
}
.upload-label:hover { background: #f1f5f9; border-color: #64748b; }
.upload-label--sm   { padding: 2px 7px; }
.sr-only { display: none; }

/* ── File list ── */
.file-list { display: flex; flex-direction: column; gap: 4px; }
.file-row {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 8px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 8px;
  font-size: 12px; cursor: default;
  transition: opacity .15s;
}
.file-row.is-dragging { opacity: .4; }
.drag-pip { color: #94a3b8; cursor: grab; flex-shrink: 0; }
.drag-pip:active { cursor: grabbing; }
.file-order { font-size: 10px; font-weight: 700; color: #94a3b8; width: 16px; text-align: center; flex-shrink: 0; }
.file-name {
  flex: 1; min-width: 0; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; color: #1d4ed8; text-decoration: none; font-weight: 500;
}
.file-name:hover { text-decoration: underline; }
.file-size   { font-size: 10px; color: #94a3b8; flex-shrink: 0; }
.file-remove {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; font-size: 11px;
  border: 1px solid #e2e8f0; border-radius: 4px;
  background: #fff; cursor: pointer; color: #dc2626;
  flex-shrink: 0;
}
.file-remove:hover { background: #fee2e2; }
.empty-files { font-size: 12px; color: #94a3b8; font-style: italic; padding: 4px 0; }

/* ── Resolution toggle ── */
.resolution-toggle {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  background: transparent; border: none; cursor: pointer; padding: 4px 0; text-align: left;
}
.resolution-toggle-right { display: flex; align-items: center; gap: 6px; }
.res-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
}
.res-dot--yes { background: #22c55e; }
.res-dot--no  { background: #cbd5e1; }
.chevron { transition: transform .2s; flex-shrink: 0; }
.chevron--open { transform: rotate(180deg); }

.resolution-body { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }

/* ── Resolution toolbar — RIGHT aligned ── */
.res-toolbar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;   /* ← moved to right */
}

.mt-3 { margin-top: 12px; }
</style>