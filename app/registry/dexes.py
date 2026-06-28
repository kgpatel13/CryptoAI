from dataclasses import dataclass


@dataclass(frozen=True)
class Dex:
    name: str
    chain: str
    dex_type: str
    router_address: str | None
    notes: str = ""


DEXES: dict[str, list[Dex]] = {
    "base": [
        Dex("Uniswap V2", "base", "v2", "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24", "Uniswap V2-compatible router on Base"),
        Dex("Uniswap V3", "base", "v3", None, "Primary concentrated liquidity DEX; quote provider not implemented yet"),
        Dex("Aerodrome", "base", "solidly", "0xcF77a3Ba9A5CA399B7c97c74d54e5bB28Aac43B9", "Aerodrome router"),
    ],
    "ethereum": [
        Dex("Uniswap V3", "ethereum", "v3", None),
        Dex("SushiSwap", "ethereum", "v2", None),
        Dex("Curve", "ethereum", "curve", None),
    ],
    "arbitrum": [
        Dex("Uniswap V3", "arbitrum", "v3", None),
        Dex("Camelot", "arbitrum", "v2/v3", None),
        Dex("SushiSwap", "arbitrum", "v2", None),
    ],
    "polygon": [
        Dex("Uniswap V3", "polygon", "v3", None),
        Dex("QuickSwap", "polygon", "v2/v3", None),
    ],
}


def get_dexes_for_chain(chain: str) -> list[Dex]:
    return DEXES.get(chain.lower(), [])
