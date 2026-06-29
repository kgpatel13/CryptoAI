from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class ReplayDiagnosticsService:
    """Explains why default replay evidence did or did not produce trades."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.input_file = self.data_dir / "multi_dex_opportunities.jsonl"
        self.report_json = self.report_dir / "replay_diagnostics.json"
        self.report_md = self.report_dir / "replay_diagnostics.md"

    def generate(
        self,
        *,
        production_cost_buffer: Decimal = Decimal("0.30"),
        cost_buffers: list[Decimal] | None = None,
        notional_usd: Decimal = Decimal("1000"),
        include_synthetic: bool = False,
    ) -> dict[str, Any]:
        rows = self._read_jsonl(self.input_file)
        deduped = self._dedupe_opportunity_rows(rows)
        cost_buffers = cost_buffers or [Decimal("0.20"), Decimal("0.25"), Decimal("0.30"), Decimal("0.35")]
        real_rows = [row for row in deduped if str(row.get("mode", "REAL")) == "REAL"]
        synthetic_rows = [row for row in deduped if str(row.get("mode", "REAL")) != "REAL"]
        considered = deduped if include_synthetic else real_rows
        scenarios = [self._scenario(considered, cost_buffer, notional_usd) for cost_buffer in cost_buffers]
        production = self._scenario(considered, production_cost_buffer, notional_usd)
        profitable = [row for row in scenarios if row["trade_count"] > 0 and self._decimal(row["total_pnl_usd"]) > 0]
        best = max(profitable, key=lambda row: (self._decimal(row["total_pnl_usd"]), row["trade_count"]), default=None)
        max_gross_edge = max((self._to_decimal(row.get("gross_edge_pct")) or Decimal("0") for row in considered), default=Decimal("0"))
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "source_file": str(self.input_file),
            "include_synthetic": include_synthetic,
            "input_row_count": len(rows),
            "deduped_row_count": len(deduped),
            "real_signal_count": len(real_rows),
            "synthetic_signal_count": len(synthetic_rows),
            "production_cost_buffer_pct": str(production_cost_buffer),
            "production_trade_count": production["trade_count"],
            "production_total_pnl_usd": production["total_pnl_usd"],
            "best_profitable_cost_buffer_pct": best["cost_buffer_pct"] if best else None,
            "best_profitable_trade_count": best["trade_count"] if best else 0,
            "best_profitable_total_pnl_usd": best["total_pnl_usd"] if best else "0.0000",
            "max_observed_gross_edge_pct": str(max_gross_edge),
            "cost_buffer_scenarios": scenarios,
            "findings": self._findings(production, best, production_cost_buffer),
            "notes": [
                "Replay Diagnostics replays recorded real opportunities only by default.",
                "It is explanatory research evidence and does not lower risk thresholds automatically.",
                "Use it to understand whether the replay blocker is caused by cost assumptions, low edge, or missing data.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _scenario(self, rows: list[dict[str, Any]], cost_buffer: Decimal, notional_usd: Decimal) -> dict[str, Any]:
        trades = []
        below_threshold = 0
        max_net_edge = Decimal("0")
        for row in rows[-1000:]:
            gross_edge = self._to_decimal(row.get("gross_edge_pct"))
            if gross_edge is None:
                below_threshold += 1
                continue
            net_edge = gross_edge - cost_buffer
            max_net_edge = max(max_net_edge, net_edge)
            if net_edge <= 0:
                below_threshold += 1
                continue
            pnl = (notional_usd * net_edge / Decimal("100")).quantize(Decimal("0.0001"))
            trades.append({"net_edge_pct": net_edge, "pnl_usd": pnl})
        total_pnl = sum((trade["pnl_usd"] for trade in trades), Decimal("0")).quantize(Decimal("0.0001"))
        avg_net_edge = (
            sum((trade["net_edge_pct"] for trade in trades), Decimal("0")) / Decimal(len(trades))
        ).quantize(Decimal("0.0001")) if trades else Decimal("0.0000")
        return {
            "cost_buffer_pct": str(cost_buffer),
            "considered_signals": len(rows),
            "trade_count": len(trades),
            "skipped_below_threshold": below_threshold,
            "total_pnl_usd": str(total_pnl),
            "avg_net_edge_pct": str(avg_net_edge),
            "max_net_edge_pct": str(max_net_edge.quantize(Decimal("0.0001"))),
        }

    @staticmethod
    def _findings(
        production: dict[str, Any],
        best: dict[str, Any] | None,
        production_cost_buffer: Decimal,
    ) -> list[dict[str, str]]:
        if production["trade_count"] > 0:
            return [
                {
                    "severity": "OK",
                    "message": f"Production buffer {production_cost_buffer}% produced {production['trade_count']} replay trade(s).",
                }
            ]
        if best:
            return [
                {
                    "severity": "WATCH",
                    "message": (
                        f"Production buffer {production_cost_buffer}% produced 0 trades; "
                        f"buffer {best['cost_buffer_pct']}% produced {best['trade_count']} trade(s)."
                    ),
                },
                {
                    "severity": "ACTION",
                    "message": "Collect execution-cost evidence before considering any lower paper threshold.",
                },
            ]
        return [
            {
                "severity": "WARN",
                "message": "No profitable replay scenario was found across tested cost buffers.",
            }
        ]

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Replay Diagnostics",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Source: `{payload['source_file']}`",
            f"- Real signals: `{payload['real_signal_count']}`",
            f"- Synthetic signals: `{payload['synthetic_signal_count']}`",
            f"- Production cost buffer %: `{payload['production_cost_buffer_pct']}`",
            f"- Production trades: `{payload['production_trade_count']}`",
            f"- Production PnL USD: `{payload['production_total_pnl_usd']}`",
            f"- Best profitable cost buffer %: `{payload['best_profitable_cost_buffer_pct']}`",
            f"- Best profitable trades: `{payload['best_profitable_trade_count']}`",
            f"- Best profitable PnL USD: `{payload['best_profitable_total_pnl_usd']}`",
            "",
            "## Cost Buffer Scenarios",
            "",
            "| Cost Buffer % | Signals | Trades | Skipped | PnL USD | Avg Net % | Max Net % |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in payload["cost_buffer_scenarios"]:
            lines.append(
                f"| {row['cost_buffer_pct']} | {row['considered_signals']} | {row['trade_count']} | "
                f"{row['skipped_below_threshold']} | {row['total_pnl_usd']} | {row['avg_net_edge_pct']} | {row['max_net_edge_pct']} |"
            )
        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
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
    def _dedupe_opportunity_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
    def _to_decimal(value: Any) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(ReplayDiagnosticsService().generate(), indent=2))


if __name__ == "__main__":
    main()
