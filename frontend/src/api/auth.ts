import { apiClient } from './client'
import type { LoginRequest, LoginResponse, SignupRequest, SignupResponse } from '../types/auth'

const AUTH = '/auth'

export async function signup(body: SignupRequest): Promise<SignupResponse> {
  const { data } = await apiClient.post<SignupResponse>(`${AUTH}/signup`, body)
  return data
}

export async function login(body: LoginRequest): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>(`${AUTH}/login`, body)
  return data
}
