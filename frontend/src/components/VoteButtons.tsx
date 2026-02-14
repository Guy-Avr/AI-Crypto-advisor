import type { SectionType, VoteType } from '../types/vote'
import './VoteButtons.css'

interface VoteButtonsProps {
  sectionType: SectionType
  itemId: string
  currentVote: VoteType | null
  onVote: (section: SectionType, itemId: string, type: VoteType) => void
  onCancel: (section: SectionType, itemId: string) => void
  loading?: boolean
}

export function VoteButtons({
  sectionType,
  itemId,
  currentVote,
  onVote,
  onCancel,
  loading = false,
}: VoteButtonsProps) {
  function handleUp() {
    if (loading) return
    if (currentVote === 'up') onCancel(sectionType, itemId)
    else onVote(sectionType, itemId, 'up')
  }

  function handleDown() {
    if (loading) return
    if (currentVote === 'down') onCancel(sectionType, itemId)
    else onVote(sectionType, itemId, 'down')
  }

  return (
    <span className="vote-buttons" role="group" aria-label="Vote">
      <button
        type="button"
        className={`vote-btn vote-up ${currentVote === 'up' ? 'active' : ''}`}
        onClick={handleUp}
        disabled={loading}
        title={currentVote === 'up' ? 'Remove vote' : 'Vote up'}
        aria-pressed={currentVote === 'up'}
      >
        👍
      </button>
      <button
        type="button"
        className={`vote-btn vote-down ${currentVote === 'down' ? 'active' : ''}`}
        onClick={handleDown}
        disabled={loading}
        title={currentVote === 'down' ? 'Remove vote' : 'Vote down'}
        aria-pressed={currentVote === 'down'}
      >
        👎
      </button>
    </span>
  )
}
