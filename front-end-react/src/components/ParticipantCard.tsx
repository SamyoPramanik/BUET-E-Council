import { useMemo, useState } from 'react'
import { Mail, Check, Building2, X } from 'lucide-react'
import type { ParticipantRead } from '../types/api'

interface ParticipantCardProps {
  participant: ParticipantRead
  selectable?: boolean
  selected?: boolean
  /** When provided, renders an always-visible remove (X) button top-left. */
  onRemove?: () => void
}

export default function ParticipantCard({
  participant,
  selectable = false,
  selected = false,
  onRemove,
}: ParticipantCardProps) {
  // ── email copy with brief check-mark feedback ─────────────────────────────
  const [copied, setCopied] = useState(false)
  const copyEmail = () => {
    if (!participant.email) return
    navigator.clipboard.writeText(participant.email)
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  const hasEmail = !!participant.email

  // ── split content on first comma (Arabic or Latin) ────────────────────────
  const splitContent = useMemo(() => {
    const text = participant.content || ''
    const idx = text.indexOf('،') !== -1 ? text.indexOf('،') : text.indexOf(',')
    if (idx === -1) return { name: text.trim(), rest: '' }
    return {
      name: text.slice(0, idx).trim(),
      rest: text.slice(idx + 1).trim(),
    }
  }, [participant.content])

  const Icon = copied ? Check : Mail

  return (
    <div
      className={[
        'relative flex flex-col justify-between',
        'rounded-2xl border transition-all duration-200',
        'p-4 sm:p-5 min-h-[90px]',
        // Selected takes priority over the hasEmail styling — these are mutually
        // exclusive branches (not appended classes) so bg-*/border-* utilities
        // never collide for the same element.
        selectable && selected
          ? 'border-blue-400 bg-blue-50 ring-1 ring-blue-200 shadow-sm'
          : hasEmail
            ? 'bg-white border-blue-100 hover:border-blue-300 hover:shadow-md hover:shadow-blue-50'
            : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm',
        selectable ? 'cursor-pointer' : '',
      ].join(' ')}
    >
      {/* ── remove button (top-left) ────────────────────────────────────── */}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onRemove()
          }}
          title="Remove"
          aria-label="Remove participant"
          className="absolute -top-2 -left-2 z-10 flex items-center justify-center
                     h-6 w-6 rounded-full bg-red-500 text-white shadow-sm
                     hover:bg-red-600 transition-colors"
        >
          <X size={13} strokeWidth={2.5} />
        </button>
      )}

      {/* ── top section: name + rest ────────────────────────────────────── */}
      <div className="pr-2">
        <p className="font-semibold text-slate-900 text-sm leading-snug break-words">
          {splitContent.name}
        </p>
        {splitContent.rest && (
          <p className="mt-1 text-slate-500 text-xs leading-relaxed break-words">
            {splitContent.rest}
          </p>
        )}
        {participant.department && (
          <div className="mt-2 inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
            <Building2 size={11} className="shrink-0" />
            <span className="truncate max-w-[160px]">{participant.department}</span>
          </div>
        )}
      </div>

      {/* ── bottom-left: email icon + tooltip ───────────────────────────── */}
      {hasEmail && (
        <div className="mt-3 flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation()
              copyEmail()
            }}
            title={participant.email ?? undefined}
            className={[
              'group/btn flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs',
              'transition-all duration-150',
              copied
                ? 'bg-green-50 text-green-600'
                : 'text-blue-500 hover:bg-blue-50 hover:text-blue-700',
            ].join(' ')}
          >
            <Icon size={13} strokeWidth={2.2} className="shrink-0" />
            <span className="max-w-[120px] truncate hidden sm:inline">{participant.email}</span>
          </button>
        </div>
      )}
    </div>
  )
}
