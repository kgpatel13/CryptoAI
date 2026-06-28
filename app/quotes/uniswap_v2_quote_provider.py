from decimal import Decimal

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.quotes.models import DexQuote
from app.quotes.provider import QuoteProvider
from app.registry.tokens import get_token


UNISWAP_V2_BASE_ROUTER = "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24"

UNISWAP_V2_ROUTER_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    }
]


class UniswapV2QuoteProvider(QuoteProvider):
    chain = "base"
    dex_name = "Uniswap V2"

    def __init__(self) -> None:
        chain_config = SUPPORTED_CHAINS["base"]
        self.client = RpcClient(chain_config)
        self.web3 = self.client.web3
        self.router = self.web3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V2_BASE_ROUTER),
            abi=UNISWAP_V2_ROUTER_ABI,
        )

    def get_quote(
        self,
        token_in_symbol: str,
        token_out_symbol: str,
        amount_in: Decimal,
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

            path = [
                Web3.to_checksum_address(token_in.address),
                Web3.to_checksum_address(token_out.address),
            ]

            amounts = self.router.functions.getAmountsOut(amount_in_units, path).call()

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
