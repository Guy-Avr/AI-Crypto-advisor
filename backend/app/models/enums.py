import enum


class AssetSymbol(str, enum.Enum):
    """Supported crypto assets for onboarding and price feed. API accepts only these."""
    BTC = "BTC"
    ETH = "ETH"
    BNB = "BNB"
    SOL = "SOL"
    XRP = "XRP"
    USDT = "USDT"
    USDC = "USDC"
    ADA = "ADA"
    DOGE = "DOGE"
    AVAX = "AVAX"
    DOT = "DOT"
    MATIC = "MATIC"
    LINK = "LINK"
    UNI = "UNI"
    ATOM = "ATOM"
    LTC = "LTC"
    ETC = "ETC"
    XLM = "XLM"
    BCH = "BCH"
    NEAR = "NEAR"
    APT = "APT"
    ARB = "ARB"
    OP = "OP"
    INJ = "INJ"
    SUI = "SUI"
    SEI = "SEI"
    TIA = "TIA"
    PEPE = "PEPE"
    WIF = "WIF"
    FLOKI = "FLOKI"
    BONK = "BONK"


class InvestorType(str, enum.Enum):
    HODLer = "HODLer"
    DayTrader = "DayTrader"
    SwingTrader = "SwingTrader"
    LongTermInvestor = "LongTermInvestor"
    NFTCollector = "NFTCollector"
    DeFiFarmer = "DeFiFarmer"


class SectionType(str, enum.Enum):
    """Dashboard section – must match section_type in votes table."""
    news = "news"
    price = "price"
    ai = "ai"
    meme = "meme"


class VoteType(str, enum.Enum):
    up = "up"
    down = "down"