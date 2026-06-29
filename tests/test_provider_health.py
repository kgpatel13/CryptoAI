import json
import tempfile
import unittest
from pathlib import Path

from app.resilience.provider_health import ProviderHealthRegistry


class ProviderHealthTests(unittest.TestCase):
    def test_records_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = ProviderHealthRegistry(Path(tmp) / "provider_health.json")
            registry.record_success("rpc1", "rpc", 100, chain="base")
            registry.record_failure("rpc1", "rpc", "timeout", 200, chain="base")
            rows = registry.snapshot()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["success_count"], 1)
            self.assertEqual(rows[0]["failure_count"], 1)
            self.assertTrue((Path(tmp) / "provider_health.json").exists())

    def test_normalizes_display_chain_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = ProviderHealthRegistry(Path(tmp) / "provider_health.json")
            registry.record_success("rpc1", "rpc", 100, chain="Base")
            registry.record_failure("rpc1", "rpc", "timeout", 200, chain="base")
            rows = registry.snapshot()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["chain"], "base")
            self.assertEqual(rows[0]["success_count"], 1)
            self.assertEqual(rows[0]["failure_count"], 1)

    def test_preserves_existing_provider_rows_across_process_like_instances(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provider_health.json"
            first = ProviderHealthRegistry(path)
            first.record_failure("Aerodrome", "dex", "route unavailable", chain="base")

            second = ProviderHealthRegistry(path)
            second.record_success("Uniswap V2", "dex", 12, chain="base")

            rows = json.loads(path.read_text(encoding="utf-8"))["providers"]
            names = {row["name"] for row in rows}

            self.assertEqual(names, {"Aerodrome", "Uniswap V2"})
            aerodrome = next(row for row in rows if row["name"] == "Aerodrome")
            self.assertEqual(aerodrome["failure_count"], 1)


if __name__ == "__main__":
    unittest.main()
