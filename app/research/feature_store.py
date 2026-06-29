from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from app.database.db import get_connection, initialize_database
from app.events.event_service import EventBusService
from app.events.models import EventType
from app.research.models import FeatureVector, utc_now


class FeatureStoreService:
    """Builds and persists research feature vectors from CryptoAI runtime artifacts."""

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.report_dir = Path("reports")
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        initialize_database()
        self._ensure_schema()

    def build_from_runtime(self) -> dict[str, Any]:
        opportunities = self._read_jsonl(self.data_dir / "opportunity_decisions.jsonl")
        multi_dex = self._read_jsonl(self.data_dir / "multi_dex_opportunities.jsonl")
        orders = self._read_jsonl(self.data_dir / "paper_orders.jsonl")
        strategy_signals = self._read_jsonl(self.data_dir / "strategy_ranked_signals.jsonl")

        vectors: list[FeatureVector] = []
        vectors.extend(FeatureVector.from_opportunity(row, "opportunity_decision") for row in opportunities)
        vectors.extend(FeatureVector.from_opportunity(row, "multi_dex_opportunity") for row in multi_dex)
        vectors.extend(FeatureVector.from_order(row, "paper_order") for row in orders)
        vectors.extend(self._vectors_from_strategy_signals(strategy_signals))

        # Dedupe by source + timestamp + pair + decision + reason to avoid explosive repeat records
        deduped: list[FeatureVector] = []
        seen: set[tuple[str, str, str, str, str]] = set()
        for vector in vectors:
            key = (vector.source, vector.created_at, vector.pair, vector.decision, vector.reason[:120])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(vector)

        self._write_jsonl(deduped)
        self._write_csv(deduped)
        self._persist_sqlite(deduped)
        summary = self._summarize(deduped)
        self._write_summary(summary)
        EventBusService().publish(
            EventType.SYSTEM,
            "FeatureStoreService",
            {"message": "Feature store rebuilt", "feature_count": len(deduped)},
        )
        return summary

    def recent_features(self, limit: int = 100) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT feature_id, created_at, source, chain, pair, strategy_id, decision,
                       estimated_net_edge_pct, readiness_score, confidence_score, risk_status,
                       execution_quality, latency_ms, slippage_bps, reason
                FROM feature_vectors
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _vectors_from_strategy_signals(self, rows: list[dict[str, Any]]) -> list[FeatureVector]:
        vectors = []
        for row in rows:
            normalized = {
                "timestamp": row.get("timestamp"),
                "chain": row.get("chain", "base"),
                "pair": row.get("pair", "-"),
                "strategy_id": row.get("strategy_id", "arbitrage"),
                "decision": row.get("action", "SIGNAL"),
                "estimated_net_edge_pct": row.get("expected_edge_pct"),
                "readiness_score": row.get("confidence_score", 0),
                "reason": row.get("reason", ""),
                "mode": row.get("mode", "paper"),
            }
            v = FeatureVector.from_opportunity(normalized, "strategy_signal")
            vectors.append(v)
        return vectors

    def _summarize(self, vectors: list[FeatureVector]) -> dict[str, Any]:
        by_source = Counter(v.source for v in vectors)
        by_chain = Counter(v.chain for v in vectors)
        by_pair = Counter(v.pair for v in vectors if v.pair and v.pair != "-")
        by_decision = Counter(v.decision for v in vectors)
        tradeable = [v for v in vectors if v.decision.upper() in {"BUY", "FILLED", "READY_FOR_PAPER"}]
        rejected = [v for v in vectors if "reject" in v.decision.lower() or "rejected" in v.risk_status.lower()]
        edges = []
        for v in vectors:
            try:
                if v.estimated_net_edge_pct is not None:
                    edges.append(float(v.estimated_net_edge_pct))
            except Exception:
                pass

        top_pairs = [
            {"pair": pair, "count": count}
            for pair, count in by_pair.most_common(10)
        ]

        top_sources = [
            {"source": source, "count": count}
            for source, count in by_source.most_common(10)
        ]

        return {
            "generated_at": utc_now(),
            "mode": "paper",
            "feature_count": len(vectors),
            "tradeable_or_filled_count": len(tradeable),
            "risk_or_execution_rejected_count": len(rejected),
            "source_counts": dict(by_source),
            "chain_counts": dict(by_chain),
            "pair_counts": dict(by_pair),
            "decision_counts": dict(by_decision),
            "avg_net_edge_pct": f"{sum(edges) / len(edges):.4f}" if edges else "-",
            "max_net_edge_pct": f"{max(edges):.4f}" if edges else "-",
            "top_pairs": top_pairs,
            "top_sources": top_sources,
            "data_quality": {
                "has_opportunities": bool(by_source.get("opportunity_decision") or by_source.get("multi_dex_opportunity")),
                "has_orders": bool(by_source.get("paper_order")),
                "has_strategy_signals": bool(by_source.get("strategy_signal")),
                "sqlite_enabled": True,
                "jsonl_enabled": True,
                "csv_enabled": True,
            },
            "notes": [
                "Feature vectors are research inputs, not live-trading approvals.",
                "Synthetic paper opportunities are labeled and must not be treated as live executable edge.",
                "Future AI ranking should consume these features only after enough historical outcomes exist.",
            ],
        }

    def _write_summary(self, summary: dict[str, Any]) -> None:
        (self.report_dir / "feature_store.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        lines = [
            "# CryptoAI Feature Store Report",
            "",
            f"Generated: `{summary['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{summary['mode']}`",
            f"- Feature vectors: `{summary['feature_count']}`",
            f"- Tradeable or filled: `{summary['tradeable_or_filled_count']}`",
            f"- Risk/execution rejected: `{summary['risk_or_execution_rejected_count']}`",
            f"- Average net edge %: `{summary['avg_net_edge_pct']}`",
            f"- Max net edge %: `{summary['max_net_edge_pct']}`",
            "",
            "## Source Counts",
            "",
        ]
        for source, count in summary["source_counts"].items():
            lines.append(f"- `{source}`: {count}")
        lines += ["", "## Decision Counts", ""]
        for decision, count in summary["decision_counts"].items():
            lines.append(f"- `{decision}`: {count}")
        lines += ["", "## Top Pairs", "", "| Pair | Count |", "|---|---:|"]
        for row in summary["top_pairs"]:
            lines.append(f"| {row['pair']} | {row['count']} |")
        lines += ["", "## Data Quality", ""]
        for key, value in summary["data_quality"].items():
            lines.append(f"- `{key}`: `{value}`")
        lines += ["", "## Notes", ""]
        for note in summary["notes"]:
            lines.append(f"- {note}")
        (self.report_dir / "feature_store.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _ensure_schema(self) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feature_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chain TEXT NOT NULL,
                    pair TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    buy_source TEXT,
                    sell_source TEXT,
                    buy_price TEXT,
                    sell_price TEXT,
                    gross_spread_pct TEXT,
                    estimated_net_edge_pct TEXT,
                    readiness_score INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    confidence_score INTEGER NOT NULL,
                    rank_score INTEGER NOT NULL,
                    quote_health_score INTEGER NOT NULL,
                    risk_status TEXT NOT NULL,
                    execution_quality TEXT,
                    slippage_bps TEXT,
                    latency_ms TEXT,
                    realized_pnl_usd TEXT,
                    hour_utc INTEGER NOT NULL,
                    weekday_utc INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    raw_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feature_vectors_created_at ON feature_vectors(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feature_vectors_pair ON feature_vectors(pair)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feature_vectors_strategy ON feature_vectors(strategy_id)")
            conn.commit()

    def _persist_sqlite(self, vectors: list[FeatureVector]) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM feature_vectors")
            for v in vectors:
                conn.execute(
                    """
                    INSERT INTO feature_vectors (
                        feature_id, created_at, source, chain, pair, strategy_id, mode,
                        buy_source, sell_source, buy_price, sell_price, gross_spread_pct,
                        estimated_net_edge_pct, readiness_score, decision, confidence_score,
                        rank_score, quote_health_score, risk_status, execution_quality,
                        slippage_bps, latency_ms, realized_pnl_usd, hour_utc, weekday_utc,
                        reason, tags_json, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v.feature_id, v.created_at, v.source, v.chain, v.pair, v.strategy_id, v.mode,
                        v.buy_source, v.sell_source, v.buy_price, v.sell_price, v.gross_spread_pct,
                        v.estimated_net_edge_pct, v.readiness_score, v.decision, v.confidence_score,
                        v.rank_score, v.quote_health_score, v.risk_status, v.execution_quality,
                        v.slippage_bps, v.latency_ms, v.realized_pnl_usd, v.hour_utc, v.weekday_utc,
                        v.reason, json.dumps(v.tags), json.dumps(v.raw, default=str),
                    ),
                )
            conn.commit()

    def _write_jsonl(self, vectors: list[FeatureVector]) -> None:
        with (self.data_dir / "feature_vectors.jsonl").open("w", encoding="utf-8") as fh:
            for vector in vectors:
                fh.write(json.dumps(vector.to_dict(), default=str) + "\n")

    def _write_csv(self, vectors: list[FeatureVector]) -> None:
        if not vectors:
            (self.data_dir / "feature_vectors.csv").write_text("", encoding="utf-8")
            return
        fields = [
            "feature_id", "created_at", "source", "chain", "pair", "strategy_id", "mode",
            "buy_source", "sell_source", "buy_price", "sell_price", "gross_spread_pct",
            "estimated_net_edge_pct", "readiness_score", "decision", "confidence_score",
            "rank_score", "quote_health_score", "risk_status", "execution_quality",
            "slippage_bps", "latency_ms", "realized_pnl_usd", "hour_utc", "weekday_utc", "reason",
        ]
        with (self.data_dir / "feature_vectors.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for vector in vectors:
                row = vector.to_dict()
                writer.writerow({field: row.get(field) for field in fields})

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
        return rows


def main() -> None:
    summary = FeatureStoreService().build_from_runtime()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
