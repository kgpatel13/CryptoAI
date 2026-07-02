from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

REPORT_FILES = [
    "atomic_live_arbitrage.json",
    "atomic_live_arbitrage.md",
    "transaction_simulation.json",
    "transaction_simulation.md",
    "live_execution_engine.json",
    "live_execution_engine.md",
    "live_control_center.json",
    "live_control_center.md",
    "live_readiness_checklist.json",
    "live_readiness_checklist.md",
    "live_safety.json",
    "live_safety.md",
    "live_shadow_gate.json",
    "live_shadow_gate.md",
    "execution_realism.json",
    "execution_realism.md",
    "quote_diagnostics.md",
    "provider_monitor.json",
    "provider_monitor.md",
    "report_audit.json",
    "report_audit.md",
    "wallet_preflight.json",
    "wallet_preflight.md",
]

DATA_FILES = [
    "live_autopilot_decisions.jsonl",
    "live_pilot_orders.jsonl",
    "multi_dex_opportunities.jsonl",
    "opportunity_decisions.jsonl",
    "quote_diagnostics.jsonl",
    "quote_snapshot.json",
    "runtime_state.json",
    "live_autopilot.lock",
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def backup_file(path: Path, backup_root: Path) -> None:
    if not path.exists():
        return
    target = backup_root / path.parent.name / path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clear stale CryptoAI live runtime reports/caches without touching wallet, .env, contracts, or code.")
    parser.add_argument("--confirm", required=True, help="Must be RESET_LIVE_STATE")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--report-dir", default="reports")
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()
    if args.confirm != "RESET_LIVE_STATE":
        raise SystemExit("Refusing reset. Use --confirm RESET_LIVE_STATE")

    data_dir = Path(args.data_dir)
    report_dir = Path(args.report_dir)
    backup_root = Path("backups") / f"live_reset_{utc_now().replace(':', '').replace('-', '').replace('Z', 'Z')}"
    removed: list[str] = []
    backed_up: list[str] = []

    for folder, names in [(report_dir, REPORT_FILES), (data_dir, DATA_FILES)]:
        folder.mkdir(parents=True, exist_ok=True)
        for name in names:
            path = folder / name
            if not path.exists():
                continue
            if not args.no_backup:
                backup_file(path, backup_root)
                backed_up.append(str(path))
            path.unlink()
            removed.append(str(path))

    marker = {
        "reset_at": utc_now(),
        "removed_count": len(removed),
        "removed": removed,
        "backup_dir": None if args.no_backup else str(backup_root),
        "note": "This cleared local reports/caches only. It did not revoke USDC allowance, move funds, modify .env, or touch the deployed contract.",
    }
    (data_dir / "live_runtime_reset_marker.json").write_text(json.dumps(marker, indent=2), encoding="utf-8")
    print(json.dumps(marker, indent=2))


if __name__ == "__main__":
    main()
