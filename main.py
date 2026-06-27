from rich.console import Console
from rich.table import Table

from app.services.chain_health_service import ChainHealthService

console = Console()


def main() -> None:
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


if __name__ == "__main__":
    main()