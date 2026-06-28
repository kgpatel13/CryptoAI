from __future__ import annotations

import traceback
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="CryptoAI", page_icon="📊", layout="wide")


def safe_import(module_path: str, class_name: str):
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name), None
    except Exception as exc:
        return None, exc


PaperAutopilot, PaperAutopilotErr = safe_import("app.automation.paper_autopilot", "PaperAutopilot")
OpportunityExplorerService, OpportunityExplorerErr = safe_import("app.opportunities.opportunity_explorer", "OpportunityExplorerService")
PaperExecutionService, PaperExecutionErr = safe_import("app.execution.paper_execution_service", "PaperExecutionService")
TradingControlsService, TradingControlsErr = safe_import("app.execution.trading_controls_service", "TradingControlsService")
PortfolioService, PortfolioErr = safe_import("app.portfolio.portfolio_service", "PortfolioService")
SystemHealthService, SystemHealthErr = safe_import("app.services.system_health_service", "SystemHealthService")


def dataframe_or_info(rows, message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(message)


def show_module_error(name: str, err: Exception | None) -> None:
    if err is None:
        return
    st.error(f"{name} failed to import.")
    st.code("".join(traceback.format_exception(type(err), err, err.__traceback__)), language="text")


def render_header() -> None:
    st.title("📊 CryptoAI Paper Trading Control Center")
    st.caption("Focused dashboard: paper autopilot, opportunity decisions, reports, risk, and health.")


def render_autopilot() -> None:
    st.subheader("Paper Autopilot")
    show_module_error("PaperAutopilot", PaperAutopilotErr)

    if PaperAutopilot is None:
        return

    enable_paper = st.checkbox("Enable paper execution", value=True)

    if st.button("Run Paper Autopilot Once"):
        result = PaperAutopilot(enable_paper_execution=enable_paper).run_once()
        st.json(result)

    st.markdown("### GitHub Actions")
    st.write("Use GitHub Actions for scheduled paper runs. Each run is one cycle and uploads reports.")
    st.code("python -m app.automation.paper_autopilot --once", language="bash")


def render_opportunity_explorer() -> None:
    st.subheader("Opportunity Explorer")
    st.caption("This explains why trades are BUY / WATCH / SKIP.")
    show_module_error("OpportunityExplorerService", OpportunityExplorerErr)

    if OpportunityExplorerService is None:
        return

    service = OpportunityExplorerService()

    if st.button("Run Opportunity Scan"):
        decisions = service.scan()
    else:
        decisions = []

    rows = []
    source = decisions if decisions else service.recent_decisions(limit=50)

    for d in source:
        if isinstance(d, dict):
            rows.append(d)
        else:
            rows.append(
                {
                    "timestamp": "",
                    "pair": d.pair,
                    "buy_source": d.buy_source,
                    "sell_source": d.sell_source,
                    "gross_spread_pct": str(d.gross_spread_pct) if d.gross_spread_pct is not None else "-",
                    "total_cost_buffer_pct": str(d.total_cost_buffer_pct),
                    "estimated_net_edge_pct": str(d.estimated_net_edge_pct) if d.estimated_net_edge_pct is not None else "-",
                    "readiness_score": d.readiness_score,
                    "decision": d.decision.value,
                    "reason": d.reason,
                }
            )

    dataframe_or_info(rows, "No opportunity decisions yet. Run Opportunity Scan or Paper Autopilot.")


def render_reports() -> None:
    st.subheader("Reports")

    for label, path in [
        ("Paper Report", Path("reports/paper_report.md")),
        ("Opportunity Explorer Report", Path("reports/opportunity_explorer.md")),
    ]:
        st.markdown(f"### {label}")
        if path.exists():
            st.markdown(path.read_text(encoding="utf-8"))
        else:
            st.info(f"{path} not found yet. Run the related scanner/report command first.")


def render_paper_orders() -> None:
    st.subheader("Paper Orders")
    show_module_error("PaperExecutionService", PaperExecutionErr)

    if PaperExecutionService is None:
        return

    service = PaperExecutionService()
    dataframe_or_info(service.recent_orders(), "No paper orders saved yet.")


def render_portfolio() -> None:
    st.subheader("Portfolio")
    show_module_error("PortfolioService", PortfolioErr)

    if PortfolioService is None:
        return

    snapshot = PortfolioService().get_snapshot()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Value", f"${snapshot.total_value_usd:.2f}")
    c2.metric("Cash", f"${snapshot.cash_usd:.2f}")
    c3.metric("Holdings", f"${snapshot.holdings_value_usd:.2f}")
    c4.metric("Unrealized P/L", f"${snapshot.unrealized_pnl_usd:.2f}")

    st.markdown("### Holdings")
    dataframe_or_info(
        [
            {
                "chain": h.chain,
                "symbol": h.symbol,
                "quantity": str(h.quantity),
                "market_value_usd": str(h.market_value_usd),
                "unrealized_pnl_usd": str(h.unrealized_pnl_usd),
            }
            for h in snapshot.holdings
        ],
        "No holdings.",
    )


def render_risk_controls() -> None:
    st.subheader("Risk & Trading Controls")
    show_module_error("TradingControlsService", TradingControlsErr)

    if TradingControlsService is None:
        return

    service = TradingControlsService()
    status = service.get_status()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Trading", "ON" if status["live_trading_enabled"] else "OFF")
    c2.metric("Paper Trading", "ON" if status["paper_trading_enabled"] else "OFF")
    c3.metric("Private Key", "Present" if status["private_key_configured"] else "Absent")
    c4.metric("Live Guard", "Allowed" if status["live_guard_allowed"] else "Blocked")

    dataframe_or_info(service.checklist(), "No checklist available.")
    st.json(status)


def render_system_health() -> None:
    st.subheader("System Health")
    show_module_error("SystemHealthService", SystemHealthErr)

    if SystemHealthService is None:
        return

    service = SystemHealthService()
    dataframe_or_info(service.get_metric_rows(), "No metrics yet.")

    st.markdown("### Cache")
    st.json(service.get_cache_stats())


def render_diagnostics() -> None:
    st.subheader("Diagnostics")
    st.write("This page helps identify why a dashboard module is blank.")

    rows = [
        {"Module": "PaperAutopilot", "Status": "OK" if PaperAutopilotErr is None else "FAILED", "Error": str(PaperAutopilotErr or "")},
        {"Module": "OpportunityExplorerService", "Status": "OK" if OpportunityExplorerErr is None else "FAILED", "Error": str(OpportunityExplorerErr or "")},
        {"Module": "PaperExecutionService", "Status": "OK" if PaperExecutionErr is None else "FAILED", "Error": str(PaperExecutionErr or "")},
        {"Module": "TradingControlsService", "Status": "OK" if TradingControlsErr is None else "FAILED", "Error": str(TradingControlsErr or "")},
        {"Module": "PortfolioService", "Status": "OK" if PortfolioErr is None else "FAILED", "Error": str(PortfolioErr or "")},
        {"Module": "SystemHealthService", "Status": "OK" if SystemHealthErr is None else "FAILED", "Error": str(SystemHealthErr or "")},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.markdown("### Runtime files")
    runtime_rows = []
    for path in ["data", "reports", "data/paper_orders.jsonl", "reports/paper_report.md", "reports/opportunity_explorer.md"]:
        p = Path(path)
        runtime_rows.append(
            {
                "Path": path,
                "Exists": p.exists(),
                "Type": "dir" if p.is_dir() else "file" if p.exists() else "-",
            }
        )
    st.dataframe(pd.DataFrame(runtime_rows), use_container_width=True)


def render_setup() -> None:
    st.subheader("Setup / Roadmap")
    st.markdown(
        """
        ### Current focus

        1. Explain why opportunities are skipped.
        2. Get paper trades to execute only when net edge is positive.
        3. Collect reports from GitHub Actions.
        4. Improve strategy thresholds and quote quality.
        5. Only later consider VPS and live trading.

        ### Useful commands

        ```bash
        python -m app.opportunities.opportunity_explorer
        python -m app.automation.paper_autopilot --once
        python -m app.reporting.paper_report
        python -m streamlit run streamlit_app.py
        ```
        """
    )


PAGES = {
    "1 Paper Autopilot": render_autopilot,
    "2 Opportunity Explorer": render_opportunity_explorer,
    "3 Reports": render_reports,
    "4 Paper Orders": render_paper_orders,
    "5 Portfolio": render_portfolio,
    "6 Risk & Controls": render_risk_controls,
    "7 System Health": render_system_health,
    "8 Diagnostics": render_diagnostics,
    "9 Setup / Roadmap": render_setup,
}


def safe_render_page(page_name: str) -> None:
    try:
        PAGES[page_name]()
    except Exception as exc:
        st.error(f"Page failed: {page_name}")
        st.code("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)), language="text")


render_header()

with st.sidebar:
    st.header("CryptoAI")
    page = st.radio("Navigate", list(PAGES.keys()), index=0)
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.rerun()

safe_render_page(page)
