from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class ExperimentService:
    """Records research evidence from replay, optimization, and operations reports."""

    def __init__(self, data_dir: Path | str = "data", report_dir: Path | str = "reports") -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "experiments.jsonl"
        self.report_json = self.report_dir / "experiment_report.json"
        self.report_md = self.report_dir / "experiment_report.md"

    def run(
        self,
        *,
        label: str = "default-replay-optimization",
        run_backtest: bool = True,
        run_optimization: bool = True,
        min_optimization_trades: int = 5,
    ) -> dict[str, Any]:
        if run_backtest:
            from app.backtesting.backtest_service import BacktestService

            BacktestService(data_dir=self.data_dir, report_dir=self.report_dir).run_default_backtest()
        if run_optimization:
            from app.backtesting.optimization_service import OptimizationService

            OptimizationService(data_dir=self.data_dir, report_dir=self.report_dir).run()
        from app.backtesting.replay_diagnostics_service import ReplayDiagnosticsService
        from app.execution.execution_cost_evidence_service import ExecutionCostEvidenceService

        ReplayDiagnosticsService(data_dir=self.data_dir, report_dir=self.report_dir).generate()
        ExecutionCostEvidenceService(data_dir=self.data_dir, report_dir=self.report_dir).generate()

        generated_at = self._utc_now()
        backtest = self._read_json(self.report_json.with_name("backtest_report.json"))
        optimization = self._read_json(self.report_json.with_name("optimization_report.json"))
        replay_diagnostics = self._read_json(self.report_json.with_name("replay_diagnostics.json"))
        execution_cost = self._read_json(self.report_json.with_name("execution_cost_evidence.json"))
        provider = self._read_json(self.report_json.with_name("provider_monitor.json"))
        paper = self._read_json(self.report_json.with_name("paper_report.json"))
        audit = self._read_json(self.report_json.with_name("report_audit.json"))

        gates = self._evaluate_gates(
            backtest=backtest,
            optimization=optimization,
            provider=provider,
            paper=paper,
            audit=audit,
            min_optimization_trades=min_optimization_trades,
        )
        fail_count = sum(1 for gate in gates if gate["status"] == "FAIL")
        warn_count = sum(1 for gate in gates if gate["status"] == "WARN")
        pass_count = sum(1 for gate in gates if gate["status"] == "PASS")
        if fail_count:
            status = "RESEARCH_ONLY"
        elif warn_count:
            status = "WATCHLIST"
        else:
            status = "PAPER_EVIDENCE_CANDIDATE"

        experiment = {
            "experiment_id": self._experiment_id(generated_at, label, gates),
            "generated_at": generated_at,
            "mode": "paper",
            "label": label,
            "status": status,
            "promotion_allowed": False,
            "gate_count": len(gates),
            "pass_count": pass_count,
            "warn_count": warn_count,
            "fail_count": fail_count,
            "summary": self._summary(backtest, optimization, provider, paper, audit, execution_cost),
            "replay_diagnostics": self._replay_diagnostic_summary(replay_diagnostics),
            "execution_cost_evidence": self._execution_cost_summary(execution_cost),
            "gates": gates,
            "notes": [
                "Experiment tracking records research evidence only.",
                "promotion_allowed is always false until separate live-readiness gates are implemented and approved.",
                "A PAPER_EVIDENCE_CANDIDATE status is not live-trading approval.",
            ],
        }
        self._append_history(experiment)
        payload = {
            "generated_at": generated_at,
            "mode": "paper",
            "status": experiment["status"],
            "gate_count": experiment["gate_count"],
            "pass_count": experiment["pass_count"],
            "warn_count": experiment["warn_count"],
            "fail_count": experiment["fail_count"],
            "latest_experiment": experiment,
            "experiment_count": len(self._read_history()),
            "history_file": str(self.history_file),
            "recent_experiments": self._read_history(limit=25),
        }
        self.report_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.report_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _evaluate_gates(
        self,
        *,
        backtest: dict[str, Any],
        optimization: dict[str, Any],
        provider: dict[str, Any],
        paper: dict[str, Any],
        audit: dict[str, Any],
        min_optimization_trades: int,
    ) -> list[dict[str, str]]:
        trades = self._int(backtest.get("simulated_trades"))
        replay_pnl = self._decimal(backtest.get("total_simulated_profit_usd")) or Decimal("0")
        best = optimization.get("best_scenario") if isinstance(optimization.get("best_scenario"), dict) else {}
        best_trades = self._int(best.get("trade_count"))
        best_pnl = self._decimal(best.get("total_pnl_usd")) or Decimal("0")
        provider_status = str(provider.get("overall_status", "UNKNOWN"))
        provider_alerts = self._int(provider.get("alert_count"))
        paper_pnl = self._decimal(paper.get("portfolio_analytics", {}).get("total_pnl_usd"))
        audit_findings = self._audit_finding_count(audit)

        gates = [
            self._gate(
                "default_replay_has_positive_trades",
                trades > 0 and replay_pnl > 0,
                f"Default replay trades={trades}, pnl_usd={replay_pnl}.",
                fail_reason="Default replay did not produce positive production-buffer evidence.",
            ),
            self._gate(
                "optimization_has_minimum_sample",
                best_trades >= min_optimization_trades and best_pnl > 0,
                f"Best scenario trades={best_trades}, pnl_usd={best_pnl}, min_trades={min_optimization_trades}.",
                fail_reason="Optimization does not have enough positive research samples.",
            ),
        ]

        if provider_status == "CRITICAL":
            gates.append(
                {
                    "name": "provider_health_not_critical",
                    "status": "FAIL",
                    "message": f"Provider status is CRITICAL with {provider_alerts} alert(s).",
                }
            )
        elif provider_status in {"DEGRADED", "WATCH"}:
            gates.append(
                {
                    "name": "provider_health_not_critical",
                    "status": "WARN",
                    "message": f"Provider status is {provider_status} with {provider_alerts} alert(s).",
                }
            )
        else:
            gates.append(
                {
                    "name": "provider_health_not_critical",
                    "status": "PASS",
                    "message": f"Provider status is {provider_status}.",
                }
            )

        if paper_pnl is None:
            gates.append({"name": "paper_pnl_non_negative", "status": "WARN", "message": "Paper PnL is unavailable."})
        else:
            gates.append(
                self._gate(
                    "paper_pnl_non_negative",
                    paper_pnl >= 0,
                    f"Paper total_pnl_usd={paper_pnl}.",
                    fail_reason="Paper PnL is negative.",
                )
            )

        if audit_findings:
            gates.append(
                {
                    "name": "report_audit_has_no_findings",
                    "status": "WARN",
                    "message": f"Report audit has {audit_findings} finding(s). Review before tuning.",
                }
            )
        else:
            gates.append({"name": "report_audit_has_no_findings", "status": "PASS", "message": "Report audit has no findings."})
        return gates

    def _summary(
        self,
        backtest: dict[str, Any],
        optimization: dict[str, Any],
        provider: dict[str, Any],
        paper: dict[str, Any],
        audit: dict[str, Any],
        execution_cost: dict[str, Any],
    ) -> dict[str, Any]:
        best = optimization.get("best_scenario") if isinstance(optimization.get("best_scenario"), dict) else {}
        cost_assessment = execution_cost.get("assessment") if isinstance(execution_cost.get("assessment"), dict) else {}
        return {
            "backtest_total_signals": backtest.get("total_signals"),
            "backtest_trades": backtest.get("simulated_trades"),
            "backtest_pnl_usd": backtest.get("total_simulated_profit_usd"),
            "optimization_scenarios": optimization.get("scenario_count"),
            "optimization_best_trades": best.get("trade_count"),
            "optimization_best_pnl_usd": best.get("total_pnl_usd"),
            "optimization_best_cost_buffer_pct": best.get("cost_buffer_pct"),
            "provider_status": provider.get("overall_status"),
            "provider_alert_count": provider.get("alert_count"),
            "paper_total_pnl_usd": paper.get("portfolio_analytics", {}).get("total_pnl_usd"),
            "audit_finding_count": self._audit_finding_count(audit),
            "execution_cost_buffer_status": execution_cost.get("buffer_status", cost_assessment.get("buffer_status")),
            "execution_cost_confidence": execution_cost.get("confidence", cost_assessment.get("confidence")),
            "observed_total_cost_lower_bound_pct": execution_cost.get(
                "observed_total_cost_lower_bound_pct",
                cost_assessment.get("observed_total_cost_lower_bound_pct"),
            ),
        }

    @staticmethod
    def _replay_diagnostic_summary(replay_diagnostics: dict[str, Any]) -> dict[str, Any]:
        return {
            "production_cost_buffer_pct": replay_diagnostics.get("production_cost_buffer_pct"),
            "production_trade_count": replay_diagnostics.get("production_trade_count"),
            "best_profitable_cost_buffer_pct": replay_diagnostics.get("best_profitable_cost_buffer_pct"),
            "best_profitable_trade_count": replay_diagnostics.get("best_profitable_trade_count"),
            "best_profitable_total_pnl_usd": replay_diagnostics.get("best_profitable_total_pnl_usd"),
            "findings": replay_diagnostics.get("findings", []),
        }

    @staticmethod
    def _execution_cost_summary(execution_cost: dict[str, Any]) -> dict[str, Any]:
        assessment = execution_cost.get("assessment") if isinstance(execution_cost.get("assessment"), dict) else {}
        return {
            "buffer_status": execution_cost.get("buffer_status", assessment.get("buffer_status")),
            "confidence": execution_cost.get("confidence", assessment.get("confidence")),
            "production_cost_buffer_pct": execution_cost.get("production_cost_buffer_pct", assessment.get("production_cost_buffer_pct")),
            "observed_total_cost_lower_bound_pct": execution_cost.get(
                "observed_total_cost_lower_bound_pct",
                assessment.get("observed_total_cost_lower_bound_pct"),
            ),
            "buffer_surplus_vs_lower_bound_pct": execution_cost.get(
                "buffer_surplus_vs_lower_bound_pct",
                assessment.get("buffer_surplus_vs_lower_bound_pct"),
            ),
            "findings": execution_cost.get("findings", []),
        }

    @staticmethod
    def _gate(name: str, passed: bool, success_message: str, fail_reason: str) -> dict[str, str]:
        return {
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "message": success_message if passed else f"{fail_reason} {success_message}",
        }

    def _append_history(self, experiment: dict[str, Any]) -> None:
        with self.history_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(experiment) + "\n")

    def _read_history(self, limit: int | None = None) -> list[dict[str, Any]]:
        if not self.history_file.exists():
            return []
        rows = []
        for line in self.history_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if limit is None:
            return rows
        return rows[-limit:]

    def _markdown(self, payload: dict[str, Any]) -> str:
        latest = payload["latest_experiment"]
        lines = [
            "# CryptoAI Experiment Report",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Latest Experiment",
            "",
            f"- Experiment ID: `{latest['experiment_id']}`",
            f"- Label: `{latest['label']}`",
            f"- Status: `{latest['status']}`",
            f"- Promotion allowed: `{latest['promotion_allowed']}`",
            f"- Gates: `{latest['pass_count']} pass / {latest['warn_count']} warn / {latest['fail_count']} fail`",
            f"- History count: `{payload['experiment_count']}`",
            "",
            "## Summary",
            "",
        ]
        for key, value in latest["summary"].items():
            lines.append(f"- {key}: `{value}`")
        lines += ["", "## Replay Diagnostics", ""]
        for key, value in latest.get("replay_diagnostics", {}).items():
            if key == "findings":
                continue
            lines.append(f"- {key}: `{value}`")
        findings = latest.get("replay_diagnostics", {}).get("findings", [])
        for finding in findings:
            lines.append(f"- {finding.get('severity', '-')}: {finding.get('message', '-')}")
        lines += ["", "## Execution Cost Evidence", ""]
        for key, value in latest.get("execution_cost_evidence", {}).items():
            if key == "findings":
                continue
            lines.append(f"- {key}: `{value}`")
        cost_findings = latest.get("execution_cost_evidence", {}).get("findings", [])
        for finding in cost_findings:
            lines.append(f"- {finding.get('severity', '-')}: {finding.get('message', '-')}")
        lines += ["", "## Gates", "", "| Gate | Status | Message |", "|---|---|---|"]
        for gate in latest["gates"]:
            lines.append(f"| {gate['name']} | {gate['status']} | {gate['message'].replace('|', '/')} |")
        lines += ["", "## Recent Experiments", "", "| Time | ID | Status | Pass | Warn | Fail |", "|---|---|---|---:|---:|---:|"]
        for experiment in payload["recent_experiments"][-10:]:
            lines.append(
                f"| {experiment.get('generated_at')} | {experiment.get('experiment_id')} | {experiment.get('status')} | "
                f"{experiment.get('pass_count')} | {experiment.get('warn_count')} | {experiment.get('fail_count')} |"
            )
        lines += ["", "## Notes", ""]
        for note in latest.get("notes", []):
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _experiment_id(generated_at: str, label: str, gates: list[dict[str, str]]) -> str:
        raw = json.dumps({"generated_at": generated_at, "label": label, "gates": gates}, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

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
    def _decimal(value: Any) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value)
        except Exception:
            return 0

    @classmethod
    def _audit_finding_count(cls, audit: dict[str, Any]) -> int:
        findings = audit.get("findings")
        if not isinstance(findings, list):
            return cls._int(audit.get("finding_count"))
        downstream_reports = {
            "experiment_report.json",
            "experiment_report.md",
            "strategy_intelligence.json",
            "strategy_intelligence.md",
        }
        actionable = [
            finding
            for finding in findings
            if not (
                isinstance(finding, dict)
                and finding.get("report") in downstream_reports
                and finding.get("message") == "Report is older than freshness window."
            )
        ]
        return len(actionable)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    print(json.dumps(ExperimentService().run(), indent=2))


if __name__ == "__main__":
    main()
