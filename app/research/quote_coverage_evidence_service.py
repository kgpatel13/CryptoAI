from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import TRADING_PAIRS
from app.registry.tokens import get_token


class QuoteCoverageEvidenceService:
    """Ranks quote-provider coverage gaps before expanding the trade universe."""

    IMPLEMENTED_PROVIDERS = {
        ("base", "Uniswap V2"),
        ("base", "Aerodrome"),
        ("base", "Uniswap V3"),
    }

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.report_json = self.report_dir / "quote_coverage_evidence.json"
        self.report_md = self.report_dir / "quote_coverage_evidence.md"

    def generate(self) -> dict[str, Any]:
        quote_rows = self._read_jsonl(self.data_dir / "quote_diagnostics.jsonl")[-500:]
        provider_monitor = self._read_json(self.report_dir / "provider_monitor.json")
        coverage_rows = self._coverage_rows(quote_rows)
        pair_rows = self._pair_rows(coverage_rows)
        active_pair_count = sum(1 for row in pair_rows if row["status"] == "ACTIVE_QUOTED")
        provider_gap_count = sum(1 for row in pair_rows if row["status"] in {"PROVIDER_GAP", "ROUTER_OR_PROVIDER_GAP"})
        quote_gap_count = sum(1 for row in pair_rows if row["status"] == "NEEDS_QUOTE_TEST")
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "implemented_provider_count": len(self.IMPLEMENTED_PROVIDERS),
            "configured_pair_count": len(pair_rows),
            "active_pair_count": active_pair_count,
            "provider_gap_count": provider_gap_count,
            "quote_gap_count": quote_gap_count,
            "provider_status": provider_monitor.get("overall_status", "UNKNOWN"),
            "provider_alert_count": provider_monitor.get("alert_count", 0),
            "pair_coverage": pair_rows,
            "dex_coverage": coverage_rows,
            "next_provider_targets": self._next_targets(pair_rows),
            "findings": self._findings(pair_rows, provider_monitor),
            "notes": [
                "Quote Coverage Evidence is paper-mode expansion planning.",
                "A configured pair is not tradeable evidence until at least two DEXes have recent OK quotes for the same route.",
                "This report does not add live trading, change thresholds, or approve new production venues.",
            ],
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _coverage_rows(self, quote_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = []
        for pair in TRADING_PAIRS:
            chain = pair.chain.lower()
            pair_name = f"{pair.base_symbol}/{pair.quote_symbol}".upper()
            inverse_name = f"{pair.quote_symbol}/{pair.base_symbol}".upper()
            token_ready = get_token(chain, pair.base_symbol) is not None and get_token(chain, pair.quote_symbol) is not None
            for dex in get_dexes_for_chain(chain):
                implemented = (chain, dex.name) in self.IMPLEMENTED_PROVIDERS
                direct_ok = self._ok_count(quote_rows, chain=chain, dex=dex.name, pair=pair_name)
                inverse_ok = self._ok_count(quote_rows, chain=chain, dex=dex.name, pair=inverse_name)
                rows.append(
                    {
                        "chain": chain,
                        "pair": pair_name,
                        "priority": pair.priority,
                        "dex": dex.name,
                        "dex_type": dex.dex_type,
                        "token_ready": token_ready,
                        "router_configured": bool(dex.router_address),
                        "provider_implemented": implemented,
                        "direct_ok_count": direct_ok,
                        "inverse_ok_count": inverse_ok,
                        "recent_quote_ready": direct_ok > 0,
                        "coverage_status": self._dex_status(
                            token_ready=token_ready,
                            router_configured=bool(dex.router_address),
                            provider_implemented=implemented,
                            direct_ok=direct_ok,
                        ),
                        "next_action": self._dex_next_action(
                            chain=chain,
                            pair=pair_name,
                            dex=dex.name,
                            token_ready=token_ready,
                            router_configured=bool(dex.router_address),
                            provider_implemented=implemented,
                            direct_ok=direct_ok,
                        ),
                    }
                )
        return rows

    def _pair_rows(self, coverage_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in coverage_rows:
            grouped.setdefault((row["chain"], row["pair"]), []).append(row)

        pairs = []
        for (chain, pair), rows in grouped.items():
            implemented = [row for row in rows if row["provider_implemented"]]
            routers = [row for row in rows if row["router_configured"]]
            direct_ok_dexes = sorted({row["dex"] for row in rows if row["direct_ok_count"] > 0})
            status = self._pair_status(
                implemented_count=len(implemented),
                router_count=len(routers),
                direct_ok_dex_count=len(direct_ok_dexes),
            )
            score = self._pair_score(
                priority=self._int(rows[0].get("priority"), default=50),
                implemented_count=len(implemented),
                router_count=len(routers),
                direct_ok_dex_count=len(direct_ok_dexes),
                dex_count=len(rows),
            )
            pairs.append(
                {
                    "chain": chain,
                    "pair": pair,
                    "priority": rows[0].get("priority"),
                    "dex_count": len(rows),
                    "implemented_provider_dex_count": len(implemented),
                    "router_configured_dex_count": len(routers),
                    "direct_ok_dex_count": len(direct_ok_dexes),
                    "direct_ok_dexes": direct_ok_dexes,
                    "status": status,
                    "score": score,
                    "next_action": self._pair_next_action(status, chain, pair),
                }
            )
        return sorted(pairs, key=lambda row: (row["score"], -self._int(row["priority"], 50), row["chain"], row["pair"]), reverse=True)

    @staticmethod
    def _dex_status(
        *,
        token_ready: bool,
        router_configured: bool,
        provider_implemented: bool,
        direct_ok: int,
    ) -> str:
        if not token_ready:
            return "TOKEN_GAP"
        if direct_ok > 0:
            return "QUOTE_OK"
        if provider_implemented:
            return "NEEDS_QUOTE_TEST"
        if router_configured:
            return "NEEDS_PROVIDER_IMPLEMENTATION"
        return "NEEDS_ROUTER_AND_PROVIDER"

    @staticmethod
    def _pair_status(*, implemented_count: int, router_count: int, direct_ok_dex_count: int) -> str:
        if direct_ok_dex_count >= 2:
            return "ACTIVE_QUOTED"
        if implemented_count >= 2:
            return "NEEDS_QUOTE_TEST"
        if router_count >= 2:
            return "PROVIDER_GAP"
        return "ROUTER_OR_PROVIDER_GAP"

    @staticmethod
    def _pair_score(
        *,
        priority: int,
        implemented_count: int,
        router_count: int,
        direct_ok_dex_count: int,
        dex_count: int,
    ) -> int:
        score = 0
        if priority == 1:
            score += 20
        elif priority <= 2:
            score += 10
        score += min(30, implemented_count * 15)
        score += min(20, router_count * 8)
        score += min(30, direct_ok_dex_count * 15)
        if dex_count >= 3:
            score += 5
        return min(100, score)

    @staticmethod
    def _pair_next_action(status: str, chain: str, pair: str) -> str:
        if status == "ACTIVE_QUOTED":
            return "Keep collecting quote, opportunity, and execution-cost evidence."
        if status == "NEEDS_QUOTE_TEST":
            return f"Run targeted quote diagnostics for {chain} {pair} across implemented providers."
        if status == "PROVIDER_GAP":
            return f"Implement at least two quote providers for {chain} {pair} before expansion."
        return f"Add verified router metadata and quote providers for {chain} {pair}."

    @staticmethod
    def _dex_next_action(
        *,
        chain: str,
        pair: str,
        dex: str,
        token_ready: bool,
        router_configured: bool,
        provider_implemented: bool,
        direct_ok: int,
    ) -> str:
        if direct_ok > 0:
            return "Recent direct OK quote exists."
        if not token_ready:
            return f"Add token metadata before quote testing {chain} {pair}."
        if provider_implemented:
            return f"Run quote diagnostics for {chain} {pair} on {dex}."
        if router_configured:
            return f"Implement quote provider for {chain} {dex}."
        return f"Verify router metadata, then implement quote provider for {chain} {dex}."

    @staticmethod
    def _next_targets(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        targets = [row for row in pair_rows if row["status"] != "ACTIVE_QUOTED"]
        return [
            {
                "chain": row["chain"],
                "pair": row["pair"],
                "status": row["status"],
                "score": row["score"],
                "next_action": row["next_action"],
            }
            for row in targets[:5]
        ]

    @staticmethod
    def _findings(pair_rows: list[dict[str, Any]], provider_monitor: dict[str, Any]) -> list[dict[str, str]]:
        active = [row for row in pair_rows if row["status"] == "ACTIVE_QUOTED"]
        gaps = [row for row in pair_rows if row["status"] != "ACTIVE_QUOTED"]
        findings = [
            {"severity": "INFO", "message": f"{len(active)} configured pair(s) have active two-DEX quote evidence."},
            {"severity": "ACTION", "message": f"{len(gaps)} configured pair(s) still need quote coverage before expansion."},
        ]
        quote_tests = [row for row in pair_rows if row["status"] == "NEEDS_QUOTE_TEST"]
        if quote_tests:
            first = quote_tests[0]
            findings.append(
                {
                    "severity": "ACTION",
                    "message": f"Next targeted quote test: {first['chain']} {first['pair']}.",
                }
            )
        if provider_monitor.get("overall_status") == "WATCH":
            findings.append(
                {
                    "severity": "WATCH",
                    "message": f"Provider monitor remains WATCH with {provider_monitor.get('alert_count', 0)} alert(s).",
                }
            )
        return findings

    @staticmethod
    def _ok_count(rows: list[dict[str, Any]], *, chain: str, dex: str, pair: str) -> int:
        return sum(
            1
            for row in rows
            if str(row.get("chain", "")).lower() == chain
            and str(row.get("dex", "")).lower() == dex.lower()
            and str(row.get("pair", "")).upper() == pair
            and str(row.get("status", "")) == "OK"
        )

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# CryptoAI Quote Coverage Evidence",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Implemented providers: `{payload['implemented_provider_count']}`",
            f"- Configured pairs: `{payload['configured_pair_count']}`",
            f"- Active quoted pairs: `{payload['active_pair_count']}`",
            f"- Provider gap pairs: `{payload['provider_gap_count']}`",
            f"- Quote-test gap pairs: `{payload['quote_gap_count']}`",
            f"- Provider status: `{payload['provider_status']}` with `{payload['provider_alert_count']}` alert(s)",
            "",
            "## Pair Coverage",
            "",
            "| Status | Chain | Pair | Score | DEXs | Implemented | Direct OK | Next Action |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
        for row in payload["pair_coverage"]:
            lines.append(
                f"| {row['status']} | {row['chain']} | {row['pair']} | {row['score']} | "
                f"{row['dex_count']} | {row['implemented_provider_dex_count']} | {row['direct_ok_dex_count']} | "
                f"{row['next_action'].replace('|', '/')} |"
            )
        lines += ["", "## Next Provider Targets", ""]
        for row in payload["next_provider_targets"]:
            lines.append(f"- `{row['chain']} {row['pair']}` {row['status']}: {row['next_action']}")
        lines += ["", "## Findings", ""]
        for finding in payload["findings"]:
            lines.append(f"- `{finding['severity']}` {finding['message']}")
        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
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
    def _int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(QuoteCoverageEvidenceService().generate(), indent=2))


if __name__ == "__main__":
    main()
