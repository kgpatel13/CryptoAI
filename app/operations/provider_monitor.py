from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProviderAlert:
    severity: str
    provider: str
    provider_type: str
    chain: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderMonitorRow:
    name: str
    provider_type: str
    chain: str
    score: int
    status: str
    success_rate_pct: float
    consecutive_failures: int
    avg_latency_ms: float | None
    last_observed_age_seconds: float | None
    last_error: str | None = None
    alerts: list[ProviderAlert] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["alerts"] = [alert.to_dict() for alert in self.alerts]
        return payload


class ProviderMonitorService:
    """Summarizes provider-health observations for operations monitoring."""

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        stale_after_seconds: int | None = None,
        degraded_score_threshold: int | None = None,
        critical_score_threshold: int | None = None,
        consecutive_failure_threshold: int | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.stale_after_seconds = stale_after_seconds or int(os.getenv("CRYPTOAI_PROVIDER_STALE_AFTER_SECONDS", "900"))
        self.degraded_score_threshold = degraded_score_threshold or int(os.getenv("CRYPTOAI_PROVIDER_DEGRADED_SCORE", "70"))
        self.critical_score_threshold = critical_score_threshold or int(os.getenv("CRYPTOAI_PROVIDER_CRITICAL_SCORE", "40"))
        self.consecutive_failure_threshold = consecutive_failure_threshold or int(os.getenv("CRYPTOAI_PROVIDER_FAILURE_THRESHOLD", "3"))

    def generate(self) -> dict[str, Any]:
        provider_rows = self._read_provider_rows()
        now = time.time()
        monitored = [self._monitor_row(row, now) for row in provider_rows]
        alerts = [alert for row in monitored for alert in row.alerts]
        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "provider_count": len(monitored),
            "overall_status": self._overall_status(monitored),
            "alert_count": len(alerts),
            "critical_alert_count": sum(1 for alert in alerts if alert.severity == "CRITICAL"),
            "degraded_alert_count": sum(1 for alert in alerts if alert.severity == "DEGRADED"),
            "stale_after_seconds": self.stale_after_seconds,
            "providers": [row.to_dict() for row in monitored],
            "chains": self._chain_summary(monitored),
            "provider_types": self._type_summary(monitored),
            "alerts": [alert.to_dict() for alert in alerts],
            "notes": [
                "Provider Monitor summarizes existing provider-health observations.",
                "It does not make network calls or execute trades.",
                "Missing provider observations should be treated as incomplete operational evidence.",
            ],
        }
        self._write_json(self.report_dir / "provider_monitor.json", payload)
        self._write_markdown(payload)
        return payload

    def _monitor_row(self, row: dict[str, Any], now: float) -> ProviderMonitorRow:
        score = self._int(row.get("score"), 0)
        consecutive_failures = self._int(row.get("consecutive_failures"), 0)
        last_success_at = self._float(row.get("last_success_at"))
        last_failure_at = self._float(row.get("last_failure_at"))
        last_observed_at = max(value for value in [last_success_at, last_failure_at] if value is not None) if (last_success_at or last_failure_at) else None
        age_seconds = round(now - last_observed_at, 2) if last_observed_at else None

        alerts = self._alerts_for_row(
            row=row,
            score=score,
            consecutive_failures=consecutive_failures,
            age_seconds=age_seconds,
        )
        status = self._status_from_alerts(alerts)
        return ProviderMonitorRow(
            name=str(row.get("name", "unknown")),
            provider_type=str(row.get("provider_type", "unknown")),
            chain=self._normalize_chain(row.get("chain", "unknown")),
            score=score,
            status=status,
            success_rate_pct=self._float(row.get("success_rate_pct")) or 0.0,
            consecutive_failures=consecutive_failures,
            avg_latency_ms=self._float(row.get("avg_latency_ms")),
            last_observed_age_seconds=age_seconds,
            last_error=row.get("last_error"),
            alerts=alerts,
        )

    def _alerts_for_row(
        self,
        row: dict[str, Any],
        score: int,
        consecutive_failures: int,
        age_seconds: float | None,
    ) -> list[ProviderAlert]:
        name = str(row.get("name", "unknown"))
        provider_type = str(row.get("provider_type", "unknown"))
        chain = str(row.get("chain", "unknown"))
        chain = self._normalize_chain(chain)
        alerts: list[ProviderAlert] = []

        if score <= self.critical_score_threshold:
            alerts.append(
                ProviderAlert("CRITICAL", name, provider_type, chain, f"Provider score {score} is at or below critical threshold.")
            )
        elif score < self.degraded_score_threshold:
            alerts.append(
                ProviderAlert("DEGRADED", name, provider_type, chain, f"Provider score {score} is below degraded threshold.")
            )

        if consecutive_failures >= self.consecutive_failure_threshold:
            alerts.append(
                ProviderAlert(
                    "CRITICAL",
                    name,
                    provider_type,
                    chain,
                    f"Provider has {consecutive_failures} consecutive failures.",
                )
            )

        if age_seconds is None:
            alerts.append(ProviderAlert("WATCH", name, provider_type, chain, "Provider has no observation timestamp."))
        elif age_seconds > self.stale_after_seconds:
            alerts.append(
                ProviderAlert(
                    "WATCH",
                    name,
                    provider_type,
                    chain,
                    f"Provider observation is stale at {age_seconds} seconds old.",
                )
            )

        return alerts

    @staticmethod
    def _status_from_alerts(alerts: list[ProviderAlert]) -> str:
        severities = {alert.severity for alert in alerts}
        if "CRITICAL" in severities:
            return "CRITICAL"
        if "DEGRADED" in severities:
            return "DEGRADED"
        if "WATCH" in severities:
            return "WATCH"
        return "OK"

    @staticmethod
    def _overall_status(rows: list[ProviderMonitorRow]) -> str:
        if not rows:
            return "NEEDS_DATA"
        statuses = {row.status for row in rows}
        if "CRITICAL" in statuses:
            return "CRITICAL"
        if "DEGRADED" in statuses:
            return "DEGRADED"
        if "WATCH" in statuses:
            return "WATCH"
        return "OK"

    @staticmethod
    def _chain_summary(rows: list[ProviderMonitorRow]) -> list[dict[str, Any]]:
        by_chain: dict[str, list[ProviderMonitorRow]] = {}
        for row in rows:
            by_chain.setdefault(row.chain, []).append(row)
        summary = []
        for chain, chain_rows in sorted(by_chain.items()):
            scores = [row.score for row in chain_rows]
            summary.append(
                {
                    "chain": chain,
                    "provider_count": len(chain_rows),
                    "average_score": round(sum(scores) / len(scores)) if scores else 0,
                    "status": ProviderMonitorService._overall_status(chain_rows),
                    "critical_count": sum(1 for row in chain_rows if row.status == "CRITICAL"),
                    "degraded_count": sum(1 for row in chain_rows if row.status == "DEGRADED"),
                    "watch_count": sum(1 for row in chain_rows if row.status == "WATCH"),
                }
            )
        return summary

    @staticmethod
    def _type_summary(rows: list[ProviderMonitorRow]) -> list[dict[str, Any]]:
        by_type: dict[str, list[ProviderMonitorRow]] = {}
        for row in rows:
            by_type.setdefault(row.provider_type, []).append(row)
        summary = []
        for provider_type, type_rows in sorted(by_type.items()):
            scores = [row.score for row in type_rows]
            summary.append(
                {
                    "provider_type": provider_type,
                    "provider_count": len(type_rows),
                    "average_score": round(sum(scores) / len(scores)) if scores else 0,
                    "status": ProviderMonitorService._overall_status(type_rows),
                }
            )
        return summary

    def _read_provider_rows(self) -> list[dict[str, Any]]:
        path = self.data_dir / "provider_health.json"
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            return []
        rows = payload.get("providers", [])
        return rows if isinstance(rows, list) else []

    def _write_markdown(self, payload: dict[str, Any]) -> None:
        lines = [
            "# CryptoAI Provider Monitor",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{payload['mode']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Providers: `{payload['provider_count']}`",
            f"- Alerts: `{payload['alert_count']}`",
            f"- Critical alerts: `{payload['critical_alert_count']}`",
            "",
            "## Providers",
            "",
            "| Chain | Type | Provider | Score | Status | Consecutive Failures | Age Seconds | Error |",
            "|---|---|---|---:|---|---:|---:|---|",
        ]
        for row in payload["providers"]:
            error = str(row.get("last_error") or "").replace("|", "/")[:100]
            lines.append(
                f"| {row['chain']} | {row['provider_type']} | {row['name']} | {row['score']} | "
                f"{row['status']} | {row['consecutive_failures']} | {row['last_observed_age_seconds']} | {error} |"
            )

        lines += ["", "## Alerts", "", "| Severity | Chain | Type | Provider | Message |", "|---|---|---|---|---|"]
        for alert in payload["alerts"]:
            message = str(alert["message"]).replace("|", "/")
            lines.append(
                f"| {alert['severity']} | {alert['chain']} | {alert['provider_type']} | "
                f"{alert['provider']} | {message} |"
            )
        if not payload["alerts"]:
            lines.append("| OK | - | - | - | No provider alerts. |")

        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        (self.report_dir / "provider_monitor.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _normalize_chain(chain: Any) -> str:
        normalized = str(chain).strip().lower()
        aliases = {
            "base": "base",
            "ethereum": "ethereum",
            "ethereum mainnet": "ethereum",
            "arbitrum one": "arbitrum",
            "arbitrum": "arbitrum",
            "polygon": "polygon",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _int(value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = ProviderMonitorService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
