from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any


class QuoteDiagnosticStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    INVALID = "INVALID"


@dataclass(frozen=True)
class QuoteDiagnostic:
    timestamp: str
    chain: str
    dex: str
    pair: str
    token_in: str
    token_out: str
    amount_in: str
    amount_out: str | None
    price: str | None
    latency_ms: float
    status: QuoteDiagnosticStatus
    error: str


class QuoteDiagnosticsService:
    """Quote-layer debugger that preserves cache/snapshots."""

    def __init__(self) -> None:
        self.data_dir = Path("data")
        self.report_dir = Path("reports")
        self.data_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.output_file = self.data_dir / "quote_diagnostics.jsonl"
        self.report_file = self.report_dir / "quote_diagnostics.md"

    def run(self) -> list[QuoteDiagnostic]:
        start = time.perf_counter()
        diagnostics: list[QuoteDiagnostic] = []

        try:
            from app.quotes.quote_service import QuoteService
            quote_service = QuoteService()
        except Exception as exc:
            diagnostics.append(self._service_error("QuoteService import/init failed", exc, start))
            self._persist(diagnostics)
            self._write_report(diagnostics)
            return diagnostics

        try:
            quote_start = time.perf_counter()
            quotes = quote_service.get_base_quotes()
            base_latency = (time.perf_counter() - quote_start) * 1000
        except Exception as exc:
            diagnostics.append(self._service_error("QuoteService.get_base_quotes failed", exc, start))
            self._persist(diagnostics)
            self._write_report(diagnostics)
            return diagnostics

        if not quotes:
            diagnostics.append(QuoteDiagnostic(timestamp=self._utc_now(), chain="base", dex="-", pair="-", token_in="-", token_out="-", amount_in="-", amount_out=None, price=None, latency_ms=round(base_latency, 2), status=QuoteDiagnosticStatus.ERROR, error="QuoteService returned an empty quote list."))
        else:
            per_quote_latency = round(base_latency / max(1, len(quotes)), 2)
            for quote in quotes:
                diagnostics.append(self._diagnose_quote(quote, per_quote_latency))

        self._persist(diagnostics)
        self._write_report(diagnostics)
        return diagnostics

    def recent(self, limit: int = 100) -> list[dict]:
        if not self.output_file.exists():
            return []
        rows = []
        for line in self.output_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
        return rows[-limit:]

    def _diagnose_quote(self, quote: Any, latency_ms: float) -> QuoteDiagnostic:
        chain = str(getattr(quote, "chain", "base"))
        dex = str(getattr(quote, "dex", "-"))
        token_in = str(getattr(quote, "token_in", "-"))
        token_out = str(getattr(quote, "token_out", "-"))
        pair = f"{token_in}/{token_out}"
        amount_in = str(getattr(quote, "amount_in", "-"))
        amount_out = getattr(quote, "amount_out", None)
        price = getattr(quote, "price", None)
        error = getattr(quote, "error", None)

        if error:
            status = QuoteDiagnosticStatus.ERROR
            error_text = str(error)
        elif self._to_decimal(price) is None or self._to_decimal(price) <= 0:
            status = QuoteDiagnosticStatus.INVALID
            error_text = "Quote has missing/zero/invalid price."
        elif self._to_decimal(amount_out) is None or self._to_decimal(amount_out) <= 0:
            status = QuoteDiagnosticStatus.INVALID
            error_text = "Quote has missing/zero/invalid amount_out."
        else:
            status = QuoteDiagnosticStatus.OK
            error_text = ""

        return QuoteDiagnostic(timestamp=self._utc_now(), chain=chain, dex=dex, pair=pair, token_in=token_in, token_out=token_out, amount_in=amount_in, amount_out=str(amount_out) if amount_out is not None else None, price=str(price) if price is not None else None, latency_ms=latency_ms, status=status, error=error_text)

    def _service_error(self, context: str, exc: Exception, start: float) -> QuoteDiagnostic:
        return QuoteDiagnostic(timestamp=self._utc_now(), chain="base", dex="-", pair="-", token_in="-", token_out="-", amount_in="-", amount_out=None, price=None, latency_ms=round((time.perf_counter() - start) * 1000, 2), status=QuoteDiagnosticStatus.ERROR, error=f"{context}: {type(exc).__name__}: {exc}")

    def _persist(self, diagnostics: list[QuoteDiagnostic]) -> None:
        with self.output_file.open("a", encoding="utf-8") as fh:
            for diag in diagnostics:
                payload = asdict(diag)
                payload["status"] = diag.status.value
                fh.write(json.dumps(payload) + "\n")

    def _write_report(self, diagnostics: list[QuoteDiagnostic]) -> None:
        ok = sum(1 for d in diagnostics if d.status == QuoteDiagnosticStatus.OK)
        errors = sum(1 for d in diagnostics if d.status == QuoteDiagnosticStatus.ERROR)
        invalid = sum(1 for d in diagnostics if d.status == QuoteDiagnosticStatus.INVALID)

        lines = [
            "# CryptoAI Quote Diagnostics",
            "",
            f"Generated: `{self._utc_now()}`",
            "",
            "## Summary",
            "",
            f"- Total quote diagnostics: `{len(diagnostics)}`",
            f"- OK: `{ok}`",
            f"- Error: `{errors}`",
            f"- Invalid: `{invalid}`",
            "",
            "## Quote Rows",
            "",
            "| Chain | DEX | Pair | Status | Price | Amount Out | Latency ms | Error |",
            "|---|---|---|---|---:|---:|---:|---|",
        ]

        for d in diagnostics:
            lines.append(f"| {d.chain} | {d.dex} | {d.pair} | {d.status.value} | {d.price or '-'} | {d.amount_out or '-'} | {d.latency_ms:.2f} | {d.error.replace('|', '/')} |")

        lines += ["", "## Interpretation", ""]
        if ok >= 2:
            lines.append("- Quote layer has at least two valid quotes or a recent healthy snapshot.")
        elif ok > 0:
            lines.append("- Quote layer has one valid quote. Real arbitrage needs another venue, but simulated paper validation may still run.")
        else:
            lines.append("- No valid quotes. Check RPC limits and provider errors. Configure BASE_RPC with a private RPC.")

        if errors:
            lines.append("- Errors are isolated and should not crash the paper pipeline.")

        self.report_file.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    diagnostics = QuoteDiagnosticsService().run()
    for diag in diagnostics:
        payload = asdict(diag)
        payload["status"] = diag.status.value
        print(payload)


if __name__ == "__main__":
    main()
