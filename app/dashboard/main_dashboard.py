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
    st.caption("Focus: resilient quotes → strategy framework → risk-gated paper execution → analytics.")


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



def render_mission_control() -> None:
    st.subheader("Mission Control")
    paper_report = REPORT_DIR / "paper_report.json"
    research_report = REPORT_DIR / "research_dashboard.json"
    strategy_report = REPORT_DIR / "strategy_center.json"
    mission_summary_report = REPORT_DIR / "mission_summary.json"
    heartbeat_report = DATA_DIR / "heartbeat.json"
    market_intelligence_report = REPORT_DIR / "market_intelligence.json"
    provider_monitor_report = REPORT_DIR / "provider_monitor.json"

    paper = {}
    research = {}
    strategy = {}
    mission_summary = {}
    heartbeat = {}
    market_intelligence = {}
    provider_monitor = {}
    for target, name in [(paper_report, "paper"), (research_report, "research"), (strategy_report, "strategy")]:
        if target.exists():
            try:
                payload = json.loads(target.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                payload = {}
            if name == "paper":
                paper = payload
            elif name == "research":
                research = payload
            else:
                strategy = payload

    for target, name in [(mission_summary_report, "mission"), (heartbeat_report, "heartbeat")]:
        if target.exists():
            try:
                payload = json.loads(target.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                payload = {}
            if name == "mission":
                mission_summary = payload
            else:
                heartbeat = payload

    if market_intelligence_report.exists():
        try:
            market_intelligence = json.loads(market_intelligence_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            market_intelligence = {}

    if provider_monitor_report.exists():
        try:
            provider_monitor = json.loads(provider_monitor_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            provider_monitor = {}

    analytics = paper.get("portfolio_analytics", {})
    feature_store = research.get("feature_store", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equity USD", analytics.get("equity_usd", "-"))
    c2.metric("Total PnL USD", analytics.get("total_pnl_usd", "-"))
    c3.metric("Open Positions", paper.get("portfolio", {}).get("open_positions", "-"))
    c4.metric("Mode", "PAPER")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Feature Vectors", feature_store.get("feature_count", "-"))
    c6.metric("Active Strategies", strategy.get("active_strategy_count", "-"))
    c7.metric("Risk Rejections", paper.get("risk_rejected_orders", "-"))
    c8.metric("Avg Slippage bps", paper.get("avg_slippage_bps", "-"))

    st.markdown("### Operations")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Runtime", mission_summary.get("status", "-"))
    o2.metric("Uptime Seconds", mission_summary.get("uptime_seconds", "-"))
    o3.metric("Cycles", mission_summary.get("cycles_completed", "-"))
    o4.metric("Heartbeat", heartbeat.get("status", "-"))

    if mission_summary:
        st.json(mission_summary)
    else:
        st.info("No mission summary yet. Start paper autopilot with --loop to publish operations state.")

    st.markdown("### Market Intelligence")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Readiness", market_intelligence.get("overall_readiness_score", "-"))
    m2.metric("Chains", market_intelligence.get("chain_count", "-"))
    m3.metric("Pair Candidates", market_intelligence.get("pair_candidate_count", "-"))
    m4.metric("Configured Pairs", market_intelligence.get("configured_pair_count", "-"))

    st.markdown("### Provider Monitor")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Provider Status", provider_monitor.get("overall_status", "-"))
    p2.metric("Providers", provider_monitor.get("provider_count", "-"))
    p3.metric("Alerts", provider_monitor.get("alert_count", "-"))
    p4.metric("Critical", provider_monitor.get("critical_alert_count", "-"))

    st.markdown("### Safety Status")
    st.success("Paper trading only. Live execution remains disabled.")
    if feature_store:
        st.markdown("### Research Data Quality")
        st.json(feature_store.get("data_quality", {}))
    else:
        st.info("Research dashboard not generated yet. Run Research Dashboard from the Research page.")


def render_research_dashboard() -> None:
    st.subheader("Research Dashboard")
    if st.button("Generate Research Dashboard / Feature Store"):
        def task():
            ResearchReportService = import_object("app.research.research_report", "ResearchReportService")
            return ResearchReportService().generate()

        result = safe_run("Building feature store and research dashboard...", task)
        if result is not None:
            st.success("Research dashboard generated.")
            st.json(result)

    feature_json = REPORT_DIR / "feature_store.json"
    research_json = REPORT_DIR / "research_dashboard.json"
    if feature_json.exists():
        try:
            payload = json.loads(feature_json.read_text(encoding="utf-8", errors="replace"))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Feature Vectors", payload.get("feature_count", 0))
            c2.metric("Tradeable/Filled", payload.get("tradeable_or_filled_count", 0))
            c3.metric("Rejected", payload.get("risk_or_execution_rejected_count", 0))
            c4.metric("Avg Edge %", payload.get("avg_net_edge_pct", "-"))
            st.markdown("### Top Pairs")
            dataframe_or_info(payload.get("top_pairs", []), "No pair feature data yet.")
            st.markdown("### Source Counts")
            st.json(payload.get("source_counts", {}))
        except Exception as exc:
            st.error(f"Could not read feature store report: {exc}")
    else:
        st.info("No feature_store.json yet.")

    st.markdown("### Recent Feature Vectors")
    dataframe_or_info(read_jsonl(DATA_DIR / "feature_vectors.jsonl", limit=100), "No feature vectors saved yet.")

    st.markdown("### Research Report")
    txt = read_text(REPORT_DIR / "research_dashboard.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No research_dashboard.md found yet.")


def render_market_intelligence() -> None:
    st.subheader("Market Intelligence")
    if st.button("Generate Market Intelligence"):
        def task():
            Service = import_object("app.market_intelligence.market_intelligence_service", "MarketIntelligenceService")
            return Service().generate()

        result = safe_run("Generating market intelligence...", task)
        if result is not None:
            st.success("Market intelligence generated.")
            st.json(result)

    report_json = REPORT_DIR / "market_intelligence.json"
    if report_json.exists():
        try:
            payload = json.loads(report_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read market intelligence: {exc}")
            payload = {}

        if payload:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Readiness", payload.get("overall_readiness_score", "-"))
            c2.metric("Chains", payload.get("chain_count", "-"))
            c3.metric("Pairs", payload.get("pair_candidate_count", "-"))
            c4.metric("Configured", payload.get("configured_pair_count", "-"))

            st.markdown("### Chain Readiness")
            dataframe_or_info(payload.get("chains", []), "No chain readiness rows yet.")

            st.markdown("### Pair Candidates")
            dataframe_or_info(payload.get("pair_candidates", []), "No pair candidates yet.")

            st.markdown("### Provider Summary")
            st.json(payload.get("provider_summary", {}))
    else:
        st.info("No market_intelligence.json yet. Generate Market Intelligence or run paper autopilot.")

    st.markdown("### Market Intelligence Report")
    txt = read_text(REPORT_DIR / "market_intelligence.md")
    if txt:
        st.markdown(txt)


def render_provider_monitor() -> None:
    st.subheader("Provider Monitor")
    if st.button("Generate Provider Monitor"):
        def task():
            Service = import_object("app.operations.provider_monitor", "ProviderMonitorService")
            return Service().generate()

        result = safe_run("Generating provider monitor...", task)
        if result is not None:
            st.success("Provider monitor generated.")
            st.json(result)

    report_json = REPORT_DIR / "provider_monitor.json"
    if report_json.exists():
        try:
            payload = json.loads(report_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read provider monitor: {exc}")
            payload = {}

        if payload:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", payload.get("overall_status", "-"))
            c2.metric("Providers", payload.get("provider_count", "-"))
            c3.metric("Alerts", payload.get("alert_count", "-"))
            c4.metric("Critical", payload.get("critical_alert_count", "-"))

            st.markdown("### Chain Summary")
            dataframe_or_info(payload.get("chains", []), "No chain provider rows yet.")

            st.markdown("### Providers")
            dataframe_or_info(payload.get("providers", []), "No provider rows yet.")

            st.markdown("### Alerts")
            dataframe_or_info(payload.get("alerts", []), "No provider alerts.")
    else:
        st.info("No provider_monitor.json yet. Generate Provider Monitor or run paper autopilot.")

    st.markdown("### Provider Monitor Report")
    txt = read_text(REPORT_DIR / "provider_monitor.md")
    if txt:
        st.markdown(txt)


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


def render_multi_dex_opportunities() -> None:
    st.subheader("Multi-DEX Opportunities")

    if st.button("Run Multi-DEX Opportunity Scan"):
        def task():
            Engine = import_object("app.opportunities.multi_dex_opportunity_engine", "MultiDexOpportunityEngine")
            return Engine().scan()

        result = safe_run("Running multi-DEX opportunity scan...", task)
        if result is not None:
            st.success(f"Multi-DEX scan completed. Rows: {len(result)}")

    st.markdown("### Recent Multi-DEX Opportunities")
    dataframe_or_info(read_jsonl(DATA_DIR / "multi_dex_opportunities.jsonl", limit=100), "No multi-DEX opportunities saved yet.")

    st.markdown("### Multi-DEX Report")
    txt = read_text(REPORT_DIR / "multi_dex_opportunities.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No multi_dex_opportunities.md found yet.")


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
        ("Multi-DEX Opportunities", REPORT_DIR / "multi_dex_opportunities.md"),
        ("Opportunity Explorer", REPORT_DIR / "opportunity_explorer.md"),
        ("Paper Trading", REPORT_DIR / "paper_report.md"),
        ("Portfolio Analytics", REPORT_DIR / "portfolio_analytics.md"),
        ("Strategy Center", REPORT_DIR / "strategy_center.md"),
        ("Feature Store", REPORT_DIR / "feature_store.md"),
        ("Research Dashboard", REPORT_DIR / "research_dashboard.md"),
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


def render_paper_portfolio() -> None:
    st.subheader("Paper Portfolio")
    state_path = DATA_DIR / "paper_portfolio_state.json"
    if not state_path.exists():
        st.info("No paper portfolio state yet. Run Paper Autopilot once.")
        return

    try:
        state = json.loads(state_path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        st.error(f"Could not read paper portfolio state: {exc}")
        return

    positions = [p for p in state.get("positions", []) if str(p.get("status", "OPEN")).upper() == "OPEN"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cash USD", state.get("cash_usd", "-"))
    c2.metric("Open Positions", len(positions))
    c3.metric("Daily Fills", state.get("daily_filled_trades", 0))
    c4.metric("Daily PnL", state.get("daily_realized_pnl_usd", "0"))

    st.markdown("### Open Positions")
    dataframe_or_info(positions, "No open paper positions.")

    st.markdown("### Risk State")
    safe_state = dict(state)
    safe_state["positions"] = f"{len(state.get('positions', []))} row(s)"
    safe_state["signal_history"] = f"{len(state.get('signal_history', []))} row(s)"
    st.json(safe_state)


def render_portfolio_analytics() -> None:
    st.subheader("Portfolio Analytics & PnL")

    if st.button("Generate Portfolio Analytics"):
        def task():
            PnLAnalyticsService = import_object("app.analytics.pnl_analytics_service", "PnLAnalyticsService")
            return PnLAnalyticsService().generate()

        result = safe_run("Generating portfolio analytics...", task)
        if result is not None:
            st.success("Portfolio analytics generated.")
            st.json(result)

    analytics_path = REPORT_DIR / "portfolio_analytics.json"
    if analytics_path.exists():
        try:
            analytics = json.loads(analytics_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read portfolio analytics: {exc}")
            analytics = {}

        if analytics:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Equity USD", analytics.get("equity_usd", "-"))
            c2.metric("Total PnL USD", analytics.get("total_pnl_usd", "-"))
            c3.metric("Return %", analytics.get("total_return_pct", "-"))
            c4.metric("Win Rate %", analytics.get("win_rate_pct", "-"))

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Profit Factor", analytics.get("profit_factor", "-"))
            c6.metric("Max Drawdown %", analytics.get("max_drawdown_pct", "-"))
            c7.metric("Avg Slip bps", analytics.get("avg_slippage_bps", "-"))
            c8.metric("Avg Latency ms", analytics.get("avg_latency_ms", "-"))

            st.markdown("### Daily PnL")
            dataframe_or_info(analytics.get("daily_pnl", []), "No daily PnL rows yet.")

            st.markdown("### Equity Curve")
            equity_curve = analytics.get("equity_curve", [])
            dataframe_or_info(equity_curve, "No equity curve rows yet.")
            if equity_curve:
                try:
                    chart_df = pd.DataFrame(equity_curve)
                    chart_df["equity_usd"] = pd.to_numeric(chart_df["equity_usd"], errors="coerce")
                    st.line_chart(chart_df.set_index("date")[["equity_usd"]])
                except Exception:
                    pass

            st.markdown("### Performance by Pair")
            dataframe_or_info(analytics.get("performance_by_pair", []), "No pair-level performance yet.")

            st.markdown("### Trade Journal")
            dataframe_or_info(analytics.get("trade_journal", []), "No trade journal rows yet.")
    else:
        st.info("No portfolio_analytics.json found yet. Generate analytics or paper report first.")

    st.markdown("### Portfolio Analytics Report")
    txt = read_text(REPORT_DIR / "portfolio_analytics.md")
    if txt:
        st.markdown(txt)



def render_strategy_center() -> None:
    st.subheader("Strategy Center")

    if st.button("Generate Strategy Center"):
        def task():
            StrategyCenterService = import_object("app.strategy.strategy_center", "StrategyCenterService")
            return StrategyCenterService().generate()

        result = safe_run("Generating strategy center...", task)
        if result is not None:
            st.success("Strategy Center generated.")
            st.json(result)

    strategy_json = REPORT_DIR / "strategy_center.json"
    if strategy_json.exists():
        try:
            payload = json.loads(strategy_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read strategy center JSON: {exc}")
            payload = {}

        if payload:
            c1, c2, c3 = st.columns(3)
            c1.metric("Strategies", payload.get("strategy_count", 0))
            c2.metric("Active", payload.get("active_strategy_count", 0))
            c3.metric("Disabled", payload.get("disabled_strategy_count", 0))

            st.markdown("### Strategy Registry & Performance")
            dataframe_or_info(payload.get("strategies", []), "No strategy rows yet.")

            st.markdown("### Ranked Signals")
            dataframe_or_info(payload.get("ranked_signals", []), "No ranked strategy signals yet.")
    else:
        st.info("No strategy_center.json found yet. Generate Strategy Center or run paper autopilot.")

    st.markdown("### Strategy Center Report")
    txt = read_text(REPORT_DIR / "strategy_center.md")
    if txt:
        st.markdown(txt)


def render_risk_controls() -> None:
    st.subheader("Risk & Trading Controls")
    flags = {
        "CRYPTOAI_LIVE_TRADING_ENABLED": os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false"),
        "CRYPTOAI_PAPER_TRADING_ENABLED": os.getenv("CRYPTOAI_PAPER_TRADING_ENABLED", "true"),
        "CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION": os.getenv("CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION", "true"),
        "CRYPTOAI_MAX_LIVE_TRADE_USD": os.getenv("CRYPTOAI_MAX_LIVE_TRADE_USD", "0"),
        "CRYPTOAI_MAX_DAILY_LOSS_USD": os.getenv("CRYPTOAI_MAX_DAILY_LOSS_USD", "0"),
        "CRYPTOAI_PRIVATE_KEY": "PRESENT" if os.getenv("CRYPTOAI_PRIVATE_KEY") else "ABSENT",
        "CRYPTOAI_PAPER_INITIAL_CASH_USD": os.getenv("CRYPTOAI_PAPER_INITIAL_CASH_USD", "10000"),
        "CRYPTOAI_PAPER_RISK_PER_TRADE_PCT": os.getenv("CRYPTOAI_PAPER_RISK_PER_TRADE_PCT", "1.00"),
        "CRYPTOAI_MAX_DAILY_PAPER_TRADES": os.getenv("CRYPTOAI_MAX_DAILY_PAPER_TRADES", "8"),
        "CRYPTOAI_TRADE_COOLDOWN_SECONDS": os.getenv("CRYPTOAI_TRADE_COOLDOWN_SECONDS", "900"),
        "CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS": os.getenv("CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS", "900"),
        "CRYPTOAI_MAX_OPEN_POSITIONS": os.getenv("CRYPTOAI_MAX_OPEN_POSITIONS", "8"),
    }
    st.json(flags)

    if flags["CRYPTOAI_LIVE_TRADING_ENABLED"].lower() in {"1", "true", "yes", "on"}:
        st.error("Live trading flag is ON. Turn it OFF during paper testing.")
    else:
        st.success("Live trading is disabled.")


def render_system_health() -> None:
    st.subheader("System Health")

    st.markdown("### Runtime Files")
    rows = []
    for path in [
        DATA_DIR,
        REPORT_DIR,
        DATA_DIR / "provider_health.json",
        DATA_DIR / "heartbeat.json",
        DATA_DIR / "heartbeat_history.jsonl",
        DATA_DIR / "runtime_state.json",
        DATA_DIR / "quote_snapshot.json",
        DATA_DIR / "quote_diagnostics.jsonl",
        DATA_DIR / "multi_dex_opportunities.jsonl",
        DATA_DIR / "opportunity_decisions.jsonl",
        DATA_DIR / "paper_orders.jsonl",
        DATA_DIR / "paper_portfolio_state.json",
        REPORT_DIR / "quote_diagnostics.md",
        REPORT_DIR / "multi_dex_opportunities.md",
        REPORT_DIR / "opportunity_explorer.md",
        REPORT_DIR / "paper_report.md",
        REPORT_DIR / "portfolio_analytics.json",
        REPORT_DIR / "portfolio_analytics.md",
        DATA_DIR / "strategy_signals.jsonl",
        DATA_DIR / "strategy_ranked_signals.jsonl",
        REPORT_DIR / "strategy_center.json",
        REPORT_DIR / "strategy_center.md",
        DATA_DIR / "feature_vectors.jsonl",
        DATA_DIR / "feature_vectors.csv",
        REPORT_DIR / "feature_store.json",
        REPORT_DIR / "feature_store.md",
        REPORT_DIR / "research_dashboard.json",
        REPORT_DIR / "research_dashboard.md",
        REPORT_DIR / "mission_summary.json",
        REPORT_DIR / "mission_summary.md",
        REPORT_DIR / "operational_metrics.json",
        REPORT_DIR / "market_intelligence.json",
        REPORT_DIR / "market_intelligence.md",
        REPORT_DIR / "provider_monitor.json",
        REPORT_DIR / "provider_monitor.md",
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

    st.markdown("### Provider Health")
    provider_health_path = DATA_DIR / "provider_health.json"
    if provider_health_path.exists():
        try:
            payload = json.loads(provider_health_path.read_text(encoding="utf-8", errors="replace"))
            providers = payload.get("providers", [])
            if providers:
                st.dataframe(pd.DataFrame(providers), use_container_width=True)
            else:
                st.info("Provider health file exists but has no provider rows yet.")
        except Exception as exc:
            st.error(f"Could not read provider health: {exc}")
    else:
        st.info("No provider_health.json yet. Run quote diagnostics or paper autopilot once.")

    st.markdown("### Quote Snapshot")
    snapshot_path = DATA_DIR / "quote_snapshot.json"
    if snapshot_path.exists():
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8", errors="replace"))
            saved_at = payload.get("saved_at")
            st.json({"saved_at_epoch": saved_at, "quote_count": len(payload.get("quotes", []))})
        except Exception as exc:
            st.error(f"Could not read quote snapshot: {exc}")
    else:
        st.info("No quote snapshot yet.")


def render_setup() -> None:
    st.subheader("Setup / Roadmap")
    st.markdown(
        """
        ### Current debugging order

        1. Quote Diagnostics — quote provider health.
        2. Multi-DEX Opportunities — real or simulated paper comparison.
        3. Opportunity Explorer — BUY/WATCH/SKIP decision.
        4. Paper Autopilot — simulated execution.
        5. Reports — review results.

        ### Commands

        ```bash
        python -m app.diagnostics.quote_diagnostics
        python -m app.opportunities.multi_dex_opportunity_engine
        python -m app.opportunities.opportunity_explorer
        python -m app.automation.paper_autopilot --once
        python -m app.reporting.paper_report
        python -m app.research.research_report
        python -m app.market_intelligence.market_intelligence_service
        python -m app.operations.provider_monitor
        ```
        """
    )


PAGES = {
    "1 Mission Control": render_mission_control,
    "2 Paper Autopilot": render_paper_autopilot,
    "3 Quote Diagnostics": render_quote_diagnostics,
    "4 Multi-DEX Opportunities": render_multi_dex_opportunities,
    "5 Opportunity Explorer": render_opportunity_explorer,
    "6 Reports": render_reports,
    "7 Paper Orders": render_paper_orders,
    "8 Paper Portfolio": render_paper_portfolio,
    "9 Portfolio Analytics": render_portfolio_analytics,
    "10 Strategy Center": render_strategy_center,
    "11 Market Intelligence": render_market_intelligence,
    "12 Provider Monitor": render_provider_monitor,
    "13 Research Dashboard": render_research_dashboard,
    "14 Risk & Controls": render_risk_controls,
    "15 System Health": render_system_health,
    "16 Setup / Roadmap": render_setup,
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
