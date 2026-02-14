import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/AuthContext'
import { validateLogin } from '../utils/validation'
import './Auth.css'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setApiError('')
    const err = validateLogin(email, password)
    setErrors(err)
    if (Object.keys(err).length > 0) return

    setLoading(true)
    try {
      await login({ email: email.trim(), password })
      navigate('/', { replace: true })
    } catch (err: unknown) {
      const res = err as { response?: { data?: { detail?: string } } }
      const msg = res?.response?.data?.detail
      setApiError(typeof msg === 'string' ? msg : 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-screen">
      <h1>Log in</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        {apiError && <p className="auth-error">{apiError}</p>}
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            autoComplete="email"
            aria-invalid={!!errors.email}
          />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            autoComplete="current-password"
            aria-invalid={!!errors.password}
          />
          {errors.password && <span className="field-error">{errors.password}</span>}
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="auth-footer">
        Don’t have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  )
}
