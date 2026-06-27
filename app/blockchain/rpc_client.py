import os
from dataclasses import dataclass
from decimal import Decimal

from dotenv import load_dotenv
from web3 import Web3

from app.blockchain.chains import ChainConfig

load_dotenv()


@dataclass
class ChainHealth:
    chain_name: str
    connected: bool
    latest_block: int | None
    chain_id: int | None
    gas_price_gwei: Decimal | None
    error: str | None = None


class RpcClient:
    def __init__(self, chain: ChainConfig):
        self.chain = chain
        rpc_url = os.getenv(chain.rpc_env_key)

        if not rpc_url:
            raise ValueError(f"Missing RPC URL for {chain.name}: {chain.rpc_env_key}")

        self.web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 20}))

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
            )

        except Exception as exc:
            return ChainHealth(
                chain_name=self.chain.name,
                connected=False,
                latest_block=None,
                chain_id=None,
                gas_price_gwei=None,
                error=str(exc),
            )