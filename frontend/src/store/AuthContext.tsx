import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { login as apiLogin, signup as apiSignup, getMe } from '../api'
import { clearStoredToken, getStoredToken, setStoredToken } from '../api/client'
import type { User } from '../types/auth'
import type { LoginRequest, SignupRequest } from '../types/auth'

interface AuthState {
  user: User | null
  token: string | null
  initializing: boolean
}

interface AuthContextValue extends AuthState {
  login: (body: LoginRequest) => Promise<void>
  register: (body: SignupRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [storedToken, setStored] = useState<string | null>(() => getStoredToken())
  const [initializing, setInitializing] = useState(() => !!getStoredToken())

  const refreshUser = useCallback(async () => {
    const t = getStoredToken()
    if (!t) {
      setUser(null)
      return
    }
    try {
      const me = await getMe()
      setUser(me)
    } catch {
      clearStoredToken()
      setStored(null)
      setUser(null)
    }
  }, [])

  useEffect(() => {
    if (!getStoredToken()) {
      setInitializing(false)
      return
    }
    getMe()
      .then(setUser)
      .catch(() => {
        clearStoredToken()
        setStored(null)
      })
      .finally(() => setInitializing(false))
  }, [])

  const login = useCallback(async (body: LoginRequest) => {
    const { access_token } = await apiLogin(body)
    setStoredToken(access_token)
    setStored(access_token)
    const me = await getMe()
    setUser(me)
  }, [])

  const register = useCallback(async (body: SignupRequest) => {
    await apiSignup(body)
    await login({ email: body.email, password: body.password })
  }, [login])

  const logout = useCallback(() => {
    clearStoredToken()
    setStored(null)
    setUser(null)
  }, [])

  const value: AuthContextValue = {
    user,
    token: storedToken,
    initializing,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
