<!-- components/SignatureCardItem.vue -->
<!--
  Displays one signature card as a visual block that mirrors
  how it appears at the bottom of official meeting minutes:

      ─────────────────────
      (Name)
      Title line 1
      ও
      Title line 2
      ─────────────────────

  Props:
    card        — SignatureCard object { id, content, created_at }
    removable   — show the × remove button (staff/admin only)
    draggable   — show drag grip (for reorder UX)
    isDragging  — faded style when this card is being dragged

  Emits:
    remove(cardId)
-->
<template>
  <div
    class="sig-card"
    :class="{
      'sig-card--dragging': isDragging,
      'sig-card--removable': removable,
    }"
  >
    <!-- Drag grip -->
    <div v-if="draggable" class="sig-card__grip" title="Drag to reorder">
      <GripVertical :size="14" class="text-slate-300 group-hover:text-slate-500 transition-colors" />
    </div>

    <!-- Signature line (decorative) -->
    <div class="sig-card__line-wrap">
      <div class="sig-card__sig-area">
        <div class="sig-card__blank-line" />
      </div>
    </div>

    <!-- Content: multi-line, each \n becomes its own line -->
    <div class="sig-card__content">
      <span
        v-for="(line, i) in lines"
        :key="i"
        class="sig-card__line"
        :class="{
          'sig-card__line--name':  i === 0,
          'sig-card__line--joiner': line.trim() === 'ও' || line.trim() === 'and',
        }"
      >{{ line }}</span>
    </div>

    <!-- Remove button -->
    <button
      v-if="removable"
      @click.stop="$emit('remove', card.id)"
      class="sig-card__remove"
      title="Remove from meeting"
    >
      <X :size="13" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { GripVertical, X } from 'lucide-vue-next'

const props = defineProps({
  card:       { type: Object,  required: true },
  removable:  { type: Boolean, default: false },
  draggable:  { type: Boolean, default: false },
  isDragging: { type: Boolean, default: false },
})

defineEmits(['remove'])

const lines = computed(() =>
  (props.card.content || '').split('\n').map(l => l.trim()).filter(Boolean)
)
</script>

<style scoped>
.sig-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 20px 14px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  transition: box-shadow .15s, opacity .15s;
  min-width: 180px;
  text-align: center;
}
.sig-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,.07); }

.sig-card--dragging { opacity: .35; }

/* Drag grip — top-left corner */
.sig-card__grip {
  position: absolute;
  top: 8px;
  left: 8px;
  cursor: grab;
  display: flex;
  align-items: center;
}
.sig-card__grip:active { cursor: grabbing; }

/* Remove button — top-right */
.sig-card__remove {
  position: absolute;
  top: 7px;
  right: 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  border: 1px solid #fecaca;
  background: #fff;
  color: #ef4444;
  cursor: pointer;
  opacity: 0;
  transition: opacity .12s, background .12s;
}
.sig-card:hover .sig-card__remove,
.sig-card--removable .sig-card__remove { opacity: 1; }
.sig-card__remove:hover { background: #fee2e2; }

/* Signature blank area */
.sig-card__line-wrap {
  width: 100%;
}
.sig-card__sig-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 36px;
  justify-content: flex-end;
}
.sig-card__blank-line {
  width: 80%;
  height: 1px;
  background: #94a3b8;
  margin-top: 6px;
}

/* Text content */
.sig-card__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  width: 100%;
}
.sig-card__line {
  display: block;
  font-size: 12px;
  color: #475569;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.sig-card__line--name {
  font-weight: 700;
  font-size: 12.5px;
  color: #1e293b;
}
.sig-card__line--joiner {
  font-size: 11px;
  color: #94a3b8;
}
</style>