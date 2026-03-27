<!-- views/MeetingDetails.vue -->
<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import { useToast } from 'vue-toastification'
import Swal from 'sweetalert2'
import {
  Menu, X, Info, Layout, FileText, CheckCircle,
  Hash, Calendar, Edit3, Save, Users,
  ListOrdered, FileDown, Trash2, Plus
} from 'lucide-vue-next'
import { authState } from '../store/auth'
import { confirmDestructive } from '../utils/alerts'

import ParticipantsSection from '../components/ParticipantsSection.vue'
import ParticipantCard     from '../components/ParticipantCard.vue'
import AgendaBox           from '../components/AgendaBox.vue'
import InsertStrip         from '../components/InsertStrip.vue'

const route = useRoute()
const toast  = useToast()

// ── layout ────────────────────────────────────────────────────────────────────
const showSections = ref(false)

// ── data ──────────────────────────────────────────────────────────────────────
const meeting         = ref(null)
const loading         = ref(true)
const allParticipants = ref([])
const meetingMembers  = ref([])
const agendas         = ref([])   // raw list from API, kept in display order

const canModify = computed(() => ['admin', 'staff'].includes(authState.userRole))

const currentPresident = computed(() => {
  if (!meeting.value?.president_card_id) return null
  return allParticipants.value.find(p => p.id === meeting.value.president_card_id) || null
})

// Single flat sorted list — regular first, then supplementary, each group by serial
const sortedAgendas = computed(() =>
  [...agendas.value].sort((a, b) => {
    if (a.is_supplementary !== b.is_supplementary) return a.is_supplementary ? 1 : -1
    return a.serial - b.serial
  })
)

// ── sidebar sections ──────────────────────────────────────────────────────────
const activeSection = ref('info')
let observers = []

const staticSections = [
  { id: 'info',         label: 'Basic Info',          icon: Info        },
  { id: 'title',        label: 'Meeting Title',        icon: Layout      },
  { id: 'description',  label: 'Discussion & Minutes', icon: FileText    },
  { id: 'participants', label: 'Participants',          icon: Users       },
  { id: 'agendas',      label: 'Agendas',              icon: ListOrdered },
  { id: 'materials',    label: 'Materials',            icon: FileDown    },
  { id: 'conclusion',   label: 'Final Conclusion',     icon: CheckCircle },
]

const setupObservers = () => {
  observers.forEach(o => o.disconnect())
  observers = []
  const ids = [
    ...staticSections.map(s => s.id),
    ...agendas.value.map(a => `agenda-${a.id}`),
  ]
  ids.forEach(id => {
    const el = document.getElementById(id)
    if (!el) return
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) activeSection.value = id },
      { rootMargin: '-15% 0px -65% 0px', threshold: 0 }
    )
    obs.observe(el)
    observers.push(obs)
  })
}
onBeforeUnmount(() => observers.forEach(o => o.disconnect()))

// ── fetch ─────────────────────────────────────────────────────────────────────
const fetchAllData = async () => {
  loading.value = true
  try {
    const [mRes, pRes, mbRes, agRes] = await Promise.all([
      api.get(`/meetings/${route.params.id}`),
      api.get('/participants'),
      api.get(`/meetings/${route.params.id}/participants`),
      api.get(`/agendas/?meeting_id=${route.params.id}`),
    ])
    meeting.value         = mRes.data
    allParticipants.value = pRes.data  || []
    meetingMembers.value  = mbRes.data || []
    agendas.value         = agRes.data || []
  } catch (e) {
    console.error(e)
    toast.error('Could not load meeting data.')
  } finally {
    loading.value = false
    nextTick(() => setTimeout(setupObservers, 120))
  }
}
onMounted(fetchAllData)

// ── navigation ────────────────────────────────────────────────────────────────
const navTo = (id) => {
  showSections.value = false
  nextTick(() => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

// ── edit state ────────────────────────────────────────────────────────────────
const isEditingBasic       = ref(false)
const isEditingTitle       = ref(false)
const isEditingDescription = ref(false)
const isEditingConclusion  = ref(false)

const confirmSave = async (name) => {
  const r = await Swal.fire({
    title: `Save ${name}?`,
    text: 'This will permanently update the meeting record.',
    icon: 'info', iconColor: '#3b82f6',
    showCancelButton: true,
    confirmButtonText: 'Yes, Save',
    cancelButtonText: 'Cancel',
    reverseButtons: true,
    background: '#fff',
    buttonsStyling: false,
    customClass: {
      popup:         'rounded-[2rem] shadow-2xl p-8',
      title:         'text-2xl font-black text-slate-800 pt-4',
      htmlContainer: 'text-slate-500 font-medium pb-2',
      confirmButton: 'bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest mx-2 shadow-lg',
      cancelButton:  'bg-slate-100 hover:bg-slate-200 text-slate-600 px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest mx-2',
    }
  })
  return r.isConfirmed
}

const patch = async (payload) => api.patch(`/meetings/${route.params.id}`, payload)

const saveBasic = async () => {
  if (!await confirmSave('Basic Information')) return
  try {
    await patch({
      serial_num:   meeting.value.serial_num,
      is_academic:  meeting.value.is_academic,
      meeting_date: meeting.value.meeting_date,
      is_finished:  meeting.value.is_finished,
    })
    toast.success('Basic info saved.')
    isEditingBasic.value = false
  } catch (e) { toast.error(e.response?.data?.detail ?? 'Failed.') }
}
const cancelBasic = async () => { isEditingBasic.value = false; await fetchAllData() }

const saveTitle = async () => {
  if (!await confirmSave('Title')) return
  try { await patch({ title: meeting.value.title }); toast.success('Title saved.'); isEditingTitle.value = false }
  catch (e) { toast.error(e.response?.data?.detail ?? 'Failed.') }
}
const cancelTitle = async () => { isEditingTitle.value = false; await fetchAllData() }

const saveDescription = async () => {
  if (!await confirmSave('Discussion & Minutes')) return
  try { await patch({ description: meeting.value.description }); toast.success('Minutes saved.'); isEditingDescription.value = false }
  catch (e) { toast.error(e.response?.data?.detail ?? 'Failed.') }
}
const cancelDescription = async () => { isEditingDescription.value = false; await fetchAllData() }

const saveConclusion = async () => {
  if (!await confirmSave('Final Conclusion')) return
  try { await patch({ conclusion: meeting.value.conclusion }); toast.success('Conclusion saved.'); isEditingConclusion.value = false }
  catch (e) { toast.error(e.response?.data?.detail ?? 'Failed.') }
}
const cancelConclusion = async () => { isEditingConclusion.value = false; await fetchAllData() }

// ── participants ───────────────────────────────────────────────────────────────
const handlePresidentUpdate = id => { if (meeting.value) meeting.value.president_card_id = id }
const handleMembersUpdate = ids => {
  meetingMembers.value = allParticipants.value.filter(p => ids.includes(p.id))
}

// ── agendas ────────────────────────────────────────────────────────────────────
const creatingAgenda = ref(false)

const refreshAgendas = async () => {
  const res = await api.get(`/agendas/?meeting_id=${route.params.id}`)
  agendas.value = res.data || []
  nextTick(() => setTimeout(setupObservers, 80))
}

const handleAgendumUpdated = (updated) => {
  const idx = agendas.value.findIndex(a => a.id === updated.id)
  if (idx !== -1) agendas.value[idx] = updated
  else agendas.value.push(updated)
}

const handleAgendumDeleted = (id) => {
  agendas.value = agendas.value.filter(a => a.id !== id)
  // Re-number serials locally so Ag-N labels update immediately
  agendas.value.forEach((ag, i) => { ag.serial = i + 1 })
  nextTick(() => setTimeout(setupObservers, 80))
}

// insertIdx: position in sortedAgendas to insert BEFORE (null = append)
async function addAgendum(insertIdx = null) {
  creatingAgenda.value = true
  try {
    const sorted = sortedAgendas.value
    let targetSerial

    if (insertIdx === null) {
      targetSerial = sorted.length + 1
    } else {
      targetSerial = insertIdx + 1
      // shift everything from insertIdx upward by 1
      const toShift = sorted.slice(insertIdx)
      await Promise.all(
        toShift.map((ag, i) =>
          api.patch(`/agendas/${ag.id}`, { serial: insertIdx + 2 + i })
        )
      )
    }

    await api.post('/agendas/', {
      meeting_id:       route.params.id,
      serial:           targetSerial,
      is_supplementary: false,
    })
    toast.success('Agenda item added')
    await refreshAgendas()
  } catch (e) {
    toast.error(e.response?.data?.detail ?? 'Failed to add agenda')
  } finally {
    creatingAgenda.value = false
  }
}

async function deleteAllAgendas() {
  const ok = await confirmDestructive(
    'Delete all agenda items?',
    'Every agenda, resolution, and attached file will be permanently deleted.',
    'Yes, Delete All'
  )
  if (!ok) return
  try {
    await api.delete(`/agendas/?meeting_id=${route.params.id}`)
    toast.success('All agendas deleted')
    agendas.value = []
    nextTick(() => setTimeout(setupObservers, 80))
  } catch {
    toast.error('Failed to delete agendas')
  }
}

// ── drag-to-reorder agendas ────────────────────────────────────────────────────
const dragFromIdx = ref(null)

const onAgendaDragStart = (idx) => { dragFromIdx.value = idx }

const onAgendaDragOver = (e, idx) => {
  e.preventDefault()
  if (dragFromIdx.value === null || dragFromIdx.value === idx) return
  // Mutate agendas array to show live reordering
  const arr = [...agendas.value]
  const sorted = [...sortedAgendas.value]
  const [moved] = sorted.splice(dragFromIdx.value, 1)
  sorted.splice(idx, 0, moved)
  // Re-assign serials to match new order
  sorted.forEach((ag, i) => { ag.serial = i + 1 })
  agendas.value   = sorted
  dragFromIdx.value = idx
}

const onAgendaDragEnd = async () => {
  dragFromIdx.value = null
  try {
    await Promise.all(
      agendas.value.map((ag, i) =>
        api.patch(`/agendas/${ag.id}`, { serial: i + 1 })
      )
    )
  } catch {
    toast.error('Failed to save new order')
    await refreshAgendas()  // revert to server state if patch fails
  }
}

// ── materials / pdf ────────────────────────────────────────────────────────────
const pdfLoading = ref({ agenda: false, resolution: false })

async function downloadPdf(type) {
  pdfLoading.value[type] = true
  try {
    const res = await api.get(`/meetings/${route.params.id}/pdf/${type}`, { responseType: 'blob' })
    const url  = URL.createObjectURL(res.data)
    const a    = document.createElement('a')
    a.href = url
    a.download = `${type}_meeting_${meeting.value.serial_num}.pdf`
    a.click()
    URL.revokeObjectURL(url)
    toast.success(`${type === 'agenda' ? 'Agenda' : 'Resolution'} PDF downloaded`)
    await fetchAllData()
  } catch {
    toast.error('PDF generation failed')
  } finally {
    pdfLoading.value[type] = false
  }
}

async function clearPdf(type) {
  const ok = await confirmDestructive(
    `Clear ${type} PDF?`,
    'The cached PDF will be deleted and regenerated on next download.',
    'Clear'
  )
  if (!ok) return
  try {
    await api.delete(`/meetings/${route.params.id}/pdf/${type}`)
    toast.success('PDF cleared')
    await fetchAllData()
  } catch {
    toast.error('Failed to clear PDF')
  }
}
</script>

<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">

    <!-- ══ HEADER ══════════════════════════════════════════════════════════ -->
    <header class="h-16 shrink-0 bg-white border-b border-slate-200 shadow-sm
                   px-4 sm:px-6 flex items-center gap-3 z-50">
      <button @click="showSections = !showSections"
        class="lg:hidden p-2.5 -ml-1 rounded-xl hover:bg-slate-100 text-slate-600 transition-colors shrink-0">
        <component :is="showSections ? X : Menu" :size="22" />
      </button>

      <div v-if="meeting" class="flex items-center gap-3 sm:gap-4 min-w-0">
        <span class="px-3 sm:px-4 py-1 text-xs font-black uppercase tracking-widest rounded-xl shrink-0"
          :class="meeting.is_academic ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
          {{ meeting.is_academic ? 'Academic' : 'Syndicate' }}
        </span>
        <span class="h-4 w-px bg-slate-200 shrink-0 hidden sm:block" />
        <span class="font-black text-2xl tracking-tighter text-slate-800 shrink-0">
          #{{ meeting.serial_num }}
        </span>
      </div>

      <div class="flex-1 min-w-0" />

      <div v-if="meeting" class="shrink-0">
        <span class="px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5"
          :class="meeting.is_finished ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
          <CheckCircle v-if="meeting.is_finished" :size="13" />
          {{ meeting.is_finished ? 'Finished' : 'Ongoing' }}
        </span>
      </div>
    </header>

    <!-- ══ BODY ═══════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex overflow-hidden relative">

      <!-- mobile overlay -->
      <Transition
        enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
        leave-active-class="transition duration-150" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="showSections" @click="showSections = false"
          class="lg:hidden absolute inset-0 bg-black/40 z-30" />
      </Transition>

      <!-- ── SIDEBAR ──────────────────────────────────────────────────── -->
      <aside :class="[
        'absolute lg:relative z-40 h-full bg-white border-r border-slate-200',
        'transition-transform duration-300 ease-in-out shadow-xl lg:shadow-none',
        showSections ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0 lg:w-64 xl:w-72'
      ]">
        <div class="p-4 h-full flex flex-col overflow-hidden">
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 px-2">
            Sections
          </p>

          <nav class="flex-1 overflow-y-auto space-y-0.5 pr-1">
            <!-- static section links -->
            <button v-for="s in staticSections" :key="s.id" @click="navTo(s.id)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all text-left',
                activeSection === s.id ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'
              ]">
              <span :class="['w-1 h-4 rounded-full shrink-0 transition-all', activeSection === s.id ? 'bg-blue-500' : 'bg-transparent']" />
              <component :is="s.icon" :size="16"
                :class="activeSection === s.id ? 'text-blue-600' : 'text-slate-400'" />
              {{ s.label }}
            </button>

            <!-- per-agenda sub-links (indented under Agendas) -->
            <template v-if="sortedAgendas.length > 0">
              <div class="mt-1 ml-5 pl-3 border-l border-slate-100 space-y-0.5">
                <button v-for="(ag, idx) in sortedAgendas" :key="ag.id"
                  @click="navTo(`agenda-${ag.id}`)"
                  :class="[
                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs font-medium transition-all text-left',
                    activeSection === `agenda-${ag.id}` ? 'bg-blue-50 text-blue-700' : 'text-slate-500 hover:bg-slate-50'
                  ]">
                  <span class="shrink-0 font-bold text-[11px]">Ag-{{ idx + 1 }}</span>
                  <span v-if="ag.is_supplementary"
                    class="text-[9px] font-bold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full uppercase tracking-wide shrink-0">
                    S
                  </span>
                  <span class="truncate text-slate-400 italic text-[11px]"
                    v-if="!ag.body || ag.body === '{}'">
                    Empty
                  </span>
                </button>
              </div>
            </template>
          </nav>
        </div>
      </aside>

      <!-- ── MAIN ─────────────────────────────────────────────────────── -->
      <main class="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-7 lg:p-10">

        <!-- loading -->
        <div v-if="loading" class="flex flex-col items-center justify-center h-96 gap-4">
          <div class="w-8 h-8 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
          <p class="text-sm font-medium text-slate-400">Loading meeting…</p>
        </div>

        <div v-else-if="meeting" class="max-w-4xl mx-auto space-y-14 pb-28">

          <!-- ── BASIC INFO ──────────────────────────────────────────── -->
          <section id="info" class="scroll-mt-20">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-3">
                <div class="w-8 h-px bg-slate-300" />
                <span class="text-sm font-black uppercase tracking-widest text-slate-500">Basic Information</span>
              </div>
              <button v-if="canModify && !isEditingBasic" @click="isEditingBasic = true"
                class="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                <Edit3 :size="14" /> Edit
              </button>
            </div>

            <!-- view -->
            <div v-if="!isEditingBasic" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div v-for="card in [
                { icon: Hash,        color: 'text-blue-500',    label: 'Serial No.', value: `#${meeting.serial_num}`, big: true },
                { icon: Calendar,    color: 'text-violet-500',  label: 'Date',       value: meeting.meeting_date ? new Date(meeting.meeting_date).toLocaleDateString('en-US',{weekday:'short',month:'long',day:'numeric',year:'numeric'}) : 'Not set' },
                { icon: CheckCircle, color: 'text-emerald-500', label: 'Status',     value: meeting.is_finished ? 'Completed' : 'In Progress', status: true },
              ]" :key="card.label"
                class="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                <div class="flex items-center gap-2 mb-2">
                  <component :is="card.icon" :class="card.color" :size="16" />
                  <p class="text-xs text-slate-500 font-medium">{{ card.label }}</p>
                </div>
                <p :class="[card.big ? 'text-3xl font-black text-slate-800' : 'text-sm font-semibold text-slate-700', card.status ? (meeting.is_finished ? 'text-emerald-700 text-lg' : 'text-amber-700 text-lg') : '']">
                  {{ card.value }}
                </p>
              </div>
              <div class="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                <div class="flex items-center gap-2 mb-2">
                  <span class="w-4 h-4 rounded bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-500">T</span>
                  <p class="text-xs text-slate-500 font-medium">Type</p>
                </div>
                <p class="text-lg font-semibold text-slate-700">{{ meeting.is_academic ? 'Academic' : 'Syndicate' }}</p>
              </div>
            </div>

            <!-- edit -->
            <div v-else class="bg-white rounded-2xl border border-slate-100 shadow-sm p-7">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2">Serial Number</label>
                  <input v-model.number="meeting.serial_num" type="number"
                    class="w-full px-4 py-3 text-xl font-semibold rounded-xl border border-slate-200 focus:border-blue-400 outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2">Meeting Date</label>
                  <input type="date"
                    :value="meeting.meeting_date ? new Date(meeting.meeting_date).toISOString().split('T')[0] : ''"
                    @input="meeting.meeting_date = $event.target.value ? new Date($event.target.value + 'T00:00:00Z') : null"
                    class="w-full px-4 py-3 text-base rounded-xl border border-slate-200 focus:border-blue-400 outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2">Status</label>
                  <label class="flex items-center gap-3 cursor-pointer mt-1">
                    <input type="checkbox" v-model="meeting.is_finished" class="w-5 h-5 accent-blue-600" />
                    <span class="text-base font-medium">Finished / Completed</span>
                  </label>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2">Council Type</label>
                  <select v-model="meeting.is_academic"
                    class="w-full px-4 py-3 text-base font-medium rounded-xl border border-slate-200 focus:border-blue-400 outline-none">
                    <option :value="true">Academic Council</option>
                    <option :value="false">Syndicate</option>
                  </select>
                </div>
              </div>
              <div class="flex gap-3 mt-8 justify-end">
                <button @click="cancelBasic"
                  class="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">
                  Cancel
                </button>
                <button @click="saveBasic"
                  class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                  <Save :size="14" /> Save
                </button>
              </div>
            </div>
          </section>

          <!-- ── MEETING TITLE ───────────────────────────────────────── -->
          <section id="title" class="scroll-mt-20">
            <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div class="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                <div class="flex items-center gap-3">
                  <Layout class="text-violet-500" :size="18" />
                  <h3 class="text-xl font-black text-slate-800">Meeting Title</h3>
                </div>
                <button v-if="canModify && !isEditingTitle" @click="isEditingTitle = true"
                  class="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                  <Edit3 :size="14" /> Edit
                </button>
              </div>
              <div v-if="!isEditingTitle" class="px-7 py-8">
                <h2 class="text-xl font-semibold leading-relaxed text-slate-800">
                  {{ meeting.title || 'No title set' }}
                </h2>
              </div>
              <div v-else class="p-7">
                <input v-model="meeting.title"
                  class="w-full bg-slate-50 border border-slate-200 focus:border-violet-300 rounded-xl px-5 py-4 text-xl font-semibold outline-none"
                  placeholder="Enter meeting title…" />
                <div class="flex gap-3 mt-6 justify-end">
                  <button @click="cancelTitle"
                    class="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">Cancel</button>
                  <button @click="saveTitle"
                    class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                    <Save :size="14" /> Save Title
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- ── DISCUSSION & MINUTES ────────────────────────────────── -->
          <section id="description" class="scroll-mt-20">
            <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div class="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                <div class="flex items-center gap-3">
                  <FileText class="text-emerald-500" :size="18" />
                  <h3 class="text-xl font-black text-slate-800">Discussion & Minutes</h3>
                </div>
                <button v-if="canModify && !isEditingDescription" @click="isEditingDescription = true"
                  class="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                  <Edit3 :size="14" /> Edit
                </button>
              </div>
              <div v-if="!isEditingDescription" class="px-7 py-8 prose prose-slate max-w-none">
                <div v-if="meeting.description" v-html="meeting.description" class="text-[15px] leading-relaxed text-slate-700" />
                <p v-else class="text-slate-400 italic">No discussion minutes recorded yet.</p>
              </div>
              <div v-else class="p-7">
                <textarea v-model="meeting.description" rows="12"
                  class="w-full resize-y bg-slate-50 border border-slate-200 focus:border-emerald-300 rounded-2xl px-5 py-4 text-[15px] leading-relaxed outline-none font-medium"
                  placeholder="Write detailed minutes here…" />
                <div class="flex gap-3 mt-6 justify-end">
                  <button @click="cancelDescription"
                    class="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">Cancel</button>
                  <button @click="saveDescription"
                    class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                    <Save :size="14" /> Save Minutes
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- ── PARTICIPANTS ────────────────────────────────────────── -->
          <section id="participants" class="scroll-mt-20">
            <ParticipantsSection v-if="canModify"
              :meeting-id="route.params.id"
              :current-president-id="meeting.president_card_id"
              :current-members="meetingMembers"
              :all-participants="allParticipants"
              @president-updated="handlePresidentUpdate"
              @members-updated="handleMembersUpdate"
            />

            <!-- viewer read-only -->
            <div v-else class="space-y-8">
              <div class="flex items-center gap-3">
                <div class="w-8 h-px bg-slate-300" />
                <span class="text-sm font-black uppercase tracking-widest text-slate-500">Participants</span>
              </div>
              <div>
                <p class="text-xs uppercase tracking-widest font-black text-slate-400 mb-3">President</p>
                <div v-if="currentPresident" class="max-w-sm">
                  <ParticipantCard :participant="currentPresident" />
                </div>
                <div v-else class="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-10 text-center text-sm text-slate-400">
                  No president assigned
                </div>
              </div>
              <div>
                <p class="text-xs uppercase tracking-widest font-black text-slate-400 mb-3">
                  Members ({{ meetingMembers.length }})
                </p>
                <div v-if="meetingMembers.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  <ParticipantCard v-for="m in meetingMembers" :key="m.id" :participant="m" />
                </div>
                <div v-else class="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-12 text-center">
                  <Users class="mx-auto mb-2 text-slate-300" :size="32" />
                  <p class="text-slate-400 text-sm font-medium">No members added yet</p>
                </div>
              </div>
            </div>
          </section>

          <!-- ══════════════════════════════════════════════════════════ -->
          <!-- ── AGENDAS ─────────────────────────────────────────────── -->
          <!-- ══════════════════════════════════════════════════════════ -->
          <section id="agendas" class="scroll-mt-20">

            <!-- Section header -->
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-3">
                <div class="w-8 h-px bg-slate-300" />
                <span class="text-sm font-black uppercase tracking-widest text-slate-500">Agendas</span>
                <span class="text-xs font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">
                  {{ agendas.length }}
                </span>
              </div>

              <div v-if="canModify" class="flex items-center gap-2 flex-wrap justify-end">
                <!-- Delete all (only when items exist) -->
                <button v-if="agendas.length" @click="deleteAllAgendas"
                  class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                         text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all">
                  <Trash2 :size="11" /> Delete All
                </button>
                <!-- Add (append to end) -->
                <button @click="addAgendum(null)" :disabled="creatingAgenda"
                  class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                         bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50">
                  <Plus :size="11" /> Add Agenda
                </button>
              </div>
            </div>

            <!-- ── EMPTY STATE ─────────────────────────────────────── -->
            <div v-if="agendas.length === 0" class="ag-empty">
              <div class="ag-empty-icon">
                <ListOrdered :size="30" class="text-slate-300" />
              </div>
              <p class="ag-empty-title">No agenda items yet</p>
              <p class="ag-empty-sub">Use the button above or the strip below to add an agenda item</p>
              <div v-if="canModify" class="mt-4">
                <!-- Single insert strip for the empty state -->
                <InsertStrip
                  :disabled="creatingAgenda"
                  @add-regular="addAgendum(0)"
                />
              </div>
            </div>

            <!-- ── AGENDA LIST ─────────────────────────────────────── -->
            <div v-else class="ag-list">

              <!-- Insert strip before first item -->
              <InsertStrip
                v-if="canModify"
                :disabled="creatingAgenda"
                @add-regular="addAgendum(0)"
              />

              <template v-for="(ag, idx) in sortedAgendas" :key="ag.id">

                <!-- Draggable agenda card wrapper -->
                <div
                  :id="`agenda-${ag.id}`"
                  class="scroll-mt-20 ag-card-wrap"
                  draggable="true"
                  @dragstart="onAgendaDragStart(idx)"
                  @dragover="onAgendaDragOver($event, idx)"
                  @dragend="onAgendaDragEnd"
                  :class="{ 'ag-dragging': dragFromIdx === idx }"
                >
                  <!--
                    Pass a modified agendum with Ag-N serial label.
                    The actual .serial value drives the Ag-N display in AgendaBox.
                    We pass idx+1 so the label always reflects display order.
                  -->
                  <AgendaBox
                    :agendum="{ ...ag, serial: idx + 1 }"
                    :meeting-id="route.params.id"
                    :can-modify="canModify"
                    @updated="handleAgendumUpdated"
                    @deleted="handleAgendumDeleted"
                  />
                </div>

                <!-- Insert strip after each item -->
                <InsertStrip
                  v-if="canModify"
                  :disabled="creatingAgenda"
                  @add-regular="addAgendum(idx + 1)"
                />

              </template>
            </div>
          </section>

          <!-- ── MATERIALS ──────────────────────────────────────────── -->
          <section id="materials" class="scroll-mt-20">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-8 h-px bg-slate-300" />
              <span class="text-sm font-black uppercase tracking-widest text-slate-500">Materials</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <!-- Agenda PDF -->
              <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center">
                    <FileDown class="text-blue-600" :size="18" />
                  </div>
                  <div>
                    <p class="text-sm font-black text-slate-800">Agenda PDF</p>
                    <p class="text-xs text-slate-400">Full meeting agenda</p>
                  </div>
                  <span v-if="meeting.agenda_pdf"
                    class="ml-auto text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                    Cached
                  </span>
                </div>
                <div class="flex gap-2">
                  <button @click="downloadPdf('agenda')" :disabled="pdfLoading.agenda"
                    class="flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold
                           bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all disabled:opacity-60">
                    <FileDown :size="14" />
                    {{ pdfLoading.agenda ? 'Generating…' : 'Download' }}
                  </button>
                  <button v-if="meeting.agenda_pdf && canModify" @click="clearPdf('agenda')"
                    class="p-2.5 text-red-500 border border-red-200 rounded-xl hover:bg-red-50 transition-all"
                    title="Clear cached PDF">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>

              <!-- Resolution PDF -->
              <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                <div class="flex items-center gap-3 mb-4">
                  <div class="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center">
                    <FileDown class="text-emerald-600" :size="18" />
                  </div>
                  <div>
                    <p class="text-sm font-black text-slate-800">Resolution PDF</p>
                    <p class="text-xs text-slate-400">All resolutions</p>
                  </div>
                  <span v-if="meeting.resolution_pdf"
                    class="ml-auto text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                    Cached
                  </span>
                </div>
                <div class="flex gap-2">
                  <button @click="downloadPdf('resolution')" :disabled="pdfLoading.resolution"
                    class="flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold
                           bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-all disabled:opacity-60">
                    <FileDown :size="14" />
                    {{ pdfLoading.resolution ? 'Generating…' : 'Download' }}
                  </button>
                  <button v-if="meeting.resolution_pdf && canModify" @click="clearPdf('resolution')"
                    class="p-2.5 text-red-500 border border-red-200 rounded-xl hover:bg-red-50 transition-all"
                    title="Clear cached PDF">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- ── FINAL CONCLUSION ───────────────────────────────────── -->
          <section id="conclusion" class="scroll-mt-20">
            <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div class="px-7 pt-6 pb-5 flex items-start justify-between border-b border-slate-100">
                <div class="flex items-center gap-3">
                  <CheckCircle class="text-rose-500" :size="18" />
                  <h3 class="text-xl font-black text-slate-800">Final Conclusion</h3>
                </div>
                <button v-if="canModify && !isEditingConclusion" @click="isEditingConclusion = true"
                  class="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
                  <Edit3 :size="14" /> Edit
                </button>
              </div>
              <div v-if="!isEditingConclusion" class="px-7 py-8 prose prose-slate max-w-none">
                <div v-if="meeting.conclusion" v-html="meeting.conclusion" class="text-[15px] leading-relaxed text-slate-700" />
                <p v-else class="text-slate-400 italic">No conclusion recorded yet.</p>
              </div>
              <div v-else class="p-7">
                <textarea v-model="meeting.conclusion" rows="9"
                  class="w-full resize-y bg-slate-50 border border-slate-200 focus:border-rose-300 rounded-2xl px-5 py-4 text-[15px] leading-relaxed outline-none font-medium"
                  placeholder="Write final decisions and closing remarks…" />
                <div class="flex gap-3 mt-6 justify-end">
                  <button @click="cancelConclusion"
                    class="px-5 py-2.5 rounded-xl border border-slate-200 font-medium text-slate-600 hover:bg-slate-50 text-sm">Cancel</button>
                  <button @click="saveConclusion"
                    class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm">
                    <Save :size="14" /> Save Conclusion
                  </button>
                </div>
              </div>
            </div>
          </section>

        </div><!-- /meeting content -->

        <div v-else class="flex items-center justify-center h-96 text-slate-400">
          Meeting not found or has been deleted.
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
@reference "../style.css";

.prose :deep(p) { margin-top: 1.25em; margin-bottom: 1.25em; }

/* ── Agenda list ── */
.ag-list { display: flex; flex-direction: column; }

.ag-card-wrap {
  transition: opacity .15s, transform .15s;
}
.ag-card-wrap.ag-dragging {
  opacity: .35;
  transform: scale(.99);
}

/* ── Empty state ── */
.ag-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1.5rem;
  background: #f8fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 20px;
  text-align: center;
  gap: 6px;
}
.ag-empty-icon {
  width: 52px; height: 52px;
  border-radius: 14px;
  background: #f1f5f9;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}
.ag-empty-title { font-size: 15px; font-weight: 700; color: #475569; margin: 0; }
.ag-empty-sub   { font-size: 13px; color: #94a3b8; margin: 0; max-width: 320px; }
</style>