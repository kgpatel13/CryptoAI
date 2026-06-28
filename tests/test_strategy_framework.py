from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.strategy.strategy_config import StrategyConfigService
from app.strategy.strategy_registry import StrategyRegistry
from app.strategy.strategy_service import StrategyService
from app.strategy.strategy_center import StrategyCenterService


class StrategyFrameworkTests(unittest.TestCase):
    def test_registry_loads_enabled_arbitrage_and_disabled_research(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "strategies.json"
            cfg.write_text(
                json.dumps(
                    {
                        "strategies": {
                            "arbitrage": {"enabled": True, "weight": "1.0"},
                            "momentum": {"enabled": False},
                        }
                    }
                ),
                encoding="utf-8",
            )
            registry = StrategyRegistry(StrategyConfigService(cfg))
            descriptors = registry.descriptors()
            names = {d.strategy_id: d for d in descriptors}
            self.assertTrue(names["arbitrage"].enabled)
            self.assertFalse(names["momentum"].enabled)
            self.assertGreaterEqual(len(registry.enabled_strategies()), 1)

    def test_strategy_service_persists_ranked_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = root / "strategies.json"
            cfg.write_text(json.dumps({"strategies": {"arbitrage": {"enabled": True, "min_confidence": 0}}}), encoding="utf-8")
            svc = StrategyService(registry=StrategyRegistry(StrategyConfigService(cfg)), data_dir=root / "data")
            ranked = svc.ranked_signals()
            self.assertTrue((root / "data" / "strategy_signals.jsonl").exists())
            self.assertTrue((root / "data" / "strategy_ranked_signals.jsonl").exists())
            self.assertIsInstance(ranked, list)

    def test_strategy_center_generates_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            reports.mkdir()
            (data / "paper_orders.jsonl").write_text(
                json.dumps(
                    {
                        "order_id": "o1",
                        "timestamp": "2026-06-28T00:00:00Z",
                        "strategy_name": "DEX Arbitrage Strategy",
                        "pair": "WETH/USDC",
                        "status": "FILLED",
                        "filled_notional_usd": "100",
                        "slippage_bps": "5",
                        "latency_ms": "250",
                    }
                ) + "\n",
                encoding="utf-8",
            )
            (data / "paper_portfolio_state.json").write_text(
                json.dumps(
                    {
                        "positions": [
                            {
                                "strategy_name": "DEX Arbitrage Strategy",
                                "status": "CLOSED",
                                "realized_pnl_usd": "0.35",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            report = StrategyCenterService(data_dir=data, report_dir=reports).generate()
            self.assertGreaterEqual(report["strategy_count"], 1)
            self.assertTrue((reports / "strategy_center.json").exists())
            self.assertTrue((reports / "strategy_center.md").exists())


if __name__ == "__main__":
    unittest.main()
