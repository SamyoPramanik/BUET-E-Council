import { useMemo } from 'react'
import { GripVertical, X } from 'lucide-react'
import type { SignatureCardResponse } from '../types/api'
import './SignatureCardItem.css'

/**
 * Displays one signature card as a visual block that mirrors how it appears
 * at the bottom of official meeting minutes:
 *
 *     ─────────────────────
 *     (Name)
 *     Title line 1
 *     ও
 *     Title line 2
 *     ─────────────────────
 */
interface SignatureCardItemProps {
  card: SignatureCardResponse
  removable?: boolean
  draggable?: boolean
  isDragging?: boolean
  onRemove?: (cardId: string) => void
}

export default function SignatureCardItem({
  card,
  removable = false,
  draggable = false,
  isDragging = false,
  onRemove,
}: SignatureCardItemProps) {
  const lines = useMemo(
    () => (card.content || '').split('\n').map((l) => l.trim()).filter(Boolean),
    [card.content],
  )

  return (
    <div
      className={[
        'sig-card',
        isDragging ? 'sig-card--dragging' : '',
        removable ? 'sig-card--removable' : '',
      ].join(' ')}
    >
      {/* Drag grip */}
      {draggable && (
        <div className="sig-card__grip" title="Drag to reorder">
          <GripVertical size={14} className="text-slate-300 group-hover:text-slate-500 transition-colors" />
        </div>
      )}

      {/* Signature line (decorative) */}
      <div className="sig-card__line-wrap">
        <div className="sig-card__sig-area">
          <div className="sig-card__blank-line" />
        </div>
      </div>

      {/* Content: multi-line, each \n becomes its own line */}
      <div className="sig-card__content">
        {lines.map((line, i) => (
          <span
            key={i}
            className={[
              'sig-card__line',
              i === 0 ? 'sig-card__line--name' : '',
              line.trim() === 'ও' || line.trim() === 'and' ? 'sig-card__line--joiner' : '',
            ].join(' ')}
          >
            {line}
          </span>
        ))}
      </div>

      {/* Remove button */}
      {removable && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onRemove?.(card.id)
          }}
          className="sig-card__remove"
          title="Remove from meeting"
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
}
