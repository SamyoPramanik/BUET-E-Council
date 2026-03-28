<!-- components/SignatureCardsSection.vue -->
<!--
  Full signature-cards management section for MeetingDetails.

  Props:
    meetingId   — UUID string of the current meeting
    canModify   — true for admin/staff; false for viewers

  Behaviour:
    • Viewers    — read-only grid of SignatureCardItem (no buttons)
    • Modifiers  — can add from catalogue (modal), remove, drag-to-reorder,
                   and create brand-new cards inline in the modal
-->
<template>
  <div class="space-y-0">

    <!-- ══ Section header ══════════════════════════════════════════════════ -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-8 h-px bg-slate-300" />
        <span class="text-sm font-black uppercase tracking-widest text-slate-500">
          Signature Cards
        </span>
        <span class="text-xs font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">
          {{ meetingCards.length }}
        </span>
      </div>

      <div v-if="canModify" class="flex items-center gap-2">
        <button v-if="meetingCards.length" @click="clearAll"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all">
          <Trash2 :size="12" /> Clear All
        </button>
        <button @click="openModal"
          class="flex items-center gap-2 px-4 py-2 text-sm font-semibold
                 bg-slate-800 hover:bg-slate-900 text-white rounded-xl
                 transition-all active:scale-95 shadow-sm">
          <PenLine :size="15" /> Manage Signatures
        </button>
      </div>
    </div>

    <!-- ══ Content ══════════════════════════════════════════════════════════ -->

    <!-- Empty state -->
    <div v-if="!meetingCards.length && !loading"
      class="flex flex-col items-center gap-3 py-14 bg-slate-50
             border-2 border-dashed border-slate-200 rounded-2xl text-center">
      <div class="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center">
        <PenLine :size="22" class="text-slate-300" />
      </div>
      <p class="text-sm font-semibold text-slate-500">No signature cards yet</p>
      <p class="text-xs text-slate-400 max-w-xs">
        {{ canModify ? 'Use "Manage Signatures" to add the authorising signatures.' : 'No signatures have been added to this meeting.' }}
      </p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex items-center justify-center py-10">
      <div class="w-6 h-6 border-4 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
    </div>

    <!-- Card grid -->
    <div v-else class="sig-grid">
      <div
        v-for="(card, idx) in meetingCards"
        :key="card.id"
        class="group"
        :draggable="canModify ? 'true' : 'false'"
        @dragstart="canModify && onDragStart(idx)"
        @dragover="canModify && onDragOver($event, idx)"
        @dragend="canModify && onDragEnd()"
      >
        <SignatureCardItem
          :card="card"
          :removable="canModify"
          :draggable="canModify"
          :is-dragging="dragFromIdx === idx"
          @remove="removeCard"
        />
      </div>
    </div>

  </div>

  <!-- ══════════════════════════════════════════════════════════════════════
       MANAGE MODAL
  ══════════════════════════════════════════════════════════════════════════ -->
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
        class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm
               flex items-center justify-center p-4"
        @click.self="closeModal">

        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div v-if="showModal"
            class="w-full max-w-4xl bg-white rounded-3xl shadow-2xl
                   flex flex-col overflow-hidden"
            style="max-height: 88vh;">

            <!-- Modal header -->
            <div class="px-7 py-5 border-b border-slate-100 flex items-center justify-between shrink-0">
              <div>
                <h2 class="text-lg font-black text-slate-800">Manage Signature Cards</h2>
                <p class="text-xs text-slate-400 mt-0.5">
                  Attach from catalogue · create new · drag to reorder
                </p>
              </div>
              <button @click="closeModal"
                class="p-2 rounded-xl hover:bg-slate-100 text-slate-500 transition-all">
                <X :size="20" />
              </button>
            </div>

            <!-- Modal body: two columns -->
            <div class="flex-1 min-h-0 flex flex-col lg:flex-row overflow-hidden">

              <!-- LEFT: attached (draggable) -->
              <div class="flex-1 border-b lg:border-b-0 lg:border-r border-slate-100 flex flex-col overflow-hidden">
                <div class="px-5 py-3 border-b border-slate-100 flex items-center gap-2 shrink-0 bg-slate-50/70">
                  <PenLine :size="14" class="text-slate-500" />
                  <span class="text-xs font-black uppercase tracking-widest text-slate-500">
                    Attached
                  </span>
                  <span class="ml-auto px-2 py-0.5 bg-slate-200 text-slate-600 text-xs font-bold rounded-full">
                    {{ modalDraft.length }}
                  </span>
                </div>

                <div class="flex-1 overflow-y-auto p-4">
                  <div v-if="!modalDraft.length"
                    class="h-full flex flex-col items-center justify-center
                           text-slate-400 gap-2 py-10">
                    <PenLine :size="32" class="text-slate-200" />
                    <p class="text-sm">No cards attached yet</p>
                  </div>

                  <div class="flex flex-col gap-3">
                    <div
                      v-for="(card, idx) in modalDraftCards"
                      :key="card.id"
                      class="group relative"
                      draggable="true"
                      @dragstart="onModalDragStart(idx)"
                      @dragover="onModalDragOver($event, idx)"
                      @dragend="onModalDragEnd()"
                      :class="modalDragFrom === idx ? 'opacity-40' : ''"
                    >
                      <SignatureCardItem
                        :card="card"
                        :removable="true"
                        :draggable="true"
                        @remove="modalRemove"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- RIGHT: catalogue + create new -->
              <div class="flex-1 flex flex-col overflow-hidden">
                <div class="px-5 py-3 border-b border-slate-100 shrink-0 bg-slate-50/70 space-y-2">
                  <!-- Search -->
                  <div class="relative">
                    <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" :size="14" />
                    <input v-model="catalogueSearch" @input="onSearchInput"
                      placeholder="Search catalogue…"
                      class="w-full pl-9 pr-3 py-2 text-sm bg-white border border-slate-200
                             rounded-xl outline-none focus:border-slate-400 transition-colors" />
                  </div>
                  <div class="flex items-center gap-2">
                    <Plus :size="13" class="text-emerald-500" />
                    <span class="text-xs font-black uppercase tracking-widest text-slate-500">Catalogue</span>
                    <span class="ml-auto px-2 py-0.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-full">
                      {{ catalogueTotal }}
                    </span>
                  </div>
                </div>

                <div class="flex-1 overflow-y-auto p-4 space-y-3" @scroll="onCatalogueScroll">

                  <!-- Create new card form -->
                  <div class="border border-dashed border-slate-300 rounded-xl p-4 bg-slate-50/60">
                    <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">
                      + Create New Card
                    </p>
                    <textarea
                      v-model="newCardContent"
                      rows="3"
                      placeholder="(Name)\nTitle\nও\nRole"
                      class="w-full text-sm bg-white border border-slate-200 rounded-lg px-3 py-2
                             outline-none focus:border-slate-400 resize-none font-mono"
                    />
                    <button @click="createAndAttach"
                      :disabled="!newCardContent.trim() || creating"
                      class="mt-2 w-full py-2 text-xs font-bold bg-slate-800 hover:bg-slate-900
                             text-white rounded-lg transition-all disabled:opacity-40">
                      {{ creating ? 'Creating…' : 'Create & Attach' }}
                    </button>
                  </div>

                  <!-- Catalogue items -->
                  <div
                    v-for="card in filteredCatalogue"
                    :key="card.id"
                    class="group relative"
                  >
                    <SignatureCardItem :card="card" />
                    <button
                      @click="modalAdd(card)"
                      :disabled="modalDraft.includes(card.id)"
                      class="absolute top-2 right-2 p-1.5 rounded-lg bg-emerald-50 text-emerald-600
                             hover:bg-emerald-100 transition-all duration-150 z-10 text-xs font-bold"
                      :class="modalDraft.includes(card.id)
                        ? 'opacity-40 cursor-not-allowed'
                        : 'opacity-0 group-hover:opacity-100'"
                      :title="modalDraft.includes(card.id) ? 'Already attached' : 'Attach'"
                    >
                      <Plus :size="14" />
                    </button>
                  </div>

                  <!-- Infinite scroll loader -->
                  <div v-if="catalogueLoading" class="flex justify-center py-4">
                    <div class="w-5 h-5 border-4 border-slate-200 border-t-slate-500 rounded-full animate-spin" />
                  </div>
                  <p v-if="!catalogueLoading && !filteredCatalogue.length && !newCardContent"
                    class="text-center text-sm text-slate-400 italic py-6">
                    {{ catalogueSearch ? 'No results' : 'Catalogue is empty' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Modal footer -->
            <div class="px-7 py-5 border-t border-slate-100 flex items-center justify-end gap-3 shrink-0 bg-slate-50/50">
              <button @click="closeModal"
                class="px-6 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold
                       text-slate-600 hover:bg-slate-100 transition-all">
                Cancel
              </button>
              <button @click="saveModal"
                :disabled="saving"
                class="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white
                       text-sm font-bold flex items-center gap-2 transition-all active:scale-95
                       disabled:opacity-50">
                <Save :size="15" />
                {{ saving ? 'Saving…' : `Save (${modalDraft.length})` }}
              </button>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { X, Plus, Search, Trash2, Save, PenLine, GripVertical } from 'lucide-vue-next'
import api from '../utils/api'
import { confirmDestructive } from '../utils/alerts'
import SignatureCardItem from './SignatureCardItem.vue'

const props = defineProps({
  meetingId:  { type: String,  required: true },
  canModify:  { type: Boolean, default: false },
})

const toast = useToast()

// ── Meeting cards (attached, ordered) ─────────────────────────────────────
const meetingCards = ref([])
const loading      = ref(false)

const fetchMeetingCards = async () => {
  loading.value = true
  try {
    const res = await api.get(`/meetings/${props.meetingId}/signature-cards`)
    meetingCards.value = res.data || []
  } catch { toast.error('Failed to load signature cards') }
  finally { loading.value = false }
}
onMounted(fetchMeetingCards)

// ── Drag-to-reorder on the main grid ──────────────────────────────────────
const dragFromIdx = ref(null)
let dragOrder = []

const onDragStart = (idx) => {
  dragOrder = [...meetingCards.value]
  dragFromIdx.value = idx
}
const onDragOver = (e, idx) => {
  e.preventDefault()
  if (dragFromIdx.value === null || dragFromIdx.value === idx) return
  const arr = [...meetingCards.value]
  const [m] = arr.splice(dragFromIdx.value, 1)
  arr.splice(idx, 0, m)
  meetingCards.value = arr
  dragFromIdx.value = idx
}
const onDragEnd = async () => {
  dragFromIdx.value = null
  try {
    // Patch each card's order sequentially
    for (let i = 0; i < meetingCards.value.length; i++) {
      await api.patch(
        `/meetings/${props.meetingId}/signature-cards/${meetingCards.value[i].id}`,
        { order: i + 1 }
      )
    }
    toast.success('Order saved')
    await fetchMeetingCards()
  } catch {
    toast.error('Failed to save order')
    meetingCards.value = dragOrder // revert
  }
}

// ── Remove one card ────────────────────────────────────────────────────────
const removeCard = async (cardId) => {
  const ok = await confirmDestructive(
    'Remove signature card?',
    'This card will be detached from this meeting. It remains in the global catalogue.',
    'Remove'
  )
  if (!ok) return
  try {
    await api.delete(`/meetings/${props.meetingId}/signature-cards/${cardId}`)
    toast.success('Removed')
    await fetchMeetingCards()
  } catch { toast.error('Failed to remove card') }
}

// ── Clear all ──────────────────────────────────────────────────────────────
const clearAll = async () => {
  const ok = await confirmDestructive(
    'Remove all signature cards?',
    'All cards will be detached from this meeting.',
    'Clear All'
  )
  if (!ok) return
  try {
    await api.delete(`/meetings/${props.meetingId}/signature-cards`)
    meetingCards.value = []
    toast.success('All signature cards removed')
  } catch { toast.error('Failed to clear cards') }
}

// ── Modal state ────────────────────────────────────────────────────────────
const showModal       = ref(false)
const saving          = ref(false)
const creating        = ref(false)
const newCardContent  = ref('')

// Draft: list of card UUIDs in display order
const modalDraft      = ref([])
// Full card objects for the draft (resolved from catalogue)
const modalDraftCards = computed(() =>
  modalDraft.value
    .map(id => [...catalogue.value, ...meetingCards.value].find(c => c.id === id))
    .filter(Boolean)
)

const openModal = () => {
  modalDraft.value   = meetingCards.value.map(c => c.id)
  newCardContent.value = ''
  showModal.value    = true
  loadCatalogue(true)
}

const closeModal = () => { showModal.value = false }

// ── Catalogue (paginated) ─────────────────────────────────────────────────
const catalogue       = ref([])
const catalogueSearch = ref('')
const cataloguePage   = ref(1)
const catalogueTotal  = ref(0)
const catalogueLoading = ref(false)
const CATALOGUE_LIMIT  = 20

const filteredCatalogue = computed(() =>
  catalogue.value.filter(c => !modalDraft.value.includes(c.id))
)

let searchTimeout = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadCatalogue(true), 300)
}

const loadCatalogue = async (reset = false) => {
  if (catalogueLoading.value) return
  if (reset) { cataloguePage.value = 1; catalogue.value = [] }
  catalogueLoading.value = true
  try {
    const params = { page: cataloguePage.value, limit: CATALOGUE_LIMIT }
    if (catalogueSearch.value.trim()) params.search = catalogueSearch.value.trim()
    const res = await api.get('/signature-cards/', { params })
    catalogueTotal.value = res.data.total_count
    catalogue.value = reset
      ? res.data.data
      : [...catalogue.value, ...res.data.data]
    cataloguePage.value++
  } catch { /* silent */ }
  finally { catalogueLoading.value = false }
}

const onCatalogueScroll = (e) => {
  const el = e.target
  const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 60
  const hasMore = catalogue.value.length < catalogueTotal.value
  if (nearBottom && hasMore && !catalogueLoading.value) loadCatalogue()
}

// ── Modal: add / remove / drag ────────────────────────────────────────────
const modalAdd    = (card) => {
  if (!modalDraft.value.includes(card.id)) {
    // Ensure the full card object is in catalogue for resolution
    if (!catalogue.value.find(c => c.id === card.id)) catalogue.value.push(card)
    modalDraft.value.push(card.id)
  }
}
const modalRemove = (cardId) => {
  modalDraft.value = modalDraft.value.filter(id => id !== cardId)
}

let modalDragFrom = null
const onModalDragStart = (idx) => { modalDragFrom = idx }
const onModalDragOver  = (e, idx) => {
  e.preventDefault()
  if (modalDragFrom === null || modalDragFrom === idx) return
  const arr = [...modalDraft.value]
  const [m] = arr.splice(modalDragFrom, 1)
  arr.splice(idx, 0, m)
  modalDraft.value = arr
  modalDragFrom = idx
}
const onModalDragEnd = () => { modalDragFrom = null }

// ── Create & attach new card ──────────────────────────────────────────────
const createAndAttach = async () => {
  if (!newCardContent.value.trim()) return
  creating.value = true
  try {
    const res = await api.post('/signature-cards/', { content: newCardContent.value.trim() })
    const newCard = res.data
    catalogue.value.unshift(newCard)
    catalogueTotal.value++
    modalAdd(newCard)
    newCardContent.value = ''
    toast.success('Card created and attached')
  } catch (e) {
    toast.error(e.response?.data?.detail ?? 'Failed to create card')
  } finally { creating.value = false }
}

// ── Save modal: sync meeting's signature cards to modalDraft ──────────────
const saveModal = async () => {
  saving.value = true
  try {
    // 1. Clear all existing links
    await api.delete(`/meetings/${props.meetingId}/signature-cards`)
    // 2. Attach in new order
    for (let i = 0; i < modalDraft.value.length; i++) {
      await api.post(`/meetings/${props.meetingId}/signature-cards`, {
        signature_card_id: modalDraft.value[i],
        order: i + 1,
      })
    }
    toast.success('Signature cards saved')
    await fetchMeetingCards()
    showModal.value = false
  } catch {
    toast.error('Failed to save signature cards')
  } finally { saving.value = false }
}
</script>

<style scoped>
.sig-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 16px;
}

@media (max-width: 480px) {
  .sig-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>