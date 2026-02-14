import { apiClient } from './client'
import type { OnboardingRequest, OnboardingResponse } from '../types/onboarding'

export async function submitOnboarding(body: OnboardingRequest): Promise<OnboardingResponse> {
  const { data } = await apiClient.post<OnboardingResponse>('/onboarding', body)
  return data
}
