import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { createPortal } from 'react-dom'
import { useEditor, EditorContent, type JSONContent } from '@tiptap/react'
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
import './RichTextEditor.css'

// ── Custom FontSize extension — ported verbatim (logic-for-logic),
// framework-agnostic Tiptap code. Commands are named setCustomFontSize /
// unsetCustomFontSize (rather than the Vue version's setFontSize) because
// the installed @tiptap/extension-text-style now ships its OWN built-in
// `fontSize` command group (added after the Vue app pinned an older
// version) — reusing the name would conflict at the TS type level. The
// stored attribute is still a bare numeric string (e.g. "16"), matching
// the Vue app's format exactly, not the built-in extension's "16px" format.
declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    customFontSize: {
      setCustomFontSize: (size: number) => ReturnType
      unsetCustomFontSize: () => ReturnType
    }
  }
}

const FontSize = Extension.create({
  name: 'customFontSize',
  addOptions() {
    return { types: ['textStyle'] }
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: (el: HTMLElement) => el.style.fontSize?.replace('px', '') || null,
            renderHTML: (a: { fontSize?: string }) => (a.fontSize ? { style: `font-size:${a.fontSize}px` } : {}),
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      setCustomFontSize:
        (size: number) =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: String(size) }).run(),
      unsetCustomFontSize:
        () =>
        ({ chain }) =>
          chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run(),
    }
  },
})

/** Walks up from a DOM node (which may be a text node) to the nearest matching ancestor element. */
function closestAncestor(node: Node, selector: string): Element | null {
  const el = node.nodeType === Node.ELEMENT_NODE ? (node as Element) : node.parentElement
  return el?.closest(selector) ?? null
}

type DropdownName = 'bullet' | 'order' | 'table' | null

interface RichTextEditorProps {
  value?: JSONContent
  editable?: boolean
  minHeight?: string
  onChange?: (value: JSONContent) => void
}

const bulletStyles = [
  { label: '● Disc', value: 'disc' },
  { label: '○ Circle', value: 'circle' },
  { label: '■ Square', value: 'square' },
  { label: '➤ Arrow', value: '"➤"' },
  { label: '✦ Star', value: '"✦"' },
]
const orderStyles = [
  { label: '1. Decimal', value: 'decimal' },
  { label: 'a. Lower alpha', value: 'lower-alpha' },
  { label: 'A. Upper alpha', value: 'upper-alpha' },
  { label: 'i. Lower roman', value: 'lower-roman' },
  { label: 'I. Upper roman', value: 'upper-roman' },
]

export default function RichTextEditor({
  value = {},
  editable = false,
  minHeight = '160px',
  onChange,
}: RichTextEditorProps) {
  // ── Dropdown state ─────────────────────────────────────────────────────────
  const [openDropdown, setOpenDropdown] = useState<DropdownName>(null)
  const [dropdownStyle, setDropdownStyle] = useState<CSSProperties>({})
  const [gridRows, setGridRows] = useState(3)
  const [gridCols, setGridCols] = useState(3)

  const bulletBtnRef = useRef<HTMLButtonElement>(null)
  const orderBtnRef = useRef<HTMLButtonElement>(null)
  const tableBtnRef = useRef<HTMLButtonElement>(null)
  const btnRefs = { bullet: bulletBtnRef, order: orderBtnRef, table: tableBtnRef }

  function toggleDropdown(name: 'bullet' | 'order' | 'table') {
    if (openDropdown === name) {
      setOpenDropdown(null)
      return
    }
    const btn = btnRefs[name].current
    if (!btn) return

    const rect = btn.getBoundingClientRect()
    const ABOVE = 8 // gap above the button
    setDropdownStyle({
      position: 'fixed',
      left: `${rect.left}px`,
      bottom: `${window.innerHeight - rect.top + ABOVE}px`,
      top: 'auto',
      zIndex: 99999,
      minWidth: name === 'table' ? 'auto' : '148px',
    })
    setOpenDropdown(name)
  }
  const closeDropdown = () => setOpenDropdown(null)

  // Close on outside click
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      const btns = [bulletBtnRef.current, orderBtnRef.current, tableBtnRef.current]
      if (btns.some((b) => b && b.contains(e.target as Node))) return
      closeDropdown()
    }
    document.addEventListener('click', onDocClick, true)
    return () => document.removeEventListener('click', onDocClick, true)
  }, [])

  // ── Editor ─────────────────────────────────────────────────────────────────
  const editor = useEditor(
    {
      content: value,
      editable,
      extensions: [
        StarterKit.configure({
          bulletList: { keepMarks: true, keepAttributes: false },
          orderedList: { keepMarks: true, keepAttributes: false },
        }),
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
      onUpdate: ({ editor }) => onChange?.(editor.getJSON()),
    },
    [],
  )

  const currentFontSize = (() => {
    const a = editor?.getAttributes('textStyle')
    return a?.fontSize ? Number(a.fontSize) : 16
  })()

  const setFont = (f: string) => editor?.chain().focus().setFontFamily(f).run()
  const setFontSize = (sz: number) => {
    if (sz >= 8 && sz <= 96) editor?.chain().focus().setCustomFontSize(sz).run()
  }
  const adjustFontSize = (d: number) => setFontSize(currentFontSize + d)

  function applyBulletStyle(style: string) {
    if (!editor) return
    if (!editor.isActive('bulletList')) editor.chain().focus().toggleBulletList().run()
    const { node } = editor.view.domAtPos(editor.view.state.selection.from)
    const ul = closestAncestor(node, 'ul')
    if (ul) (ul as HTMLElement).style.listStyleType = style
    closeDropdown()
  }

  function applyOrderStyle(style: string) {
    if (!editor) return
    if (!editor.isActive('orderedList')) editor.chain().focus().toggleOrderedList().run()
    const { node } = editor.view.domAtPos(editor.view.state.selection.from)
    const ol = closestAncestor(node, 'ol')
    if (ol) (ol as HTMLElement).style.listStyleType = style
    closeDropdown()
  }

  function insertTable(r: number, c: number) {
    editor?.chain().focus().insertTable({ rows: r, cols: c, withHeaderRow: true }).run()
    closeDropdown()
  }

  // Keep the editor's content in sync with a controlled `value` prop without
  // resetting the cursor on every keystroke (guarded by a JSON equality check).
  useEffect(() => {
    if (!editor) return
    if (JSON.stringify(value) !== JSON.stringify(editor.getJSON())) {
      editor.commands.setContent(value, { emitUpdate: false })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, editor])

  useEffect(() => {
    editor?.setEditable(editable)
  }, [editable, editor])

  return (
    <div
      className={['rte-wrapper', editable ? 'rte-editable' : ''].join(' ')}
      style={{ '--rte-min-height': minHeight } as CSSProperties}
    >
      {/* ── TOOLBAR ─────────────────────────────────────────────────────── */}
      {editor && editable && (
        <div className="rte-toolbar">
          {/* Font Family */}
          <div className="rte-group">
            <select className="rte-select" onChange={(e) => setFont(e.target.value)} title="Font family" defaultValue="Kalpurush">
              <option value="Kalpurush">কালপুরুষ</option>
              <option value="SolaimanLipi">SolaimanLipi</option>
              <option value="Georgia">Georgia</option>
              <option value="'Playfair Display'">Playfair</option>
            </select>
          </div>

          {/* Font Size */}
          <div className="rte-group">
            <button className="rte-btn icon-btn" onClick={() => adjustFontSize(-1)} title="Decrease size">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <line x1="2" y1="6" x2="10" y2="6" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
              </svg>
            </button>
            <input
              className="rte-size-input"
              type="number"
              value={currentFontSize}
              min={8}
              max={96}
              onChange={(e) => setFontSize(Number(e.target.value))}
              title="Font size"
            />
            <button className="rte-btn icon-btn" onClick={() => adjustFontSize(1)} title="Increase size">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <line x1="6" y1="2" x2="6" y2="10" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
                <line x1="2" y1="6" x2="10" y2="6" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
              </svg>
            </button>
          </div>

          {/* Bold / Italic / Underline */}
          <div className="rte-group">
            <button
              className={['rte-btn', editor.isActive('bold') ? 'active' : ''].join(' ')}
              title="Bold"
              onClick={() => editor.chain().focus().toggleBold().run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                <path d="M6 4h8a4 4 0 0 1 0 8H6z" />
                <path d="M6 12h9a4 4 0 0 1 0 8H6z" />
              </svg>
            </button>
            <button
              className={['rte-btn', editor.isActive('italic') ? 'active' : ''].join(' ')}
              title="Italic"
              onClick={() => editor.chain().focus().toggleItalic().run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                <line x1="19" y1="4" x2="10" y2="4" />
                <line x1="14" y1="20" x2="5" y2="20" />
                <line x1="15" y1="4" x2="9" y2="20" />
              </svg>
            </button>
            <button
              className={['rte-btn', editor.isActive('underline') ? 'active' : ''].join(' ')}
              title="Underline"
              onClick={() => editor.chain().focus().toggleUnderline().run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                <path d="M6 4v6a6 6 0 0 0 12 0V4" />
                <line x1="4" y1="20" x2="20" y2="20" />
              </svg>
            </button>
          </div>

          {/* Text Alignment */}
          <div className="rte-group">
            <button
              className={['rte-btn', editor.isActive({ textAlign: 'left' }) ? 'active' : ''].join(' ')}
              title="Align left"
              onClick={() => editor.chain().focus().setTextAlign('left').run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="11" x2="15" y2="11" />
                <line x1="3" y1="16" x2="18" y2="16" />
              </svg>
            </button>
            <button
              className={['rte-btn', editor.isActive({ textAlign: 'center' }) ? 'active' : ''].join(' ')}
              title="Center"
              onClick={() => editor.chain().focus().setTextAlign('center').run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="6" y1="11" x2="18" y2="11" />
                <line x1="4" y1="16" x2="20" y2="16" />
              </svg>
            </button>
            <button
              className={['rte-btn', editor.isActive({ textAlign: 'right' }) ? 'active' : ''].join(' ')}
              title="Align right"
              onClick={() => editor.chain().focus().setTextAlign('right').run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="9" y1="11" x2="21" y2="11" />
                <line x1="6" y1="16" x2="21" y2="16" />
              </svg>
            </button>
            <button
              className={['rte-btn', editor.isActive({ textAlign: 'justify' }) ? 'active' : ''].join(' ')}
              title="Justify"
              onClick={() => editor.chain().focus().setTextAlign('justify').run()}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="11" x2="21" y2="11" />
                <line x1="3" y1="16" x2="21" y2="16" />
              </svg>
            </button>
          </div>

          {/* Lists — dropdowns portaled to body to escape overflow clipping */}
          <div className="rte-group">
            {/* Bullet list */}
            <button
              className={['rte-btn', 'split-left', editor.isActive('bulletList') ? 'active' : ''].join(' ')}
              title="Bullet list"
              onClick={() => editor.chain().focus().toggleBulletList().run()}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" strokeLinecap="round">
                <circle cx="4" cy="6" r="1.8" fill="currentColor" />
                <circle cx="4" cy="12" r="1.8" fill="currentColor" />
                <circle cx="4" cy="18" r="1.8" fill="currentColor" />
                <line x1="9" y1="6" x2="21" y2="6" stroke="currentColor" strokeWidth={2} />
                <line x1="9" y1="12" x2="21" y2="12" stroke="currentColor" strokeWidth={2} />
                <line x1="9" y1="18" x2="21" y2="18" stroke="currentColor" strokeWidth={2} />
              </svg>
            </button>
            <button className="rte-btn split-right" title="Bullet style" ref={bulletBtnRef} onClick={() => toggleDropdown('bullet')}>
              <svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor">
                <path d="M0 0l4 6 4-6z" />
              </svg>
            </button>

            {/* Ordered list */}
            <button
              className={['rte-btn', 'split-left', editor.isActive('orderedList') ? 'active' : ''].join(' ')}
              title="Ordered list"
              onClick={() => editor.chain().focus().toggleOrderedList().run()}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" strokeLinecap="round">
                <line x1="10" y1="6" x2="21" y2="6" stroke="currentColor" strokeWidth={2} />
                <line x1="10" y1="12" x2="21" y2="12" stroke="currentColor" strokeWidth={2} />
                <line x1="10" y1="18" x2="21" y2="18" stroke="currentColor" strokeWidth={2} />
                <text x="1.5" y="8.5" fontSize={7.5} fill="currentColor" fontWeight={700} fontFamily="monospace">1</text>
                <text x="1" y="14.5" fontSize={7.5} fill="currentColor" fontWeight={700} fontFamily="monospace">2</text>
                <text x="1" y="20.5" fontSize={7.5} fill="currentColor" fontWeight={700} fontFamily="monospace">3</text>
              </svg>
            </button>
            <button className="rte-btn split-right" title="Number style" ref={orderBtnRef} onClick={() => toggleDropdown('order')}>
              <svg width="8" height="6" viewBox="0 0 8 6" fill="currentColor">
                <path d="M0 0l4 6 4-6z" />
              </svg>
            </button>
          </div>

          {/* Table */}
          <div className="rte-group">
            <button className="rte-btn" style={{ gap: '4px' }} title="Insert table" ref={tableBtnRef} onClick={() => toggleDropdown('table')}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <rect x="3" y="3" width="18" height="18" rx="1" />
                <line x1="3" y1="9" x2="21" y2="9" />
                <line x1="3" y1="15" x2="21" y2="15" />
                <line x1="9" y1="3" x2="9" y2="21" />
                <line x1="15" y1="3" x2="15" y2="21" />
              </svg>
              <span style={{ fontSize: '12px' }}>Table</span>
            </button>

            {editor.isActive('table') && (
              <>
                <button className="rte-btn sm" onClick={() => editor.chain().focus().addColumnBefore().run()} title="Add col left">←C</button>
                <button className="rte-btn sm" onClick={() => editor.chain().focus().addColumnAfter().run()} title="Add col right">C→</button>
                <button className="rte-btn sm" onClick={() => editor.chain().focus().addRowBefore().run()} title="Add row above">↑R</button>
                <button className="rte-btn sm" onClick={() => editor.chain().focus().addRowAfter().run()} title="Add row below">R↓</button>
                <button className="rte-btn sm danger" onClick={() => editor.chain().focus().deleteColumn().run()}>–C</button>
                <button className="rte-btn sm danger" onClick={() => editor.chain().focus().deleteRow().run()}>–R</button>
                <button className="rte-btn sm danger" onClick={() => editor.chain().focus().deleteTable().run()}>✕T</button>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── CONTENT ───────────────────────────────────────────────────── */}
      <EditorContent editor={editor} className="rte-content" />

      {/* ── PORTALED DROPDOWNS — always above everything ────────────────
           Rendered into document.body so no parent overflow:hidden can
           clip them. Position is calculated from the trigger button's
           getBoundingClientRect(). */}
      {openDropdown === 'bullet' &&
        createPortal(
          <div className="rte-float-dropdown" style={dropdownStyle} onMouseLeave={closeDropdown}>
            {bulletStyles.map((s) => (
              <button key={s.value} className="rte-float-item" onClick={() => applyBulletStyle(s.value)}>
                {s.label}
              </button>
            ))}
          </div>,
          document.body,
        )}

      {openDropdown === 'order' &&
        createPortal(
          <div className="rte-float-dropdown" style={dropdownStyle} onMouseLeave={closeDropdown}>
            {orderStyles.map((s) => (
              <button key={s.value} className="rte-float-item" onClick={() => applyOrderStyle(s.value)}>
                {s.label}
              </button>
            ))}
          </div>,
          document.body,
        )}

      {openDropdown === 'table' &&
        createPortal(
          <div className="rte-float-dropdown rte-float-grid" style={dropdownStyle} onMouseLeave={closeDropdown}>
            <p className="grid-label">
              {gridRows} × {gridCols}
            </p>
            <div className="grid-cells">
              {Array.from({ length: 8 }, (_, ri) => ri + 1).map((r) => (
                <div key={`r${r}`} className="grid-row">
                  {Array.from({ length: 8 }, (_, ci) => ci + 1).map((c) => (
                    <div
                      key={`c${c}`}
                      className={['grid-cell', r <= gridRows && c <= gridCols ? 'highlighted' : ''].join(' ')}
                      onMouseOver={() => {
                        setGridRows(r)
                        setGridCols(c)
                      }}
                      onClick={() => insertTable(r, c)}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>,
          document.body,
        )}
    </div>
  )
}
