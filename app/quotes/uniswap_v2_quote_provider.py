from __future__ import annotations

import time
from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.abis import UNISWAP_V2_ROUTER_ABI
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.registry.tokens import get_token
from app.resilience.provider_health import provider_health_registry
from app.resilience.retry_policy import RetryPolicy


UNISWAP_V2_BASE_ROUTER = "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24"


class UniswapV2QuoteProvider(QuoteProvider):
    @property
    def chain(self) -> str:
        return "base"

    @property
    def dex(self) -> str:
        return "Uniswap V2"

    def __init__(self) -> None:
        chain_config = SUPPORTED_CHAINS["base"]
        self.client = RpcClient(chain_config)
        self.rpc_urls = self.client.rpc_urls
        self.retry_policy = RetryPolicy(max_attempts=2, base_delay_seconds=0.15, max_delay_seconds=1.0)

    def supports(self, request: QuoteRequest) -> bool:
        return request.chain.lower() == self.chain and request.dex.lower() == self.dex.lower()

    def get_quote(self, request: QuoteRequest) -> DexQuote:
        token_in = get_token("base", request.token_in)
        token_out = get_token("base", request.token_out)

        if token_in is None or token_out is None:
            return self._error_quote(request, "Token not found in registry")

        amount_in_units = int(request.amount_in * Decimal(10**token_in.decimals))
        path = [
            Web3.to_checksum_address(token_in.address),
            Web3.to_checksum_address(token_out.address),
        ]

        last_error = "No RPC candidates available."
        for endpoint, web3 in self.client.iter_web3_candidates():
            start = time.perf_counter()
            try:
                router = web3.eth.contract(
                    address=Web3.to_checksum_address(UNISWAP_V2_BASE_ROUTER),
                    abi=UNISWAP_V2_ROUTER_ABI,
                )

                def call_router():
                    return router.functions.getAmountsOut(amount_in_units, path).call()

                amounts = self.retry_policy.run(call_router)
                amount_out = Decimal(amounts[-1]) / Decimal(10**token_out.decimals)
                price = amount_out / request.amount_in if request.amount_in > 0 else None
                latency_ms = (time.perf_counter() - start) * 1000
                self.client.record_rpc_success(endpoint, latency_ms)
                provider_health_registry.record_success(self.dex, "dex", latency_ms, chain=self.chain, rpc=endpoint.name)

                return DexQuote(
                    chain=request.chain,
                    dex=self.dex,
                    token_in=token_in.symbol,
                    token_out=token_out.symbol,
                    amount_in=request.amount_in,
                    amount_out=amount_out,
                    price=price,
                )
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                last_error = f"{type(exc).__name__}: {exc}"
                self.client.record_rpc_failure(endpoint, last_error, latency_ms)
                provider_health_registry.record_failure(self.dex, "dex", self._friendly_error(last_error), latency_ms, chain=self.chain, rpc=endpoint.name)

        return self._error_quote(request, self._friendly_error(last_error))

    def _error_quote(self, request: QuoteRequest, error: str) -> DexQuote:
        return DexQuote(
            chain=request.chain,
            dex=self.dex,
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            amount_out=None,
            price=None,
            error=error[:300],
        )

    @staticmethod
    def _is_rate_limit(error: str) -> bool:
        lower = error.lower()
        return "429" in lower or "too many requests" in lower or "rate limit" in lower

    @classmethod
    def _friendly_error(cls, error: str) -> str:
        if cls._is_rate_limit(error):
            return "RPC rate limit while reading Uniswap V2 quote. Configure BASE_RPC with a private RPC or wait for cache fallback."
        return error[:300]
