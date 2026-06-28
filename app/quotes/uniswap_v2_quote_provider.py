from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.abis import UNISWAP_V2_ROUTER_ABI
from app.quotes.models import DexQuote, QuoteRequest
from app.quotes.provider_interface import QuoteProvider
from app.registry.tokens import get_token


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
        self.web3 = self.client.web3
        self.router = self.web3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V2_BASE_ROUTER),
            abi=UNISWAP_V2_ROUTER_ABI,
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
            path = [
                Web3.to_checksum_address(token_in.address),
                Web3.to_checksum_address(token_out.address),
            ]
            amounts = self.router.functions.getAmountsOut(amount_in_units, path).call()
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
