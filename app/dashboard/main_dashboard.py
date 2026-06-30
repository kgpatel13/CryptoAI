from __future__ import annotations

import importlib
import json
import os
import traceback
from decimal import Decimal, InvalidOperation
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


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def decimal_or_none(value) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def format_decimal(value: Decimal | None, places: str = "0.0000") -> str:
    if value is None:
        return "-"
    return str(value.quantize(Decimal(places)))


def dataframe_or_info(rows: list[dict], message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch")
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
    strategy_intelligence_report = REPORT_DIR / "strategy_intelligence.json"
    mission_summary_report = REPORT_DIR / "mission_summary.json"
    heartbeat_report = DATA_DIR / "heartbeat.json"
    market_intelligence_report = REPORT_DIR / "market_intelligence.json"
    provider_monitor_report = REPORT_DIR / "provider_monitor.json"
    eth_market_coverage_report = REPORT_DIR / "eth_market_coverage.json"
    pool_depth_report = REPORT_DIR / "pool_depth_ladder.json"
    execution_realism_report = REPORT_DIR / "execution_realism.json"
    paper_run_review_report = REPORT_DIR / "paper_run_review.json"

    paper = {}
    research = {}
    strategy = {}
    strategy_intelligence = {}
    mission_summary = {}
    heartbeat = {}
    market_intelligence = {}
    provider_monitor = {}
    eth_market_coverage = {}
    pool_depth = {}
    execution_realism = {}
    paper_run_review = {}
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

    if eth_market_coverage_report.exists():
        try:
            eth_market_coverage = json.loads(eth_market_coverage_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            eth_market_coverage = {}

    if pool_depth_report.exists():
        try:
            pool_depth = json.loads(pool_depth_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pool_depth = {}

    if execution_realism_report.exists():
        try:
            execution_realism = json.loads(execution_realism_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            execution_realism = {}

    if paper_run_review_report.exists():
        try:
            paper_run_review = json.loads(paper_run_review_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            paper_run_review = {}

    if strategy_intelligence_report.exists():
        try:
            strategy_intelligence = json.loads(strategy_intelligence_report.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            strategy_intelligence = {}

    analytics = paper.get("portfolio_analytics", {})
    portfolio_state = read_json(DATA_DIR / "paper_portfolio_state.json")
    if portfolio_state:
        cash = decimal_or_none(portfolio_state.get("cash_usd"))
        initial_cash = decimal_or_none(portfolio_state.get("initial_cash_usd"))
        realized = decimal_or_none(portfolio_state.get("realized_pnl_usd")) or Decimal("0")
        unrealized = decimal_or_none(portfolio_state.get("unrealized_pnl_usd")) or Decimal("0")
        total_pnl = realized + unrealized
        equity = cash + unrealized if cash is not None else None
        analytics = {
            **analytics,
            "cash_usd": format_decimal(cash),
            "equity_usd": format_decimal(equity),
            "realized_pnl_usd": format_decimal(realized),
            "unrealized_pnl_usd": format_decimal(unrealized),
            "total_pnl_usd": format_decimal(total_pnl),
        }
        paper = {
            **paper,
            "portfolio": {
                **(paper.get("portfolio", {}) if isinstance(paper.get("portfolio"), dict) else {}),
                "cash_usd": portfolio_state.get("cash_usd", "-"),
                "initial_cash_usd": portfolio_state.get("initial_cash_usd", "-"),
                "open_positions": len(portfolio_state.get("positions", []) if isinstance(portfolio_state.get("positions"), list) else []),
                "daily_filled_trades": portfolio_state.get("daily_filled_trades", 0),
                "daily_realized_pnl_usd": portfolio_state.get("daily_realized_pnl_usd", "0"),
                "realized_pnl_usd": portfolio_state.get("realized_pnl_usd", "0"),
                "updated_at": portfolio_state.get("updated_at", "-"),
            },
            "portfolio_analytics": analytics,
        }
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

    st.markdown("### Paper Run Review")
    pr1, pr2, pr3, pr4 = st.columns(4)
    pr1.metric("Run Status", paper_run_review.get("overall_status", "-"))
    pr2.metric("Shadow Decision", paper_run_review.get("shadow_decision", "-"))
    pr3.metric("Closed Trades", paper_run_review.get("closed_trade_count", "-"))
    pr4.metric("Losing Trades", paper_run_review.get("losing_trade_count", "-"))
    pr5, pr6, pr7, pr8 = st.columns(4)
    pr5.metric("Run PnL USD", paper_run_review.get("realized_pnl_usd", "-"))
    pr6.metric("Run Return %", paper_run_review.get("return_pct", "-"))
    pr7.metric("Depth Ready", paper_run_review.get("pool_depth_ready_route_count", "-"))
    pr8.metric("Live Decision", paper_run_review.get("live_decision", "-"))
    if paper_run_review:
        st.caption(str(paper_run_review.get("recommendation", "-")))
        blocked = [gate for gate in paper_run_review.get("gates", []) if gate.get("status") != "PASS"]
        dataframe_or_info(blocked[:10], "No blocked review gates.")
    else:
        st.info("No paper_run_review.json yet. Paper autopilot will create it on the next cycle.")

    st.markdown("### Last Cycle Decision")
    latest_opportunities = read_jsonl(DATA_DIR / "opportunity_decisions.jsonl", limit=100)
    if not latest_opportunities:
        latest_opportunities = paper.get("latest_opportunities", []) if isinstance(paper.get("latest_opportunities"), list) else []
    latest_orders = read_jsonl(DATA_DIR / "paper_orders.jsonl", limit=100)
    if not latest_orders:
        latest_orders = paper.get("latest_orders", []) if isinstance(paper.get("latest_orders"), list) else []
    latest_opportunity_batch = latest_opportunities
    if latest_opportunities:
        latest_timestamp = latest_opportunities[-1].get("timestamp")
        latest_opportunity_batch = [row for row in latest_opportunities if row.get("timestamp") == latest_timestamp] or latest_opportunities
    best_opp = max(
        latest_opportunity_batch,
        key=lambda row: decimal_or_none(row.get("estimated_net_edge_pct") or row.get("net_edge_pct")) or Decimal("-999999"),
    ) if latest_opportunity_batch else {}
    latest_order = latest_orders[-1] if latest_orders else {}
    quote_snapshot = read_json(DATA_DIR / "quote_snapshot.json")
    quote_rows = quote_snapshot.get("quotes", []) if isinstance(quote_snapshot.get("quotes"), list) else []
    healthy_quotes = len([row for row in quote_rows if not row.get("error")])
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Last Scan", best_opp.get("timestamp", latest_order.get("timestamp", "-")))
    d2.metric("Healthy Quotes", healthy_quotes if quote_rows else "-")
    d3.metric("Best Net Edge %", best_opp.get("estimated_net_edge_pct", "-"))
    d4.metric("Threshold %", "0.30")
    d5, d6, d7, d8 = st.columns(4)
    d5.metric("Decision", best_opp.get("decision", latest_order.get("status", "-")))
    d6.metric("Order Created", "YES" if latest_order.get("status") == "CLOSED" else "NO")
    d7.metric("Order Status", latest_order.get("status", "-"))
    d8.metric("Realized PnL", latest_order.get("realized_pnl_usd", "-"))
    if best_opp:
        st.caption(str(best_opp.get("reason", "-")))
    if latest_order:
        st.caption(str(latest_order.get("reason", "-")))

    st.markdown("### Pool Depth Ladder")
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Depth Status", pool_depth.get("overall_status", "-"))
    l2.metric("Depth Confidence", pool_depth.get("confidence", "-"))
    l3.metric("Depth Ready Routes", pool_depth.get("depth_ready_route_count", "-"))
    l4.metric("Requested Size", pool_depth.get("requested_notional_usd", "-"))
    depth_routes = pool_depth.get("routes", []) if isinstance(pool_depth.get("routes"), list) else []
    if depth_routes:
        best_depth = depth_routes[0]
        st.caption(
            f"{best_depth.get('pair', '-')}: max usable ${best_depth.get('max_usable_notional_usd', '-')}, "
            f"worst impact {best_depth.get('worst_price_impact_pct', '-')}%, "
            f"status {best_depth.get('status', '-')}"
        )
    else:
        st.caption("No pool-depth ladder report yet.")

    st.markdown("### Execution Realism")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Realism Status", execution_realism.get("overall_status", "-"))
    r2.metric("Confidence", execution_realism.get("confidence", "-"))
    r3.metric("Shadow Ready", execution_realism.get("shadow_ready_count", "-"))
    r4.metric("Live Ready", execution_realism.get("live_ready_count", "-"))
    realism_rows = execution_realism.get("opportunities", []) if isinstance(execution_realism.get("opportunities"), list) else []
    if realism_rows:
        best_realism = realism_rows[0]
        st.caption(
            f"Stress net edge: {best_realism.get('stress_net_edge_pct', '-')}%, "
            f"executable size: ${best_realism.get('max_executable_notional_usd', '-')}, "
            f"status: {best_realism.get('realism_status', '-')}"
        )
    else:
        st.caption("No execution realism report yet.")

    st.markdown("### Market Intelligence")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Readiness", market_intelligence.get("overall_readiness_score", "-"))
    m2.metric("Chains", market_intelligence.get("chain_count", "-"))
    m3.metric("Pair Candidates", market_intelligence.get("pair_candidate_count", "-"))
    m4.metric("Configured Pairs", market_intelligence.get("configured_pair_count", "-"))

    st.markdown("### ETH Golden Path Coverage")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Coverage Score", eth_market_coverage.get("overall_coverage_score", "-"))
    e2.metric("Coverage Status", eth_market_coverage.get("overall_status", "-"))
    e3.metric("Target Chains", eth_market_coverage.get("target_chain_count", "-"))
    e4.metric("Quote Routes", eth_market_coverage.get("quote_ready_route_count", "-"))

    st.markdown("### Provider Monitor")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Provider Status", provider_monitor.get("overall_status", "-"))
    p2.metric("Providers", provider_monitor.get("provider_count", "-"))
    p3.metric("Alerts", provider_monitor.get("alert_count", "-"))
    p4.metric("Critical", provider_monitor.get("critical_alert_count", "-"))

    st.markdown("### Strategy Intelligence")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Top Recommendation", strategy_intelligence.get("top_recommendation", "-"))
    s2.metric("Strategies Scored", strategy_intelligence.get("strategy_count", "-"))
    s3.metric("Promotion", "NO" if strategy_intelligence else "-")
    s4.metric("Mode", strategy_intelligence.get("mode", "-"))

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

    if st.button("Generate Universe Evidence"):
        def task():
            Service = import_object("app.research.market_universe_evidence_service", "MarketUniverseEvidenceService")
            return Service().generate()

        result = safe_run("Generating market universe evidence...", task)
        if result is not None:
            st.success("Market universe evidence generated.")
            st.json(result)

    if st.button("Generate Quote Coverage"):
        def task():
            Service = import_object("app.research.quote_coverage_evidence_service", "QuoteCoverageEvidenceService")
            return Service().generate()

        result = safe_run("Generating quote coverage evidence...", task)
        if result is not None:
            st.success("Quote coverage evidence generated.")
            st.json(result)

    if st.button("Generate ETH Route Architecture"):
        def task():
            Service = import_object("app.research.eth_route_architecture_service", "EthRouteArchitectureService")
            return Service().generate()

        result = safe_run("Generating ETH route architecture evidence...", task)
        if result is not None:
            st.success("ETH route architecture evidence generated.")
            st.json(result)

    if st.button("Generate ETH Market Coverage"):
        def task():
            Service = import_object("app.research.eth_market_coverage_service", "EthMarketCoverageService")
            return Service().generate()

        result = safe_run("Generating ETH market coverage evidence...", task)
        if result is not None:
            st.success("ETH market coverage evidence generated.")
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

    universe_json = REPORT_DIR / "market_universe_evidence.json"
    if universe_json.exists():
        try:
            payload = json.loads(universe_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read market universe evidence: {exc}")
            payload = {}

        if payload:
            st.markdown("### Market Universe Evidence")
            c1, c2, c3, c4 = st.columns(4)
            focus = payload.get("primary_focus") or {}
            c1.metric("Primary Focus", f"{focus.get('chain', '-')}\n{focus.get('pair', '-')}")
            c2.metric("Active", payload.get("active_focus_count", "-"))
            c3.metric("Research", payload.get("research_target_count", "-"))
            c4.metric("Blocked", payload.get("blocked_count", "-"))
            dataframe_or_info(payload.get("universe", []), "No universe rows yet.")
            dataframe_or_info(payload.get("findings", []), "No universe findings.")
    else:
        st.info("No market_universe_evidence.json yet. Generate Universe Evidence.")

    coverage_json = REPORT_DIR / "quote_coverage_evidence.json"
    if coverage_json.exists():
        try:
            payload = json.loads(coverage_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read quote coverage evidence: {exc}")
            payload = {}

        if payload:
            st.markdown("### Quote Coverage Evidence")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Active Pairs", payload.get("active_pair_count", "-"))
            c2.metric("Quote Gaps", payload.get("quote_gap_count", "-"))
            c3.metric("Provider Gaps", payload.get("provider_gap_count", "-"))
            c4.metric("Providers", payload.get("implemented_provider_count", "-"))
            dataframe_or_info(payload.get("pair_coverage", []), "No quote coverage rows yet.")
            dataframe_or_info(payload.get("next_provider_targets", []), "No quote coverage targets.")
    else:
        st.info("No quote_coverage_evidence.json yet. Generate Quote Coverage.")

    route_json = REPORT_DIR / "eth_route_architecture.json"
    if route_json.exists():
        try:
            payload = json.loads(route_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read ETH route architecture: {exc}")
            payload = {}

        if payload:
            st.markdown("### ETH Route Architecture")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Decision", payload.get("route_architecture_decision", "-"))
            r2.metric("Production Buffer", payload.get("production_buffer_pct", "-"))
            r3.metric("Candidate Buffer", payload.get("candidate_buffer_pct", "-"))
            promotion = payload.get("buffer_promotion", {})
            r4.metric("Promotion Gates", f"{promotion.get('passed_gate_count', '-')}/{promotion.get('gate_count', '-')}")
            dataframe_or_info(payload.get("route_evidence", []), "No ETH route evidence rows yet.")
            dataframe_or_info(payload.get("trusted_venues", []), "No trusted venue rows yet.")
    else:
        st.info("No eth_route_architecture.json yet. Generate ETH Route Architecture.")

    coverage_json = REPORT_DIR / "eth_market_coverage.json"
    if coverage_json.exists():
        try:
            payload = json.loads(coverage_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read ETH market coverage: {exc}")
            payload = {}

        if payload:
            st.markdown("### ETH Golden Path Coverage")
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Score", payload.get("overall_coverage_score", "-"))
            g2.metric("Status", payload.get("overall_status", "-"))
            g3.metric("Configured Chains", f"{payload.get('configured_target_chain_count', '-')}/{payload.get('target_chain_count', '-')}")
            g4.metric("Quote Routes", payload.get("quote_ready_route_count", "-"))
            dataframe_or_info(payload.get("chains", []), "No ETH coverage chain rows yet.")
            dataframe_or_info(payload.get("next_actions", []), "No ETH coverage actions yet.")
    else:
        st.info("No eth_market_coverage.json yet. Generate ETH Market Coverage.")


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

    st.markdown("### 24/7 Launch Command")
    st.code("python -m app.automation.paper_autopilot --loop --use-settings", language="bash")


def render_paper_settings() -> None:
    st.subheader("Paper Settings")
    PaperSettingsService = import_object("app.operations.paper_settings_service", "PaperSettingsService")
    service = PaperSettingsService()
    settings = service.load()
    validation = service.validate(settings)
    latest_report_validation = read_json(REPORT_DIR / "paper_trading_settings.json")
    if latest_report_validation.get("settings") == settings:
        validation = latest_report_validation

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", validation.get("status", "-"))
    c2.metric("Paper Capital USD", validation.get("paper_capital_usd", "-"))
    c3.metric("Errors", validation.get("error_count", "-"))
    c4.metric("Warnings", validation.get("warning_count", "-"))

    if validation.get("status") == "VALID":
        st.success("Settings are valid for paper-mode launch.")
    else:
        st.error("Settings must be fixed before continuous paper launch.")
    dataframe_or_info(validation.get("findings", []), "No settings findings.")

    with st.form("paper_settings_form"):
        profile_options = ["standard", "aggressive_paper", "unbounded_paper_lab", "shadow_500", "live_parity_500"]
        selected_profile = str(settings.get("paper_profile", "standard"))
        profile = st.selectbox(
            "Paper profile",
            profile_options,
            index=profile_options.index(selected_profile) if selected_profile in profile_options else 0,
        )

        st.markdown("### Operations")
        o1, o2, o3 = st.columns(3)
        loop_interval = o1.number_input(
            "Loop interval seconds",
            min_value=0,
            max_value=3600,
            value=int(settings["operations"]["loop_interval_seconds"]),
            step=15,
        )
        heartbeat_interval = o2.number_input(
            "Heartbeat seconds",
            min_value=10,
            max_value=300,
            value=int(settings["operations"]["heartbeat_interval_seconds"]),
            step=10,
        )
        max_cycles_enabled = o3.checkbox("Limit cycles", value=settings["operations"].get("max_cycles") is not None)
        max_cycles = o3.number_input(
            "Max cycles",
            min_value=1,
            max_value=100000,
            value=int(settings["operations"].get("max_cycles") or 1),
            step=1,
            disabled=not max_cycles_enabled,
        )

        st.markdown("### Market Scope")
        m1, m2, m3 = st.columns(3)
        chains = m1.multiselect("Chains", ["base"], default=settings["market_scope"]["chains"])
        routes = m2.multiselect("Routes", ["WETH/USDC", "USDC/WETH"], default=settings["market_scope"]["routes"])
        dexes = m3.multiselect("DEXs", ["Uniswap V2", "Aerodrome", "Uniswap V3"], default=settings["market_scope"]["dexes"])

        st.markdown("### Paper Capital")
        p1, p2, p3, p4, p5 = st.columns(5)
        initial_eth = p1.number_input("Initial ETH", min_value=0.01, max_value=100000.0, value=float(settings["paper_capital"]["initial_capital_eth"]), step=0.01)
        eth_reference = p2.number_input("ETH reference USD", min_value=1.0, max_value=1000000.0, value=float(settings["paper_capital"]["eth_reference_usd"]), step=50.0)
        max_notional = p3.number_input("Max trade USD", min_value=1.0, max_value=1000000000.0, value=float(settings["paper_capital"]["max_notional_usd_per_trade"]), step=10.0)
        max_daily_trades = p4.number_input("Max daily trades", min_value=0, max_value=100000, value=int(settings["paper_capital"]["max_daily_paper_trades"]), step=1)
        sizing_mode = p5.selectbox(
            "Sizing mode",
            ["edge_scaled", "full_available_cash"],
            index=1 if settings["paper_capital"].get("sizing_mode") == "full_available_cash" else 0,
        )

        st.markdown("### Evidence And Risk")
        e1, e2, e3, e4 = st.columns(4)
        min_quote_ok = e1.number_input("Min quote OK %", min_value=0.0, max_value=100.0, value=float(settings["opportunity"]["min_quote_ok_rate_pct"]), step=1.0)
        min_coverage = e2.number_input("Min ETH coverage", min_value=0, max_value=100, value=int(settings["evidence_gates"]["min_eth_coverage_score"]), step=1)
        max_open_positions = e3.number_input("Max open positions", min_value=0, max_value=100000, value=int(settings["risk"]["max_open_positions"]), step=1)
        daily_loss = e4.number_input("Max daily loss USD", min_value=0.0, max_value=1000000000.0, value=float(settings["risk"]["max_daily_loss_usd"]), step=5.0)

        r1, r2, r3, r4 = st.columns(4)
        cooldown = r1.number_input("Cooldown seconds", min_value=0, max_value=86400, value=int(settings["risk"]["cooldown_seconds"]), step=15)
        require_clean_audit = r2.checkbox("Require clean report audit", value=bool(settings["evidence_gates"]["require_report_audit_clean"]))
        require_provider = r3.checkbox("Block critical provider status", value=bool(settings["evidence_gates"]["require_provider_not_critical"]))
        duplicate_position_block = r4.checkbox("Block duplicate position", value=bool(settings["risk"]["duplicate_position_block"]))

        st.markdown("### Locked Thresholds")
        t1, t2, t3 = st.columns(3)
        t1.text_input("Production buffer %", value=settings["opportunity"]["production_cost_buffer_pct"], disabled=True)
        t2.text_input("Research candidate %", value=settings["opportunity"]["research_candidate_buffer_pct"], disabled=True)
        t3.text_input("Paper BUY threshold %", value=settings["opportunity"]["paper_buy_threshold_pct"], disabled=True)

        submitted = st.form_submit_button("Save Paper Settings")

    if submitted:
        updated = settings.copy()
        updated["paper_profile"] = str(profile)
        updated["operations"] = {
            "loop_interval_seconds": int(loop_interval),
            "heartbeat_interval_seconds": int(heartbeat_interval),
            "max_cycles": int(max_cycles) if max_cycles_enabled else None,
        }
        updated["market_scope"] = {
            **settings["market_scope"],
            "chains": chains,
            "routes": routes,
            "dexes": dexes,
            "allow_stale_quotes_for_live": False,
        }
        updated["paper_capital"] = {
            "initial_capital_eth": f"{initial_eth:.2f}",
            "eth_reference_usd": f"{eth_reference:.2f}",
            "max_notional_usd_per_trade": f"{max_notional:.2f}",
            "max_daily_paper_trades": int(max_daily_trades),
            "sizing_mode": str(sizing_mode),
        }
        updated["opportunity"] = {
            **settings["opportunity"],
            "min_quote_ok_rate_pct": f"{min_quote_ok:.2f}",
        }
        updated["risk"] = {
            **settings["risk"],
            "max_open_positions": int(max_open_positions),
            "cooldown_seconds": int(cooldown),
            "max_daily_loss_usd": f"{daily_loss:.2f}",
            "duplicate_position_block": bool(duplicate_position_block),
            "kill_switch_enabled": True,
        }
        updated["evidence_gates"] = {
            **settings["evidence_gates"],
            "require_report_audit_clean": bool(require_clean_audit),
            "require_provider_not_critical": bool(require_provider),
            "min_eth_coverage_score": int(min_coverage),
        }
        try:
            service.save(updated)
            service.generate_report(updated)
            st.success("Paper settings saved.")
            st.rerun()
        except Exception as exc:
            show_exception(exc)

    if st.button("Reset To Safe Defaults"):
        try:
            service.reset()
            service.generate_report()
            st.success("Paper settings reset.")
            st.rerun()
        except Exception as exc:
            show_exception(exc)

    if st.button("Apply Live Parity 500 Profile"):
        try:
            profile_settings = service.save_live_parity_500_profile()
            service.generate_report(profile_settings)
            st.success("Live parity paper profile saved.")
            st.rerun()
        except Exception as exc:
            show_exception(exc)

    st.markdown("### Launch Command")
    st.code(validation.get("launch_command", "python -m app.automation.paper_autopilot --loop --use-settings"), language="bash")

    txt = read_text(REPORT_DIR / "paper_trading_settings.md")
    if txt:
        st.markdown("### Settings Report")
        st.markdown(txt)


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
        ("Paper Run Review", REPORT_DIR / "paper_run_review.md"),
        ("Live Safety", REPORT_DIR / "live_safety.md"),
        ("Wallet Preflight", REPORT_DIR / "wallet_preflight.md"),
        ("Live Readiness Checklist", REPORT_DIR / "live_readiness_checklist.md"),
        ("Transaction Simulation", REPORT_DIR / "transaction_simulation.md"),
        ("Portfolio Analytics", REPORT_DIR / "portfolio_analytics.md"),
        ("Strategy Center", REPORT_DIR / "strategy_center.md"),
        ("Strategy Intelligence", REPORT_DIR / "strategy_intelligence.md"),
        ("Market Universe Evidence", REPORT_DIR / "market_universe_evidence.md"),
        ("Quote Coverage Evidence", REPORT_DIR / "quote_coverage_evidence.md"),
        ("ETH Route Architecture", REPORT_DIR / "eth_route_architecture.md"),
        ("ETH Market Coverage", REPORT_DIR / "eth_market_coverage.md"),
        ("Backtest", REPORT_DIR / "backtest_report.md"),
        ("Replay Diagnostics", REPORT_DIR / "replay_diagnostics.md"),
        ("Pool Depth Ladder", REPORT_DIR / "pool_depth_ladder.md"),
        ("Execution Realism", REPORT_DIR / "execution_realism.md"),
        ("Execution Cost Evidence", REPORT_DIR / "execution_cost_evidence.md"),
        ("Optimization", REPORT_DIR / "optimization_report.md"),
        ("Experiment Evidence", REPORT_DIR / "experiment_report.md"),
        ("Feature Store", REPORT_DIR / "feature_store.md"),
        ("Research Dashboard", REPORT_DIR / "research_dashboard.md"),
    ]:
        st.markdown(f"### {title}")
        txt = read_text(path)
        if txt:
            st.markdown(txt)
        else:
            st.info(f"{path} not found yet.")


def render_backtesting() -> None:
    st.subheader("Replay / Backtesting")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("Run Replay Backtest"):
            def task():
                BacktestService = import_object("app.backtesting.backtest_service", "BacktestService")
                return BacktestService().run_default_backtest()

            result = safe_run("Running replay backtest...", task)
            if result is not None:
                st.success("Replay backtest generated.")

    with c2:
        if st.button("Run Optimization"):
            def task():
                OptimizationService = import_object("app.backtesting.optimization_service", "OptimizationService")
                return OptimizationService().run()

            result = safe_run("Running optimization grid...", task)
            if result is not None:
                st.success("Optimization report generated.")

    with c3:
        if st.button("Run Replay Diagnostics"):
            def task():
                ReplayDiagnosticsService = import_object("app.backtesting.replay_diagnostics_service", "ReplayDiagnosticsService")
                return ReplayDiagnosticsService().generate()

            result = safe_run("Running replay diagnostics...", task)
            if result is not None:
                st.success("Replay diagnostics generated.")

    with c4:
        if st.button("Run Cost Evidence"):
            def task():
                ExecutionCostEvidenceService = import_object("app.execution.execution_cost_evidence_service", "ExecutionCostEvidenceService")
                return ExecutionCostEvidenceService().generate()

            result = safe_run("Running execution cost evidence...", task)
            if result is not None:
                st.success("Execution cost evidence generated.")

    with c5:
        if st.button("Record Experiment"):
            def task():
                ReportAuditService = import_object("app.reporting.report_audit", "ReportAuditService")
                ExperimentService = import_object("app.backtesting.experiment_service", "ExperimentService")
                if (
                    (REPORT_DIR / "report_audit.json").exists()
                    and (REPORT_DIR / "experiment_report.json").exists()
                    and (REPORT_DIR / "strategy_intelligence.json").exists()
                ):
                    ReportAuditService().generate()
                return ExperimentService().run()

            result = safe_run("Recording experiment evidence...", task)
            if result is not None:
                st.success("Experiment report generated.")

    if st.button("Run Pool Depth Ladder"):
        def task():
            PoolDepthLadderService = import_object("app.research.pool_depth_ladder_service", "PoolDepthLadderService")
            return PoolDepthLadderService().generate()

        result = safe_run("Running pool-depth ladder probes...", task)
        if result is not None:
            st.success("Pool-depth ladder generated.")

    backtest_json = REPORT_DIR / "backtest_report.json"
    if backtest_json.exists():
        try:
            payload = json.loads(backtest_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read backtest report: {exc}")
            payload = {}
        if payload:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Replay Signals", payload.get("total_signals", "-"))
            c2.metric("Trades", payload.get("simulated_trades", "-"))
            c3.metric("PnL", payload.get("total_simulated_profit_usd", "-"))
            c4.metric("Win Rate %", payload.get("win_rate_pct", "-"))
            dataframe_or_info(payload.get("trades", []), "No replay trades met the threshold.")
    else:
        st.info("No backtest_report.json yet. Run Replay Backtest.")

    replay_diag_json = REPORT_DIR / "replay_diagnostics.json"
    if replay_diag_json.exists():
        try:
            payload = json.loads(replay_diag_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read replay diagnostics: {exc}")
            payload = {}
        if payload:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Production Trades", payload.get("production_trade_count", "-"))
            c2.metric("Production Buffer", payload.get("production_cost_buffer_pct", "-"))
            c3.metric("Best Buffer", payload.get("best_profitable_cost_buffer_pct", "-"))
            c4.metric("Best Trades", payload.get("best_profitable_trade_count", "-"))
            dataframe_or_info(payload.get("cost_buffer_scenarios", []), "No replay diagnostic scenarios yet.")
    else:
        st.info("No replay_diagnostics.json yet. Run Replay Diagnostics.")

    cost_json = REPORT_DIR / "execution_cost_evidence.json"
    if cost_json.exists():
        try:
            payload = json.loads(cost_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read execution cost evidence: {exc}")
            payload = {}
        if payload:
            assessment = payload.get("assessment") or {}
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Cost Status", assessment.get("buffer_status", payload.get("buffer_status", "-")))
            c2.metric("Confidence", assessment.get("confidence", payload.get("confidence", "-")))
            c3.metric("Lower Bound %", assessment.get("observed_total_cost_lower_bound_pct", "-"))
            c4.metric("Surplus %", assessment.get("buffer_surplus_vs_lower_bound_pct", "-"))
            dataframe_or_info(payload.get("findings", []), "No execution cost findings yet.")
    else:
        st.info("No execution_cost_evidence.json yet. Run Cost Evidence.")

    optimization_json = REPORT_DIR / "optimization_report.json"
    if optimization_json.exists():
        try:
            payload = json.loads(optimization_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read optimization report: {exc}")
            payload = {}
        if payload:
            best = payload.get("best_scenario") or {}
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Scenarios", payload.get("scenario_count", "-"))
            c2.metric("Best Trades", best.get("trade_count", "-"))
            c3.metric("Best PnL", best.get("total_pnl_usd", "-"))
            c4.metric("Best Cost %", best.get("cost_buffer_pct", "-"))
            dataframe_or_info(payload.get("scenarios", [])[:25], "No optimization scenarios yet.")
    else:
        st.info("No optimization_report.json yet. Run Optimization.")

    experiment_json = REPORT_DIR / "experiment_report.json"
    if experiment_json.exists():
        try:
            payload = json.loads(experiment_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read experiment report: {exc}")
            payload = {}
        if payload:
            latest = payload.get("latest_experiment") or {}
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Experiment Status", latest.get("status", "-"))
            c2.metric("Pass", latest.get("pass_count", "-"))
            c3.metric("Warn", latest.get("warn_count", "-"))
            c4.metric("Fail", latest.get("fail_count", "-"))
            dataframe_or_info(latest.get("gates", []), "No experiment gates yet.")
            dataframe_or_info(payload.get("recent_experiments", []), "No experiment history yet.")
    else:
        st.info("No experiment_report.json yet. Record Experiment.")

    for title, path in [
        ("Backtest Report", REPORT_DIR / "backtest_report.md"),
        ("Replay Diagnostics Report", REPORT_DIR / "replay_diagnostics.md"),
        ("Pool Depth Ladder Report", REPORT_DIR / "pool_depth_ladder.md"),
        ("Execution Realism Report", REPORT_DIR / "execution_realism.md"),
        ("Execution Cost Evidence Report", REPORT_DIR / "execution_cost_evidence.md"),
        ("Optimization Report", REPORT_DIR / "optimization_report.md"),
        ("Experiment Report", REPORT_DIR / "experiment_report.md"),
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

    paper_report = read_json(REPORT_DIR / "paper_report.json")
    reconciliation = paper_report.get("pnl_reconciliation", {}) if isinstance(paper_report, dict) else {}
    if reconciliation:
        status = reconciliation.get("status", "-")
        if status == "RECONCILED":
            st.success("PnL reconciled to active paper portfolio state.")
        else:
            st.warning(
                "Paper-order history differs from active portfolio state. "
                "Cash and Daily PnL below use paper_portfolio_state.json."
            )
        st.json(reconciliation)

    st.markdown("### Open Positions")
    dataframe_or_info(positions, "No open paper positions.")

    st.markdown("### Closed Arbitrage Trades")
    dataframe_or_info(state.get("arbitrage_trades", [])[-100:], "No closed arbitrage trades in state yet.")

    st.markdown("### Risk State")
    safe_state = dict(state)
    safe_state["positions"] = f"{len(state.get('positions', []))} row(s)"
    safe_state["arbitrage_trades"] = f"{len(state.get('arbitrage_trades', []))} row(s)"
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

            reconciliation = analytics.get("pnl_reconciliation", {})
            if reconciliation:
                status = reconciliation.get("status", "-")
                if status == "RECONCILED":
                    st.success("PnL reconciled to active paper portfolio state.")
                else:
                    st.warning(
                        "Historical paper-order journal differs from active portfolio state. "
                        "Analytics totals, Daily PnL, and equity curve use the active portfolio ledger."
                    )
                st.json(reconciliation)

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


def render_strategy_intelligence() -> None:
    st.subheader("AI Strategy Intelligence")
    if st.button("Generate Strategy Intelligence"):
        def task():
            StrategyIntelligenceService = import_object("app.ai.strategy_intelligence_service", "StrategyIntelligenceService")
            return StrategyIntelligenceService().generate()

        result = safe_run("Generating strategy intelligence...", task)
        if result is not None:
            st.success("Strategy intelligence generated.")
            st.json(result)

    report_json = REPORT_DIR / "strategy_intelligence.json"
    if report_json.exists():
        try:
            payload = json.loads(report_json.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            st.error(f"Could not read strategy intelligence: {exc}")
            payload = {}
        if payload:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Top Recommendation", payload.get("top_recommendation", "-"))
            c2.metric("Strategies", payload.get("strategy_count", "-"))
            c3.metric("Promotion Allowed", payload.get("promotion_allowed", "-"))
            c4.metric("Mode", payload.get("mode", "-"))
            st.markdown("### Context")
            st.json(payload.get("context", {}))
            st.markdown("### Strategy Scores")
            dataframe_or_info(payload.get("strategies", []), "No strategy intelligence rows yet.")
    else:
        st.info("No strategy_intelligence.json found yet. Generate Strategy Intelligence first.")

    st.markdown("### Strategy Intelligence Report")
    txt = read_text(REPORT_DIR / "strategy_intelligence.md")
    if txt:
        st.markdown(txt)


def render_risk_controls() -> None:
    st.subheader("Risk & Trading Controls")
    TradingControlsService = import_object("app.execution.trading_controls_service", "TradingControlsService")
    service = TradingControlsService()
    status = service.get_status()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Trading", "ON" if status["live_trading_enabled"] else "OFF")
    c2.metric("Kill Switch", "ON" if status["live_kill_switch_enabled"] else "OFF")
    c3.metric("Live Guard", "Allowed" if status["live_guard_allowed"] else "Blocked")
    c4.metric("Max Wallet USD", status.get("max_live_wallet_usd", "0"))

    st.markdown("### Live Safety Checklist")
    dataframe_or_info(service.checklist(), "No live safety checks available.")

    if st.button("Generate Live Safety Report"):
        def task():
            LiveSafetyReportService = import_object("app.execution.live_safety_report", "LiveSafetyReportService")
            return LiveSafetyReportService().generate()

        result = safe_run("Generating live safety report...", task)
        if result is not None:
            st.success("Live safety report generated.")
            st.json(result)

    if st.button("Generate Wallet Preflight"):
        def task():
            WalletPreflightService = import_object("app.execution.wallet_preflight_service", "WalletPreflightService")
            return WalletPreflightService().generate()

        result = safe_run("Generating wallet preflight...", task)
        if result is not None:
            st.success("Wallet preflight generated.")
            st.json(result)

    if st.button("Generate Live Readiness Checklist"):
        def task():
            LiveReadinessChecklistService = import_object("app.execution.live_readiness_checklist_service", "LiveReadinessChecklistService")
            return LiveReadinessChecklistService().generate()

        result = safe_run("Generating live readiness checklist...", task)
        if result is not None:
            st.success("Live readiness checklist generated.")
            st.json(result)

    if st.button("Generate Transaction Simulation"):
        def task():
            TransactionSimulationService = import_object("app.execution.transaction_simulation_service", "TransactionSimulationService")
            return TransactionSimulationService().generate()

        result = safe_run("Generating transaction simulation evidence...", task)
        if result is not None:
            st.success("Transaction simulation report generated.")
            st.json(result)

    st.markdown("### Transaction Simulation Report")
    tx_sim_txt = read_text(REPORT_DIR / "transaction_simulation.md")
    if tx_sim_txt:
        st.markdown(tx_sim_txt)
    else:
        st.info("No transaction_simulation.md found yet. Generate Transaction Simulation first.")

    st.markdown("### Live Readiness Checklist")
    readiness_txt = read_text(REPORT_DIR / "live_readiness_checklist.md")
    if readiness_txt:
        st.markdown(readiness_txt)
    else:
        st.info("No live_readiness_checklist.md found yet. Generate Live Readiness Checklist first.")

    st.markdown("### Wallet Preflight Report")
    wallet_txt = read_text(REPORT_DIR / "wallet_preflight.md")
    if wallet_txt:
        st.markdown(wallet_txt)
    else:
        st.info("No wallet_preflight.md found yet. Generate Wallet Preflight first.")

    st.markdown("### Live Safety Report")
    txt = read_text(REPORT_DIR / "live_safety.md")
    if txt:
        st.markdown(txt)
    else:
        st.info("No live_safety.md found yet. Generate the Live Safety Report first.")

    st.markdown("### Runtime Flags")
    flags = {
        "CRYPTOAI_LIVE_TRADING_ENABLED": os.getenv("CRYPTOAI_LIVE_TRADING_ENABLED", "false"),
        "CRYPTOAI_PAPER_TRADING_ENABLED": os.getenv("CRYPTOAI_PAPER_TRADING_ENABLED", "true"),
        "CRYPTOAI_LIVE_KILL_SWITCH_ENABLED": os.getenv("CRYPTOAI_LIVE_KILL_SWITCH_ENABLED", "true"),
        "CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION": os.getenv("CRYPTOAI_REQUIRE_MANUAL_CONFIRMATION", "true"),
        "CRYPTOAI_LIVE_WALLET_ADDRESS": "PRESENT" if os.getenv("CRYPTOAI_LIVE_WALLET_ADDRESS") else "ABSENT",
        "CRYPTOAI_MAIN_WALLET_ADDRESS": "PRESENT" if os.getenv("CRYPTOAI_MAIN_WALLET_ADDRESS") else "ABSENT",
        "CRYPTOAI_MAX_LIVE_WALLET_USD": os.getenv("CRYPTOAI_MAX_LIVE_WALLET_USD", "0"),
        "CRYPTOAI_MAX_LIVE_TRADE_USD": os.getenv("CRYPTOAI_MAX_LIVE_TRADE_USD", "0"),
        "CRYPTOAI_MAX_DAILY_LOSS_USD": os.getenv("CRYPTOAI_MAX_DAILY_LOSS_USD", "0"),
        "CRYPTOAI_LIVE_ALLOWED_CHAINS": os.getenv("CRYPTOAI_LIVE_ALLOWED_CHAINS", "base"),
        "CRYPTOAI_LIVE_ALLOWED_DEXES": os.getenv("CRYPTOAI_LIVE_ALLOWED_DEXES", "Uniswap V3,Aerodrome"),
        "CRYPTOAI_LIVE_ALLOWED_TOKENS": os.getenv("CRYPTOAI_LIVE_ALLOWED_TOKENS", "WETH,USDC"),
        "CRYPTOAI_REQUIRE_TX_SIMULATION": os.getenv("CRYPTOAI_REQUIRE_TX_SIMULATION", "true"),
        "CRYPTOAI_TX_SIMULATION_PASSED": os.getenv("CRYPTOAI_TX_SIMULATION_PASSED", "false"),
        "CRYPTOAI_REQUIRE_PAPER_EVIDENCE": os.getenv("CRYPTOAI_REQUIRE_PAPER_EVIDENCE", "true"),
        "CRYPTOAI_MIN_PAPER_CLOSED_TRADES": os.getenv("CRYPTOAI_MIN_PAPER_CLOSED_TRADES", "30"),
        "CRYPTOAI_MIN_EXECUTION_COST_CONFIDENCE": os.getenv("CRYPTOAI_MIN_EXECUTION_COST_CONFIDENCE", "HIGH"),
        "CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD": os.getenv("CRYPTOAI_TINY_LIVE_TRADE_CEILING_USD", "100"),
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
        DATA_DIR / "paper_orders_legacy_archive.jsonl",
        DATA_DIR / "paper_portfolio_state.json",
        REPORT_DIR / "quote_diagnostics.md",
        REPORT_DIR / "multi_dex_opportunities.md",
        REPORT_DIR / "opportunity_explorer.md",
        REPORT_DIR / "paper_report.md",
        REPORT_DIR / "live_safety.json",
        REPORT_DIR / "live_safety.md",
        REPORT_DIR / "wallet_preflight.json",
        REPORT_DIR / "wallet_preflight.md",
        REPORT_DIR / "live_readiness_checklist.json",
        REPORT_DIR / "live_readiness_checklist.md",
        REPORT_DIR / "transaction_simulation.json",
        REPORT_DIR / "transaction_simulation.md",
        REPORT_DIR / "portfolio_analytics.json",
        REPORT_DIR / "portfolio_analytics.md",
        DATA_DIR / "strategy_signals.jsonl",
        DATA_DIR / "strategy_ranked_signals.jsonl",
        REPORT_DIR / "strategy_center.json",
        REPORT_DIR / "strategy_center.md",
        REPORT_DIR / "strategy_intelligence.json",
        REPORT_DIR / "strategy_intelligence.md",
        REPORT_DIR / "backtest_report.json",
        REPORT_DIR / "backtest_report.md",
        REPORT_DIR / "replay_diagnostics.json",
        REPORT_DIR / "replay_diagnostics.md",
        REPORT_DIR / "execution_cost_evidence.json",
        REPORT_DIR / "execution_cost_evidence.md",
        REPORT_DIR / "optimization_report.json",
        REPORT_DIR / "optimization_report.md",
        REPORT_DIR / "experiment_report.json",
        REPORT_DIR / "experiment_report.md",
        DATA_DIR / "experiments.jsonl",
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
        REPORT_DIR / "market_universe_evidence.json",
        REPORT_DIR / "market_universe_evidence.md",
        REPORT_DIR / "quote_coverage_evidence.json",
        REPORT_DIR / "quote_coverage_evidence.md",
        REPORT_DIR / "eth_route_architecture.json",
        REPORT_DIR / "eth_route_architecture.md",
        REPORT_DIR / "eth_market_coverage.json",
        REPORT_DIR / "eth_market_coverage.md",
        Path("config") / "paper_trading_settings.json",
        REPORT_DIR / "paper_trading_settings.json",
        REPORT_DIR / "paper_trading_settings.md",
        REPORT_DIR / "provider_monitor.json",
        REPORT_DIR / "provider_monitor.md",
        REPORT_DIR / "report_audit.json",
        REPORT_DIR / "report_audit.md",
    ]:
        rows.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "type": "dir" if path.is_dir() else "file" if path.exists() else "-",
                "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch")

    st.markdown("### Provider Health")
    provider_health_path = DATA_DIR / "provider_health.json"
    if provider_health_path.exists():
        try:
            payload = json.loads(provider_health_path.read_text(encoding="utf-8", errors="replace"))
            providers = payload.get("providers", [])
            if providers:
                st.dataframe(pd.DataFrame(providers), width="stretch")
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
        python -m app.execution.live_safety_report
        python -m app.execution.wallet_preflight_service
        python -m app.execution.live_readiness_checklist_service
        python -m app.execution.transaction_simulation_service
        python -m app.strategy.strategy_center
        python -m app.research.research_report
        python -m app.market_intelligence.market_intelligence_service
        python -m app.operations.provider_monitor
        python -m app.backtesting.backtest_service
        python -m app.backtesting.replay_diagnostics_service
        python -m app.research.pool_depth_ladder_service
        python -m app.execution.execution_realism_service
        python -m app.execution.execution_cost_evidence_service
        python -m app.backtesting.optimization_service
        python -m app.research.market_universe_evidence_service
        python -m app.research.quote_coverage_evidence_service
        python -m app.research.eth_route_architecture_service
        python -m app.research.eth_market_coverage_service
        python -m app.operations.paper_settings_service
        python -m app.reporting.report_audit
        python -m app.backtesting.experiment_service
        python -m app.ai.strategy_intelligence_service
        python -m app.reporting.report_audit
        python -m app.reporting.legacy_paper_archive --dry-run
        python -m app.automation.paper_autopilot --loop --use-settings
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
    "7 Replay / Backtesting": render_backtesting,
    "8 Paper Orders": render_paper_orders,
    "9 Paper Portfolio": render_paper_portfolio,
    "10 Portfolio Analytics": render_portfolio_analytics,
    "11 Strategy Center": render_strategy_center,
    "12 AI Strategy Intelligence": render_strategy_intelligence,
    "13 Market Intelligence": render_market_intelligence,
    "14 Provider Monitor": render_provider_monitor,
    "15 Research Dashboard": render_research_dashboard,
    "16 Risk & Controls": render_risk_controls,
    "17 Paper Settings": render_paper_settings,
    "18 System Health": render_system_health,
    "19 Setup / Roadmap": render_setup,
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
