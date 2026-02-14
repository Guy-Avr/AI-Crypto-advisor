import { apiClient } from './client'
import type { DashboardResponse } from '../types/dashboard'

/** Optional signal to abort the request (e.g. on React effect cleanup to avoid duplicate calls). */
export async function getDashboard(signal?: AbortSignal): Promise<DashboardResponse> {
  const { data } = await apiClient.get<DashboardResponse>('/dashboard', {
    signal,
    timeout: 60_000, // AI insight can be slow; avoid client timeout
  })
  return data
}
