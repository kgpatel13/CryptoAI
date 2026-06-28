from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal

from dotenv import load_dotenv
from web3 import Web3

from app.blockchain.chains import ChainConfig

load_dotenv()


DEFAULT_RPC_FALLBACKS: dict[str, list[str]] = {
    "BASE_RPC": [
        "https://mainnet.base.org",
        "https://base-rpc.publicnode.com",
    ],
    "POLYGON_RPC": [
        "https://polygon-bor-rpc.publicnode.com",
        "https://polygon-rpc.com",
    ],
    "ARBITRUM_RPC": [
        "https://arb1.arbitrum.io/rpc",
        "https://arbitrum-one-rpc.publicnode.com",
    ],
    "ETHEREUM_RPC": [
        "https://ethereum-rpc.publicnode.com",
        "https://rpc.ankr.com/eth",
    ],
}


@dataclass
class ChainHealth:
    chain_name: str
    connected: bool
    latest_block: int | None
    chain_id: int | None
    gas_price_gwei: Decimal | None
    error: str | None = None
    rpc_url_used: str | None = None


class RpcClient:
    """Web3 client with simple RPC fallback support.

    Environment variables may contain one RPC URL or a comma-separated list:

        BASE_RPC=https://mainnet.base.org,https://base-rpc.publicnode.com

    The client tries each URL until one connects.
    """

    def __init__(self, chain: ChainConfig):
        self.chain = chain
        self.rpc_urls = self._load_rpc_urls(chain.rpc_env_key)
        if not self.rpc_urls:
            raise ValueError(f"Missing RPC URL for {chain.name}: {chain.rpc_env_key}")

        self.web3, self.rpc_url_used = self._connect_first_available(self.rpc_urls)

    def _load_rpc_urls(self, env_key: str) -> list[str]:
        env_value = os.getenv(env_key, "")
        urls = [item.strip() for item in env_value.split(",") if item.strip()]

        for fallback in DEFAULT_RPC_FALLBACKS.get(env_key, []):
            if fallback not in urls:
                urls.append(fallback)

        return urls

    def _connect_first_available(self, urls: list[str]) -> tuple[Web3, str]:
        last_web3 = Web3(Web3.HTTPProvider(urls[0], request_kwargs={"timeout": 20}))
        last_url = urls[0]

        for url in urls:
            candidate = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 20}))
            try:
                if candidate.is_connected():
                    return candidate, url
            except Exception:
                pass
            last_web3 = candidate
            last_url = url

        return last_web3, last_url

    def health_check(self) -> ChainHealth:
        try:
            connected = self.web3.is_connected()
            if not connected:
                return ChainHealth(
                    chain_name=self.chain.name,
                    connected=False,
                    latest_block=None,
                    chain_id=None,
                    gas_price_gwei=None,
                    error="RPC connection failed",
                    rpc_url_used=self.rpc_url_used,
                )

            latest_block = self.web3.eth.block_number
            chain_id = self.web3.eth.chain_id
            gas_price_wei = self.web3.eth.gas_price
            gas_price_gwei = Decimal(gas_price_wei) / Decimal(10**9)

            return ChainHealth(
                chain_name=self.chain.name,
                connected=True,
                latest_block=latest_block,
                chain_id=chain_id,
                gas_price_gwei=gas_price_gwei,
                rpc_url_used=self.rpc_url_used,
            )

        except Exception as exc:
            return ChainHealth(
                chain_name=self.chain.name,
                connected=False,
                latest_block=None,
                chain_id=None,
                gas_price_gwei=None,
                error=str(exc),
                rpc_url_used=self.rpc_url_used,
            )
