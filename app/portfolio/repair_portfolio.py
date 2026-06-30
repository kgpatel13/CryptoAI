from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from app.operations.paper_settings_service import PaperSettingsService
from app.risk.portfolio_risk_service import PortfolioRiskService


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair or reset CryptoAI paper portfolio accounting state.")
    parser.add_argument("--state", default="data/paper_portfolio_state.json", help="Paper portfolio state path.")
    parser.add_argument("--reset", action="store_true", help="Reset paper portfolio state to a clean initial portfolio.")
    parser.add_argument("--keep-orders", action="store_true", help="Keep paper_orders.jsonl when resetting the portfolio state.")
    parser.add_argument("--use-settings", action="store_true", help="Apply config/paper_trading_settings.json before repairing or resetting.")
    args = parser.parse_args()

    if args.use_settings:
        settings_service = PaperSettingsService()
        settings = settings_service.load()
        validation = settings_service.validate(settings)
        if validation["status"] != "VALID":
            raise RuntimeError(
                "Refusing to use invalid paper settings: "
                + "; ".join(row["message"] for row in validation["findings"])
            )
        settings_service.apply_runtime_environment(validation["settings"])

    service = PortfolioRiskService(state_path=Path(args.state))
    if args.reset:
        state = service._initial_state()
        service.save_state(state)
        archived_orders = 0
        if not args.keep_orders:
            archived_orders = _archive_paper_orders(Path(args.state).parent)
        print(f"Reset paper portfolio state at {args.state}")
        if args.keep_orders:
            print("Kept paper_orders.jsonl unchanged.")
        else:
            print(f"Archived {archived_orders} paper order row(s) and cleared active paper_orders.jsonl.")
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


def _archive_paper_orders(data_dir: Path) -> int:
    orders_file = data_dir / "paper_orders.jsonl"
    if not orders_file.exists():
        return 0
    rows = [line for line in orders_file.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    if not rows:
        return 0
    archived_at = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    archive_file = data_dir / "paper_orders_reset_archive.jsonl"
    with archive_file.open("a", encoding="utf-8") as archive:
        for line in rows:
            try:
                payload = json.loads(line)
                if isinstance(payload, dict):
                    payload["archived_at"] = archived_at
                    payload["archive_reason"] = "Paper portfolio reset."
                    archive.write(json.dumps(payload) + "\n")
                    continue
            except json.JSONDecodeError:
                pass
            archive.write(
                json.dumps(
                    {
                        "archived_at": archived_at,
                        "archive_reason": "Paper portfolio reset; original row was not valid JSON.",
                        "raw": line,
                    }
                )
                + "\n"
            )
    orders_file.write_text("", encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    main()
