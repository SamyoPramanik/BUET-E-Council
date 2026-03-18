<template>
  <div class="rte-wrapper" :class="{ 'rte-editable': editable }">

    <!-- ── TOOLBAR ── -->
    <div v-if="editor && editable" class="rte-toolbar">

      <!-- Font Family -->
      <div class="rte-group">
        <select class="rte-select" @change="setFont($event.target.value)" title="Font">
          <option value="Kalpurush">কালপুরুষ (বাংলা)</option>
          <option value="SolaimanLipi">SolaimanLipi (বাংলা)</option>
          <option value="Georgia">Georgia (EN)</option>
          <option value="'Playfair Display'">Playfair Display (EN)</option>
        </select>
      </div>

      <!-- Font Size -->
      <div class="rte-group">
        <button class="rte-btn icon-btn" @click="adjustFontSize(-1)" title="Decrease size">−</button>
        <input
          class="rte-size-input"
          type="number"
          :value="currentFontSize"
          min="8" max="96"
          @change="setFontSize(Number($event.target.value))"
          title="Font size"
        />
        <button class="rte-btn icon-btn" @click="adjustFontSize(1)" title="Increase size">+</button>
      </div>

      <!-- Formatting -->
      <div class="rte-group">
        <button class="rte-btn" :class="{ active: editor.isActive('bold') }"
          @click="editor.chain().focus().toggleBold().run()" title="Bold">
          <strong>B</strong>
        </button>
        <button class="rte-btn" :class="{ active: editor.isActive('italic') }"
          @click="editor.chain().focus().toggleItalic().run()" title="Italic">
          <em>I</em>
        </button>
        <button class="rte-btn" :class="{ active: editor.isActive('underline') }"
          @click="editor.chain().focus().toggleUnderline().run()" title="Underline">
          <span style="text-decoration:underline">U</span>
        </button>
      </div>

      <!-- Alignment -->
      <div class="rte-group">
        <button class="rte-btn" :class="{ active: editor.isActive({ textAlign: 'left' }) }"
          @click="editor.chain().focus().setTextAlign('left').run()" title="Align Left">
          <AlignLeftIcon />
        </button>
        <button class="rte-btn" :class="{ active: editor.isActive({ textAlign: 'center' }) }"
          @click="editor.chain().focus().setTextAlign('center').run()" title="Center">
          <AlignCenterIcon />
        </button>
        <button class="rte-btn" :class="{ active: editor.isActive({ textAlign: 'right' }) }"
          @click="editor.chain().focus().setTextAlign('right').run()" title="Align Right">
          <AlignRightIcon />
        </button>
        <button class="rte-btn" :class="{ active: editor.isActive({ textAlign: 'justify' }) }"
          @click="editor.chain().focus().setTextAlign('justify').run()" title="Justify">
          <AlignJustifyIcon />
        </button>
      </div>

      <!-- Lists -->
      <div class="rte-group">
        <!-- Unordered list with bullet style picker -->
        <div class="rte-dropdown-wrap">
          <button class="rte-btn split-left" :class="{ active: editor.isActive('bulletList') }"
            @click="editor.chain().focus().toggleBulletList().run()" title="Bullet List">
            <BulletListIcon />
          </button>
          <button class="rte-btn split-right" @click="showBulletMenu = !showBulletMenu" title="Bullet style">▾</button>
          <div v-if="showBulletMenu" class="rte-dropdown" @mouseleave="showBulletMenu = false">
            <button v-for="s in bulletStyles" :key="s.value" class="rte-drop-item"
              @click="applyBulletStyle(s.value)">
              {{ s.label }}
            </button>
          </div>
        </div>

        <!-- Ordered list with numbering style picker -->
        <div class="rte-dropdown-wrap">
          <button class="rte-btn split-left" :class="{ active: editor.isActive('orderedList') }"
            @click="editor.chain().focus().toggleOrderedList().run()" title="Ordered List">
            <OrderedListIcon />
          </button>
          <button class="rte-btn split-right" @click="showOrderMenu = !showOrderMenu" title="Number style">▾</button>
          <div v-if="showOrderMenu" class="rte-dropdown" @mouseleave="showOrderMenu = false">
            <button v-for="s in orderStyles" :key="s.value" class="rte-drop-item"
              @click="applyOrderStyle(s.value)">
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="rte-group">
        <div class="rte-dropdown-wrap">
          <button class="rte-btn" @click="showTableGrid = !showTableGrid" title="Insert Table">
            <TableIcon /> Table
          </button>
          <!-- Grid picker -->
          <div v-if="showTableGrid" class="rte-table-grid" @mouseleave="showTableGrid = false">
            <p class="grid-label">{{ gridRows }} × {{ gridCols }}</p>
            <div class="grid-cells">
              <div
                v-for="r in 8" :key="'r'+r"
                class="grid-row"
              >
                <div
                  v-for="c in 8" :key="'c'+c"
                  class="grid-cell"
                  :class="{ highlighted: r <= gridRows && c <= gridCols }"
                  @mouseover="gridRows = r; gridCols = c"
                  @click="insertTable(r, c)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Table editing controls (visible when inside a table) -->
        <template v-if="editor.isActive('table')">
          <div class="rte-group">
            <button class="rte-btn sm" @click="editor.chain().focus().addColumnBefore().run()" title="Add col left">←Col</button>
            <button class="rte-btn sm" @click="editor.chain().focus().addColumnAfter().run()" title="Add col right">Col→</button>
            <button class="rte-btn sm" @click="editor.chain().focus().addRowBefore().run()" title="Add row above">↑Row</button>
            <button class="rte-btn sm" @click="editor.chain().focus().addRowAfter().run()" title="Add row below">Row↓</button>
            <button class="rte-btn sm danger" @click="editor.chain().focus().deleteColumn().run()">Del Col</button>
            <button class="rte-btn sm danger" @click="editor.chain().focus().deleteRow().run()">Del Row</button>
            <button class="rte-btn sm danger" @click="editor.chain().focus().deleteTable().run()">Del Table</button>
          </div>
        </template>
      </div>
    </div>

    <!-- ── EDITOR CONTENT ── -->
    <editor-content :editor="editor" class="rte-content" />
  </div>
</template>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import { StarterKit } from '@tiptap/starter-kit'
import { Underline } from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import { FontFamily } from '@tiptap/extension-font-family'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Extension } from '@tiptap/core'
import { watch, onBeforeUnmount, ref, computed } from 'vue'

// ── Simple inline SVG icon components ──────────────────────────────────────
const AlignLeftIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg>` }
const AlignCenterIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>` }
const AlignRightIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg>` }
const AlignJustifyIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>` }
const BulletListIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="20" y2="12"/><line x1="9" y1="18" x2="20" y2="18"/><circle cx="4" cy="6" r="1.5" fill="currentColor" stroke="none"/><circle cx="4" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="4" cy="18" r="1.5" fill="currentColor" stroke="none"/></svg>` }
const OrderedListIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><text x="2" y="8" font-size="7" fill="currentColor" stroke="none">1</text><text x="2" y="14" font-size="7" fill="currentColor" stroke="none">2</text><text x="2" y="20" font-size="7" fill="currentColor" stroke="none">3</text></svg>` }
const TableIcon = { template: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>` }

// ── FontSize Extension (no Pro required) ───────────────────────────────────
const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() { return { types: ['textStyle'] } },
  addGlobalAttributes() {
    return [{
      types: this.options.types,
      attributes: {
        fontSize: {
          default: null,
          parseHTML: el => el.style.fontSize?.replace('px', '') || null,
          renderHTML: attrs => attrs.fontSize ? { style: `font-size: ${attrs.fontSize}px` } : {},
        }
      }
    }]
  },
  addCommands() {
    return {
      setFontSize: size => ({ chain }) =>
        chain().setMark('textStyle', { fontSize: String(size) }).run(),
      unsetFontSize: () => ({ chain }) =>
        chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  }
})

// ── Props / Emits ──────────────────────────────────────────────────────────
const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  editable:   { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

// ── UI state ──────────────────────────────────────────────────────────────
const showBulletMenu = ref(false)
const showOrderMenu  = ref(false)
const showTableGrid  = ref(false)
const gridRows = ref(3)
const gridCols = ref(3)

const bulletStyles = [
  { label: '● Disc',    value: 'disc' },
  { label: '○ Circle',  value: 'circle' },
  { label: '■ Square',  value: 'square' },
  { label: '➤ Arrow',   value: '"➤"' },
  { label: '✦ Star',    value: '"✦"' },
]
const orderStyles = [
  { label: '1. Decimal',       value: 'decimal' },
  { label: 'a. Lower Alpha',   value: 'lower-alpha' },
  { label: 'A. Upper Alpha',   value: 'upper-alpha' },
  { label: 'i. Lower Roman',   value: 'lower-roman' },
  { label: 'I. Upper Roman',   value: 'upper-roman' },
]

// ── Editor ─────────────────────────────────────────────────────────────────
const editor = useEditor({
  content: props.modelValue,
  editable: props.editable,
  extensions: [
    StarterKit.configure({ bulletList: { keepMarks: true }, orderedList: { keepMarks: true } }),
    Underline,
    TextStyle,
    FontFamily,
    FontSize,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Table.configure({ resizable: true }),
    TableRow,
    TableHeader,
    TableCell,
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getJSON())
  },
})

// ── Computed: current font size from selection ─────────────────────────────
const currentFontSize = computed(() => {
  const attrs = editor.value?.getAttributes('textStyle')
  return attrs?.fontSize ? Number(attrs.fontSize) : 16
})

// ── Methods ────────────────────────────────────────────────────────────────
function setFont(font) {
  editor.value.chain().focus().setFontFamily(font).run()
}

function setFontSize(size) {
  if (size >= 8 && size <= 96)
    editor.value.chain().focus().setFontSize(size).run()
}

function adjustFontSize(delta) {
  setFontSize(currentFontSize.value + delta)
}

function applyBulletStyle(style) {
  // Ensure bullet list is active, then apply CSS list-style-type via inline style on the list
  editor.value.chain().focus().toggleBulletList().run()
  // We use a workaround: wrap in a span isn't ideal, instead we inject via CSS custom property
  // For production, consider a custom BulletList extension with 'listStyleType' attr.
  // This sets list-style-type on the nearest ul via DOM (pragmatic approach)
  const { view } = editor.value
  const { from } = view.state.selection
  const domNode = view.domAtPos(from).node
  const ul = domNode.closest?.('ul')
  if (ul) ul.style.listStyleType = style
  showBulletMenu.value = false
}

function applyOrderStyle(style) {
  editor.value.chain().focus().toggleOrderedList().run()
  const { view } = editor.value
  const { from } = view.state.selection
  const domNode = view.domAtPos(from).node
  const ol = domNode.closest?.('ol')
  if (ol) ol.style.listStyleType = style
  showOrderMenu.value = false
}

function insertTable(rows, cols) {
  editor.value.chain().focus().insertTable({ rows, cols, withHeaderRow: true }).run()
  showTableGrid.value = false
}

// ── Watchers ───────────────────────────────────────────────────────────────
watch(() => props.modelValue, (value) => {
  if (!editor.value) return
  const isSame = JSON.stringify(value) === JSON.stringify(editor.value.getJSON())
  if (!isSame) editor.value.commands.setContent(value, false)
})

watch(() => props.editable, (value) => {
  editor.value?.setEditable(value)
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
/* ── Google Fonts for Bangla ── */
@import url('https://fonts.googleapis.com/css2?family=Kalpurush&display=swap');
/* SolaimanLipi needs to be self-hosted or loaded via your asset pipeline */
/* For English: Playfair Display */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Wrapper ── */
.rte-wrapper {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: visible;
  transition: box-shadow 0.2s, border-color 0.2s;
  font-family: 'Kalpurush', Georgia, serif;
  position: relative;
}
.rte-editable {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.25);
}

/* ── Toolbar ── */
.rte-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 10px 10px 0 0;
}

/* ── Button groups ── */
.rte-group {
  display: flex;
  align-items: center;
  border: 1px solid #dde2eb;
  border-radius: 6px;
  overflow: visible;
  background: #fff;
}

.rte-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 8px;
  font-size: 13px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #374151;
  border-right: 1px solid #e5e7eb;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.rte-btn:last-child { border-right: none; }
.rte-btn:hover { background: #f1f5f9; }
.rte-btn.active { background: #dbeafe; color: #1d4ed8; }
.rte-btn.icon-btn { padding: 4px 7px; font-weight: bold; }
.rte-btn.sm { font-size: 11px; padding: 3px 6px; }
.rte-btn.danger { color: #dc2626; }
.rte-btn.danger:hover { background: #fee2e2; }

/* split button (list with dropdown arrow) */
.split-left  { border-radius: 0; border-right: 1px solid #e5e7eb; }
.split-right { padding: 4px 4px; border-right: none; font-size: 10px; }

/* ── Font select ── */
.rte-select {
  padding: 3px 6px;
  font-size: 12px;
  border: none;
  outline: none;
  background: transparent;
  cursor: pointer;
  color: #374151;
  max-width: 160px;
}

/* ── Font size input ── */
.rte-size-input {
  width: 42px;
  text-align: center;
  font-size: 13px;
  border: none;
  outline: none;
  background: transparent;
  color: #374151;
  -moz-appearance: textfield;
}
.rte-size-input::-webkit-outer-spin-button,
.rte-size-input::-webkit-inner-spin-button { -webkit-appearance: none; }

/* ── Dropdown ── */
.rte-dropdown-wrap {
  position: relative;
  display: flex;
  align-items: stretch;
}
.rte-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  min-width: 150px;
  overflow: hidden;
}
.rte-drop-item {
  display: block;
  width: 100%;
  padding: 7px 14px;
  font-size: 13px;
  text-align: left;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #374151;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.1s;
}
.rte-drop-item:last-child { border-bottom: none; }
.rte-drop-item:hover { background: #f0f9ff; }

/* ── Table grid picker ── */
.rte-table-grid {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.grid-label {
  font-size: 11px;
  text-align: center;
  color: #64748b;
  margin: 0 0 6px;
}
.grid-cells { display: flex; flex-direction: column; gap: 2px; }
.grid-row   { display: flex; gap: 2px; }
.grid-cell  {
  width: 18px; height: 18px;
  border: 1px solid #cbd5e1;
  border-radius: 2px;
  cursor: pointer;
  background: #f8fafc;
  transition: background 0.1s, border-color 0.1s;
}
.grid-cell.highlighted {
  background: #bfdbfe;
  border-color: #3b82f6;
}

/* ── Content area ── */
.rte-content :deep(.tiptap) {
  min-height: 150px;
  padding: 16px 20px;
  outline: none;
  font-size: 16px;
  line-height: 1.8;
  color: #1e293b;
}
.rte-content :deep(.tiptap p)  { margin: 0 0 0.75em; }
.rte-content :deep(.tiptap ul) { padding-left: 1.5em; margin: 0.5em 0; }
.rte-content :deep(.tiptap ol) { padding-left: 1.5em; margin: 0.5em 0; }
.rte-content :deep(.tiptap li) { margin-bottom: 0.2em; }

/* ── Table styles ── */
.rte-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  table-layout: fixed;
}
.rte-content :deep(th),
.rte-content :deep(td) {
  border: 1px solid #cbd5e1;
  padding: 8px 12px;
  min-width: 80px;
  vertical-align: top;
  position: relative;
}
.rte-content :deep(th) {
  background: #f1f5f9;
  font-weight: 600;
}
/* Resize handle */
.rte-content :deep(.column-resize-handle) {
  position: absolute;
  right: -2px;
  top: 0; bottom: 0;
  width: 4px;
  background: #93c5fd;
  cursor: col-resize;
  z-index: 10;
}
/* Selected cell highlight */
.rte-content :deep(.selectedCell) {
  background: #eff6ff;
}
</style>