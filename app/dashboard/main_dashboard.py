from __future__ import annotations

import importlib
import json
import os
import traceback
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="CryptoAI", page_icon="📊", layout="wide")

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")


def render_header() -> None:
    st.title("📊 CryptoAI Paper Trading Control Center")
    st.caption("Focus: quote diagnostics → opportunity decisions → paper trading reports.")


def read_jsonl(path: Path, limit: int = 100) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
    except Exception as exc:
        return [{"error": str(exc), "path": str(path)}]
    return rows[-limit:]


def read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"Failed reading {path}: {exc}"


def dataframe_or_info(rows: list[dict], message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(message)


def show_exception(exc: BaseException) -> None:
    st.error(f"{type(exc).__name__}: {exc}")
    st.code("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)), language="text")


def import_object(module_path: str, object_name: str):
    module = importlib.import_module(module_path)
    return getattr(module, object_name)


def safe_run(label: str, fn):
    with st.spinner(label):
        try:
            return fn()
        except Exception as exc:
            show_exception(exc)
            return None


def render_paper_autopilot() -> None:
    st.subheader("Paper Autopilot")
    enable_paper = st.checkbox("Enable paper execution", value=True)

    if st.button("Run Paper Autopilot Once"):
        def task():
            PaperAutopilot = import_object("app.automation.paper_autopilot", "PaperAutopilot")
            return PaperAutopilot(enable_paper_execution=enable_paper).run_once()

        result = safe_run("Running paper autopilot...", task)
        if result is not None:
            st.success("Paper autopilot completed.")
            st.json(result)


def render_quote_diagnostics() -> None:
    st.subheader("Quote Diagnostics")
    st.caption("This is now the most important page. It tells us why quote collection is failing.")

    if st.button("Run Quote Diagnostics"):
        def task():
            QuoteDiagnosticsService = import_object("app.diagnostics.quote_diagnostics", "QuoteDiagnosticsService")
            return QuoteDiagnosticsService().run()

        result = safe_run("Running quote diagnostics...", task)
        if result is not None:
            st.success(f"Quote diagnostics completed. Rows: {len(result)}")

    st.markdown("### Recent Quote Diagnostics")
    dataframe_or_info(read_jsonl(DATA_DIR / "quote_diagnostics.jsonl", limit=100), "No quote diagnostics saved yet.")

    st.markdown("### Quote Diagnostics Report")
    txt = read_text(REPORT_DIR / "quote_diagnostics.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No quote_diagnostics.md found yet.")


def render_opportunity_explorer() -> None:
    st.subheader("Opportunity Explorer")
    if st.button("Run Opportunity Scan"):
        def task():
            OpportunityExplorerService = import_object("app.opportunities.opportunity_explorer", "OpportunityExplorerService")
            return OpportunityExplorerService().scan()

        result = safe_run("Running opportunity scan...", task)
        if result is not None:
            st.success(f"Opportunity scan completed. Decisions: {len(result)}")

    st.markdown("### Recent Opportunity Decisions")
    dataframe_or_info(read_jsonl(DATA_DIR / "opportunity_decisions.jsonl", limit=100), "No opportunity decisions saved yet.")

    st.markdown("### Opportunity Report")
    txt = read_text(REPORT_DIR / "opportunity_explorer.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No opportunity_explorer.md found yet.")


def render_reports() -> None:
    st.subheader("Reports")

    if st.button("Generate / Refresh Paper Report"):
        def task():
            PaperReportService = import_object("app.reporting.paper_report", "PaperReportService")
            return PaperReportService().generate()

        result = safe_run("Generating paper report...", task)
        if result is not None:
            st.success("Paper report generated.")
            st.json(result)

    for title, path in [
        ("Quote Diagnostics", REPORT_DIR / "quote_diagnostics.md"),
        ("Opportunity Explorer", REPORT_DIR / "opportunity_explorer.md"),
        ("Paper Trading", REPORT_DIR / "paper_report.md"),
    ]:
        st.markdown(f"### {title}")
        txt = read_text(path)
        if txt:
            st.markdown(txt)
        else:
            st.info(f"{path} not found yet.")


def render_paper_orders() -> None:
    st.subheader("Paper Orders")
    rows = read_jsonl(DATA_DIR / "paper_orders.jsonl", limit=200)
    dataframe_or_info(rows, "No paper orders saved yet.")

    if rows:
        status_counts: dict[str, int] = {}
        for row in rows:
            status = str(row.get("status", "UNKNOWN"))
            status_counts[status] = status_counts.get(status, 0) + 1
        st.markdown("### Status Counts")
        st.json(status_counts)


def render_risk_controls() -> None:
    st.subheader("Risk & Trading Controls")
    flags = {
        "CRYPTOAI_LIVE_TRADING_ENABLED": os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false"),
        "CRYPTOAI_PAPER_TRADING_ENABLED": os.getenv("CRYPTOAI_PAPER_TRADING_ENABLED", "true"),
        "CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION": os.getenv("CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION", "true"),
        "CRYPTOAI_MAX_LIVE_TRADE_USD": os.getenv("CRYPTOAI_MAX_LIVE_TRADE_USD", "0"),
        "CRYPTOAI_MAX_DAILY_LOSS_USD": os.getenv("CRYPTOAI_MAX_DAILY_LOSS_USD", "0"),
        "CRYPTOAI_PRIVATE_KEY": "PRESENT" if os.getenv("CRYPTOAI_PRIVATE_KEY") else "ABSENT",
    }
    st.json(flags)

    if flags["CRYPTOAI_LIVE_TRADING_ENABLED"].lower() in {"1", "true", "yes", "on"}:
        st.error("Live trading flag is ON. Turn it OFF during paper testing.")
    else:
        st.success("Live trading is disabled.")


def render_system_health() -> None:
    st.subheader("System Health")
    rows = []
    for path in [
        DATA_DIR,
        REPORT_DIR,
        DATA_DIR / "quote_diagnostics.jsonl",
        DATA_DIR / "opportunity_decisions.jsonl",
        DATA_DIR / "paper_orders.jsonl",
        REPORT_DIR / "quote_diagnostics.md",
        REPORT_DIR / "opportunity_explorer.md",
        REPORT_DIR / "paper_report.md",
    ]:
        rows.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "type": "dir" if path.is_dir() else "file" if path.exists() else "-",
                "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def render_setup() -> None:
    st.subheader("Setup / Roadmap")
    st.markdown(
        """
        ### Current debugging order

        1. Quote Diagnostics — fix quote errors first.
        2. Opportunity Explorer — compare valid quotes.
        3. Paper Autopilot — execute simulated trades only when opportunities exist.
        4. Reports — review results.

        ### Commands

        ```bash
        python -m app.diagnostics.quote_diagnostics
        python -m app.opportunities.opportunity_explorer
        python -m app.automation.paper_autopilot --once
        python -m app.reporting.paper_report
        ```
        """
    )


PAGES = {
    "1 Paper Autopilot": render_paper_autopilot,
    "2 Quote Diagnostics": render_quote_diagnostics,
    "3 Opportunity Explorer": render_opportunity_explorer,
    "4 Reports": render_reports,
    "5 Paper Orders": render_paper_orders,
    "6 Risk & Controls": render_risk_controls,
    "7 System Health": render_system_health,
    "8 Setup / Roadmap": render_setup,
}


def render_page(page_name: str) -> None:
    try:
        PAGES[page_name]()
    except Exception as exc:
        st.error(f"Page failed: {page_name}")
        show_exception(exc)


render_header()

with st.sidebar:
    st.header("CryptoAI")
    page = st.radio("Navigate", list(PAGES.keys()), index=0)
    st.divider()
    st.caption("Mode: Paper trading only")
    if st.button("Clear cache"):
        st.cache_data.clear()
        st.rerun()

render_page(page)
