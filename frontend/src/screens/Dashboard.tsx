import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import { VoteButtons } from '../components/VoteButtons'
import { useVoting } from '../hooks/useVoting'
import { useAuth } from '../store/AuthContext'
import type { DashboardResponse } from '../types/dashboard'
import { formatNewsDate } from '../utils/formatDate'
import './Dashboard.css'

const NEWS_TITLE_MAX_CHARS = 70

export default function Dashboard() {
  const { user, logout } = useAuth()
  const { vote, cancelVote, getVote, isLoading } = useVoting()
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    getDashboard(controller.signal)
      .then((res) => {
        if (!controller.signal.aborted) setData(res)
      })
      .catch((err) => {
        if (err?.name === 'CanceledError' || err?.name === 'AbortError' || err?.code === 'ERR_CANCELED') return
        const msg = err?.response?.data?.detail ?? 'Failed to load dashboard'
        setError(typeof msg === 'string' ? msg : 'Failed to load dashboard')
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [])

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>AI Crypto Advisor</h1>
        <p>Welcome, {user?.name ?? user?.email}</p>
        <button type="button" className="logout-btn" onClick={logout}>
          Log out
        </button>
      </header>

      {loading && <div className="dashboard-loading">Loading dashboard…</div>}
      {error && <div className="dashboard-error">{error}</div>}
      {!loading && !error && !data && null}
      {!loading && !error && data && (
        <>
      {data.news.length > 0 && (
        <section className="dashboard-section news" aria-label="News">
          <h2>News</h2>
          <ul>
            {data.news.map((item) => {
              const titleDisplay = item.title.length > NEWS_TITLE_MAX_CHARS
                ? item.title.slice(0, NEWS_TITLE_MAX_CHARS) + '…'
                : item.title
              return (
                <li key={item.url} className="section-item news-item">
                  <div className="item-content news-item-content">
                    <a href={item.url} target="_blank" rel="noopener noreferrer" title={item.title}>
                      {titleDisplay}
                    </a>
                    {item.published_at && (
                      <span className="news-time">{formatNewsDate(item.published_at)}</span>
                    )}
                  </div>
                  <VoteButtons
                    sectionType="news"
                    itemId={item.url}
                    currentVote={getVote('news', item.url)}
                    onVote={vote}
                    onCancel={cancelVote}
                    loading={isLoading('news', item.url)}
                  />
                </li>
              )
            })}
          </ul>
        </section>
      )}

      {Object.keys(data.prices).length > 0 && (
        <section className="dashboard-section prices" aria-label="Prices">
          <h2>Price</h2>
          <ul>
            {Object.entries(data.prices).map(([symbol, price]) => {
              const priceItemId = `${symbol}|${Number(price)}`
              return (
                <li key={priceItemId} className="section-item">
                  <div className="item-content">
                    <span className="symbol">{symbol}</span>
                    <span>${Number(price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</span>
                  </div>
                  <VoteButtons
                    sectionType="price"
                    itemId={priceItemId}
                    currentVote={getVote('price', priceItemId)}
                    onVote={vote}
                    onCancel={cancelVote}
                    loading={isLoading('price', priceItemId)}
                  />
                </li>
              )
            })}
          </ul>
        </section>
      )}

      {data.ai_insight && (
        <section className="dashboard-section ai" aria-label="AI Insight">
          <h2>AI</h2>
          <div className="section-item">
            <div className="item-content ai-block">{data.ai_insight}</div>
            <VoteButtons
              sectionType="ai"
              itemId={data.ai_insight.slice(0, 255)}
              currentVote={getVote('ai', data.ai_insight.slice(0, 255))}
              onVote={vote}
              onCancel={cancelVote}
              loading={isLoading('ai', data.ai_insight.slice(0, 255))}
            />
          </div>
        </section>
      )}

      {data.meme && (
        <section className="dashboard-section meme" aria-label="Meme">
          <h2>Meme</h2>
          <div className="section-item">
            <div className="item-content">
              <div className="meme-card">
                <a href={data.meme.url} target="_blank" rel="noopener noreferrer">
                  <img src={data.meme.image_url} alt={data.meme.title} />
                </a>
                <div className="meme-title">{data.meme.title}</div>
              </div>
            </div>
            <VoteButtons
              sectionType="meme"
              itemId={data.meme.image_url}
              currentVote={getVote('meme', data.meme.image_url)}
              onVote={vote}
              onCancel={cancelVote}
              loading={isLoading('meme', data.meme.image_url)}
            />
          </div>
        </section>
      )}

      {data.news.length === 0 &&
        Object.keys(data.prices).length === 0 &&
        !data.ai_insight &&
        !data.meme && (
          <p className="dashboard-section empty">No content available.</p>
        )}
        </>
      )}
    </div>
  )
}
