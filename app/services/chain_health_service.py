from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient, ChainHealth


class ChainHealthService:
    def check_all_chains(self) -> list[ChainHealth]:
        results: list[ChainHealth] = []

        for chain in SUPPORTED_CHAINS.values():
            client = RpcClient(chain)
            results.append(client.health_check())

        return results