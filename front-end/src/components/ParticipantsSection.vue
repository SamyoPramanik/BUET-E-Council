<!-- components/ParticipantsSection.vue -->
<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import api from '../utils/api'
import ParticipantCard from './ParticipantCard.vue'
import { confirmDestructive, confirmAction } from '../utils/alerts'
import {
  Search, Users, Crown, Trash2, Save, Mail, X, Plus,
  ChevronDown, GripVertical, UserPlus, ArrowLeftRight
} from 'lucide-vue-next'

// ── drag-and-drop (native HTML5, no extra lib needed) ──────────────────────
// We keep it simple: dragover reordering via index tracking.

const props = defineProps({
  meetingId:          { type: String,  required: true },
  currentPresidentId: { type: String,  default: null  },
  currentMembers:     { type: Array,   default: () => [] },
  allParticipants:    { type: Array,   required: true }
})

const emit = defineEmits(['president-updated', 'members-updated'])
const toast = useToast()

// ── President state ────────────────────────────────────────────────────────
const searchPresident   = ref('')
const isPresidentOpen   = ref(false)
const selectedPresidentId = ref(props.currentPresidentId)

watch(() => props.currentPresidentId, v => { selectedPresidentId.value = v })

const allParticipantsForPresident = computed(() => props.allParticipants)

const filteredForPresident = computed(() => {
  const term = searchPresident.value.toLowerCase().trim()
  if (!term) return allParticipantsForPresident.value
  return allParticipantsForPresident.value.filter(p =>
    p.content.toLowerCase().includes(term)
  )
})

const selectedPresidentCard = computed(() =>
  props.allParticipants.find(p => p.id === selectedPresidentId.value) || null
)

const savePresident = async () => {
  try {
    await api.patch(`/meetings/${props.meetingId}`, {
      president_card_id: selectedPresidentId.value || null
    })
    emit('president-updated', selectedPresidentId.value)
    toast.success('President updated')
  } catch {
    toast.error('Failed to update president')
  }
}

// close dropdown on outside click
const presidentDropdownRef = ref(null)
const closePresidentDropdown = () => { isPresidentOpen.value = false }

// ── Members state ──────────────────────────────────────────────────────────
const selectedMemberIds = ref(props.currentMembers.map(m => m.id))
watch(() => props.currentMembers, members => {
  selectedMemberIds.value = members.map(m => m.id)
})

const orderedMembers = computed(() =>
  selectedMemberIds.value
    .map(id => props.allParticipants.find(p => p.id === id))
    .filter(Boolean)
)

const hasMembers = computed(() => selectedMemberIds.value.length > 0)

// ── Modal state ────────────────────────────────────────────────────────────
const showModal      = ref(false)
const modalSearch    = ref('')
const modalDraftIds  = ref([])   // working copy inside modal

const openModal = () => {
  modalDraftIds.value = [...selectedMemberIds.value]
  modalSearch.value   = ''
  showModal.value     = true
}

const closeModal = async () => {
  const dirty = JSON.stringify(modalDraftIds.value) !== JSON.stringify(selectedMemberIds.value)
  if (dirty) {
    const ok = await confirmDestructive(
      'Discard changes?',
      'Your unsaved member changes will be lost.',
      'Yes, Discard'
    )
    if (!ok) return
  }
  showModal.value = false
}

const modalAvailable = computed(() => {
  const term = modalSearch.value.toLowerCase().trim()
  return props.allParticipants.filter(p =>
    !modalDraftIds.value.includes(p.id) &&
    (!term || p.content.toLowerCase().includes(term))
  )
})

const modalSelected = computed(() =>
  modalDraftIds.value
    .map(id => props.allParticipants.find(p => p.id === id))
    .filter(Boolean)
)

const modalToggleAdd = (id) => {
  if (!modalDraftIds.value.includes(id)) modalDraftIds.value.push(id)
}
const modalToggleRemove = (id) => {
  modalDraftIds.value = modalDraftIds.value.filter(i => i !== id)
}

const saveModal = async () => {
  const ok = await confirmAction(
    'Save member changes?',
    `This will update the meeting with ${modalDraftIds.value.length} member(s).`,
    'Save Members'
  )
  if (!ok) return
  selectedMemberIds.value = [...modalDraftIds.value]
  await saveMembers()
  showModal.value = false
}

// ── Drag-and-drop reorder inside modal ────────────────────────────────────
const dragFromIndex = ref(null)

const onDragStart = (idx) => { dragFromIndex.value = idx }
const onDragOver  = (e, idx) => {
  e.preventDefault()
  if (dragFromIndex.value === null || dragFromIndex.value === idx) return
  const arr = [...modalDraftIds.value]
  const [moved] = arr.splice(dragFromIndex.value, 1)
  arr.splice(idx, 0, moved)
  modalDraftIds.value   = arr
  dragFromIndex.value   = idx
}
const onDragEnd = () => { dragFromIndex.value = null }

// ── Save members to API ────────────────────────────────────────────────────
const saveMembers = async () => {
  try {
    await api.patch(`/meetings/${props.meetingId}/participants`, {
      participant_ids: selectedMemberIds.value
    })
    emit('members-updated', [...selectedMemberIds.value])
    toast.success('Members saved')
  } catch {
    toast.error('Failed to save members')
  }
}

const clearAllMembers = async () => {
  const ok = await confirmDestructive(
    'Clear all members?',
    'Every participant will be removed from this meeting.',
    'Yes, Clear All'
  )
  if (!ok) return
  selectedMemberIds.value = []
  await saveMembers()
}

const sendEmailPopup = () => {
  toast.info(`Email composer coming soon… (${selectedMemberIds.value.length} members)`)
}
</script>

<template>
  <div class="space-y-10">

    <!-- ══════════════════════════════════════════════
         SECTION HEADER  +  top action button
    ══════════════════════════════════════════════ -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-px bg-slate-300"></div>
        <span class="text-sm font-black uppercase tracking-widest text-slate-500">
          Participants
        </span>
      </div>

      <!-- exactly one button: Send Email OR Import from Previous -->
      <button
        v-if="hasMembers"
        @click="sendEmailPopup"
        class="flex items-center gap-2 px-5 py-2 text-sm font-semibold
               bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl
               transition-all active:scale-95 shadow-sm"
      >
        <Mail :size="16" /> Send Email
      </button>
      <button
        v-else
        class="flex items-center gap-2 px-5 py-2 text-sm font-semibold
               border-2 border-blue-500 text-blue-600 hover:bg-blue-50
               rounded-xl transition-all active:scale-95"
      >
        <ArrowLeftRight :size="16" /> Import from Previous Meeting
      </button>
    </div>

    <!-- ══════════════════════════════════════════════
         PRESIDENT SUB-SECTION
    ══════════════════════════════════════════════ -->
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-visible">
      <div class="px-6 py-4 border-b border-slate-100 flex items-center gap-3">
        <Crown class="text-amber-500" :size="18" />
        <span class="text-sm font-black uppercase tracking-widest text-slate-600">President</span>
      </div>

      <div class="p-6">
        <!-- search-integrated dropdown -->
        <div class="relative" v-click-outside="closePresidentDropdown">
          <!-- trigger -->
          <button
            @click="isPresidentOpen = !isPresidentOpen"
            class="w-full flex items-center justify-between px-5 py-3.5
                   bg-slate-50 border border-slate-200 rounded-xl
                   text-sm font-medium text-slate-700 hover:border-slate-300
                   transition-all"
          >
            <span class="truncate">
              {{ selectedPresidentCard ? selectedPresidentCard.content : 'Select President…' }}
            </span>
            <ChevronDown
              :size="16"
              class="shrink-0 ml-3 text-slate-400 transition-transform duration-200"
              :class="isPresidentOpen ? 'rotate-180' : ''"
            />
          </button>

          <!-- dropdown panel -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 -translate-y-1 scale-[0.98]"
            enter-to-class="opacity-100 translate-y-0 scale-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0 scale-[0.98]"
          >
            <div
              v-if="isPresidentOpen"
              class="absolute z-50 mt-2 w-full bg-white border border-slate-200
                     rounded-2xl shadow-2xl overflow-hidden flex flex-col"
              style="max-height: 22rem;"
            >
              <!-- search inside dropdown -->
              <div class="p-3 border-b border-slate-100 shrink-0">
                <div class="relative">
                  <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="15" />
                  <input
                    v-model="searchPresident"
                    placeholder="Search name…"
                    autofocus
                    class="w-full pl-9 pr-3 py-2.5 text-sm bg-slate-50
                           border border-slate-200 rounded-xl outline-none
                           focus:border-blue-400 transition-colors"
                  />
                </div>
              </div>

              <!-- list -->
              <div class="overflow-y-auto flex-1">
                <!-- none option -->
                <div
                  @click="selectedPresidentId = null; isPresidentOpen = false"
                  class="flex items-center justify-between px-5 py-3 text-sm
                         cursor-pointer hover:bg-slate-50 border-b border-slate-50
                         text-slate-500"
                  :class="selectedPresidentId === null ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <span class="italic">None — no president</span>
                  <span v-if="selectedPresidentId === null"
                        class="text-[10px] font-black text-blue-600 uppercase tracking-widest">
                    Selected
                  </span>
                </div>

                <div
                  v-for="p in filteredForPresident"
                  :key="p.id"
                  @click="selectedPresidentId = p.id; isPresidentOpen = false"
                  class="flex items-center justify-between px-5 py-3 text-sm
                         cursor-pointer hover:bg-slate-50 border-b border-slate-50
                         last:border-none"
                  :class="selectedPresidentId === p.id ? 'bg-blue-50' : ''"
                >
                  <span class="font-medium text-slate-800 truncate pr-4">{{ p.content }}</span>
                  <span v-if="selectedPresidentId === p.id"
                        class="shrink-0 text-[10px] font-black text-blue-600 uppercase tracking-widest">
                    Selected
                  </span>
                </div>

                <div v-if="filteredForPresident.length === 0"
                     class="py-8 text-center text-slate-400 text-sm italic">
                  No results
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- current president preview -->
        <div v-if="selectedPresidentCard" class="mt-4">
          <ParticipantCard :participant="selectedPresidentCard" />
        </div>

        <button
          @click="savePresident"
          class="mt-5 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white
                 text-sm font-bold rounded-xl flex items-center justify-center
                 gap-2 transition-all active:scale-95"
        >
          <Save :size="16" /> Save President
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════
         MEMBERS SUB-SECTION
    ══════════════════════════════════════════════ -->
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <!-- members header -->
      <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Users class="text-blue-500" :size="18" />
          <span class="text-sm font-black uppercase tracking-widest text-slate-600">
            Members
          </span>
          <span class="ml-1 px-2 py-0.5 bg-slate-100 text-slate-500
                       text-xs font-bold rounded-full">
            {{ selectedMemberIds.length }}
          </span>
        </div>

        <div class="flex items-center gap-3">
          <!-- clear all -->
          <button
            v-if="hasMembers"
            @click="clearAllMembers"
            class="flex items-center gap-1.5 text-xs font-semibold text-red-500
                   hover:text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-50
                   transition-all"
          >
            <Trash2 :size="14" /> Clear All
          </button>

          <!-- add members popup -->
          <button
            @click="openModal"
            class="flex items-center gap-2 px-4 py-2 text-sm font-semibold
                   bg-blue-600 hover:bg-blue-700 text-white rounded-xl
                   transition-all active:scale-95 shadow-sm"
          >
            <UserPlus :size="15" /> Add Members
          </button>
        </div>
      </div>

      <!-- members grid -->
      <div class="p-6">
        <div v-if="!hasMembers"
             class="border border-dashed border-slate-200 rounded-xl
                    py-16 flex flex-col items-center gap-3 text-slate-400">
          <Users :size="36" class="text-slate-300" />
          <p class="text-sm font-medium">No members added yet</p>
          <button
            @click="openModal"
            class="mt-1 text-xs font-semibold text-blue-500 hover:text-blue-700
                   underline underline-offset-2"
          >
            Add members
          </button>
        </div>

        <div v-else
             class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          <ParticipantCard
            v-for="m in orderedMembers"
            :key="m.id"
            :participant="m"
          />
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════
         ADD MEMBERS MODAL
    ══════════════════════════════════════════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showModal"
          class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm
                 flex items-center justify-center p-4"
          @click.self="closeModal"
        >
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="showModal"
              class="w-full max-w-5xl bg-white rounded-3xl shadow-2xl
                     flex flex-col overflow-hidden"
              style="max-height: 90vh;"
            >
              <!-- modal header -->
              <div class="px-7 py-5 border-b border-slate-100 flex items-center
                          justify-between shrink-0">
                <div>
                  <h2 class="text-lg font-black text-slate-800">
                    Manage Meeting Members
                  </h2>
                  <p class="text-xs text-slate-400 mt-0.5">
                    Drag to reorder · hover to add or remove
                  </p>
                </div>
                <button
                  @click="closeModal"
                  class="p-2 rounded-xl hover:bg-slate-100 text-slate-500
                         hover:text-slate-800 transition-all"
                >
                  <X :size="20" />
                </button>
              </div>

              <!-- modal body: two panels -->
              <div class="flex-1 overflow-hidden flex flex-col lg:flex-row min-h-0">

                <!-- LEFT: selected members (draggable) -->
                <div class="flex-1 border-b lg:border-b-0 lg:border-r border-slate-100
                            flex flex-col overflow-hidden">
                  <div class="px-5 py-3 border-b border-slate-100 flex items-center
                              gap-2 shrink-0 bg-slate-50/70">
                    <Users :size="15" class="text-blue-500" />
                    <span class="text-xs font-black uppercase tracking-widest text-slate-500">
                      Added Members
                    </span>
                    <span class="ml-auto px-2 py-0.5 bg-blue-100 text-blue-700
                                 text-xs font-bold rounded-full">
                      {{ modalSelected.length }}
                    </span>
                  </div>

                  <div class="flex-1 overflow-y-auto p-4 space-y-2">
                    <div
                      v-if="modalSelected.length === 0"
                      class="h-full flex flex-col items-center justify-center
                             text-slate-400 gap-2 py-10"
                    >
                      <Users :size="32" class="text-slate-200" />
                      <p class="text-sm">No members added yet</p>
                    </div>

                    <div
                      v-for="(m, idx) in modalSelected"
                      :key="m.id"
                      draggable="true"
                      @dragstart="onDragStart(idx)"
                      @dragover="onDragOver($event, idx)"
                      @dragend="onDragEnd"
                      class="group relative flex items-center gap-2 cursor-grab
                             active:cursor-grabbing"
                      :class="dragFromIndex === idx ? 'opacity-50' : ''"
                    >
                      <!-- grip handle -->
                      <GripVertical
                        :size="16"
                        class="shrink-0 text-slate-300 group-hover:text-slate-500
                               transition-colors"
                      />
                      <!-- card -->
                      <div class="flex-1 min-w-0">
                        <ParticipantCard :participant="m" />
                      </div>
                      <!-- remove button — appears on hover -->
                      <button
                        @click="modalToggleRemove(m.id)"
                        class="absolute top-2 right-2 p-1.5 rounded-lg
                               bg-red-50 text-red-500 hover:bg-red-100
                               opacity-0 group-hover:opacity-100
                               transition-all duration-150 z-10"
                        title="Remove"
                      >
                        <X :size="14" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- RIGHT: available to add -->
                <div class="flex-1 flex flex-col overflow-hidden">
                  <div class="px-5 py-3 border-b border-slate-100 shrink-0 bg-slate-50/70">
                    <!-- search -->
                    <div class="relative">
                      <Search
                        class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                        :size="14"
                      />
                      <input
                        v-model="modalSearch"
                        placeholder="Search participants to add…"
                        class="w-full pl-9 pr-3 py-2 text-sm bg-white
                               border border-slate-200 rounded-xl outline-none
                               focus:border-blue-400 transition-colors"
                      />
                    </div>
                    <div class="flex items-center gap-2 mt-2">
                      <Plus :size="13" class="text-green-500" />
                      <span class="text-xs font-black uppercase tracking-widest text-slate-500">
                        Available
                      </span>
                      <span class="ml-auto px-2 py-0.5 bg-slate-100 text-slate-500
                                   text-xs font-bold rounded-full">
                        {{ modalAvailable.length }}
                      </span>
                    </div>
                  </div>

                  <div class="flex-1 overflow-y-auto p-4 space-y-2">
                    <div
                      v-if="modalAvailable.length === 0"
                      class="h-full flex flex-col items-center justify-center
                             text-slate-400 gap-2 py-10"
                    >
                      <Users :size="32" class="text-slate-200" />
                      <p class="text-sm italic">
                        {{ modalSearch ? 'No results' : 'All participants added' }}
                      </p>
                    </div>

                    <div
                      v-for="p in modalAvailable"
                      :key="p.id"
                      class="group relative"
                    >
                      <ParticipantCard :participant="p" />
                      <!-- add button — appears on hover -->
                      <button
                        @click="modalToggleAdd(p.id)"
                        class="absolute top-2 right-2 p-1.5 rounded-lg
                               bg-green-50 text-green-600 hover:bg-green-100
                               opacity-0 group-hover:opacity-100
                               transition-all duration-150 z-10"
                        title="Add to meeting"
                      >
                        <Plus :size="14" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- modal footer -->
              <div class="px-7 py-5 border-t border-slate-100 flex items-center
                          justify-end gap-3 shrink-0 bg-slate-50/50">
                <button
                  @click="closeModal"
                  class="px-6 py-2.5 rounded-xl border border-slate-200
                         text-sm font-semibold text-slate-600 hover:bg-slate-100
                         transition-all"
                >
                  Cancel
                </button>
                <button
                  @click="saveModal"
                  class="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700
                         text-white text-sm font-bold flex items-center gap-2
                         transition-all active:scale-95 shadow-sm"
                >
                  <Save :size="15" />
                  Save Members ({{ modalDraftIds.length }})
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* drag ghost is slightly transparent */
[draggable="true"]:active {
  opacity: 0.6;
}
</style>