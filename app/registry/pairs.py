from dataclasses import dataclass


@dataclass(frozen=True)
class TradingPair:
    chain: str
    base_symbol: str
    quote_symbol: str
    priority: int = 1


TRADING_PAIRS: list[TradingPair] = [
    TradingPair("base", "WETH", "USDC", 1),
    TradingPair("base", "cbBTC", "USDC", 2),

    TradingPair("ethereum", "WETH", "USDC", 1),
    TradingPair("ethereum", "WBTC", "USDC", 2),

    TradingPair("arbitrum", "WETH", "USDC", 1),
    TradingPair("arbitrum", "WBTC", "USDC", 2),

    TradingPair("polygon", "WETH", "USDC", 1),
    TradingPair("polygon", "WBTC", "USDC", 2),
]


def get_pairs_for_chain(chain: str) -> list[TradingPair]:
    return [pair for pair in TRADING_PAIRS if pair.chain.lower() == chain.lower()]