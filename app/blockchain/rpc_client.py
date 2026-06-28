from __future__ import annotations

import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator

from dotenv import load_dotenv
from web3 import Web3

from app.blockchain.chains import ChainConfig
from app.resilience.rpc_provider_pool import RpcEndpoint, RpcProviderPool

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
    """Web3 client with provider pool, failover, circuit breakers, and health scoring.

    Environment variables may contain one RPC URL or a comma-separated list:

        BASE_RPC=https://mainnet.base.org,https://base-rpc.publicnode.com

    Private RPC URLs should be listed first. Public fallbacks are appended unless
    already present.
    """

    def __init__(self, chain: ChainConfig):
        self.chain = chain
        self.rpc_urls = self._load_rpc_urls(chain.rpc_env_key)
        if not self.rpc_urls:
            raise ValueError(f"Missing RPC URL for {chain.name}: {chain.rpc_env_key}")

        timeout = int(os.getenv("CRYPTOAI_RPC_TIMEOUT_SECONDS", "10"))
        failure_threshold = int(os.getenv("CRYPTOAI_RPC_CIRCUIT_FAILURE_THRESHOLD", "2"))
        cooldown = int(os.getenv("CRYPTOAI_RPC_CIRCUIT_COOLDOWN_SECONDS", "60"))
        self.provider_pool = RpcProviderPool(
            chain=chain.name,
            urls=self.rpc_urls,
            timeout_seconds=timeout,
            failure_threshold=failure_threshold,
            cooldown_seconds=cooldown,
        )
        self.web3, self.rpc_url_used = self._connect_first_available(self.rpc_urls)

    def _load_rpc_urls(self, env_key: str) -> list[str]:
        env_value = os.getenv(env_key, "")
        urls = [item.strip() for item in env_value.split(",") if item.strip()]

        for fallback in DEFAULT_RPC_FALLBACKS.get(env_key, []):
            if fallback not in urls:
                urls.append(fallback)

        return urls

    def _connect_first_available(self, urls: list[str]) -> tuple[Web3, str]:
        last_web3 = Web3(Web3.HTTPProvider(urls[0], request_kwargs={"timeout": 10}))
        last_url = urls[0]

        for endpoint, candidate in self.provider_pool.candidates():
            start = time.perf_counter()
            try:
                if candidate.is_connected():
                    latency_ms = (time.perf_counter() - start) * 1000
                    self.provider_pool.record_success(endpoint, latency_ms)
                    return candidate, endpoint.url
                latency_ms = (time.perf_counter() - start) * 1000
                self.provider_pool.record_failure(endpoint, "RPC is_connected returned false", latency_ms)
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                self.provider_pool.record_failure(endpoint, f"{type(exc).__name__}: {exc}", latency_ms)
            last_web3 = candidate
            last_url = endpoint.url

        return last_web3, last_url

    def iter_web3_candidates(self) -> Iterator[tuple[RpcEndpoint, Web3]]:
        yield from self.provider_pool.candidates()

    def record_rpc_success(self, endpoint: RpcEndpoint, latency_ms: float) -> None:
        self.rpc_url_used = endpoint.url
        self.provider_pool.record_success(endpoint, latency_ms)

    def record_rpc_failure(self, endpoint: RpcEndpoint, error: str, latency_ms: float | None = None) -> None:
        self.provider_pool.record_failure(endpoint, error, latency_ms)

    def health_check(self) -> ChainHealth:
        last_error = "No RPC candidates available; all circuits may be open."
        for endpoint, web3 in self.iter_web3_candidates():
            start = time.perf_counter()
            try:
                connected = web3.is_connected()
                if not connected:
                    latency_ms = (time.perf_counter() - start) * 1000
                    self.record_rpc_failure(endpoint, "RPC connection failed", latency_ms)
                    last_error = "RPC connection failed"
                    continue

                latest_block = web3.eth.block_number
                chain_id = web3.eth.chain_id
                gas_price_wei = web3.eth.gas_price
                gas_price_gwei = Decimal(gas_price_wei) / Decimal(10**9)
                latency_ms = (time.perf_counter() - start) * 1000
                self.record_rpc_success(endpoint, latency_ms)

                return ChainHealth(
                    chain_name=self.chain.name,
                    connected=True,
                    latest_block=latest_block,
                    chain_id=chain_id,
                    gas_price_gwei=gas_price_gwei,
                    rpc_url_used=endpoint.url,
                )

            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                last_error = f"{type(exc).__name__}: {exc}"
                self.record_rpc_failure(endpoint, last_error, latency_ms)

        return ChainHealth(
            chain_name=self.chain.name,
            connected=False,
            latest_block=None,
            chain_id=None,
            gas_price_gwei=None,
            error=last_error,
            rpc_url_used=self.rpc_url_used,
        )
