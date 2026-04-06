<script setup>
import { ref, computed } from 'vue'
import RichTextEditor from './RichTextEditor.vue'
import { Edit3, Save, X, RotateCcw } from 'lucide-vue-next'
import { useToast } from 'vue-toastification'

const props = defineProps({
  label:       { type: String,  required: true },
  description: { type: String,  default: '' },
  modelValue:  { type: Object,  default: () => ({ type: 'doc', content: [] }) },
  canModify:   { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'save'])

const toast        = useToast()
const isEditing    = ref(false)
const draftContent = ref(null)

// ── Dirty check ────────────────────────────────────────────────────────────
const isDirty = computed(() => {
  if (!isEditing.value || draftContent.value === null) return false
  return JSON.stringify(draftContent.value) !== JSON.stringify(props.modelValue)
})

// ── Actions ────────────────────────────────────────────────────────────────
const startEditing = () => {
  // Deep-clone so we never mutate the prop directly
  draftContent.value = JSON.parse(JSON.stringify(props.modelValue ?? { type: 'doc', content: [] }))
  isEditing.value = true
}

const cancelEditing = () => {
  if (isDirty.value) {
    const ok = confirm('You have unsaved changes. Discard them?')
    if (!ok) return
  }
  isEditing.value    = false
  draftContent.value = null
}

const clearContent = () => {
  if (confirm('This will clear all text in this section. Continue?')) {
    draftContent.value = { type: 'doc', content: [] }
  }
}

const saveChanges = () => {
  if (!isDirty.value) {
    toast.info('No changes to save.')
    isEditing.value = false
    return
  }
  // Push the draft up to the parent, then let parent call the API
  emit('update:modelValue', JSON.parse(JSON.stringify(draftContent.value)))
  emit('save')
  isEditing.value    = false
  draftContent.value = null
}
</script>

<template>
  <div class="section-card" :class="{ 'is-dirty': isDirty }">

    <!-- Header row -->
    <div class="flex justify-between items-start mb-4">
      <div>
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="text-lg font-bold text-slate-800">{{ label }}</h3>
          <span
            v-if="isDirty"
            class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full uppercase tracking-wider font-bold"
          >
            Unsaved Changes
          </span>
        </div>
        <p v-if="description" class="text-sm text-slate-500 mt-0.5">{{ description }}</p>
      </div>

      <!-- Action buttons -->
      <div v-if="canModify" class="flex gap-2 shrink-0 ml-4">
        <!-- View mode → pencil -->
        <button v-if="!isEditing" @click="startEditing" class="btn-icon" title="Edit">
          <Edit3 :size="18" />
        </button>

        <!-- Edit mode → clear / save / cancel -->
        <template v-else>
          <button @click="clearContent"  class="btn-icon text-slate-400"               title="Clear all">
            <RotateCcw :size="18" />
          </button>
          <button @click="saveChanges"   class="btn-icon text-green-600 bg-green-50"  title="Save">
            <Save :size="18" />
          </button>
          <button @click="cancelEditing" class="btn-icon text-red-500   bg-red-50"    title="Cancel">
            <X :size="18" />
          </button>
        </template>
      </div>
    </div>

    <!-- Editor: draft while editing, read-only prop value otherwise -->
    <RichTextEditor
      v-if="isEditing"
      v-model="draftContent"
      :editable="true"
    />
    <RichTextEditor
      v-else
      :model-value="modelValue"
      :editable="false"
    />
  </div>
</template>

<style scoped>
@reference "../style.css";

.section-card {
  @apply mb-8 p-6 bg-white rounded-xl border border-slate-200 shadow-sm transition-all duration-200;
}
.is-dirty {
  @apply border-amber-300 ring-2 ring-amber-100;
}
.btn-icon {
  @apply p-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer;
}
</style>