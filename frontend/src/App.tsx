import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthGuard } from './components/AuthGuard'
import { useAuth } from './store/AuthContext'
import Home from './screens/Home'
import Login from './screens/Login'
import Onboarding from './screens/Onboarding'
import Register from './screens/Register'
import './App.css'

function RequireNoAuth({ children }: { children: React.ReactNode }) {
  const { user, initializing } = useAuth()

  if (initializing) return <div className="app-loading">Loading…</div>
  if (user) return <Navigate to={user.onboarding_done ? '/' : '/onboarding'} replace />
  return <>{children}</>
}

function RequireAuthOnboarding({ children }: { children: React.ReactNode }) {
  const { user, initializing } = useAuth()

  if (initializing) return <div className="app-loading">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (user.onboarding_done) return <Navigate to="/" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <RequireNoAuth>
            <Login />
          </RequireNoAuth>
        }
      />
      <Route
        path="/register"
        element={
          <RequireNoAuth>
            <Register />
          </RequireNoAuth>
        }
      />
      <Route
        path="/onboarding"
        element={
          <RequireAuthOnboarding>
            <Onboarding />
          </RequireAuthOnboarding>
        }
      />
      <Route
        path="/"
        element={
          <AuthGuard>
            <Home />
          </AuthGuard>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
