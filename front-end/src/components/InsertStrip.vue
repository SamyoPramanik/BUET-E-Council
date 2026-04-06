<!-- components/InsertStrip.vue -->
<!--
  Notebook-style insert strip between agenda items.
  Hover to reveal two buttons:
    "New Agenda"              → emit add-regular
    "New Agenda from template" → toast "coming soon" (feature not yet available)
-->
<template>
  <div
    class="insert-strip"
    :class="{ 'is-hovered': hovered, 'is-disabled': disabled }"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
  >
    <div class="strip-line" />

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="hovered && !disabled" class="strip-btns">
        <!-- New Agenda -->
        <button
          class="strip-btn regular"
          title="Insert a new blank agenda item here"
          @click.stop="$emit('add-regular')"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <line x1="5" y1="1" x2="5" y2="9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="1" y1="5" x2="9" y2="5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          New Agenda
        </button>

        <!-- New Agenda from Template — coming soon -->
        <button
          class="strip-btn template"
          title="Create agenda from template (coming soon)"
          @click.stop="onTemplate"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <rect x="1" y="1" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
            <line x1="3" y1="3.5" x2="7" y2="3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="3" y1="5"   x2="7" y2="5"   stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="3" y1="6.5" x2="5.5" y2="6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          From Template
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'

defineProps({
  disabled: { type: Boolean, default: false },
})
defineEmits(['add-regular'])

const hovered = ref(false)
const toast   = useToast()

function onTemplate() {
  toast.info('Agenda templates are coming soon!')
}
</script>

<style scoped>
.insert-strip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
  margin: 0;
  cursor: default;
  z-index: 10;
}

.strip-line {
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  border-radius: 2px;
  background: transparent;
  transition: background .15s;
}
.insert-strip.is-hovered .strip-line {
  background: linear-gradient(90deg, transparent 0%, #bfdbfe 20%, #bfdbfe 80%, transparent 100%);
}

.strip-btns {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 1;
  background: #f8fafc;
  padding: 0 8px;
}

.strip-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 11px 3px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border: 1.5px solid;
  transition: all .12s;
  white-space: nowrap;
  line-height: 1.4;
}

.strip-btn.regular {
  background: #fff;
  border-color: #93c5fd;
  color: #2563eb;
}
.strip-btn.regular:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  box-shadow: 0 1px 6px rgba(59,130,246,.15);
}

.strip-btn.template {
  background: #fff;
  border-color: #d1d5db;
  color: #6b7280;
}
.strip-btn.template:hover {
  background: #f9fafb;
  border-color: #9ca3af;
  box-shadow: 0 1px 6px rgba(0,0,0,.08);
}

.insert-strip.is-disabled {
  pointer-events: none;
  opacity: .4;
}
</style>