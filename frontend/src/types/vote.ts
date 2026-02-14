export type SectionType = 'news' | 'price' | 'ai' | 'meme'
export type VoteType = 'up' | 'down'

export interface VoteRequest {
  section_type: SectionType
  item_id: string
  vote_type: VoteType
}

export interface VoteCancelRequest {
  section_type: SectionType
  item_id: string
}
