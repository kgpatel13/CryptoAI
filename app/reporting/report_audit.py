from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ReportAuditService:
    """Audits report freshness, parseability, and operational warning signals."""

    EXPECTED_REPORTS = [
        "quote_diagnostics.md",
        "multi_dex_opportunities.md",
        "opportunity_explorer.md",
        "paper_report.json",
        "paper_report.md",
        "portfolio_analytics.json",
        "portfolio_analytics.md",
        "strategy_center.json",
        "strategy_center.md",
        "strategy_intelligence.json",
        "strategy_intelligence.md",
        "feature_store.json",
        "feature_store.md",
        "research_dashboard.json",
        "research_dashboard.md",
        "backtest_report.json",
        "backtest_report.md",
        "replay_diagnostics.json",
        "replay_diagnostics.md",
        "execution_cost_evidence.json",
        "execution_cost_evidence.md",
        "optimization_report.json",
        "optimization_report.md",
        "experiment_report.json",
        "experiment_report.md",
        "market_intelligence.json",
        "market_intelligence.md",
        "market_universe_evidence.json",
        "market_universe_evidence.md",
        "provider_monitor.json",
        "provider_monitor.md",
    ]

    def __init__(self, report_dir: Path | str = "reports", stale_after_minutes: int = 30) -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.stale_after_minutes = stale_after_minutes

    def generate(self) -> dict[str, Any]:
        reports = [self._inspect_report(name) for name in self.EXPECTED_REPORTS]
        findings = self._findings(reports)
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "report_count": len(reports),
            "missing_count": sum(1 for row in reports if not row["exists"]),
            "invalid_json_count": sum(1 for row in reports if row.get("json_valid") is False),
            "stale_count": sum(1 for row in reports if row.get("stale") is True),
            "finding_count": len(findings),
            "reports": reports,
            "findings": findings,
            "notes": [
                "Report Audit is a review aid for paper-mode operations.",
                "Critical provider status and paper-simulated opportunities require operational attention before strategy tuning.",
            ],
        }
        self._write_json(self.report_dir / "report_audit.json", payload)
        self._write_markdown(payload)
        return payload

    def _inspect_report(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
        row: dict[str, Any] = {
            "name": name,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "generated_at": None,
            "stale": None,
        }
        if not path.exists():
            return row

        text = path.read_text(encoding="utf-8", errors="replace")
        generated_at = self._extract_generated_at(path, text)
        row["generated_at"] = generated_at
        row["stale"] = self._is_stale(generated_at)

        if path.suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                row["json_valid"] = False
                row["json_error"] = str(exc)
            else:
                row["json_valid"] = True
                row["summary"] = self._json_summary(name, payload)
        return row

    def _findings(self, reports: list[dict[str, Any]]) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        for row in reports:
            if not row["exists"]:
                findings.append({"severity": "WARN", "report": row["name"], "message": "Expected report is missing."})
            elif row.get("json_valid") is False:
                findings.append({"severity": "ERROR", "report": row["name"], "message": row.get("json_error", "Invalid JSON.")})
            elif row.get("stale") is True:
                findings.append({"severity": "WATCH", "report": row["name"], "message": "Report is older than freshness window."})

        provider = self._read_json("provider_monitor.json")
        if provider.get("overall_status") in {"CRITICAL", "DEGRADED"}:
            findings.append(
                {
                    "severity": "CRITICAL",
                    "report": "provider_monitor.json",
                    "message": f"Provider Monitor status is {provider.get('overall_status')} with {provider.get('alert_count', 0)} alert(s).",
                }
            )

        quote_report = self.report_dir / "quote_diagnostics.md"
        quote_text = quote_report.read_text(encoding="utf-8", errors="replace") if quote_report.exists() else ""
        quote_errors = self._extract_markdown_count(quote_text, "Error")
        quote_invalid = self._extract_markdown_count(quote_text, "Invalid")
        if quote_errors or quote_invalid:
            findings.append(
                {
                    "severity": "WATCH",
                    "report": "quote_diagnostics.md",
                    "message": f"Quote Diagnostics has {quote_errors} error row(s) and {quote_invalid} invalid row(s).",
                }
            )

        paper = self._read_json("paper_report.json")
        warning_count = int(paper.get("legacy_accounting_warning_count", 0) or 0)
        if warning_count:
            findings.append(
                {
                    "severity": "WATCH",
                    "report": "paper_report.json",
                    "message": f"{warning_count} legacy inverse-pair paper order(s) are annotated for accounting caution.",
                }
            )
        opportunity_report = self.report_dir / "opportunity_explorer.md"
        opportunity_text = opportunity_report.read_text(encoding="utf-8", errors="replace") if opportunity_report.exists() else ""
        if paper.get("opportunity_decision_counts", {}).get("BUY", 0) and "PAPER_SIMULATED" in opportunity_text:
            findings.append(
                {
                    "severity": "WATCH",
                    "report": "opportunity_explorer.md",
                    "message": "Current BUY opportunities are paper-simulated because only one healthy DEX venue is available.",
                }
            )
        return findings

    def _json_summary(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        keys = [
            "mode",
            "status",
            "overall_status",
            "overall_readiness_score",
            "active_focus_count",
            "research_target_count",
            "blocked_count",
            "provider_count",
            "alert_count",
            "feature_count",
            "total_orders",
            "filled_orders",
            "legacy_accounting_warning_count",
            "strategy_count",
            "top_recommendation",
            "total_signals",
            "simulated_trades",
            "production_trade_count",
            "best_profitable_trade_count",
            "buffer_status",
            "confidence",
            "input_row_count",
            "deduped_row_count",
            "scenario_count",
            "experiment_count",
            "gate_count",
            "pass_count",
            "warn_count",
            "fail_count",
        ]
        return {key: payload[key] for key in keys if key in payload}

    def _read_json(self, name: str) -> dict[str, Any]:
        path = self.report_dir / name
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def _extract_generated_at(self, path: Path, text: str) -> str | None:
        if path.suffix == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                return None
            value = payload.get("generated_at")
            return str(value) if value else None
        for line in text.splitlines()[:10]:
            if "Generated:" in line:
                return line.split("`")[1] if "`" in line else line.split("Generated:", 1)[1].strip()
        return None

    @staticmethod
    def _extract_markdown_count(text: str, label: str) -> int:
        prefix = f"- {label}:"
        for line in text.splitlines():
            if not line.startswith(prefix):
                continue
            raw = line.split(":", 1)[1].strip().strip("`")
            try:
                return int(raw)
            except ValueError:
                return 0
        return 0

    def _is_stale(self, generated_at: str | None) -> bool | None:
        if not generated_at:
            return None
        try:
            parsed = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            return None
        age_minutes = (datetime.now(UTC) - parsed).total_seconds() / 60
        return age_minutes > self.stale_after_minutes

    def _write_markdown(self, payload: dict[str, Any]) -> None:
        lines = [
            "# CryptoAI Report Audit",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Reports checked: `{payload['report_count']}`",
            f"- Missing: `{payload['missing_count']}`",
            f"- Invalid JSON: `{payload['invalid_json_count']}`",
            f"- Stale: `{payload['stale_count']}`",
            f"- Findings: `{payload['finding_count']}`",
            "",
            "## Findings",
            "",
            "| Severity | Report | Message |",
            "|---|---|---|",
        ]
        for finding in payload["findings"]:
            lines.append(f"| {finding['severity']} | {finding['report']} | {finding['message']} |")
        if not payload["findings"]:
            lines.append("| OK | - | No report findings. |")
        lines += ["", "## Reports", "", "| Report | Exists | Generated | Stale | Size |", "|---|---|---|---|---:|"]
        for row in payload["reports"]:
            lines.append(f"| {row['name']} | {row['exists']} | {row.get('generated_at') or '-'} | {row.get('stale')} | {row['size_bytes']} |")
        (self.report_dir / "report_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = ReportAuditService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
