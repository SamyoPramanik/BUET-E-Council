import { generateHTML, type JSONContent } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { TextStyle } from '@tiptap/extension-text-style'
import { FontFamily } from '@tiptap/extension-font-family'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { FontSize } from './fontSize'

// Same schema as RichTextEditor's editor instance (minus interaction-only
// concerns) — required so agenda/resolution bodies saved from the editor
// deserialize into identical markup when rendered read-only for print.
const extensions = [
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
]

/** Converts a Tiptap JSON document (as stored for agenda/resolution bodies) into static HTML. */
export function tiptapJsonToHtml(raw: string | null | undefined): string {
  if (!raw) return ''
  let doc: JSONContent
  try {
    doc = typeof raw === 'string' ? JSON.parse(raw) : raw
  } catch {
    return ''
  }
  if (!doc || typeof doc !== 'object' || !doc.content?.length) return ''
  try {
    return generateHTML(doc, extensions)
  } catch {
    return ''
  }
}
