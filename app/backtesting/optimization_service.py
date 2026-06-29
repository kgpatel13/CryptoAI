from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class OptimizationService:
    """Grid-search replay optimizer for recorded multi-DEX opportunities."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.input_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.report_json = self.report_dir / "optimization_report.json"
        self.report_md = self.report_dir / "optimization_report.md"

    def run(
        self,
        *,
        cost_buffers: list[Decimal] | None = None,
        min_net_edges: list[Decimal] | None = None,
        notionals: list[Decimal] | None = None,
        include_synthetic: bool = False,
    ) -> dict[str, Any]:
        rows = self._read_jsonl(self.input_file)
        deduped_rows = self._dedupe_opportunity_rows(rows)
        cost_buffers = cost_buffers or [Decimal("0.20"), Decimal("0.25"), Decimal("0.30"), Decimal("0.35")]
        min_net_edges = min_net_edges or [Decimal("0.00"), Decimal("0.05"), Decimal("0.10"), Decimal("0.20")]
        notionals = notionals or [Decimal("100"), Decimal("250"), Decimal("1000")]

        scenarios = []
        for cost_buffer in cost_buffers:
            for min_net_edge in min_net_edges:
                for notional in notionals:
                    scenarios.append(
                        self._evaluate(
                            rows=deduped_rows,
                            cost_buffer=cost_buffer,
                            min_net_edge=min_net_edge,
                            notional_usd=notional,
                            include_synthetic=include_synthetic,
                        )
                    )

        ranked = sorted(
            scenarios,
            key=lambda row: (
                self._decimal(row["total_pnl_usd"]),
                self._decimal(row["trade_count"]),
                -self._decimal(row["max_drawdown_usd"]),
            ),
            reverse=True,
        )
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "source_file": str(self.input_file),
            "include_synthetic": include_synthetic,
            "input_row_count": len(rows),
            "deduped_row_count": len(deduped_rows),
            "scenario_count": len(scenarios),
            "best_scenario": ranked[0] if ranked else None,
            "scenarios": ranked,
            "notes": [
                "Optimization replays recorded opportunities only; it does not fetch markets or execute trades.",
                "Synthetic paper opportunities are excluded unless include_synthetic is true.",
                "Results are research evidence, not live-trading approval.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _evaluate(
        self,
        *,
        rows: list[dict],
        cost_buffer: Decimal,
        min_net_edge: Decimal,
        notional_usd: Decimal,
        include_synthetic: bool,
    ) -> dict[str, Any]:
        considered = 0
        synthetic_skipped = 0
        below_threshold = 0
        trades = []

        for row in rows[-1000:]:
            mode = str(row.get("mode", "REAL"))
            if mode != "REAL" and not include_synthetic:
                synthetic_skipped += 1
                continue
            considered += 1
            gross_edge = self._to_decimal(row.get("gross_edge_pct"))
            if gross_edge is None:
                below_threshold += 1
                continue
            net_edge = gross_edge - cost_buffer
            if net_edge < min_net_edge:
                below_threshold += 1
                continue
            pnl = (notional_usd * net_edge / Decimal("100")).quantize(Decimal("0.0001"))
            trades.append(
                {
                    "timestamp": str(row.get("timestamp", "-")),
                    "mode": mode,
                    "pair": str(row.get("pair", "-")),
                    "buy_source": str(row.get("buy_dex", "-")),
                    "sell_source": str(row.get("sell_dex", "-")),
                    "gross_edge_pct": str(gross_edge),
                    "net_edge_pct": str(net_edge.quantize(Decimal("0.0001"))),
                    "pnl_usd": str(pnl),
                }
            )

        total_pnl = sum((self._decimal(row["pnl_usd"]) for row in trades), Decimal("0")).quantize(Decimal("0.0001"))
        running = Decimal("0")
        peak = Decimal("0")
        max_drawdown = Decimal("0")
        for trade in trades:
            running += self._decimal(trade["pnl_usd"])
            peak = max(peak, running)
            max_drawdown = max(max_drawdown, peak - running)

        avg_net_edge = (
            sum((self._decimal(row["net_edge_pct"]) for row in trades), Decimal("0")) / Decimal(len(trades))
        ).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")

        return {
            "cost_buffer_pct": str(cost_buffer),
            "min_net_edge_pct": str(min_net_edge),
            "notional_usd": str(notional_usd),
            "considered_signals": considered,
            "trade_count": len(trades),
            "skipped_synthetic": synthetic_skipped,
            "skipped_below_threshold": below_threshold,
            "total_pnl_usd": str(total_pnl),
            "avg_net_edge_pct": str(avg_net_edge),
            "max_drawdown_usd": str(max_drawdown.quantize(Decimal("0.0001"))),
            "trades": trades[-25:],
        }

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Optimization Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Source: `{payload['source_file']}`",
            f"- Input rows: `{payload['input_row_count']}`",
            f"- De-duplicated rows: `{payload['deduped_row_count']}`",
            f"- Scenarios: `{payload['scenario_count']}`",
            f"- Include synthetic: `{payload['include_synthetic']}`",
            "",
            "## Best Scenario",
            "",
        ]
        best = payload.get("best_scenario")
        if best:
            lines += [
                f"- Cost buffer %: `{best['cost_buffer_pct']}`",
                f"- Minimum net edge %: `{best['min_net_edge_pct']}`",
                f"- Notional USD: `{best['notional_usd']}`",
                f"- Trades: `{best['trade_count']}`",
                f"- Total PnL USD: `{best['total_pnl_usd']}`",
                f"- Max drawdown USD: `{best['max_drawdown_usd']}`",
            ]
        else:
            lines.append("- No scenarios evaluated.")

        lines += [
            "",
            "## Scenario Ranking",
            "",
            "| Cost % | Min Net % | Notional | Signals | Trades | PnL | Max DD |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in payload.get("scenarios", [])[:25]:
            lines.append(
                f"| {row['cost_buffer_pct']} | {row['min_net_edge_pct']} | {row['notional_usd']} | "
                f"{row['considered_signals']} | {row['trade_count']} | {row['total_pnl_usd']} | {row['max_drawdown_usd']} |"
            )

        lines += ["", "## Notes", ""]
        for note in payload.get("notes", []):
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    @staticmethod
    def _dedupe_opportunity_rows(rows: list[dict]) -> list[dict]:
        seen = set()
        deduped = []
        for row in rows:
            key = (
                row.get("timestamp"),
                row.get("mode"),
                row.get("chain"),
                row.get("pair"),
                row.get("buy_dex"),
                row.get("sell_dex"),
                row.get("gross_edge_pct"),
                row.get("cost_buffer_pct"),
                row.get("net_edge_pct"),
                row.get("decision"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _decimal(value) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(OptimizationService().run(), indent=2))


if __name__ == "__main__":
    main()
