import { useState } from 'react'
import { toast } from 'react-toastify'
import type { JSONContent } from '@tiptap/react'
import RichTextEditor from './RichTextEditor'
import { Edit3, Save, X, RotateCcw } from 'lucide-react'
import './MeetingSection.css'

const EMPTY_DOC: JSONContent = { type: 'doc', content: [] }

interface MeetingSectionProps {
  label: string
  description?: string
  value?: JSONContent
  canModify?: boolean
  onChange: (value: JSONContent) => void
  onSave: () => void
}

export default function MeetingSection({
  label,
  description = '',
  value = EMPTY_DOC,
  canModify = false,
  onChange,
  onSave,
}: MeetingSectionProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [draftContent, setDraftContent] = useState<JSONContent | null>(null)

  // ── Dirty check ────────────────────────────────────────────────────────────
  const isDirty = isEditing && draftContent !== null && JSON.stringify(draftContent) !== JSON.stringify(value)

  // ── Actions ────────────────────────────────────────────────────────────────
  const startEditing = () => {
    // Deep-clone so we never mutate the prop directly
    setDraftContent(JSON.parse(JSON.stringify(value ?? EMPTY_DOC)))
    setIsEditing(true)
  }

  const cancelEditing = () => {
    if (isDirty) {
      const ok = confirm('You have unsaved changes. Discard them?')
      if (!ok) return
    }
    setIsEditing(false)
    setDraftContent(null)
  }

  const clearContent = () => {
    if (confirm('This will clear all text in this section. Continue?')) {
      setDraftContent({ type: 'doc', content: [] })
    }
  }

  const saveChanges = () => {
    if (!isDirty) {
      toast.info('No changes to save.')
      setIsEditing(false)
      return
    }
    // Push the draft up to the parent, then let parent call the API
    onChange(JSON.parse(JSON.stringify(draftContent)))
    onSave()
    setIsEditing(false)
    setDraftContent(null)
  }

  return (
    <div className={['section-card', isDirty ? 'is-dirty' : ''].join(' ')}>
      {/* Header row */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-bold text-slate-800">{label}</h3>
            {isDirty && (
              <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full uppercase tracking-wider font-bold">
                Unsaved Changes
              </span>
            )}
          </div>
          {description && <p className="text-sm text-slate-500 mt-0.5">{description}</p>}
        </div>

        {/* Action buttons */}
        {canModify && (
          <div className="flex gap-2 shrink-0 ml-4">
            {!isEditing ? (
              <button onClick={startEditing} className="btn-icon" title="Edit">
                <Edit3 size={18} />
              </button>
            ) : (
              <>
                <button onClick={clearContent} className="btn-icon text-slate-400" title="Clear all">
                  <RotateCcw size={18} />
                </button>
                <button onClick={saveChanges} className="btn-icon text-green-600 bg-green-50" title="Save">
                  <Save size={18} />
                </button>
                <button onClick={cancelEditing} className="btn-icon text-red-500 bg-red-50" title="Cancel">
                  <X size={18} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Editor: draft while editing, read-only prop value otherwise */}
      {isEditing ? (
        <RichTextEditor value={draftContent ?? EMPTY_DOC} editable onChange={setDraftContent} />
      ) : (
        <RichTextEditor value={value} editable={false} />
      )}
    </div>
  )
}
