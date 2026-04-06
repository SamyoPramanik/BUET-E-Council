<!-- components/RichTextEditor.vue -->
<template>
  <div class="rte-wrapper" :class="{ 'rte-editable': editable }" ref="wrapperRef">

    <!-- ── TOOLBAR ─────────────────────────────────────────────────────── -->
    <div v-if="editor && editable" class="rte-toolbar" ref="toolbarRef">

      <!-- Font Family -->
      <div class="rte-group">
        <select class="rte-select" @change="setFont($event.target.value)" title="Font family">
          <option value="Kalpurush">কালপুরুষ</option>
          <option value="SolaimanLipi">SolaimanLipi</option>
          <option value="Georgia">Georgia</option>
          <option value="'Playfair Display'">Playfair</option>
        </select>
      </div>

      <!-- Font Size -->
      <div class="rte-group">
        <button class="rte-btn icon-btn" @click="adjustFontSize(-1)" title="Decrease size">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <line x1="2" y1="6" x2="10" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <input class="rte-size-input" type="number" :value="currentFontSize"
          min="8" max="96" @change="setFontSize(Number($event.target.value))" title="Font size" />
        <button class="rte-btn icon-btn" @click="adjustFontSize(1)" title="Increase size">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <line x1="6" y1="2" x2="6" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="2" y1="6" x2="10" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <!-- Bold / Italic / Underline -->
      <div class="rte-group">
        <button class="rte-btn" title="Bold" :class="{ active: editor.isActive('bold') }"
          @click="editor.chain().focus().toggleBold().run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M6 4h8a4 4 0 0 1 0 8H6z"/><path d="M6 12h9a4 4 0 0 1 0 8H6z"/>
          </svg>
        </button>
        <button class="rte-btn" title="Italic" :class="{ active: editor.isActive('italic') }"
          @click="editor.chain().focus().toggleItalic().run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/>
            <line x1="15" y1="4" x2="9" y2="20"/>
          </svg>
        </button>
        <button class="rte-btn" title="Underline" :class="{ active: editor.isActive('underline') }"
          @click="editor.chain().focus().toggleUnderline().run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <path d="M6 4v6a6 6 0 0 0 12 0V4"/>
            <line x1="4" y1="20" x2="20" y2="20"/>
          </svg>
        </button>
      </div>

      <!-- Text Alignment -->
      <div class="rte-group">
        <button class="rte-btn" title="Align left"
          :class="{ active: editor.isActive({ textAlign: 'left' }) }"
          @click="editor.chain().focus().setTextAlign('left').run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="11" x2="15" y2="11"/><line x1="3" y1="16" x2="18" y2="16"/>
          </svg>
        </button>
        <button class="rte-btn" title="Center"
          :class="{ active: editor.isActive({ textAlign: 'center' }) }"
          @click="editor.chain().focus().setTextAlign('center').run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="11" x2="18" y2="11"/><line x1="4" y1="16" x2="20" y2="16"/>
          </svg>
        </button>
        <button class="rte-btn" title="Align right"
          :class="{ active: editor.isActive({ textAlign: 'right' }) }"
          @click="editor.chain().focus().setTextAlign('right').run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="11" x2="21" y2="11"/><line x1="6" y1="16" x2="21" y2="16"/>
          </svg>
        </button>
        <button class="rte-btn" title="Justify"
          :class="{ active: editor.isActive({ textAlign: 'justify' }) }"
          @click="editor.chain().focus().setTextAlign('justify').run()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="11" x2="21" y2="11"/><line x1="3" y1="16" x2="21" y2="16"/>
          </svg>
        </button>
      </div>

      <!-- Lists — dropdowns teleported to body to escape overflow clipping -->
      <div class="rte-group">
        <!-- Bullet list -->
        <button class="rte-btn split-left" title="Bullet list"
          :class="{ active: editor.isActive('bulletList') }"
          @click="editor.chain().focus().toggleBulletList().run()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-linecap="round">
            <circle cx="4" cy="6" r="1.8" fill="currentColor"/>
            <circle cx="4" cy="12" r="1.8" fill="currentColor"/>
            <circle cx="4" cy="18" r="1.8" fill="currentColor"/>
            <line x1="9" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button class="rte-btn split-right" title="Bullet style"
          ref="bulletBtnRef"
          @click="toggleDropdown('bullet')">
          <svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor"><path d="M0 0l4 6 4-6z"/></svg>
        </button>

        <!-- Ordered list -->
        <button class="rte-btn split-left" title="Ordered list"
          :class="{ active: editor.isActive('orderedList') }"
          @click="editor.chain().focus().toggleOrderedList().run()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-linecap="round">
            <line x1="10" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
            <line x1="10" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
            <line x1="10" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
            <text x="1.5" y="8.5" font-size="7.5" fill="currentColor" font-weight="700" font-family="monospace">1</text>
            <text x="1" y="14.5" font-size="7.5" fill="currentColor" font-weight="700" font-family="monospace">2</text>
            <text x="1" y="20.5" font-size="7.5" fill="currentColor" font-weight="700" font-family="monospace">3</text>
          </svg>
        </button>
        <button class="rte-btn split-right" title="Number style"
          ref="orderBtnRef"
          @click="toggleDropdown('order')">
          <svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor"><path d="M0 0l4 6 4-6z"/></svg>
        </button>
      </div>

      <!-- Table -->
      <div class="rte-group">
        <button class="rte-btn" style="gap:4px" title="Insert table"
          ref="tableBtnRef"
          @click="toggleDropdown('table')">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="1"/>
            <line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/>
            <line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/>
          </svg>
          <span style="font-size:12px">Table</span>
        </button>

        <template v-if="editor.isActive('table')">
          <button class="rte-btn sm" @click="editor.chain().focus().addColumnBefore().run()" title="Add col left">←C</button>
          <button class="rte-btn sm" @click="editor.chain().focus().addColumnAfter().run()" title="Add col right">C→</button>
          <button class="rte-btn sm" @click="editor.chain().focus().addRowBefore().run()" title="Add row above">↑R</button>
          <button class="rte-btn sm" @click="editor.chain().focus().addRowAfter().run()" title="Add row below">R↓</button>
          <button class="rte-btn sm danger" @click="editor.chain().focus().deleteColumn().run()">–C</button>
          <button class="rte-btn sm danger" @click="editor.chain().focus().deleteRow().run()">–R</button>
          <button class="rte-btn sm danger" @click="editor.chain().focus().deleteTable().run()">✕T</button>
        </template>
      </div>

    </div><!-- /toolbar -->

    <!-- ── CONTENT ───────────────────────────────────────────────────── -->
    <editor-content :editor="editor" class="rte-content" />

    <!-- ── TELEPORTED DROPDOWNS — always above everything ──────────────
         Using Teleport to <body> so no parent overflow:hidden can clip them.
         Position is calculated in JS based on the trigger button's getBoundingClientRect.
    ─────────────────────────────────────────────────────────────────── -->
    <Teleport to="body">
      <!-- Bullet style dropdown -->
      <div v-if="openDropdown === 'bullet'" class="rte-float-dropdown"
        :style="dropdownStyle"
        @mouseleave="closeDropdown">
        <button v-for="s in bulletStyles" :key="s.value" class="rte-float-item"
          @click="applyBulletStyle(s.value)">{{ s.label }}</button>
      </div>

      <!-- Order style dropdown -->
      <div v-if="openDropdown === 'order'" class="rte-float-dropdown"
        :style="dropdownStyle"
        @mouseleave="closeDropdown">
        <button v-for="s in orderStyles" :key="s.value" class="rte-float-item"
          @click="applyOrderStyle(s.value)">{{ s.label }}</button>
      </div>

      <!-- Table grid picker -->
      <div v-if="openDropdown === 'table'" class="rte-float-dropdown rte-float-grid"
        :style="dropdownStyle"
        @mouseleave="closeDropdown">
        <p class="grid-label">{{ gridRows }} × {{ gridCols }}</p>
        <div class="grid-cells">
          <div v-for="r in 8" :key="'r'+r" class="grid-row">
            <div v-for="c in 8" :key="'c'+c" class="grid-cell"
              :class="{ highlighted: r <= gridRows && c <= gridCols }"
              @mouseover="gridRows=r; gridCols=c"
              @click="insertTable(r,c)" />
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import { FontFamily } from '@tiptap/extension-font-family'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Extension } from '@tiptap/core'
import { watch, onBeforeUnmount, onMounted, ref, computed } from 'vue'

// ── Custom FontSize extension ──────────────────────────────────────────────
const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() { return { types: ['textStyle'] } },
  addGlobalAttributes() {
    return [{
      types: this.options.types,
      attributes: {
        fontSize: {
          default: null,
          parseHTML: el => el.style.fontSize?.replace('px','') || null,
          renderHTML: a => a.fontSize ? { style: `font-size:${a.fontSize}px` } : {},
        }
      }
    }]
  },
  addCommands() {
    return {
      setFontSize:   size => ({ chain }) => chain().setMark('textStyle', { fontSize: String(size) }).run(),
      unsetFontSize: ()   => ({ chain }) => chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  }
})

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  editable:   { type: Boolean, default: false },
  minHeight:  { type: String,  default: '160px' },
})
const emit = defineEmits(['update:modelValue'])

// ── Dropdown state ─────────────────────────────────────────────────────────
const openDropdown  = ref(null)   // 'bullet' | 'order' | 'table' | null
const dropdownStyle = ref({})
const bulletBtnRef  = ref(null)
const orderBtnRef   = ref(null)
const tableBtnRef   = ref(null)
const gridRows      = ref(3)
const gridCols      = ref(3)

const btnRefs = { bullet: bulletBtnRef, order: orderBtnRef, table: tableBtnRef }

function toggleDropdown(name) {
  if (openDropdown.value === name) { openDropdown.value = null; return }

  const btn = btnRefs[name]?.value
  if (!btn) return

  const rect  = btn.getBoundingClientRect()
  const ABOVE = 8   // gap above the button
  // We'll position the dropdown so it opens ABOVE the button.
  // We don't know height yet, so we anchor to bottom edge of button and translate up.
  dropdownStyle.value = {
    position:  'fixed',
    left:      `${rect.left}px`,
    // Place bottom of dropdown at top of button
    bottom:    `${window.innerHeight - rect.top + ABOVE}px`,
    top:       'auto',
    zIndex:    '99999',
    minWidth:  name === 'table' ? 'auto' : '148px',
  }
  openDropdown.value = name
}

function closeDropdown() { openDropdown.value = null }

// Close on outside click
function onDocClick(e) {
  const btns = [bulletBtnRef.value, orderBtnRef.value, tableBtnRef.value]
  if (btns.some(b => b && b.contains(e.target))) return
  closeDropdown()
}
onMounted(() => document.addEventListener('click', onDocClick, true))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick, true))

// ── Styles data ────────────────────────────────────────────────────────────
const bulletStyles = [
  { label: '● Disc',   value: 'disc'   },
  { label: '○ Circle', value: 'circle' },
  { label: '■ Square', value: 'square' },
  { label: '➤ Arrow',  value: '"➤"'   },
  { label: '✦ Star',   value: '"✦"'   },
]
const orderStyles = [
  { label: '1. Decimal',     value: 'decimal'     },
  { label: 'a. Lower alpha', value: 'lower-alpha' },
  { label: 'A. Upper alpha', value: 'upper-alpha' },
  { label: 'i. Lower roman', value: 'lower-roman' },
  { label: 'I. Upper roman', value: 'upper-roman' },
]

// ── Editor ─────────────────────────────────────────────────────────────────
const editor = useEditor({
  content: props.modelValue,
  editable: props.editable,
  extensions: [
    StarterKit.configure({
      bulletList:  { keepMarks: true, keepAttributes: false },
      orderedList: { keepMarks: true, keepAttributes: false },
    }),
    Underline, TextStyle, FontFamily, FontSize,
    TextAlign.configure({ types: ['heading','paragraph'] }),
    Table.configure({ resizable: true }),
    TableRow, TableHeader, TableCell,
  ],
  onUpdate: ({ editor }) => emit('update:modelValue', editor.getJSON()),
})

const currentFontSize = computed(() => {
  const a = editor.value?.getAttributes('textStyle')
  return a?.fontSize ? Number(a.fontSize) : 16
})

const setFont      = f  => editor.value?.chain().focus().setFontFamily(f).run()
const setFontSize  = sz => { if (sz >= 8 && sz <= 96) editor.value?.chain().focus().setFontSize(sz).run() }
const adjustFontSize = d => setFontSize(currentFontSize.value + d)

function applyBulletStyle(style) {
  if (!editor.value.isActive('bulletList'))
    editor.value.chain().focus().toggleBulletList().run()
  const n  = editor.value.view.domAtPos(editor.value.view.state.selection.from).node
  const ul = n.closest?.('ul')
  if (ul) ul.style.listStyleType = style
  closeDropdown()
}

function applyOrderStyle(style) {
  if (!editor.value.isActive('orderedList'))
    editor.value.chain().focus().toggleOrderedList().run()
  const n  = editor.value.view.domAtPos(editor.value.view.state.selection.from).node
  const ol = n.closest?.('ol')
  if (ol) ol.style.listStyleType = style
  closeDropdown()
}

function insertTable(r, c) {
  editor.value.chain().focus().insertTable({ rows: r, cols: c, withHeaderRow: true }).run()
  closeDropdown()
}

watch(() => props.modelValue, val => {
  if (!editor.value) return
  if (JSON.stringify(val) !== JSON.stringify(editor.value.getJSON()))
    editor.value.commands.setContent(val, false)
})
watch(() => props.editable, val => editor.value?.setEditable(val))
onBeforeUnmount(() => editor.value?.destroy())
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Kalpurush&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

.rte-wrapper {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  transition: box-shadow .2s, border-color .2s;
  position: relative;
  /* No overflow:hidden here — that's what was clipping dropdowns */
}
.rte-editable {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(147,197,253,.2);
}

.rte-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
  overflow-x: auto;
  overflow-y: visible;
  scrollbar-width: thin;
}

.rte-group {
  display: flex;
  align-items: center;
  border: 1px solid #dde2eb;
  border-radius: 7px;
  background: #fff;
  flex-shrink: 0;
}

.rte-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 8px;
  min-width: 30px;
  min-height: 30px;
  font-size: 13px;
  background: transparent;
  border: none;
  border-right: 1px solid #e5e7eb;
  cursor: pointer;
  color: #374151;
  transition: background .12s, color .12s;
  white-space: nowrap;
  line-height: 1;
  flex-shrink: 0;
}
.rte-btn:last-child { border-right: none; }
.rte-btn:hover  { background: #f1f5f9; }
.rte-btn.active { background: #dbeafe; color: #1d4ed8; }
.rte-btn.icon-btn { padding: 5px 7px; }
.rte-btn.sm { font-size: 11px; padding: 3px 5px; min-width: auto; }
.rte-btn.danger       { color: #dc2626; }
.rte-btn.danger:hover { background: #fee2e2; }

.split-left  { border-radius: 6px 0 0 6px; border-right: 1px solid #e5e7eb; }
.split-right { padding: 5px 6px; border-right: none; border-radius: 0 6px 6px 0; }

.rte-select {
  padding: 4px 6px; font-size: 12px; border: none; outline: none;
  background: transparent; cursor: pointer; color: #374151; max-width: 120px;
}

.rte-size-input {
  width: 36px; text-align: center; font-size: 13px;
  border: none; outline: none; background: transparent; color: #374151;
  -moz-appearance: textfield;
}
.rte-size-input::-webkit-inner-spin-button,
.rte-size-input::-webkit-outer-spin-button { -webkit-appearance: none; }

/* Editor content */
.rte-content :deep(.tiptap) {
  min-height: v-bind(minHeight);
  padding: 14px 18px;
  outline: none;
  font-size: 15px;
  line-height: 1.85;
  color: #1e293b;
  font-family: 'Kalpurush', Georgia, serif;
}
.rte-content :deep(.tiptap p)  { margin: 0 0 .6em; }
.rte-content :deep(.tiptap ul) { padding-left: 1.6em; margin: .4em 0; list-style-type: disc; }
.rte-content :deep(.tiptap ol) { padding-left: 1.6em; margin: .4em 0; list-style-type: decimal; }
.rte-content :deep(.tiptap li) { margin-bottom: .15em; display: list-item; }

.rte-content :deep(table) {
  border-collapse: collapse; width: 100%; margin: 1em 0; table-layout: fixed;
}
.rte-content :deep(th),
.rte-content :deep(td) {
  border: 1px solid #cbd5e1; padding: 7px 11px;
  min-width: 60px; vertical-align: top; position: relative;
}
.rte-content :deep(th) { background: #f1f5f9; font-weight: 600; }
.rte-content :deep(.column-resize-handle) {
  position: absolute; right: -2px; top: 0; bottom: 0;
  width: 4px; background: #93c5fd; cursor: col-resize; z-index: 10;
}
.rte-content :deep(.selectedCell) { background: #eff6ff; }
</style>

<!-- Global styles for the teleported dropdowns (must NOT be scoped) -->
<style>
.rte-float-dropdown {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 -4px 20px rgba(0,0,0,.12), 0 4px 20px rgba(0,0,0,.08);
  overflow: hidden;
  min-width: 148px;
}

.rte-float-item {
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
  transition: background .1s;
}
.rte-float-item:last-child { border-bottom: none; }
.rte-float-item:hover { background: #eff6ff; color: #1d4ed8; }

.rte-float-grid {
  padding: 10px;
  min-width: auto !important;
}
.rte-float-grid .grid-label {
  font-size: 11px; text-align: center; color: #64748b; margin: 0 0 6px;
}
.rte-float-grid .grid-cells { display: flex; flex-direction: column; gap: 2px; }
.rte-float-grid .grid-row   { display: flex; gap: 2px; }
.rte-float-grid .grid-cell  {
  width: 18px; height: 18px; border: 1px solid #cbd5e1;
  border-radius: 2px; cursor: pointer; background: #f8fafc;
  transition: background .08s, border-color .08s;
}
.rte-float-grid .grid-cell.highlighted { background: #bfdbfe; border-color: #3b82f6; }
</style>