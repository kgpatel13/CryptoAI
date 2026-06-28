from __future__ import annotations

import requests


class DexScreenerProvider:
    """Read-only DexScreener provider.

    This is not an execution source. It is useful for liquidity, volume,
    pair discovery, and sanity checking quotes before any strategy considers
    execution.
    """

    BASE_URL = "https://api.dexscreener.com/latest/dex"

    def search_pairs(self, query: str) -> list[dict]:
        url = f"{self.BASE_URL}/search"
        response = requests.get(url, params={"q": query}, timeout=5)
        response.raise_for_status()
        payload = response.json()
        return payload.get("pairs", []) or []

    def get_base_major_pairs(self) -> list[dict]:
        pairs = self.search_pairs("base WETH USDC")
        return [
            p for p in pairs
            if str(p.get("chainId", "")).lower() == "base"
        ][:10]
