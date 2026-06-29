from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from app.operations.provider_monitor import ProviderMonitorService


class ProviderMonitorTests(unittest.TestCase):
    def test_provider_monitor_classifies_ok_degraded_and_critical_rows(self) -> None:
        now = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            report_dir = root / "reports"
            data_dir.mkdir()
            (data_dir / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {
                                "name": "base-rpc",
                                "provider_type": "rpc",
                                "chain": "base",
                                "score": 95,
                                "success_rate_pct": 100,
                                "consecutive_failures": 0,
                                "avg_latency_ms": 120,
                                "last_success_at": now,
                            },
                            {
                                "name": "slow-dex",
                                "provider_type": "dex",
                                "chain": "base",
                                "score": 55,
                                "success_rate_pct": 80,
                                "consecutive_failures": 1,
                                "avg_latency_ms": 1500,
                                "last_success_at": now,
                            },
                            {
                                "name": "broken-rpc",
                                "provider_type": "rpc",
                                "chain": "Polygon",
                                "score": 20,
                                "success_rate_pct": 10,
                                "consecutive_failures": 4,
                                "avg_latency_ms": None,
                                "last_failure_at": now,
                                "last_error": "timeout",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = ProviderMonitorService(
                data_dir=data_dir,
                report_dir=report_dir,
                stale_after_seconds=900,
                degraded_score_threshold=70,
                critical_score_threshold=40,
                consecutive_failure_threshold=3,
            ).generate()

            self.assertEqual(payload["provider_count"], 3)
            self.assertEqual(payload["overall_status"], "CRITICAL")
            self.assertEqual(payload["critical_alert_count"], 2)
            self.assertGreaterEqual(payload["degraded_alert_count"], 1)

            rows = {row["name"]: row for row in payload["providers"]}
            self.assertEqual(rows["base-rpc"]["status"], "OK")
            self.assertEqual(rows["slow-dex"]["status"], "DEGRADED")
            self.assertEqual(rows["broken-rpc"]["status"], "CRITICAL")
            self.assertEqual(rows["broken-rpc"]["chain"], "polygon")
            self.assertTrue((report_dir / "provider_monitor.json").exists())
            self.assertTrue((report_dir / "provider_monitor.md").exists())

    def test_provider_monitor_flags_stale_and_missing_observations(self) -> None:
        now = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {
                                "name": "stale-rpc",
                                "provider_type": "rpc",
                                "chain": "base",
                                "score": 90,
                                "success_rate_pct": 100,
                                "consecutive_failures": 0,
                                "last_success_at": now - 3600,
                            },
                            {
                                "name": "untimed-dex",
                                "provider_type": "dex",
                                "chain": "base",
                                "score": 90,
                                "success_rate_pct": 100,
                                "consecutive_failures": 0,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = ProviderMonitorService(
                data_dir=data_dir,
                report_dir=root / "reports",
                stale_after_seconds=60,
            ).generate()

            self.assertEqual(payload["overall_status"], "WATCH")
            rows = {row["name"]: row for row in payload["providers"]}
            self.assertEqual(rows["stale-rpc"]["status"], "WATCH")
            self.assertEqual(rows["untimed-dex"]["status"], "WATCH")
            self.assertGreaterEqual(rows["stale-rpc"]["last_observed_age_seconds"], 3600)

    def test_optional_backup_rpc_does_not_make_chain_critical_when_required_rpc_is_healthy(self) -> None:
        now = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {
                                "name": "Base:rpc1:https://base-rpc.publicnode.com",
                                "provider_type": "rpc",
                                "chain": "base",
                                "score": 95,
                                "success_rate_pct": 95,
                                "consecutive_failures": 0,
                                "last_success_at": now,
                            },
                            {
                                "name": "Base:rpc2:https://mainnet.base.org",
                                "provider_type": "rpc",
                                "chain": "base",
                                "score": 0,
                                "success_rate_pct": 0,
                                "consecutive_failures": 4,
                                "last_failure_at": now,
                                "last_error": "timeout",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = ProviderMonitorService(
                data_dir=data_dir,
                report_dir=root / "reports",
                stale_after_seconds=900,
            ).generate()

            rows = {row["name"]: row for row in payload["providers"]}
            self.assertEqual(payload["overall_status"], "WATCH")
            self.assertEqual(payload["critical_alert_count"], 0)
            self.assertEqual(rows["Base:rpc2:https://mainnet.base.org"]["status"], "WATCH")
            self.assertFalse(rows["Base:rpc2:https://mainnet.base.org"]["required_for_overall"])

    def test_fresh_successful_provider_with_low_rolling_score_is_recovering_watch(self) -> None:
        now = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "provider_health.json").write_text(
                json.dumps(
                    {
                        "providers": [
                            {
                                "name": "Aerodrome",
                                "provider_type": "dex",
                                "chain": "base",
                                "score": 55,
                                "success_rate_pct": 55,
                                "consecutive_failures": 0,
                                "last_success_at": now,
                                "last_failure_at": now - 60,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            payload = ProviderMonitorService(
                data_dir=data_dir,
                report_dir=root / "reports",
                stale_after_seconds=900,
            ).generate()

            row = payload["providers"][0]
            self.assertEqual(payload["overall_status"], "WATCH")
            self.assertEqual(row["status"], "WATCH")
            self.assertEqual(row["rolling_status"], "DEGRADED")
            self.assertIn("fresh successful observations", row["alerts"][0]["message"])

    def test_provider_monitor_handles_missing_health_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = ProviderMonitorService(
                data_dir=root / "data",
                report_dir=root / "reports",
            ).generate()

            self.assertEqual(payload["provider_count"], 0)
            self.assertEqual(payload["overall_status"], "NEEDS_DATA")
            self.assertEqual(payload["alert_count"], 0)


if __name__ == "__main__":
    unittest.main()
