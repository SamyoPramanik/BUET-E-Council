<!-- components/ParticipantCard.vue -->
<script setup>
import { computed, ref } from 'vue'
import { Mail, Check } from 'lucide-vue-next'

const props = defineProps({
  participant: {
    type: Object,
    required: true
  },
  selectable: { type: Boolean, default: false },
  selected:   { type: Boolean, default: false }
})

const emit = defineEmits(['email-click'])

// ── email copy with brief check-mark feedback ─────────────────────────────
const copied = ref(false)
const copyEmail = () => {
  if (!props.participant.email) return
  navigator.clipboard.writeText(props.participant.email)
  copied.value = true
  setTimeout(() => { copied.value = false }, 1800)
}

const hasEmail = computed(() => !!props.participant.email)

// ── split content on first comma (Arabic or Latin) ────────────────────────
const splitContent = computed(() => {
  const text = props.participant.content || ''
  // try Arabic comma first, then Latin
  const idx = text.indexOf('،') !== -1 ? text.indexOf('،') : text.indexOf(',')
  if (idx === -1) return { name: text.trim(), rest: '' }
  return {
    name: text.slice(0, idx).trim(),
    rest: text.slice(idx + 1).trim()
  }
})
</script>

<template>
  <div
    :class="[
      'relative flex flex-col justify-between',
      'rounded-2xl border bg-white transition-all duration-200',
      'p-4 sm:p-5 min-h-[90px]',
      hasEmail
        ? 'border-blue-100 hover:border-blue-300 hover:shadow-md hover:shadow-blue-50'
        : 'border-slate-200 hover:border-slate-300 hover:shadow-sm',
      selectable && selected
        ? 'ring-2 ring-blue-500 ring-offset-2 scale-[1.02] shadow-md'
        : '',
      selectable ? 'cursor-pointer' : ''
    ]"
  >
    <!-- ── top section: name + rest ────────────────────────────────────── -->
    <div class="pr-2">
      <!-- name — first segment before comma -->
      <p class="font-semibold text-slate-900 text-sm leading-snug break-words">
        {{ splitContent.name }}
      </p>

      <!-- rest — everything after first comma -->
      <p
        v-if="splitContent.rest"
        class="mt-1 text-slate-500 text-xs leading-relaxed break-words"
      >
        {{ splitContent.rest }}
      </p>
    </div>

    <!-- ── bottom-left: email icon + tooltip ───────────────────────────── -->
    <div v-if="hasEmail" class="mt-3 flex items-center gap-2">
      <button
        @click.stop="copyEmail"
        :title="participant.email"
        :class="[
          'group/btn flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs',
          'transition-all duration-150',
          copied
            ? 'bg-green-50 text-green-600'
            : 'text-blue-500 hover:bg-blue-50 hover:text-blue-700'
        ]"
      >
        <!-- icon swaps to checkmark on copy -->
        <component
          :is="copied ? Check : Mail"
          :size="13"
          stroke-width="2.2"
          class="shrink-0"
        />
        <!-- truncated email label -->
        <span class="max-w-[120px] truncate hidden sm:inline">
          {{ participant.email }}
        </span>
      </button>
    </div>
  </div>
</template>