<!-- views/MeetingsView.vue -->
<template>
  <div class="container mx-auto py-8 px-4">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="hidden lg:block lg:col-span-1"></div>

      <div class="col-span-1 lg:col-span-10">

        <!-- ── HEADER ──────────────────────────────────────────────────── -->
        <header class="mb-8 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 class="text-3xl font-bold text-slate-800 tracking-tight">Council Meetings</h1>
            <p class="text-slate-500 mt-1">Access and manage Academic and Syndicate records</p>
          </div>

          <!-- Create button — only for staff / admin -->
          <div v-if="canCreate" class="relative group flex-shrink-0">
            <button
              @click="openCreateModal"
              class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
                     text-white text-sm font-semibold rounded-xl shadow-sm
                     transition-all active:scale-95 focus:outline-none
                     focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              title="Create a new meeting record"
            >
              <!-- Plus icon -->
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5"  y1="12" x2="19" y2="12"/>
              </svg>
              New Meeting
            </button>
            <!-- Tooltip -->
            <div class="absolute right-0 top-full mt-2 px-3 py-1.5 bg-slate-800 text-white text-xs
                        rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100
                        transition-opacity pointer-events-none z-50 shadow-lg">
              Create a new meeting record
              <div class="absolute -top-1 right-4 w-2 h-2 bg-slate-800 rotate-45"></div>
            </div>
          </div>
        </header>

        <!-- ── TABS ────────────────────────────────────────────────────── -->
        <div class="flex space-x-1 bg-slate-200/60 p-1 rounded-xl mb-6 w-full sm:w-72 border border-slate-200">
          <button
            @click="setTab(true)"
            :class="[isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800']"
            class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
          >
            Academic
          </button>
          <button
            @click="setTab(false)"
            :class="[!isAcademic ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:text-slate-800']"
            class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
          >
            Syndicate
          </button>
        </div>

        <!-- ── TABLE ───────────────────────────────────────────────────── -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table class="w-full text-left border-collapse table-fixed">
            <thead class="bg-slate-50/80 border-b border-slate-200">
              <tr>
                <th @click="toggleSort('serial_num')"
                    class="p-4 w-24 cursor-pointer hover:bg-slate-100 transition">
                  <div class="flex items-center space-x-1">
                    <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Serial</span>
                    <span v-if="sortBy === 'serial_num'" class="text-blue-500 text-xs">
                      {{ sortDir === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th class="p-4">
                  <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Title</span>
                </th>
                <th class="p-4 w-32 text-center">
                  <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Status</span>
                </th>
                <th @click="toggleSort('meeting_date')"
                    class="p-4 w-40 cursor-pointer hover:bg-slate-100 transition">
                  <div class="flex items-center justify-end space-x-1">
                    <span class="text-xs uppercase tracking-wider font-bold text-slate-500">Date</span>
                    <span v-if="sortBy === 'meeting_date'" class="text-blue-500 text-xs">
                      {{ sortDir === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr v-for="meeting in meetings" :key="meeting.id"
                  class="hover:bg-slate-50/50 transition-colors group">
                <td class="p-4">
                  <router-link
                    :to="{ name: 'MeetingDetails', params: { id: meeting.id } }"
                    class="font-mono font-bold text-blue-600 hover:underline"
                  >
                    #{{ meeting.serial_num }}
                  </router-link>
                </td>
                <td class="p-4">
                  <p class="text-slate-700 font-medium truncate" :title="meeting.title_plain">
                    {{ meeting.title_plain || '—' }}
                  </p>
                </td>
                <td class="p-4 text-center">
                  <span v-if="meeting.is_finished"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold
                           bg-emerald-100 text-emerald-700 border border-emerald-200">
                    Finished
                  </span>
                  <span v-else
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold
                           bg-amber-100 text-amber-700 border border-amber-200">
                    Ongoing
                  </span>
                </td>
                <td class="p-4 text-right text-slate-500 text-sm font-medium">
                  {{ new Date(meeting.meeting_date).toLocaleDateString('en-GB', {
                       day: '2-digit', month: 'short', year: 'numeric'
                     }) }}
                </td>
              </tr>

              <tr v-if="loading">
                <td colspan="4" class="p-12 text-center">
                  <div class="flex flex-col items-center gap-2">
                    <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="text-sm text-slate-400 font-medium tracking-wide">Fetching meetings…</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="!loading && meetings.length === 0">
                <td colspan="4" class="p-12 text-center text-slate-400 italic">
                  No meeting records found for this category.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ── PAGINATION ──────────────────────────────────────────────── -->
        <div class="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-slate-500 font-medium">
            Showing <span class="text-slate-800">{{ meetings.length }}</span> of
            <span class="text-slate-800">{{ totalCount }}</span> records
          </p>
          <div class="flex items-center space-x-2">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1 || loading"
              class="px-4 py-2 text-sm font-semibold border rounded-xl
                     disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50">
              Previous
            </button>
            <div class="px-4 py-2 text-sm font-bold bg-white border rounded-xl shadow-sm text-blue-600">
              {{ currentPage }}
            </div>
            <button @click="changePage(currentPage + 1)"
              :disabled="currentPage * 10 >= totalCount || loading"
              class="px-4 py-2 text-sm font-semibold border rounded-xl
                     disabled:opacity-40 hover:bg-white hover:shadow-sm transition-all bg-slate-50">
              Next
            </button>
          </div>
        </div>

      </div>
      <div class="hidden lg:block lg:col-span-1"></div>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════════════════════ -->
  <!-- CREATE MEETING MODAL                                                   -->
  <!-- ══════════════════════════════════════════════════════════════════════ -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showModal"
           class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
           @click.self="closeModal">

        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-2"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          appear
        >
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">

            <!-- Modal header -->
            <div class="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-blue-100 flex items-center justify-center">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round">
                    <rect x="3" y="4" width="18" height="18" rx="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8"  y1="2" x2="8"  y2="6"/>
                    <line x1="3"  y1="10" x2="21" y2="10"/>
                  </svg>
                </div>
                <div>
                  <h2 class="text-lg font-black text-slate-800">New Meeting</h2>
                  <p class="text-xs text-slate-400">Fill in the required fields to create a record</p>
                </div>
              </div>
              <button @click="closeModal"
                class="p-2 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6"  y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <!-- Modal body -->
            <div class="px-6 py-6 space-y-5">

              <!-- Council Type -->
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-2">
                  Council Type <span class="text-red-500">*</span>
                </label>
                <div class="flex gap-3">
                  <label
                    class="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl border-2 cursor-pointer transition-all"
                    :class="form.is_academic === true
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 hover:border-slate-300'"
                  >
                    <input type="radio" v-model="form.is_academic" :value="true" class="accent-blue-600" />
                    <span class="font-semibold text-sm text-slate-700">Academic Council</span>
                  </label>
                  <label
                    class="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl border-2 cursor-pointer transition-all"
                    :class="form.is_academic === false
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-slate-200 hover:border-slate-300'"
                  >
                    <input type="radio" v-model="form.is_academic" :value="false" class="accent-purple-600" />
                    <span class="font-semibold text-sm text-slate-700">Syndicate</span>
                  </label>
                </div>
              </div>

              <!-- Serial Number -->
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-2">
                  Serial Number <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="form.serial_num"
                  type="number"
                  min="1"
                  placeholder="e.g. 465"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-800 font-semibold
                         focus:border-blue-400 focus:ring-3 focus:ring-blue-100 outline-none transition-all
                         placeholder:font-normal placeholder:text-slate-400"
                />
              </div>

              <!-- Meeting Date -->
              <div>
                <label class="block text-sm font-semibold text-slate-700 mb-2">
                  Meeting Date <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="form.meeting_date"
                  type="date"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-800
                         focus:border-blue-400 focus:ring-3 focus:ring-blue-100 outline-none transition-all"
                />
              </div>

            </div>

            <!-- Modal footer -->
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3">
              <p class="text-xs text-slate-400">
                <span class="text-red-500">*</span> All fields are required
              </p>
              <div class="flex gap-3">
                <button @click="closeModal"
                  class="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold
                         text-slate-600 hover:bg-white transition-all">
                  Cancel
                </button>
                <button @click="submitCreate" :disabled="creating"
                  class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700
                         text-white text-sm font-semibold rounded-xl transition-all
                         disabled:opacity-60 disabled:cursor-not-allowed active:scale-95">
                  <svg v-if="creating" class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="white" stroke-width="3" stroke-dasharray="31.4" stroke-dashoffset="10"/>
                  </svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5"  y1="12" x2="19" y2="12"/>
                  </svg>
                  {{ creating ? 'Creating…' : 'Create Meeting' }}
                </button>
              </div>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '../utils/api'
import { authState } from '../store/auth'

const router = useRouter()
const toast  = useToast()

// ── list state ─────────────────────────────────────────────────────────────
const meetings    = ref([])
const totalCount  = ref(0)
const loading     = ref(false)
const isAcademic  = ref(true)
const currentPage = ref(1)
const sortBy      = ref('meeting_date')
const sortDir     = ref('desc')

// ── permissions ────────────────────────────────────────────────────────────
const canCreate = computed(() =>
  ['admin', 'staff'].includes(authState.userRole)
)

// ── fetch meetings ─────────────────────────────────────────────────────────
const fetchMeetings = async () => {
  loading.value = true
  try {
    const response = await api.get('/meetings/', {
      params: { is_academic: isAcademic.value, page: currentPage.value, limit: 10 }
    })
    meetings.value  = response.data.data
    totalCount.value = response.data.total_count
  } catch (error) {
    console.error('Failed to fetch meetings', error)
    toast.error('Could not load meetings.')
  } finally {
    loading.value = false
  }
}

const setTab = (val) => {
  if (isAcademic.value === val) return
  isAcademic.value = val
  currentPage.value = 1
}

const changePage = (page) => { currentPage.value = page }

const toggleSort = (column) => {
  if (sortBy.value === column) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortDir.value = 'asc'
  }
  meetings.value.sort((a, b) => {
    const mod = sortDir.value === 'asc' ? 1 : -1
    if (a[column] < b[column]) return -1 * mod
    if (a[column] > b[column]) return 1 * mod
    return 0
  })
}

watch([isAcademic, currentPage], fetchMeetings)
onMounted(fetchMeetings)

// ── create meeting modal ───────────────────────────────────────────────────
const showModal = ref(false)
const creating  = ref(false)

const emptyForm = () => ({
  is_academic:  null,   // null so neither radio is pre-selected
  serial_num:   null,
  meeting_date: '',
})

const form = ref(emptyForm())

function openCreateModal() {
  form.value = emptyForm()
  showModal.value = true
}

function closeModal() {
  if (creating.value) return   // don't close mid-request
  showModal.value = false
}

async function submitCreate() {
  // ── client-side validation ──────────────────────────────────────────────
  const errors = []
  if (form.value.is_academic === null)
    errors.push('Please select a council type.')
  if (!form.value.serial_num || form.value.serial_num < 1)
    errors.push('Serial number is required and must be a positive integer.')
  if (!form.value.meeting_date)
    errors.push('Meeting date is required.')

  if (errors.length) {
    errors.forEach(e => toast.warning(e))
    return
  }

  creating.value = true
  try {
    const payload = {
      is_academic:  form.value.is_academic,
      serial_num:   form.value.serial_num,
      meeting_date: new Date(form.value.meeting_date + 'T00:00:00Z').toISOString(),
    }

    const res = await api.post('/meetings/', payload)
    const newMeeting = res.data

    toast.success(
      `Meeting #${newMeeting.serial_num} created — redirecting…`
    )

    showModal.value = false

    // Redirect to the newly created meeting's detail page
    router.push({ name: 'MeetingDetails', params: { id: newMeeting.id } })

  } catch (err) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      toast.error(detail)
    } else {
      toast.error('Failed to create meeting. Please try again.')
    }
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
th { white-space: nowrap; }
</style>