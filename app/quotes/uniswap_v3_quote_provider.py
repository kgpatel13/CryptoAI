from __future__ import annotations

import time
from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.abis import UNISWAP_V3_QUOTER_V2_ABI
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.registry.tokens import get_token
from app.resilience.provider_health import provider_health_registry
from app.resilience.retry_policy import RetryPolicy


UNISWAP_V3_BASE_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
UNISWAP_V3_BASE_SWAP_ROUTER_02 = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_BASE_QUOTER_V2 = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"
UNISWAP_V3_FEE_TIERS = (500, 3000, 10000)


class UniswapV3QuoteProvider(QuoteProvider):
    @property
    def chain(self) -> str:
        return "base"

    @property
    def dex(self) -> str:
        return "Uniswap V3"

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
        token_in_address = Web3.to_checksum_address(token_in.address)
        token_out_address = Web3.to_checksum_address(token_out.address)

        last_error = "No RPC candidates available."
        for endpoint, web3 in self.client.iter_web3_candidates():
            start = time.perf_counter()
            try:
                quoter = web3.eth.contract(
                    address=Web3.to_checksum_address(UNISWAP_V3_BASE_QUOTER_V2),
                    abi=UNISWAP_V3_QUOTER_V2_ABI,
                )
                best_amount_out: Decimal | None = None
                best_fee_tier: int | None = None
                tier_errors: list[str] = []

                for fee_tier in UNISWAP_V3_FEE_TIERS:
                    params = (token_in_address, token_out_address, amount_in_units, fee_tier, 0)
                    try:
                        amounts = self.retry_policy.run(lambda: quoter.functions.quoteExactInputSingle(params).call())
                    except Exception as exc:
                        tier_errors.append(f"{fee_tier}: {type(exc).__name__}: {exc}")
                        continue

                    amount_out = Decimal(amounts[0]) / Decimal(10**token_out.decimals)
                    if best_amount_out is None or amount_out > best_amount_out:
                        best_amount_out = amount_out
                        best_fee_tier = fee_tier

                latency_ms = (time.perf_counter() - start) * 1000
                if best_amount_out is None:
                    last_error = "; ".join(tier_errors[-2:]) if tier_errors else "No Uniswap V3 fee tier returned a quote."
                    self.client.record_rpc_failure(endpoint, last_error, latency_ms)
                    provider_health_registry.record_failure(self.dex, "dex", self._friendly_error(last_error), latency_ms, chain=self.chain, rpc=endpoint.name)
                    continue

                price = best_amount_out / request.amount_in if request.amount_in > 0 else None
                self.client.record_rpc_success(endpoint, latency_ms)
                provider_health_registry.record_success(self.dex, "dex", latency_ms, chain=self.chain, rpc=endpoint.name)

                return DexQuote(
                    chain=request.chain,
                    dex=self.dex,
                    token_in=token_in.symbol,
                    token_out=token_out.symbol,
                    amount_in=request.amount_in,
                    amount_out=best_amount_out,
                    price=price,
                    error=None if best_fee_tier is not None else "Uniswap V3 quote returned without fee tier metadata.",
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
            return "RPC rate limit while reading Uniswap V3 quote. Configure BASE_RPC with a private RPC or wait for cache fallback."
        lower = error.lower()
        if "execution reverted" in lower or "call contract function" in lower or "bad function call" in lower:
            return "Uniswap V3 quote unavailable for this route/fee tier/RPC. Provider kept registered; scanner will skip this row."
        return error[:300]
