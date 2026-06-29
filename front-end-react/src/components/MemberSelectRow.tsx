import ParticipantCard from './ParticipantCard'
import type { ParticipantRead } from '../types/api'

/** First segment of a participant's bio text — used for a concise aria-label. */
const participantName = (content: string) => content.split(/[,،]/)[0].trim()

/**
 * One row in the "Available Members" list of the Meeting Members modal.
 * Checkbox + row-click both toggle selection (selecting does NOT remove the
 * participant from this list or persist anything — see
 * ParticipantsSection.tsx's modalDraftIds, which is the single source of
 * truth mirrored into the Selected Members panel).
 */
interface MemberSelectRowProps {
  participant: ParticipantRead
  selected: boolean
  onToggle: (id: string) => void
}

export default function MemberSelectRow({ participant, selected, onToggle }: MemberSelectRowProps) {
  const name = participantName(participant.content)

  return (
    <div
      onClick={() => onToggle(participant.id)}
      className="flex items-center gap-3 cursor-pointer rounded-2xl transition-colors duration-150 hover:bg-slate-50/80"
    >
      <input
        type="checkbox"
        checked={selected}
        onChange={() => onToggle(participant.id)}
        onClick={(e) => e.stopPropagation()}
        aria-label={`Select ${name}`}
        className="shrink-0 ml-1 h-5 w-5 rounded-md border-2 border-slate-300 text-blue-600
                   accent-blue-600 cursor-pointer
                   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
      />
      <div className="flex-1 min-w-0">
        <ParticipantCard participant={participant} selectable selected={selected} />
      </div>
    </div>
  )
}
