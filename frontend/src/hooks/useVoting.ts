import { useCallback, useState } from 'react'
import { deleteVote, postVote } from '../api'
import type { SectionType, VoteType } from '../types/vote'

function voteKey(section: SectionType, itemId: string): string {
  return `${section}:${itemId}`
}

export function useVoting() {
  const [votes, setVotes] = useState<Record<string, VoteType>>({})
  const [loadingKeys, setLoadingKeys] = useState<Set<string>>(new Set())

  const setVote = useCallback(
    (section: SectionType, itemId: string, type: VoteType | null) => {
      const key = voteKey(section, itemId)
      setVotes((prev) => {
        const next = { ...prev }
        if (type === null) delete next[key]
        else next[key] = type
        return next
      })
    },
    []
  )

  const vote = useCallback(
    async (section: SectionType, itemId: string, voteType: VoteType) => {
      const key = voteKey(section, itemId)
      setLoadingKeys((prev) => new Set(prev).add(key))
      const previous = votes[key] ?? null
      setVote(section, itemId, voteType)

      try {
        await postVote({ section_type: section, item_id: itemId, vote_type: voteType })
      } catch {
        setVote(section, itemId, previous)
      } finally {
        setLoadingKeys((prev) => {
          const next = new Set(prev)
          next.delete(key)
          return next
        })
      }
    },
    [votes, setVote]
  )

  const cancelVote = useCallback(
    async (section: SectionType, itemId: string) => {
      const key = voteKey(section, itemId)
      setLoadingKeys((prev) => new Set(prev).add(key))
      const previous = votes[key] ?? null
      setVote(section, itemId, null)

      try {
        await deleteVote({ section_type: section, item_id: itemId })
      } catch {
        setVote(section, itemId, previous)
      } finally {
        setLoadingKeys((prev) => {
          const next = new Set(prev)
          next.delete(key)
          return next
        })
      }
    },
    [votes, setVote]
  )

  const getVote = useCallback(
    (section: SectionType, itemId: string): VoteType | null => {
      return votes[voteKey(section, itemId)] ?? null
    },
    [votes]
  )

  const isLoading = useCallback(
    (section: SectionType, itemId: string): boolean => {
      return loadingKeys.has(voteKey(section, itemId))
    },
    [loadingKeys]
  )

  return { vote, cancelVote, getVote, isLoading }
}
