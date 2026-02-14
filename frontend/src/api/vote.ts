import { apiClient } from './client'
import type { VoteCancelRequest, VoteRequest } from '../types/vote'

export interface VoteResponse {
  status: string
  action: 'created' | 'updated'
}

export interface VoteCancelResponse {
  status: string
  action: string
}

export async function postVote(body: VoteRequest): Promise<VoteResponse> {
  const { data } = await apiClient.post<VoteResponse>('/vote', body)
  return data
}

export async function deleteVote(body: VoteCancelRequest): Promise<VoteCancelResponse> {
  const { data } = await apiClient.delete<VoteCancelResponse>('/vote', { data: body })
  return data
}
