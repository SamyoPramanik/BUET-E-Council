import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'react-toastify'
import { X, Plus, Search, Trash2, Save, PenLine } from 'lucide-react'
import api from '../utils/api'
import { confirmDestructive } from '../utils/alerts'
import SignatureCardItem from './SignatureCardItem'
import type { SignatureCardResponse, PaginatedSignatureCardResponse } from '../types/api'
import './SignatureCardsSection.css'

/**
 * Full signature-cards management section for MeetingDetails.
 *
 * Behaviour:
 *   - Viewers   — read-only grid of SignatureCardItem (no buttons)
 *   - Modifiers — can add from catalogue (modal), remove, drag-to-reorder,
 *                 and create brand-new cards inline in the modal
 */
interface SignatureCardsSectionProps {
  meetingId: string
  canModify?: boolean
}

const CATALOGUE_LIMIT = 20

export default function SignatureCardsSection({ meetingId, canModify = false }: SignatureCardsSectionProps) {
  // ── Meeting cards (attached, ordered) ─────────────────────────────────────
  const [meetingCards, setMeetingCards] = useState<SignatureCardResponse[]>([])
  const [loading, setLoading] = useState(false)

  const fetchMeetingCards = async () => {
    setLoading(true)
    try {
      const res = await api.get<SignatureCardResponse[]>(`/meetings/${meetingId}/signature-cards`)
      setMeetingCards(res.data || [])
    } catch {
      toast.error('Failed to load signature cards')
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => {
    fetchMeetingCards()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meetingId])

  // ── Drag-to-reorder on the main grid ──────────────────────────────────────
  const [dragFromIdx, setDragFromIdx] = useState<number | null>(null)
  const dragOrder = useRef<SignatureCardResponse[]>([])

  const onDragStart = (idx: number) => {
    dragOrder.current = [...meetingCards]
    setDragFromIdx(idx)
  }
  const onDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (dragFromIdx === null || dragFromIdx === idx) return
    const arr = [...meetingCards]
    const [m] = arr.splice(dragFromIdx, 1)
    arr.splice(idx, 0, m)
    setMeetingCards(arr)
    setDragFromIdx(idx)
  }
  const onDragEnd = async () => {
    setDragFromIdx(null)
    try {
      // Patch each card's order sequentially
      for (let i = 0; i < meetingCards.length; i++) {
        await api.patch(`/meetings/${meetingId}/signature-cards/${meetingCards[i].id}`, { order: i + 1 })
      }
      toast.success('Order saved')
      await fetchMeetingCards()
    } catch {
      toast.error('Failed to save order')
      setMeetingCards(dragOrder.current) // revert
    }
  }

  // ── Remove one card ────────────────────────────────────────────────────────
  const removeCard = async (cardId: string) => {
    const ok = await confirmDestructive(
      'Remove signature card?',
      'This card will be detached from this meeting. It remains in the global catalogue.',
      'Remove',
    )
    if (!ok) return
    try {
      await api.delete(`/meetings/${meetingId}/signature-cards/${cardId}`)
      toast.success('Removed')
      await fetchMeetingCards()
    } catch {
      toast.error('Failed to remove card')
    }
  }

  // ── Clear all ──────────────────────────────────────────────────────────────
  const clearAll = async () => {
    const ok = await confirmDestructive('Remove all signature cards?', 'All cards will be detached from this meeting.', 'Clear All')
    if (!ok) return
    try {
      await api.delete(`/meetings/${meetingId}/signature-cards`)
      setMeetingCards([])
      toast.success('All signature cards removed')
    } catch {
      toast.error('Failed to clear cards')
    }
  }

  // ── Modal state ────────────────────────────────────────────────────────────
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [creating, setCreating] = useState(false)
  const [newCardContent, setNewCardContent] = useState('')

  // Draft: list of card UUIDs in display order
  const [modalDraft, setModalDraft] = useState<string[]>([])

  // ── Catalogue (paginated) ─────────────────────────────────────────────────
  const [catalogue, setCatalogue] = useState<SignatureCardResponse[]>([])
  const [catalogueSearch, setCatalogueSearch] = useState('')
  const cataloguePage = useRef(1)
  const [catalogueTotal, setCatalogueTotal] = useState(0)
  const [catalogueLoading, setCatalogueLoading] = useState(false)

  // Full card objects for the draft (resolved from catalogue)
  const modalDraftCards = modalDraft
    .map((id) => [...catalogue, ...meetingCards].find((c) => c.id === id))
    .filter((c): c is SignatureCardResponse => Boolean(c))

  const loadCatalogue = async (reset = false) => {
    if (catalogueLoading) return
    if (reset) {
      cataloguePage.current = 1
      setCatalogue([])
    }
    setCatalogueLoading(true)
    try {
      const params: Record<string, unknown> = { page: cataloguePage.current, limit: CATALOGUE_LIMIT }
      if (catalogueSearch.trim()) params.search = catalogueSearch.trim()
      const res = await api.get<PaginatedSignatureCardResponse>('/signature-cards/', { params })
      setCatalogueTotal(res.data.total_count)
      setCatalogue((prev) => (reset ? res.data.data : [...prev, ...res.data.data]))
      cataloguePage.current++
    } catch {
      /* silent */
    } finally {
      setCatalogueLoading(false)
    }
  }

  const openModal = () => {
    setModalDraft(meetingCards.map((c) => c.id))
    setNewCardContent('')
    setShowModal(true)
    loadCatalogue(true)
  }
  const closeModal = () => setShowModal(false)

  const filteredCatalogue = catalogue.filter((c) => !modalDraft.includes(c.id))

  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)
  const onSearchInput = (v: string) => {
    setCatalogueSearch(v)
    if (searchTimeout.current) clearTimeout(searchTimeout.current)
    searchTimeout.current = setTimeout(() => loadCatalogue(true), 300)
  }

  const onCatalogueScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget
    const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 60
    const hasMore = catalogue.length < catalogueTotal
    if (nearBottom && hasMore && !catalogueLoading) loadCatalogue()
  }

  // ── Modal: add / remove / drag ────────────────────────────────────────────
  const modalAdd = (card: SignatureCardResponse) => {
    if (!modalDraft.includes(card.id)) {
      // Ensure the full card object is in catalogue for resolution
      if (!catalogue.find((c) => c.id === card.id)) setCatalogue((prev) => [...prev, card])
      setModalDraft((prev) => [...prev, card.id])
    }
  }
  const modalRemove = (cardId: string) => {
    setModalDraft((prev) => prev.filter((id) => id !== cardId))
  }

  const modalDragFrom = useRef<number | null>(null)
  const onModalDragStart = (idx: number) => {
    modalDragFrom.current = idx
  }
  const onModalDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (modalDragFrom.current === null || modalDragFrom.current === idx) return
    const arr = [...modalDraft]
    const [m] = arr.splice(modalDragFrom.current, 1)
    arr.splice(idx, 0, m)
    setModalDraft(arr)
    modalDragFrom.current = idx
  }
  const onModalDragEnd = () => {
    modalDragFrom.current = null
  }

  // ── Create & attach new card ──────────────────────────────────────────────
  const createAndAttach = async () => {
    if (!newCardContent.trim()) return
    setCreating(true)
    try {
      const res = await api.post<SignatureCardResponse>('/signature-cards/', { content: newCardContent.trim() })
      const newCard = res.data
      setCatalogue((prev) => [newCard, ...prev])
      setCatalogueTotal((prev) => prev + 1)
      modalAdd(newCard)
      setNewCardContent('')
      toast.success('Card created and attached')
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to create card')
    } finally {
      setCreating(false)
    }
  }

  // ── Save modal: sync meeting's signature cards to modalDraft ──────────────
  const saveModal = async () => {
    setSaving(true)
    try {
      // 1. Clear all existing links
      await api.delete(`/meetings/${meetingId}/signature-cards`)
      // 2. Attach in new order
      for (let i = 0; i < modalDraft.length; i++) {
        await api.post(`/meetings/${meetingId}/signature-cards`, {
          signature_card_id: modalDraft[i],
          order: i + 1,
        })
      }
      toast.success('Signature cards saved')
      await fetchMeetingCards()
      setShowModal(false)
    } catch {
      toast.error('Failed to save signature cards')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="space-y-0">
        {/* ══ Section header ══════════════════════════════════════════════════ */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-px bg-slate-300" />
            <span className="text-sm font-black uppercase tracking-widest text-slate-500">Signature Cards</span>
            <span className="text-xs font-bold text-slate-500 bg-slate-200 px-2 py-0.5 rounded-full">{meetingCards.length}</span>
          </div>

          {canModify && (
            <div className="flex items-center gap-2">
              {meetingCards.length > 0 && (
                <button
                  onClick={clearAll}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                             text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all"
                >
                  <Trash2 size={12} /> Clear All
                </button>
              )}
              <button
                onClick={openModal}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold
                           bg-slate-800 hover:bg-slate-900 text-white rounded-xl
                           transition-all active:scale-95 shadow-sm"
              >
                <PenLine size={15} /> Manage Signatures
              </button>
            </div>
          )}
        </div>

        {/* ══ Content ══════════════════════════════════════════════════════════ */}
        {!meetingCards.length && !loading ? (
          <div
            className="flex flex-col items-center gap-3 py-14 bg-slate-50
                        border-2 border-dashed border-slate-200 rounded-2xl text-center"
          >
            <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center">
              <PenLine size={22} className="text-slate-300" />
            </div>
            <p className="text-sm font-semibold text-slate-500">No signature cards yet</p>
            <p className="text-xs text-slate-400 max-w-xs">
              {canModify ? 'Use "Manage Signatures" to add the authorising signatures.' : 'No signatures have been added to this meeting.'}
            </p>
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="w-6 h-6 border-4 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
          </div>
        ) : (
          <div className="sig-grid">
            {meetingCards.map((card, idx) => (
              <div
                key={card.id}
                className="group"
                draggable={canModify}
                onDragStart={() => canModify && onDragStart(idx)}
                onDragOver={(e) => canModify && onDragOver(e, idx)}
                onDragEnd={() => canModify && onDragEnd()}
              >
                <SignatureCardItem card={card} removable={canModify} draggable={canModify} isDragging={dragFromIdx === idx} onRemove={removeCard} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ══ MANAGE MODAL ══════════════════════════════════════════════════════ */}
      {showModal &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) closeModal()
            }}
          >
            <div className="w-full max-w-4xl bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden" style={{ maxHeight: '88vh' }}>
              {/* Modal header */}
              <div className="px-7 py-5 border-b border-slate-100 flex items-center justify-between shrink-0">
                <div>
                  <h2 className="text-lg font-black text-slate-800">Manage Signature Cards</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Attach from catalogue · create new · drag to reorder</p>
                </div>
                <button onClick={closeModal} className="p-2 rounded-xl hover:bg-slate-100 text-slate-500 transition-all">
                  <X size={20} />
                </button>
              </div>

              {/* Modal body: two columns */}
              <div className="flex-1 min-h-0 flex flex-col lg:flex-row overflow-hidden">
                {/* LEFT: attached (draggable) */}
                <div className="flex-1 border-b lg:border-b-0 lg:border-r border-slate-100 flex flex-col overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-100 flex items-center gap-2 shrink-0 bg-slate-50/70">
                    <PenLine size={14} className="text-slate-500" />
                    <span className="text-xs font-black uppercase tracking-widest text-slate-500">Attached</span>
                    <span className="ml-auto px-2 py-0.5 bg-slate-200 text-slate-600 text-xs font-bold rounded-full">{modalDraft.length}</span>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4">
                    {!modalDraft.length && (
                      <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-2 py-10">
                        <PenLine size={32} className="text-slate-200" />
                        <p className="text-sm">No cards attached yet</p>
                      </div>
                    )}

                    <div className="flex flex-col gap-3">
                      {modalDraftCards.map((card, idx) => (
                        <div
                          key={card.id}
                          className={['group relative', modalDragFrom.current === idx ? 'opacity-40' : ''].join(' ')}
                          draggable
                          onDragStart={() => onModalDragStart(idx)}
                          onDragOver={(e) => onModalDragOver(e, idx)}
                          onDragEnd={onModalDragEnd}
                        >
                          <SignatureCardItem card={card} removable draggable onRemove={modalRemove} />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* RIGHT: catalogue + create new */}
                <div className="flex-1 flex flex-col overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-100 shrink-0 bg-slate-50/70 space-y-2">
                    {/* Search */}
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                      <input
                        value={catalogueSearch}
                        onChange={(e) => onSearchInput(e.target.value)}
                        placeholder="Search catalogue…"
                        className="w-full pl-9 pr-3 py-2 text-sm bg-white border border-slate-200
                                   rounded-xl outline-none focus:border-slate-400 transition-colors"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Plus size={13} className="text-emerald-500" />
                      <span className="text-xs font-black uppercase tracking-widest text-slate-500">Catalogue</span>
                      <span className="ml-auto px-2 py-0.5 bg-slate-100 text-slate-500 text-xs font-bold rounded-full">{catalogueTotal}</span>
                    </div>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 space-y-3" onScroll={onCatalogueScroll}>
                    {/* Create new card form */}
                    <div className="border border-dashed border-slate-300 rounded-xl p-4 bg-slate-50/60">
                      <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">+ Create New Card</p>
                      <textarea
                        value={newCardContent}
                        onChange={(e) => setNewCardContent(e.target.value)}
                        rows={3}
                        placeholder={'(Name)\\nTitle\\nও\\nRole'}
                        className="w-full text-sm bg-white border border-slate-200 rounded-lg px-3 py-2
                                   outline-none focus:border-slate-400 resize-none font-mono"
                      />
                      <button
                        onClick={createAndAttach}
                        disabled={!newCardContent.trim() || creating}
                        className="mt-2 w-full py-2 text-xs font-bold bg-slate-800 hover:bg-slate-900
                                   text-white rounded-lg transition-all disabled:opacity-40"
                      >
                        {creating ? 'Creating…' : 'Create & Attach'}
                      </button>
                    </div>

                    {/* Catalogue items */}
                    {filteredCatalogue.map((card) => (
                      <div key={card.id} className="group relative">
                        <SignatureCardItem card={card} />
                        <button
                          onClick={() => modalAdd(card)}
                          disabled={modalDraft.includes(card.id)}
                          className={[
                            'absolute top-2 right-2 p-1.5 rounded-lg bg-emerald-50 text-emerald-600',
                            'hover:bg-emerald-100 transition-all duration-150 z-10 text-xs font-bold',
                            modalDraft.includes(card.id) ? 'opacity-40 cursor-not-allowed' : 'opacity-0 group-hover:opacity-100',
                          ].join(' ')}
                          title={modalDraft.includes(card.id) ? 'Already attached' : 'Attach'}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                    ))}

                    {/* Infinite scroll loader */}
                    {catalogueLoading && (
                      <div className="flex justify-center py-4">
                        <div className="w-5 h-5 border-4 border-slate-200 border-t-slate-500 rounded-full animate-spin" />
                      </div>
                    )}
                    {!catalogueLoading && !filteredCatalogue.length && !newCardContent && (
                      <p className="text-center text-sm text-slate-400 italic py-6">{catalogueSearch ? 'No results' : 'Catalogue is empty'}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Modal footer */}
              <div className="px-7 py-5 border-t border-slate-100 flex items-center justify-end gap-3 shrink-0 bg-slate-50/50">
                <button
                  onClick={closeModal}
                  className="px-6 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={saveModal}
                  disabled={saving}
                  className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white
                             text-sm font-bold flex items-center gap-2 transition-all active:scale-95
                             disabled:opacity-50"
                >
                  <Save size={15} />
                  {saving ? 'Saving…' : `Save (${modalDraft.length})`}
                </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </>
  )
}
