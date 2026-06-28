from __future__ import annotations

import importlib
import json
import os
import traceback
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


st.set_page_config(page_title="CryptoAI", page_icon="📊", layout="wide")

DATA_DIR = Path("data")
REPORT_DIR = Path("reports")


def render_header() -> None:
    st.title("📊 CryptoAI Paper Trading Control Center")
    st.caption("Stable dashboard: reads reports/files by default; runs heavy services only when you click a button.")


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


def read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}


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
    st.write("This runs one local paper cycle only when you click the button.")

    enable_paper = st.checkbox("Enable paper execution", value=True)

    if st.button("Run Paper Autopilot Once"):
        def task():
            PaperAutopilot = import_object("app.automation.paper_autopilot", "PaperAutopilot")
            return PaperAutopilot(enable_paper_execution=enable_paper).run_once()

        result = safe_run("Running paper autopilot...", task)
        if result is not None:
            st.success("Paper autopilot completed.")
            st.json(result)

    st.markdown("### GitHub Actions")
    st.write("For scheduled runs, use GitHub Actions. Each run executes once and uploads reports.")
    st.code("python -m app.automation.paper_autopilot --once", language="bash")


def render_opportunity_explorer() -> None:
    st.subheader("Opportunity Explorer")
    st.caption("Explains why candidates are BUY / WATCH / SKIP.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Run Opportunity Scan"):
            def task():
                OpportunityExplorerService = import_object(
                    "app.opportunities.opportunity_explorer",
                    "OpportunityExplorerService",
                )
                return OpportunityExplorerService().scan()

            decisions = safe_run("Running opportunity scan...", task)
            if decisions is not None:
                st.success(f"Scan completed. Decisions: {len(decisions)}")

    with c2:
        if st.button("Refresh File View"):
            st.rerun()

    st.markdown("### Recent Opportunity Decisions")
    rows = read_jsonl(DATA_DIR / "opportunity_decisions.jsonl", limit=100)
    dataframe_or_info(rows, "No opportunity decisions saved yet. Run Opportunity Scan.")

    st.markdown("### Opportunity Report")
    txt = read_text(REPORT_DIR / "opportunity_explorer.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No opportunity_explorer.md found yet.")


def render_reports() -> None:
    st.subheader("Reports")

    for title, path in [
        ("Paper Trading Report", REPORT_DIR / "paper_report.md"),
        ("Opportunity Explorer Report", REPORT_DIR / "opportunity_explorer.md"),
    ]:
        st.markdown(f"### {title}")
        txt = read_text(path)
        if txt:
            st.markdown(txt)
        else:
            st.info(f"{path} not found yet.")

    st.markdown("### Generate Paper Report")
    if st.button("Generate / Refresh Paper Report"):
        def task():
            PaperReportService = import_object("app.reporting.paper_report", "PaperReportService")
            return PaperReportService().generate()

        result = safe_run("Generating paper report...", task)
        if result is not None:
            st.success("Paper report generated.")
            st.json(result)


def render_paper_orders() -> None:
    st.subheader("Paper Orders")
    st.caption("This reads `data/paper_orders.jsonl` directly, without invoking trading services.")

    rows = read_jsonl(DATA_DIR / "paper_orders.jsonl", limit=200)
    dataframe_or_info(rows, "No paper orders saved yet.")

    if rows:
        status_counts: dict[str, int] = {}
        for row in rows:
            status = str(row.get("status", "UNKNOWN"))
            status_counts[status] = status_counts.get(status, 0) + 1
        st.markdown("### Status Counts")
        st.json(status_counts)


def render_portfolio() -> None:
    st.subheader("Portfolio")
    st.caption("File-first view. Live snapshot only runs if you click the button.")

    st.markdown("### Latest Saved Portfolio Snapshots")
    db_path = DATA_DIR / "cryptoai.db"
    if db_path.exists():
        st.info("SQLite database exists. For now this stable dashboard does not query SQLite directly.")
    else:
        st.info("No local SQLite database found yet.")

    if st.button("Load Live Simulated Portfolio Snapshot"):
        def task():
            PortfolioService = import_object("app.portfolio.portfolio_service", "PortfolioService")
            return PortfolioService().get_snapshot()

        snapshot = safe_run("Loading portfolio snapshot...", task)
        if snapshot is not None:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Value", f"${snapshot.total_value_usd:.2f}")
            c2.metric("Cash", f"${snapshot.cash_usd:.2f}")
            c3.metric("Holdings", f"${snapshot.holdings_value_usd:.2f}")
            c4.metric("Unrealized P/L", f"${snapshot.unrealized_pnl_usd:.2f}")

            rows = [
                {
                    "chain": h.chain,
                    "symbol": h.symbol,
                    "quantity": str(h.quantity),
                    "market_value_usd": str(h.market_value_usd),
                    "unrealized_pnl_usd": str(h.unrealized_pnl_usd),
                }
                for h in snapshot.holdings
            ]
            dataframe_or_info(rows, "No holdings.")


def render_risk_controls() -> None:
    st.subheader("Risk & Trading Controls")

    st.markdown("### Environment Safety Flags")
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

    if st.button("Run Trading Controls Service"):
        def task():
            TradingControlsService = import_object(
                "app.execution.trading_controls_service",
                "TradingControlsService",
            )
            service = TradingControlsService()
            return {"status": service.get_status(), "checklist": service.checklist()}

        result = safe_run("Checking trading controls...", task)
        if result is not None:
            st.markdown("### Status")
            st.json(result["status"])
            st.markdown("### Checklist")
            dataframe_or_info(result["checklist"], "No checklist.")


def render_system_health() -> None:
    st.subheader("System Health")

    st.markdown("### Runtime Files")
    rows = []
    for path in [
        DATA_DIR,
        REPORT_DIR,
        DATA_DIR / "paper_orders.jsonl",
        DATA_DIR / "opportunity_decisions.jsonl",
        DATA_DIR / "cryptoai.db",
        REPORT_DIR / "paper_report.md",
        REPORT_DIR / "paper_report.json",
        REPORT_DIR / "opportunity_explorer.md",
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

    if st.button("Run System Health Service"):
        def task():
            SystemHealthService = import_object("app.services.system_health_service", "SystemHealthService")
            service = SystemHealthService()
            return {"metrics": service.get_metric_rows(), "cache": service.get_cache_stats()}

        result = safe_run("Loading system health...", task)
        if result is not None:
            st.markdown("### Metrics")
            dataframe_or_info(result["metrics"], "No metrics.")
            st.markdown("### Cache")
            st.json(result["cache"])


def render_diagnostics() -> None:
    st.subheader("Diagnostics")
    st.write("This checks imports without running heavy scans.")

    checks = [
        ("PaperAutopilot", "app.automation.paper_autopilot", "PaperAutopilot"),
        ("OpportunityExplorerService", "app.opportunities.opportunity_explorer", "OpportunityExplorerService"),
        ("PaperReportService", "app.reporting.paper_report", "PaperReportService"),
        ("PaperExecutionService", "app.execution.paper_execution_service", "PaperExecutionService"),
        ("TradingControlsService", "app.execution.trading_controls_service", "TradingControlsService"),
        ("PortfolioService", "app.portfolio.portfolio_service", "PortfolioService"),
        ("SystemHealthService", "app.services.system_health_service", "SystemHealthService"),
    ]

    rows = []
    for name, module_path, object_name in checks:
        try:
            import_object(module_path, object_name)
            rows.append({"module": name, "status": "OK", "error": ""})
        except Exception as exc:
            rows.append({"module": name, "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"})

    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def render_setup() -> None:
    st.subheader("Setup / Roadmap")
    st.markdown(
        """
        ### Practical next steps

        1. Keep GitHub Actions running every 15 minutes for paper validation.
        2. Use Opportunity Explorer to understand each SKIP/WATCH reason.
        3. Tune thresholds only after reviewing several reports.
        4. Do not connect a wallet or private key yet.

        ### Commands

        ```bash
        python -m app.opportunities.opportunity_explorer
        python -m app.automation.paper_autopilot --once
        python -m app.reporting.paper_report
        python -m streamlit run streamlit_app.py
        ```
        """
    )


PAGES = {
    "1 Paper Autopilot": render_paper_autopilot,
    "2 Opportunity Explorer": render_opportunity_explorer,
    "3 Reports": render_reports,
    "4 Paper Orders": render_paper_orders,
    "5 Portfolio": render_portfolio,
    "6 Risk & Controls": render_risk_controls,
    "7 System Health": render_system_health,
    "8 Diagnostics": render_diagnostics,
    "9 Setup / Roadmap": render_setup,
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
