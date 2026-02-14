export interface User {
  id: string
  email: string
  name: string
  onboarding_done: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface SignupRequest {
  email: string
  name: string
  password: string
}

export interface SignupResponse {
  id: string
  email: string
  name: string
}
