from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.abis import AERODROME_ROUTER_ABI
from app.quotes.models import DexQuote
from app.quotes.provider import QuoteProvider
from app.registry.tokens import get_token


AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5bB28Aac43B9"
AERODROME_FACTORY = "0x420dd381b31aef6683db6b902084cb0ffece40da"


class AerodromeQuoteProvider(QuoteProvider):
    chain = "base"
    dex_name = "Aerodrome"

    def __init__(self) -> None:
        chain_config = SUPPORTED_CHAINS["base"]
        self.client = RpcClient(chain_config)
        self.web3 = self.client.web3
        self.router = self.web3.eth.contract(
            address=Web3.to_checksum_address(AERODROME_ROUTER),
            abi=AERODROME_ROUTER_ABI,
        )

    def get_quote(
        self,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in: Decimal,
    ) -> DexQuote:
        return self._get_quote(
            token_in_symbol=token_in_symbol,
            token_out_symbol=token_out_symbol,
            amount_in=amount_in,
            stable=False,
        )

    def _get_quote(
        self,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in: Decimal,
        stable: bool = False,
    ) -> DexQuote:
        token_in = get_token("base", token_in_symbol)
        token_out = get_token("base", token_out_symbol)

        if token_in is None or token_out is None:
            return DexQuote(
                chain=self.chain,
                dex=self.dex_name,
                token_in=token_in_symbol,
                token_out=token_out_symbol,
                amount_in=amount_in,
                amount_out=None,
                price=None,
                error="Token not found in registry",
            )

        try:
            amount_in_units = int(amount_in * Decimal(10 ** token_in.decimals))

            routes = [
                (
                    Web3.to_checksum_address(token_in.address),
                    Web3.to_checksum_address(token_out.address),
                    stable,
                    Web3.to_checksum_address(AERODROME_FACTORY),
                )
            ]

            amounts = self.router.functions.getAmountsOut(amount_in_units, routes).call()

            amount_out_units = amounts[-1]
            amount_out = Decimal(amount_out_units) / Decimal(10 ** token_out.decimals)
            price = amount_out / amount_in if amount_in > 0 else None

            return DexQuote(
                chain=self.chain,
                dex=self.dex_name,
                token_in=token_in.symbol,
                token_out=token_out.symbol,
                amount_in=amount_in,
                amount_out=amount_out,
                price=price,
            )

        except Exception as exc:
            return DexQuote(
                chain=self.chain,
                dex=self.dex_name,
                token_in=token_in_symbol,
                token_out=token_out_symbol,
                amount_in=amount_in,
                amount_out=None,
                price=None,
                error=str(exc),
            )
