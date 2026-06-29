from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.reporting.legacy_paper_archive import LegacyPaperArchiveService


class LegacyPaperArchiveTests(unittest.TestCase):
    def test_archives_only_legacy_inverse_pair_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            active_order = {
                "order_id": "clean",
                "pair": "WETH/USDC",
                "status": "FILLED",
                "notional_usd": "100",
                "simulated_fill_price_usd": "1500",
                "simulated_quantity": "0.066",
            }
            legacy_order = {
                "order_id": "legacy",
                "pair": "USDC/WETH",
                "status": "FILLED",
                "notional_usd": "100",
                "simulated_fill_price_usd": "0.00063",
                "simulated_quantity": "158000",
            }
            (data_dir / "paper_orders.jsonl").write_text(
                json.dumps(active_order) + "\n" + json.dumps(legacy_order) + "\n",
                encoding="utf-8",
            )

            payload = LegacyPaperArchiveService(data_dir=data_dir).archive()

            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["archived_order_count"], 1)
            active_rows = self._read_jsonl(data_dir / "paper_orders.jsonl")
            archived_rows = self._read_jsonl(data_dir / "paper_orders_legacy_archive.jsonl")
            self.assertEqual([row["order_id"] for row in active_rows], ["clean"])
            self.assertEqual([row["order_id"] for row in archived_rows], ["legacy"])
            self.assertIn("archive_reason", archived_rows[0])

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
