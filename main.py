from rich.console import Console
from rich.table import Table

from app.blockchain.chains import SUPPORTED_CHAINS
from app.services.chain_health_service import ChainHealthService
from app.registry.tokens import get_tokens_for_chain
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain

console = Console()


def show_chain_health() -> None:
    service = ChainHealthService()
    results = service.check_all_chains()

    table = Table(title="CryptoAI Multi-Chain RPC Health Check")
    table.add_column("Chain", style="bold")
    table.add_column("Connected")
    table.add_column("Chain ID")
    table.add_column("Latest Block")
    table.add_column("Gas Gwei")
    table.add_column("Error")

    for result in results:
        table.add_row(
            result.chain_name,
            "✅ Yes" if result.connected else "❌ No",
            str(result.chain_id) if result.chain_id else "-",
            str(result.latest_block) if result.latest_block else "-",
            f"{result.gas_price_gwei:.6f}" if result.gas_price_gwei else "-",
            result.error or "",
        )

    console.print(table)


def show_registry_summary() -> None:
    table = Table(title="CryptoAI Registry Summary")
    table.add_column("Chain", style="bold")
    table.add_column("Tokens")
    table.add_column("DEXs")
    table.add_column("Pairs")

    for chain_key, chain in SUPPORTED_CHAINS.items():
        tokens = get_tokens_for_chain(chain_key)
        dexes = get_dexes_for_chain(chain_key)
        pairs = get_pairs_for_chain(chain_key)

        table.add_row(
            chain.name,
            ", ".join(token.symbol for token in tokens),
            ", ".join(dex.name for dex in dexes),
            ", ".join(f"{pair.base_symbol}/{pair.quote_symbol}" for pair in pairs),
        )

    console.print(table)


def main() -> None:
    show_chain_health()
    console.print()
    show_registry_summary()


if __name__ == "__main__":
    main()