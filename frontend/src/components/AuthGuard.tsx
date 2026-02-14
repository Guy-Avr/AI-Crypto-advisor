import { type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../store/AuthContext'

interface AuthGuardProps {
  children: ReactNode
}

/** Redirects to /login if not authenticated, to /onboarding if onboarding_done is false. */
export function AuthGuard({ children }: AuthGuardProps) {
  const { user, initializing } = useAuth()
  const location = useLocation()

  if (initializing) {
    return (
      <div className="auth-guard-loading" role="status" aria-live="polite">
        Loading…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (!user.onboarding_done) {
    return <Navigate to="/onboarding" state={{ from: location }} replace />
  }

  return <>{children}</>
}
