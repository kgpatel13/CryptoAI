from __future__ import annotations

import pandas as pd
import streamlit as st

try:
    from app.automation.paper_autopilot import PaperAutopilot
except Exception:
    PaperAutopilot = None

try:
    from app.opportunities.opportunity_explorer import OpportunityExplorerService
except Exception:
    OpportunityExplorerService = None

try:
    from app.execution.paper_execution_service import PaperExecutionService
    from app.execution.trading_controls_service import TradingControlsService
except Exception:
    PaperExecutionService = None
    TradingControlsService = None

try:
    from app.portfolio.portfolio_service import PortfolioService
except Exception:
    PortfolioService = None

try:
    from app.services.system_health_service import SystemHealthService
except Exception:
    SystemHealthService = None


st.set_page_config(page_title="CryptoAI", page_icon="📊", layout="wide")


def dataframe_or_info(rows, message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(message)


def render_header() -> None:
    st.title("📊 CryptoAI Paper Trading Control Center")
    st.caption("Focused dashboard: paper autopilot, opportunity decisions, reports, risk, and health.")


def render_autopilot() -> None:
    st.subheader("Paper Autopilot")

    if PaperAutopilot is None:
        st.error("PaperAutopilot module not available.")
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

    if OpportunityExplorerService is None:
        st.error("OpportunityExplorerService module not available.")
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

    report_path = "reports/paper_report.md"
    opp_path = "reports/opportunity_explorer.md"

    st.markdown("### Paper Report")
    try:
        with open(report_path, "r", encoding="utf-8") as fh:
            st.markdown(fh.read())
    except FileNotFoundError:
        st.info("No paper report yet. Run paper autopilot then generate report.")

    st.markdown("### Opportunity Explorer Report")
    try:
        with open(opp_path, "r", encoding="utf-8") as fh:
            st.markdown(fh.read())
    except FileNotFoundError:
        st.info("No opportunity report yet. Run opportunity scan.")


def render_paper_orders() -> None:
    st.subheader("Paper Orders")

    if PaperExecutionService is None:
        st.info("PaperExecutionService not available.")
        return

    service = PaperExecutionService()
    dataframe_or_info(service.recent_orders(), "No paper orders saved yet.")


def render_portfolio() -> None:
    st.subheader("Portfolio")

    if PortfolioService is None:
        st.info("PortfolioService not available.")
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

    if TradingControlsService is None:
        st.info("TradingControlsService not available.")
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

    if SystemHealthService is None:
        st.info("SystemHealthService not available.")
        return

    service = SystemHealthService()
    dataframe_or_info(service.get_metric_rows(), "No metrics yet.")

    st.markdown("### Cache")
    st.json(service.get_cache_stats())


def render_setup() -> None:
    st.subheader("Setup / Roadmap")

    st.markdown(
        """
        ### Current focus
        We are no longer adding broad infrastructure. The focus is now:

        1. Explain why opportunities are skipped.
        2. Get paper trades to execute only when net edge is positive.
        3. Collect reports from GitHub Actions.
        4. Improve strategy thresholds and quote quality.
        5. Only later consider VPS and live trading.

        ### Useful local commands

        ```bash
        python -m app.opportunities.opportunity_explorer
        python -m app.automation.paper_autopilot --once
        python -m app.reporting.paper_report
        python -m streamlit run streamlit_app.py
        ```

        ### GitHub Actions
        Scheduled run every 15 minutes is enough for validation, but not enough for fast arbitrage.
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
    "8 Setup / Roadmap": render_setup,
}

render_header()

with st.sidebar:
    st.header("CryptoAI")
    page = st.radio("Navigate", list(PAGES.keys()), index=0)
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.rerun()

PAGES[page]()
