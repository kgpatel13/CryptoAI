from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.portfolio.repair_portfolio import _archive_paper_orders


class RepairPortfolioTests(unittest.TestCase):
    def test_archive_paper_orders_preserves_rows_and_clears_active_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            orders_file = data / "paper_orders.jsonl"
            orders_file.write_text(
                json.dumps({"order_id": "o1", "status": "CLOSED"}) + "\n",
                encoding="utf-8",
            )

            archived = _archive_paper_orders(data)

            self.assertEqual(archived, 1)
            self.assertEqual(orders_file.read_text(encoding="utf-8"), "")
            archive_rows = [
                json.loads(line)
                for line in (data / "paper_orders_reset_archive.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(archive_rows[0]["order_id"], "o1")
            self.assertEqual(archive_rows[0]["archive_reason"], "Paper portfolio reset.")


if __name__ == "__main__":
    unittest.main()
