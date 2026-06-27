from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    symbol: str
    name: str
    chain: str
    address: str
    decimals: int
    coingecko_id: str | None = None


TOKENS: dict[str, list[Token]] = {
    "base": [
        Token("USDC", "USD Coin", "base", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6, "usd-coin"),
        Token("WETH", "Wrapped Ether", "base", "0x4200000000000000000000000000000000000006", 18, "ethereum"),
        Token("cbBTC", "Coinbase Wrapped BTC", "base", "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33BF", 8, "bitcoin"),
    ],
    "ethereum": [
        Token("USDC", "USD Coin", "ethereum", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6, "usd-coin"),
        Token("WETH", "Wrapped Ether", "ethereum", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18, "ethereum"),
        Token("WBTC", "Wrapped Bitcoin", "ethereum", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8, "bitcoin"),
    ],
    "arbitrum": [
        Token("USDC", "USD Coin", "arbitrum", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6, "usd-coin"),
        Token("WETH", "Wrapped Ether", "arbitrum", "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", 18, "ethereum"),
        Token("WBTC", "Wrapped Bitcoin", "arbitrum", "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", 8, "bitcoin"),
    ],
    "polygon": [
        Token("USDC", "USD Coin", "polygon", "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359", 6, "usd-coin"),
        Token("WETH", "Wrapped Ether", "polygon", "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18, "ethereum"),
        Token("WBTC", "Wrapped Bitcoin", "polygon", "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6", 8, "bitcoin"),
    ],
}


def get_tokens_for_chain(chain: str) -> list[Token]:
    return TOKENS.get(chain.lower(), [])


def get_token(chain: str, symbol: str) -> Token | None:
    for token in get_tokens_for_chain(chain):
        if token.symbol.upper() == symbol.upper():
            return token
    return None