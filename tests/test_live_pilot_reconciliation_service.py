from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.execution.live_pilot_reconciliation_service import LivePilotReconciliationService


class LivePilotReconciliationServiceTests(unittest.TestCase):
    def test_successful_approval_and_swap_reconcile_with_balances(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            self._write_journal(
                data,
                [
                    self._row("approve", "0xaaa", 1, 100, "20"),
                    self._row("swap", "0xbbb", 1, 200, "20"),
                ],
            )

            payload = LivePilotReconciliationService(
                data_dir=data,
                report_dir=reports,
                balance_reader=lambda wallet: {
                    "USDC": "429.998478",
                    "WETH": "0.0125",
                    "ETH": "0.024",
                    "block_number": "123",
                },
            ).generate()

        self.assertEqual(payload["overall_status"], "LIVE_PILOT_RECONCILED")
        self.assertEqual(payload["approval_count"], 1)
        self.assertEqual(payload["swap_count"], 1)
        self.assertEqual(payload["failed_transaction_count"], 0)
        self.assertEqual(payload["total_gas_used"], 300)
        self.assertEqual(payload["total_swap_usd"], "20.0000")
        self.assertEqual(payload["latest_swap"]["tx_hash"], "0xbbb")
        self.assertEqual(payload["current_balances"]["USDC"], "429.998478")

    def test_failed_receipt_requires_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            data.mkdir()
            self._write_journal(data, [self._row("swap", "0xfailed", 0, 123, "20")])

            payload = LivePilotReconciliationService(
                data_dir=data,
                report_dir=root / "reports",
                balance_reader=lambda wallet: {"USDC": "449", "WETH": "0", "ETH": "0.02", "block_number": "123"},
            ).generate()

        self.assertEqual(payload["overall_status"], "LIVE_PILOT_RECONCILE_ACTION")
        self.assertEqual(payload["failed_transaction_count"], 1)
        self.assertTrue(any(row["severity"] == "BLOCK" for row in payload["findings"]))

    @staticmethod
    def _row(mode: str, tx_hash: str, receipt_status: int, gas_used: int, smoke_usd: str) -> dict:
        return {
            "timestamp": "2026-07-01T04:00:00Z",
            "mode": mode,
            "wallet_address": "0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7",
            "dex": "Uniswap V3",
            "smoke_usd": smoke_usd,
            "send_result": {
                "tx_hash": tx_hash,
                "receipt_status": receipt_status,
                "block_number": 1,
                "gas_used": gas_used,
            },
        }

    @staticmethod
    def _write_journal(data: Path, rows: list[dict]) -> None:
        (data / "live_pilot_orders.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
