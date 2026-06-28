from __future__ import annotations

import argparse
from pathlib import Path

from app.risk.portfolio_risk_service import PortfolioRiskService


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair or reset CryptoAI paper portfolio accounting state.")
    parser.add_argument("--state", default="data/paper_portfolio_state.json", help="Paper portfolio state path.")
    parser.add_argument("--reset", action="store_true", help="Reset paper portfolio state to a clean initial portfolio.")
    args = parser.parse_args()

    service = PortfolioRiskService(state_path=Path(args.state))
    if args.reset:
        state = service._initial_state()
        service.save_state(state)
        print(f"Reset paper portfolio state at {args.state}")
        return

    state = service.load_state()
    service.save_state(state)
    summary = service.summary()
    print("Repaired paper portfolio state")
    print(f"state_path={args.state}")
    print(f"version={state.get('version')}")
    print(f"cash_usd={summary.get('cash_usd')}")
    print(f"realized_pnl_usd={summary.get('realized_pnl_usd')}")
    print(f"unrealized_pnl_usd={summary.get('unrealized_pnl_usd')}")
    print(f"open_positions={summary.get('open_positions')}")
    print(f"closed_positions={summary.get('closed_positions')}")


if __name__ == "__main__":
    main()
