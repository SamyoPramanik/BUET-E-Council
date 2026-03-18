<script setup>
import { ref, computed } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import { Download, X, ZoomIn, ZoomOut } from 'lucide-vue-next' // Using your icon library

const props = defineProps({
  agendaSource: { type: String, required: true },
  resolutionSource: { type: String, required: true },
  isOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const activeTab = ref('agenda') // 'agenda' or 'resolution'
const scale = ref(1.0)

// Determine which PDF to show based on the active tab
const currentSource = computed(() => {
  return activeTab.value === 'agenda' ? props.agendaSource : props.resolutionSource
})

const zoomIn = () => { scale.value += 0.1 }
const zoomOut = () => { if (scale.value > 0.5) scale.value -= 0.1 }
</script>

<template>
  <div 
    v-if="isOpen"
    class="pdf-sidebar-container shadow-2xl border-l bg-slate-100 flex flex-col"
  >
    <div class="flex flex-col shrink-0 bg-slate-800">
      <div class="flex w-full h-10 border-b border-slate-700">
        <button 
          @click="activeTab = 'agenda'"
          :class="['flex-1 text-xs font-semibold uppercase tracking-wider transition-colors', 
                   activeTab === 'agenda' ? 'bg-slate-700 text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:bg-slate-700']"
        >
          Agenda
        </button>
        <button 
          @click="activeTab = 'resolution'"
          :class="['flex-1 text-xs font-semibold uppercase tracking-wider transition-colors', 
                   activeTab === 'resolution' ? 'bg-slate-700 text-blue-400 border-b-2 border-blue-400' : 'text-slate-400 hover:bg-slate-700']"
        >
          Resolution
        </button>
      </div>

      <div class="h-10 flex items-center justify-between px-3">
        <div class="flex items-center space-x-2">
          <button @click="zoomOut" class="p-1 hover:bg-slate-700 rounded text-slate-300"><ZoomOut :size="16"/></button>
          <span class="text-[10px] text-slate-400 w-8 text-center">{{ Math.round(scale * 100) }}%</span>
          <button @click="zoomIn" class="p-1 hover:bg-slate-700 rounded text-slate-300"><ZoomIn :size="16"/></button>
        </div>

        <div class="flex items-center space-x-2">
          <button class="p-1 hover:bg-slate-700 rounded text-slate-300" title="Download"><Download :size="16"/></button>
          <button @click="$emit('close')" class="p-1 hover:bg-red-500 rounded text-white transition"><X :size="16"/></button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-4 bg-slate-200 flex justify-center">
      <div :style="{ width: (scale * 100) + '%' }" class="transition-all duration-200">
        <vue-pdf-embed 
          :key="activeTab" 
          :source="currentSource" 
          class="shadow-xl bg-white"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "../style.css";

.pdf-sidebar-container {
  position: fixed;
  right: 0;
  top: 0;
  height: 100vh;
  width: 100%; /* Default for mobile */
  z-index: 1050;
  transition: transform 0.3s ease-in-out;
}

/* On Desktop, make it a side panel (e.g., 40% of the screen) */
@media (min-width: 1024px) {
  .pdf-sidebar-container {
    width: 45vw; 
  }
}

/* Custom Scrollbar for a cleaner look */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-slate-400 rounded;
}
</style>