<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import { useToast } from 'vue-toastification'
import { Menu, X, FileText, Layout, Info, Users, Calendar, Hash, CheckCircle } from 'lucide-vue-next'

import MeetingSection from '../components/MeetingSection.vue'
import { authState } from '../store/auth'

const route = useRoute()
const toast = useToast()

// ── State ──────────────────────────────────────────────────────────────────
const meeting      = ref(null)
const loading      = ref(true)
const showSections = ref(false) // mobile sidebar toggle

// ── Permissions ────────────────────────────────────────────────────────────
const canModify = computed(() => ['admin', 'staff'].includes(authState.userRole))

// ── Data fetching ──────────────────────────────────────────────────────────
const fetchMeeting = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/meetings/${route.params.id}`)
    meeting.value = data
  } catch (err) {
    console.error('Failed to load meeting:', err)
    toast.error('Could not load meeting data.')
  } finally {
    loading.value = false
  }
}

// ── Save handler ───────────────────────────────────────────────────────────
// Called by each MeetingSection's @save event AFTER it has already emitted
// update:modelValue, so meeting.value.* is already up-to-date.
const handleSaveSection = async (payload) => {
  try {
    await api.patch(`/meetings/${route.params.id}`, payload)
    toast.success('Section saved successfully.')
    // Re-fetch to stay in sync with server (optional but safe)
    await fetchMeeting()
  } catch (err) {
    toast.error(err.response?.data?.detail ?? 'Save failed.')
  }
}

onMounted(fetchMeeting)
</script>

<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">

    <!-- ── Top header ── -->
    <header class="h-14 bg-white border-b px-4 flex items-center gap-4 z-50 shrink-0">
      <!-- Mobile sidebar toggle -->
      <button @click="showSections = !showSections" class="lg:hidden p-2 hover:bg-slate-100 rounded">
        <Menu v-if="!showSections" :size="20" />
        <X v-else :size="20" />
      </button>

      <div class="flex items-center gap-2">
        <span class="px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-bold uppercase">
          {{ meeting?.is_academic ? 'Academic' : 'Syndicate' }}
        </span>
        <h2 class="font-bold text-slate-700">
          Meeting #{{ meeting?.serial_num ?? '—' }}
        </h2>
      </div>
    </header>

    <!-- ── Body ── -->
    <div class="flex-1 flex overflow-hidden relative">

      <!-- Sidebar -->
      <aside
        :class="[
          'absolute lg:relative z-40 h-full bg-white border-r transition-all duration-300 ease-in-out',
          showSections
            ? 'translate-x-0 w-64 shadow-xl'
            : '-translate-x-full lg:translate-x-0 lg:w-56 lg:shadow-none',
        ]"
      >
        <nav class="p-4 space-y-1">
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4 px-3">
            Sections
          </p>
          <a href="#info"        class="nav-link"><Info         :size="18" /> Meeting Info</a>
          <a href="#title"       class="nav-link"><Layout       :size="18" /> Title</a>
          <a href="#description" class="nav-link"><FileText     :size="18" /> Minutes</a>
          <a href="#conclusion"  class="nav-link"><CheckCircle  :size="18" /> Conclusion</a>

          <!-- Coming soon placeholder -->
          <div class="pt-4 border-t mt-4 opacity-40 grayscale pointer-events-none">
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4 px-3">
              Coming Soon
            </p>
            <div class="nav-link"><Users :size="18" /> Participants</div>
          </div>
        </nav>
      </aside>

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto p-6">

        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center h-64 text-slate-400 text-sm">
          Loading meeting…
        </div>

        <div v-else-if="meeting" class="max-w-4xl mx-auto space-y-6">

          <!-- Info bento cards -->
          <section id="info" class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bento-card">
              <Hash class="text-blue-500 shrink-0" :size="20" />
              <div>
                <p class="text-xs text-slate-500">Serial</p>
                <p class="font-bold">#{{ meeting.serial_num }}</p>
              </div>
            </div>
            <div class="bento-card">
              <Calendar class="text-purple-500 shrink-0" :size="20" />
              <div>
                <p class="text-xs text-slate-500">Date</p>
                <p class="font-bold text-sm">
                  {{ new Date(meeting.meeting_date).toLocaleDateString() }}
                </p>
              </div>
            </div>
          </section>

          <!-- Title section -->
          <MeetingSection
            id="title"
            label="Meeting Title"
            description="Official title of the council meeting."
            v-model="meeting.title"
            :canModify="canModify"
            @save="handleSaveSection({ title: meeting.title })"
          />

          <!-- Description / Minutes section -->
          <MeetingSection
            id="description"
            label="Discussion & Minutes"
            description="Primary record of the agenda discussions."
            v-model="meeting.description"
            :canModify="canModify"
            @save="handleSaveSection({ description: meeting.description })"
          />

          <!-- Conclusion section -->
          <MeetingSection
            id="conclusion"
            label="Final Conclusion"
            description="Decisions and closing remarks."
            v-model="meeting.conclusion"
            :canModify="canModify"
            @save="handleSaveSection({ conclusion: meeting.conclusion })"
          />

        </div>

        <!-- Error / empty state -->
        <div v-else class="flex items-center justify-center h-64 text-slate-400 text-sm">
          Meeting not found.
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
@reference "../style.css";

.nav-link {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
         text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition-all cursor-pointer;
}
.nav-link.active {
  @apply bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100;
}
.bento-card {
  @apply bg-white p-4 rounded-xl border border-slate-200 flex items-center gap-4 shadow-sm;
}
</style>