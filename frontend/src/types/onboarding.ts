/** Must match backend AssetSymbol enum */
export const ASSET_SYMBOLS = [
  'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'USDT', 'USDC', 'ADA', 'DOGE', 'AVAX',
  'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'BCH', 'NEAR',
  'APT', 'ARB', 'OP', 'INJ', 'SUI', 'SEI', 'TIA', 'PEPE', 'WIF', 'FLOKI', 'BONK',
] as const
export type AssetSymbol = (typeof ASSET_SYMBOLS)[number]

/** Must match backend InvestorType enum */
export const INVESTOR_TYPES = [
  'HODLer',
  'DayTrader',
  'SwingTrader',
  'LongTermInvestor',
  'NFTCollector',
  'DeFiFarmer',
] as const
export type InvestorType = (typeof INVESTOR_TYPES)[number]

/** Dashboard sections – must match backend SectionType */
export const SECTION_TYPES = ['news', 'price', 'ai', 'meme'] as const
export type SectionType = (typeof SECTION_TYPES)[number]

export interface OnboardingRequest {
  assets: AssetSymbol[]
  investor_type: InvestorType
  content_types: SectionType[]
}

export interface OnboardingResponse {
  id: string
  user_id: string
  assets: string[]
  investor_type: string
  content_types: string[]
}
