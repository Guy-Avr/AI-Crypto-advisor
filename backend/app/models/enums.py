import enum


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