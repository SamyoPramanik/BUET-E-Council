import { tiptapJsonToHtml } from '../tiptap/renderHtml'
import type { Meeting, ParticipantRead, AgendumResponse, SignatureCardResponse } from '../types/api'
import './PrintableMeeting.css'

interface PrintableMeetingProps {
  meeting: Meeting
  president: ParticipantRead | null
  members: ParticipantRead[]
  regularAgendas: AgendumResponse[]
  supplAgendas: AgendumResponse[]
  signatureCards: SignatureCardResponse[]
}

function fmtDate(iso: string | null): string {
  if (!iso) return 'Not set'
  return new Date(iso).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}

function AgendaPrintBlock({ agendum, label }: { agendum: AgendumResponse; label: string }) {
  const bodyHtml = tiptapJsonToHtml(agendum.body)
  const resHtml = tiptapJsonToHtml(agendum.resolution?.body)
  return (
    <div className="pm-agenda">
      <h4 className="pm-agenda-title">{label}</h4>
      {bodyHtml ? <div className="pm-rich" dangerouslySetInnerHTML={{ __html: bodyHtml }} /> : <p className="pm-empty">No content recorded.</p>}

      {!!agendum.annexures?.length && (
        <ul className="pm-file-list">
          {agendum.annexures.map((a) => (
            <li key={a.id}>📎 {a.original_filename}</li>
          ))}
        </ul>
      )}

      {agendum.resolution && (
        <div className="pm-resolution">
          <p className="pm-resolution-label">Resolution</p>
          {resHtml ? <div className="pm-rich" dangerouslySetInnerHTML={{ __html: resHtml }} /> : <p className="pm-empty">No resolution text recorded.</p>}
          {!!agendum.resolution.attachments?.length && (
            <ul className="pm-file-list">
              {agendum.resolution.attachments.map((a) => (
                <li key={a.id}>📎 {a.original_filename}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default function PrintableMeeting({ meeting, president, members, regularAgendas, supplAgendas, signatureCards }: PrintableMeetingProps) {
  return (
    <div className="pm-page">
      {/* ── MASTHEAD ── */}
      <header className="pm-masthead">
        <p className="pm-org">BUET E-Council</p>
        <p className="pm-council-type">{meeting.is_academic ? 'Academic Council' : 'Syndicate'}</p>
        <h1 className="pm-title">{meeting.title || `Meeting #${meeting.serial_num}`}</h1>
        <div className="pm-meta-row">
          <span>Meeting No. {meeting.serial_num}</span>
          <span>·</span>
          <span>{fmtDate(meeting.meeting_date)}</span>
          <span>·</span>
          <span>{meeting.is_finished ? 'Finished' : 'Ongoing'}</span>
        </div>
      </header>

      {/* ── DISCUSSION & MINUTES ── */}
      <section className="pm-section">
        <h2 className="pm-section-title">Discussion &amp; Minutes</h2>
        {meeting.description ? <div className="pm-rich" dangerouslySetInnerHTML={{ __html: meeting.description }} /> : <p className="pm-empty">No discussion minutes recorded.</p>}
      </section>

      {/* ── PARTICIPANTS ── */}
      <section className="pm-section">
        <h2 className="pm-section-title">Participants</h2>
        <p className="pm-sub-label">President</p>
        <p className="pm-participant">{president ? president.content : '—'}</p>

        <p className="pm-sub-label">Members ({members.length})</p>
        {members.length ? (
          <ol className="pm-participant-list">
            {members.map((m) => (
              <li key={m.id}>{m.content}</li>
            ))}
          </ol>
        ) : (
          <p className="pm-empty">No members recorded.</p>
        )}
      </section>

      {/* ── AGENDAS ── */}
      <section className="pm-section">
        <h2 className="pm-section-title">Agendas</h2>
        {regularAgendas.length ? (
          regularAgendas.map((ag, idx) => <AgendaPrintBlock key={ag.id} agendum={ag} label={`Agenda ${idx + 1}`} />)
        ) : (
          <p className="pm-empty">No agenda items recorded.</p>
        )}
      </section>

      {/* ── SUPPLEMENTARY AGENDAS ── */}
      {!!supplAgendas.length && (
        <section className="pm-section">
          <h2 className="pm-section-title">Supplementary Agendas</h2>
          {supplAgendas.map((ag, idx) => (
            <AgendaPrintBlock key={ag.id} agendum={ag} label={`Supplementary Agenda ${idx + 1}`} />
          ))}
        </section>
      )}

      {/* ── FINAL CONCLUSION ── */}
      <section className="pm-section">
        <h2 className="pm-section-title">Final Conclusion</h2>
        {meeting.conclusion ? <div className="pm-rich" dangerouslySetInnerHTML={{ __html: meeting.conclusion }} /> : <p className="pm-empty">No conclusion recorded.</p>}
      </section>

      {/* ── SIGNATURES ── */}
      {!!signatureCards.length && (
        <section className="pm-section pm-signatures-section">
          <h2 className="pm-section-title">Signatures</h2>
          <div className="pm-signatures-grid">
            {signatureCards.map((card) => (
              <div key={card.id} className="pm-sig-card">
                <div className="pm-sig-line" />
                {(card.content || '')
                  .split('\n')
                  .map((l) => l.trim())
                  .filter(Boolean)
                  .map((line, i) => (
                    <p key={i} className="pm-sig-card-line">
                      {line}
                    </p>
                  ))}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
