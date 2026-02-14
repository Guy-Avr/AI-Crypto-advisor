import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitOnboarding } from '../api'
import { useAuth } from '../store/AuthContext'
import {
  ASSET_SYMBOLS,
  INVESTOR_TYPES,
  SECTION_TYPES,
} from '../types/onboarding'
import type { AssetSymbol, InvestorType, SectionType } from '../types/onboarding'
import './Auth.css'
import './Onboarding.css'

export default function Onboarding() {
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const [assets, setAssets] = useState<AssetSymbol[]>([])
  const [investorType, setInvestorType] = useState<InvestorType | ''>('')
  const [contentTypes, setContentTypes] = useState<SectionType[]>([])
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)

  function toggleAsset(sym: AssetSymbol) {
    setAssets((prev) =>
      prev.includes(sym) ? prev.filter((s) => s !== sym) : [...prev, sym]
    )
  }

  function toggleContentType(ct: SectionType) {
    setContentTypes((prev) =>
      prev.includes(ct) ? prev.filter((c) => c !== ct) : [...prev, ct]
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setApiError('')
    const err: Record<string, string> = {}
    if (assets.length === 0) err.assets = 'Select at least one asset'
    if (!investorType) err.investor_type = 'Select your investor type'
    if (contentTypes.length === 0) err.content_types = 'Select at least one content type'
    setErrors(err)
    if (Object.keys(err).length > 0) return

    setLoading(true)
    try {
      await submitOnboarding({
        assets,
        investor_type: investorType as InvestorType,
        content_types: contentTypes,
      })
      await refreshUser()
      navigate('/', { replace: true })
    } catch (err: unknown) {
      const res = err as { response?: { data?: { detail?: string } } }
      const msg = res?.response?.data?.detail
      setApiError(typeof msg === 'string' ? msg : 'Failed to save preferences.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="onboarding-screen">
      <h1>Set up your dashboard</h1>
      <p className="onboarding-intro">Choose assets, your style, and what you want to see.</p>
      <form onSubmit={handleSubmit} className="onboarding-form">
        {apiError && <p className="auth-error">{apiError}</p>}

        <fieldset>
          <legend>Assets (at least one)</legend>
          {errors.assets && <span className="field-error">{errors.assets}</span>}
          <div className="asset-grid">
            {ASSET_SYMBOLS.map((sym) => (
              <label key={sym} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={assets.includes(sym)}
                  onChange={() => toggleAsset(sym)}
                  disabled={loading}
                />
                {sym}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Investor type</legend>
          {errors.investor_type && <span className="field-error">{errors.investor_type}</span>}
          <select
            value={investorType}
            onChange={(e) => setInvestorType(e.target.value as InvestorType | '')}
            disabled={loading}
            aria-invalid={!!errors.investor_type}
          >
            <option value="">Select</option>
            {INVESTOR_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </fieldset>

        <fieldset>
          <legend>Dashboard sections (at least one)</legend>
          {errors.content_types && <span className="field-error">{errors.content_types}</span>}
          <div className="content-types">
            {SECTION_TYPES.map((ct) => (
              <label key={ct} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={contentTypes.includes(ct)}
                  onChange={() => toggleContentType(ct)}
                  disabled={loading}
                />
                {ct}
              </label>
            ))}
          </div>
        </fieldset>

        <button type="submit" disabled={loading}>
          {loading ? 'Saving…' : 'Save and continue'}
        </button>
      </form>
    </div>
  )
}
