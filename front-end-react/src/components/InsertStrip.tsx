import { useState } from 'react'
import { toast } from 'react-toastify'
import './InsertStrip.css'

/**
 * Notebook-style insert strip between agenda items.
 * Hover to reveal two buttons:
 *   "New Agenda"               → onAddRegular
 *   "New Agenda from template" → toast "coming soon" (feature not yet available)
 */
interface InsertStripProps {
  disabled?: boolean
  onAddRegular: () => void
}

export default function InsertStrip({ disabled = false, onAddRegular }: InsertStripProps) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      className={['insert-strip', hovered ? 'is-hovered' : '', disabled ? 'is-disabled' : ''].join(' ')}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="strip-line" />

      {hovered && !disabled && (
        <div className="strip-btns">
          {/* New Agenda */}
          <button
            className="strip-btn regular"
            title="Insert a new blank agenda item here"
            onClick={(e) => {
              e.stopPropagation()
              onAddRegular()
            }}
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <line x1="5" y1="1" x2="5" y2="9" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <line x1="1" y1="5" x2="9" y2="5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
            New Agenda
          </button>

          {/* New Agenda from Template — coming soon */}
          <button
            className="strip-btn template"
            title="Create agenda from template (coming soon)"
            onClick={(e) => {
              e.stopPropagation()
              toast.info('Agenda templates are coming soon!')
            }}
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <rect x="1" y="1" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
              <line x1="3" y1="3.5" x2="7" y2="3.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              <line x1="3" y1="5" x2="7" y2="5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              <line x1="3" y1="6.5" x2="5.5" y2="6.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
            </svg>
            From Template
          </button>
        </div>
      )}
    </div>
  )
}
