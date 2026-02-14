export interface NewsItem {
  title: string
  url: string
  source?: string
  published_at?: string
  coins?: string[]
}

export interface MemeItem {
  title: string
  url: string
  image_url: string
}

export interface DashboardResponse {
  news: NewsItem[]
  prices: Record<string, number>
  ai_insight: string
  meme: MemeItem | null
}
