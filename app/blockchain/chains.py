from dataclasses import dataclass


@dataclass(frozen=True)
class ChainConfig:
    name: str
    chain_id: int
    rpc_env_key: str
    native_symbol: str
    block_explorer: str


SUPPORTED_CHAINS: dict[str, ChainConfig] = {
    "base": ChainConfig(
        name="Base",
        chain_id=8453,
        rpc_env_key="BASE_RPC",
        native_symbol="ETH",
        block_explorer="https://basescan.org",
    ),
    "polygon": ChainConfig(
        name="Polygon",
        chain_id=137,
        rpc_env_key="POLYGON_RPC",
        native_symbol="POL",
        block_explorer="https://polygonscan.com",
    ),
    "arbitrum": ChainConfig(
        name="Arbitrum One",
        chain_id=42161,
        rpc_env_key="ARBITRUM_RPC",
        native_symbol="ETH",
        block_explorer="https://arbiscan.io",
    ),
    "ethereum": ChainConfig(
        name="Ethereum",
        chain_id=1,
        rpc_env_key="ETHEREUM_RPC",
        native_symbol="ETH",
        block_explorer="https://etherscan.io",
    ),
}