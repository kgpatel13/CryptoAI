from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.reporting.paper_report import PaperReportService


class LegacyPaperArchiveService:
    """Archives pre-repair paper rows that should not count as clean evidence."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.paper_orders_file = self.data_dir / "paper_orders.jsonl"
        self.archive_file = self.data_dir / "paper_orders_legacy_archive.jsonl"

    def archive(self, *, dry_run: bool = False) -> dict[str, Any]:
        orders = self._read_jsonl(self.paper_orders_file)
        legacy = [order for order in orders if PaperReportService._legacy_accounting_warning(order)]
        active = [order for order in orders if not PaperReportService._legacy_accounting_warning(order)]
        archived_at = self._utc_now()
        payload = {
            "generated_at": archived_at,
            "mode": "paper",
            "dry_run": dry_run,
            "input_order_count": len(orders),
            "archived_order_count": len(legacy),
            "active_order_count": len(active),
            "paper_orders_file": str(self.paper_orders_file),
            "archive_file": str(self.archive_file),
            "notes": [
                "Only legacy inverse-pair rows from pre-repair accounting are archived.",
                "Archived rows are excluded from future clean evidence gates but remain available for audit.",
            ],
        }
        if dry_run or not legacy:
            return payload

        with self.archive_file.open("a", encoding="utf-8") as archive:
            for order in legacy:
                archived = dict(order)
                archived["archived_at"] = archived_at
                archived["archive_reason"] = (
                    "Pre-repair inverse-pair accounting row; excluded from clean evidence."
                )
                archive.write(json.dumps(archived) + "\n")

        self.paper_orders_file.write_text(
            "".join(json.dumps(order) + "\n" for order in active),
            encoding="utf-8",
        )
        return payload

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive legacy paper-order rows from clean evidence.")
    parser.add_argument("--dry-run", action="store_true", help="Count legacy rows without rewriting paper_orders.jsonl.")
    args = parser.parse_args()
    print(json.dumps(LegacyPaperArchiveService().archive(dry_run=args.dry_run), indent=2))


if __name__ == "__main__":
    main()
