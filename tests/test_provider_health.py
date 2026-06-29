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


if __name__ == "__main__":
    unittest.main()
