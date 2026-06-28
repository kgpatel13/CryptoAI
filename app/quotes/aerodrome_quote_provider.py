from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.abis import AERODROME_ROUTER_ABI
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.registry.tokens import get_token


AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5bB28Aac43B9"
AERODROME_FACTORY = "0x420dd381b31aef6683db6b902084cb0ffece40da"


class AerodromeQuoteProvider(QuoteProvider):
    @property
    def chain(self) -> str:
        return "base"

    @property
    def dex(self) -> str:
        return "Aerodrome"

    def __init__(self) -> None:
        chain_config = SUPPORTED_CHAINS["base"]
        self.client = RpcClient(chain_config)
        self.web3 = self.client.web3
        self.router = self.web3.eth.contract(
            address=Web3.to_checksum_address(AERODROME_ROUTER),
            abi=AERODROME_ROUTER_ABI,
        )

    def supports(self, request: QuoteRequest) -> bool:
        return request.chain.lower() == self.chain and request.dex.lower() == self.dex.lower()

    def get_quote(self, request: QuoteRequest) -> DexQuote:
        token_in = get_token("base", request.token_in)
        token_out = get_token("base", request.token_out)

        if token_in is None or token_out is None:
            return DexQuote(
                chain=request.chain,
                dex=self.dex,
                token_in=request.token_in,
                token_out=request.token_out,
                amount_in=request.amount_in,
                amount_out=None,
                price=None,
                error="Token not found in registry",
            )

        try:
            amount_in_units = int(request.amount_in * Decimal(10**token_in.decimals))
            routes = [
                (
                    Web3.to_checksum_address(token_in.address),
                    Web3.to_checksum_address(token_out.address),
                    False,
                    Web3.to_checksum_address(AERODROME_FACTORY),
                )
            ]
            amounts = self.router.functions.getAmountsOut(amount_in_units, routes).call()
            amount_out = Decimal(amounts[-1]) / Decimal(10**token_out.decimals)
            price = amount_out / request.amount_in if request.amount_in > 0 else None
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
            return DexQuote(
                chain=request.chain,
                dex=self.dex,
                token_in=request.token_in,
                token_out=request.token_out,
                amount_in=request.amount_in,
                amount_out=None,
                price=None,
                error=str(exc),
            )
