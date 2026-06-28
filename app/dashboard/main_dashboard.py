from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from app.blockchain.chains import SUPPORTED_CHAINS
from app.marketdata.market_service import MarketDataService
from app.quotes.quote_service import QuoteService
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain
from app.registry.tokens import get_tokens_for_chain
from app.services.chain_health_service import ChainHealthService
from app.services.system_health_service import SystemHealthService

try:
    from app.ai.ranking_service import AiRankingService
except Exception:
    AiRankingService = None

try:
    from app.analytics.analytics_service import AnalyticsService
except Exception:
    AnalyticsService = None

try:
    from app.automation.paper_autopilot import PaperAutopilot
except Exception:
    PaperAutopilot = None

try:
    from app.backtesting.backtest_service import BacktestService
except Exception:
    BacktestService = None

try:
    from app.database.state_service import StateService
    from app.database.event_store import EventStore
except Exception:
    StateService = None
    EventStore = None

try:
    from app.events.event_service import EventBusService
except Exception:
    EventBusService = None

try:
    from app.execution.paper_execution_service import PaperExecutionService
    from app.execution.trading_controls_service import TradingControlsService
except Exception:
    PaperExecutionService = None
    TradingControlsService = None

try:
    from app.opportunities.opportunity_service import OpportunityService
except Exception:
    OpportunityService = None

try:
    from app.portfolio.portfolio_service import PortfolioService
except Exception:
    PortfolioService = None

try:
    from app.realtime.market_data_service import RealtimeMarketDataService
except Exception:
    RealtimeMarketDataService = None

try:
    from app.risk.risk_service import RiskService
except Exception:
    RiskService = None

try:
    from app.scheduler.scheduler_service import SchedulerService
except Exception:
    SchedulerService = None

try:
    from app.scanner.opportunity_scanner import OpportunityScanner
except Exception:
    OpportunityScanner = None

try:
    from app.scanner.net_opportunity_scanner import NetOpportunityScanner
except Exception:
    NetOpportunityScanner = None

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None


st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon="📊",
    layout="wide",
)


def dataframe_or_info(rows, message: str) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(message)


@st.cache_data(ttl=30)
def load_chain_health():
    return ChainHealthService().check_all_chains()


@st.cache_data(ttl=60)
def load_market_prices():
    return MarketDataService().get_registered_asset_prices()


@st.cache_data(ttl=10)
def load_dex_quotes():
    return QuoteService().get_base_quotes()


@st.cache_data(ttl=15)
def load_gross_opportunities():
    if OpportunityScanner is None:
        return []
    return OpportunityScanner().scan_base_gross_opportunities()


@st.cache_data(ttl=15)
def load_net_estimates():
    if NetOpportunityScanner is None:
        return []
    scanner = NetOpportunityScanner()
    if hasattr(scanner, "scan_base_net_opportunities"):
        return scanner.scan_base_net_opportunities()
    return []


@st.cache_data(ttl=15)
def load_strategy_signals():
    if StrategyService is None:
        return []
    return StrategyService().get_all_signals()


@st.cache_data(ttl=15)
def load_ai_rankings():
    if AiRankingService is None:
        return []
    return AiRankingService().rank_strategy_signals()


@st.cache_data(ttl=15)
def load_risk_assessments():
    if RiskService is None:
        return []
    return RiskService().assess_ranked_signals()


@st.cache_data(ttl=20)
def load_portfolio_snapshot():
    if PortfolioService is None:
        return None
    return PortfolioService().get_snapshot()


@st.cache_data(ttl=20)
def run_backtest(notional: float):
    if BacktestService is None:
        return None
    return BacktestService().run_default_backtest(Decimal(str(notional)))


def render_header() -> None:
    st.title("📊 CryptoAI Quant Trading Dashboard")
    st.caption("Multi-chain crypto research platform — paper trading only, no wallet, no live trading.")


def render_chain_health() -> None:
    st.subheader("Multi-Chain RPC Health")
    rows = []
    for result in load_chain_health():
        rows.append(
            {
                "Chain": result.chain_name,
                "Connected": "✅ Yes" if result.connected else "❌ No",
                "Chain ID": result.chain_id,
                "Latest Block": result.latest_block,
                "Gas Gwei": float(result.gas_price_gwei) if result.gas_price_gwei else None,
                "Error": result.error or "",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def render_live_prices() -> None:
    st.subheader("Live Market Prices")
    rows = []
    for price in load_market_prices():
        rows.append(
            {
                "Asset": price.name,
                "Symbol": price.symbol,
                "CoinGecko ID": price.coingecko_id,
                "USD Price": float(price.usd_price) if price.usd_price else None,
                "24h Change %": float(price.change_24h_pct) if price.change_24h_pct else None,
                "24h Volume": float(price.volume_24h) if price.volume_24h else None,
                "Market Cap": float(price.market_cap) if price.market_cap else None,
            }
        )
    dataframe_or_info(rows, "No live market prices available.")


def render_realtime() -> None:
    st.subheader("Real-Time Market Data")
    if RealtimeMarketDataService is None:
        st.info("Real-time market data module not installed.")
        return

    service = RealtimeMarketDataService()
    symbol = st.selectbox("Symbol", ["ethusdt", "btcusdt", "solusdt", "bnbusdt"], index=0)

    if st.button("Fetch One Live Tick"):
        snap = service.snapshot(symbol=symbol)
        c1, c2, c3 = st.columns(3)
        c1.metric("Connected", "Yes" if snap["connected"] else "No")
        c2.metric("Symbol", snap["symbol"])
        c3.metric("Price USD", snap["price_usd"] or "-")
        st.write(snap["message"])

    st.markdown("### Recent Ticks")
    dataframe_or_info(service.recent_ticks(), "No stored real-time ticks yet.")


def render_dex_quotes() -> None:
    st.subheader("Live DEX Quotes")
    rows = []
    for quote in load_dex_quotes():
        ok = quote.error is None and quote.amount_out is not None
        rows.append(
            {
                "Chain": quote.chain,
                "DEX": quote.dex,
                "Token In": quote.token_in,
                "Token Out": quote.token_out,
                "Amount In": float(quote.amount_in),
                "Amount Out": float(quote.amount_out) if quote.amount_out else None,
                "Price": float(quote.price) if quote.price else None,
                "Status": "✅ OK" if ok else "⚠️ Skipped",
                "Error": quote.error or "",
            }
        )
    dataframe_or_info(rows, "No DEX quotes available.")


def render_opportunity_engine() -> None:
    st.subheader("Advanced Opportunity Engine")
    if OpportunityService is None:
        st.info("Opportunity engine module not installed.")
        return

    if st.button("Run Advanced Opportunity Scan"):
        candidates = OpportunityService().scan()
        rows = []
        for c in candidates:
            rows.append(
                {
                    "ID": c.opportunity_id,
                    "Type": c.opportunity_type.value,
                    "Chain": c.chain,
                    "Pair": c.pair,
                    "Buy": c.source_buy,
                    "Sell": c.source_sell,
                    "Gross Spread %": str(c.gross_spread_pct) if c.gross_spread_pct is not None else "-",
                    "Cost Buffer %": str(c.estimated_cost_pct),
                    "Net Edge %": str(c.estimated_net_edge_pct) if c.estimated_net_edge_pct is not None else "-",
                    "Status": c.status.value,
                    "Reason": c.reason,
                }
            )
        dataframe_or_info(rows, "No opportunity candidates found.")

    st.warning("Read-only; no real execution.")


def render_gross_opps() -> None:
    st.subheader("Gross Opportunity Scanner")
    rows = []
    for opp in load_gross_opportunities():
        rows.append(
            {
                "Chain": getattr(opp, "chain", "-"),
                "Pair": getattr(opp, "pair", "-"),
                "Buy DEX": getattr(opp, "best_buy_dex", "-"),
                "Sell DEX": getattr(opp, "best_sell_dex", "-"),
                "Buy Price": float(getattr(opp, "buy_price", 0)),
                "Sell Price": float(getattr(opp, "sell_price", 0)),
                "Gross Spread %": float(getattr(opp, "gross_spread_pct", 0)),
            }
        )
    dataframe_or_info(rows, "No gross opportunities detected.")


def render_net_estimates() -> None:
    st.subheader("Net Opportunity Estimates")
    rows = []
    for opp in load_net_estimates():
        d = opp.__dict__ if hasattr(opp, "__dict__") else {}
        rows.append({k: str(v) for k, v in d.items()})
    dataframe_or_info(rows, "No net estimates available.")
    st.warning("Estimates are not trade instructions.")


def render_strategies() -> None:
    st.subheader("Strategy Engine")
    rows = []
    for signal in load_strategy_signals():
        rows.append(
            {
                "Strategy": signal.strategy_name,
                "Chain": signal.chain,
                "Pair": signal.pair,
                "Action": signal.action.value if hasattr(signal.action, "value") else str(signal.action),
                "Confidence": signal.confidence_score,
                "Expected Edge %": str(signal.expected_edge_pct) if signal.expected_edge_pct is not None else "-",
                "Reason": signal.reason,
            }
        )
    dataframe_or_info(rows, "No strategy signals available.")
    st.warning("READY_FOR_PAPER means simulation only.")


def render_ai_ranking() -> None:
    st.subheader("AI Ranking Engine")
    rows = []
    for ranked in load_ai_rankings():
        rows.append(
            {
                "Strategy": ranked.strategy_name,
                "Chain": ranked.chain,
                "Pair": ranked.pair,
                "Source Action": ranked.source_action,
                "Confidence": ranked.confidence_score,
                "Expected Edge %": str(ranked.expected_edge_pct) if ranked.expected_edge_pct is not None else "-",
                "AI Score": ranked.ai_score,
                "Recommendation": ranked.recommendation.value if hasattr(ranked.recommendation, "value") else str(ranked.recommendation),
                "Reasoning": ranked.reasoning,
            }
        )
    dataframe_or_info(rows, "No AI-ranked signals available.")


def render_risk() -> None:
    st.subheader("Risk Engine")
    rows = []
    for assessment in load_risk_assessments():
        rows.append(
            {
                "Strategy": assessment.strategy_name,
                "Chain": assessment.chain,
                "Pair": assessment.pair,
                "AI Score": assessment.ai_score,
                "Expected Edge %": str(assessment.expected_edge_pct) if assessment.expected_edge_pct is not None else "-",
                "Risk Decision": assessment.decision.value if hasattr(assessment.decision, "value") else str(assessment.decision),
                "Max Paper Notional USD": str(assessment.max_allowed_notional_usd),
                "Reason": assessment.reason,
            }
        )
    dataframe_or_info(rows, "No risk assessments available.")


def render_portfolio() -> None:
    st.subheader("Portfolio Engine")
    snapshot = load_portfolio_snapshot()

    if snapshot is None:
        st.info("Portfolio module not installed.")
        return

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Value", f"${snapshot.total_value_usd:.2f}")
    c2.metric("Cash", f"${snapshot.cash_usd:.2f}")
    c3.metric("Holdings", f"${snapshot.holdings_value_usd:.2f}")
    c4.metric("Unrealized P/L", f"${snapshot.unrealized_pnl_usd:.2f}")
    c5.metric("Total P/L", f"${snapshot.total_pnl_usd:.2f}")
    c6.metric("Open Positions", snapshot.open_positions)

    st.markdown("### Holdings")
    dataframe_or_info(
        [
            {
                "Chain": h.chain,
                "Symbol": h.symbol,
                "Quantity": str(h.quantity),
                "Avg Cost": str(h.avg_cost_usd),
                "Current Price": str(h.current_price_usd),
                "Market Value": str(h.market_value_usd),
                "Unrealized P/L": str(h.unrealized_pnl_usd),
            }
            for h in snapshot.holdings
        ],
        "No holdings.",
    )

    st.markdown("### Positions")
    dataframe_or_info(
        [
            {
                "ID": p.position_id,
                "Strategy": p.strategy_name,
                "Chain": p.chain,
                "Pair": p.pair,
                "Quantity": str(p.quantity),
                "Entry": str(p.entry_price_usd),
                "Current": str(p.current_price_usd),
                "P/L": str(p.unrealized_pnl_usd),
                "Status": p.status.value if hasattr(p.status, "value") else str(p.status),
            }
            for p in snapshot.positions
        ],
        "No open simulated positions.",
    )


def render_paper_execution() -> None:
    st.subheader("Paper Execution Engine")
    if PaperExecutionService is None:
        st.info("Paper execution module not installed.")
        return

    service = PaperExecutionService()
    if st.button("Run Paper Execution Once"):
        st.cache_data.clear()
        batch = service.run_once()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Candidates", batch.total_candidates)
        c2.metric("Filled", batch.filled_orders)
        c3.metric("Rejected", batch.rejected_orders)
        c4.metric("Skipped", batch.skipped_orders)
        c5.metric("Notional", f"${batch.total_notional_usd:.2f}")

    st.markdown("### Recent Paper Orders")
    dataframe_or_info(service.recent_orders(), "No paper orders saved yet.")


def render_autopilot() -> None:
    st.subheader("Paper Autopilot")
    if PaperAutopilot is None:
        st.info("Autopilot module not installed.")
        return

    enable_paper = st.checkbox("Enable paper execution", value=True)
    if st.button("Run Paper Autopilot Once"):
        result = PaperAutopilot(enable_paper_execution=enable_paper).run_once()
        st.json(result)

    st.code("python -m app.automation.paper_autopilot --loop --interval-seconds 300", language="powershell")
    st.warning("Use this for paper mode only. Live trading remains blocked.")


def render_scheduler() -> None:
    st.subheader("Scheduler")
    if SchedulerService is None:
        st.info("Scheduler module not installed.")
        return

    enable_paper = st.checkbox("Enable paper execution for scheduler run", value=False)
    if st.button("Run Scheduler Once"):
        st.cache_data.clear()
        result = SchedulerService().run_once(enable_paper_execution=enable_paper)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Run ID", result.run_id)
        c2.metric("Status", result.status.value if hasattr(result.status, "value") else str(result.status))
        c3.metric("Paper Exec", "ON" if result.paper_execution_enabled else "OFF")
        c4.metric("Latency ms", result.total_latency_ms)

        dataframe_or_info(
            [
                {
                    "Step": step.step_name,
                    "Status": step.status.value if hasattr(step.status, "value") else str(step.status),
                    "Items": step.items_processed,
                    "Latency ms": step.latency_ms,
                    "Message": step.message,
                }
                for step in result.steps
            ],
            "No scheduler steps.",
        )


def render_event_bus() -> None:
    st.subheader("Event Bus")
    if EventBusService is None:
        st.info("Event bus module not installed.")
        return

    service = EventBusService()
    if st.button("Publish Test Event"):
        service.publish_system_event("dashboard", "Manual test event from dashboard.")

    dataframe_or_info(service.recent_events(), "No in-memory events yet. Run scheduler once.")


def render_database() -> None:
    st.subheader("Database State")
    if StateService is None:
        st.info("Database module not installed.")
        return

    service = StateService()
    summary = service.summary()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Events", summary.get("events", 0))
    c2.metric("Scheduler Runs", summary.get("scheduler_runs", 0))
    c3.metric("Paper Orders", summary.get("paper_orders", 0))
    c4.metric("Portfolio Snapshots", summary.get("portfolio_snapshots", 0))

    st.markdown("### Recent Scheduler Runs")
    dataframe_or_info(service.recent_scheduler_runs(), "No scheduler runs saved yet.")

    st.markdown("### Recent Paper Orders")
    dataframe_or_info(service.recent_paper_orders(), "No paper orders saved yet.")

    if hasattr(service, "recent_portfolio_snapshots"):
        st.markdown("### Recent Portfolio Snapshots")
        dataframe_or_info(service.recent_portfolio_snapshots(), "No portfolio snapshots saved yet.")

    if EventStore is not None:
        st.markdown("### Recent Events")
        dataframe_or_info(EventStore().recent_events(), "No events saved yet.")


def render_backtesting() -> None:
    st.subheader("Backtesting")
    if BacktestService is None:
        st.info("Backtesting module not installed.")
        return

    notional = st.number_input("Simulated trade notional USD", min_value=10.0, max_value=100000.0, value=1000.0, step=100.0)
    result = run_backtest(notional)
    if result is None:
        st.info("No backtest result.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Signals", result.total_signals)
    c2.metric("Trades", result.simulated_trades)
    c3.metric("Winners", result.winning_trades)
    c4.metric("Win Rate", f"{result.win_rate_pct:.2f}%")
    c5.metric("P/L", f"${result.total_simulated_profit_usd:.4f}")
    st.info(result.notes)

    dataframe_or_info(
        [
            {
                "Timestamp": t.timestamp,
                "Strategy": t.strategy_name,
                "Chain": t.chain,
                "Pair": t.pair,
                "Edge %": str(t.estimated_edge_pct),
                "Profit USD": str(t.simulated_profit_usd),
                "Reason": t.reason,
            }
            for t in result.trades
        ],
        "No simulated trades.",
    )


def render_performance() -> None:
    st.subheader("Performance Metrics")
    service = SystemHealthService()
    dataframe_or_info(service.get_metric_rows(), "Metrics will populate after calls complete.")
    st.markdown("### Cache Stats")
    st.json(service.get_cache_stats())


def render_system_health() -> None:
    st.subheader("System Health & Latency Budget")
    service = SystemHealthService()
    dataframe_or_info(
        [
            {
                "Stage": item.stage,
                "Target ms": item.target_ms,
                "Current ms": item.current_ms,
                "Status": item.status,
            }
            for item in service.get_latency_budget()
        ],
        "No latency budget data.",
    )


def render_trading_controls() -> None:
    st.subheader("Trading Controls")
    if TradingControlsService is None:
        st.info("Trading controls module not installed.")
        return

    service = TradingControlsService()
    status = service.get_status()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Trading", "ON" if status["live_trading_enabled"] else "OFF")
    c2.metric("Paper Trading", "ON" if status["paper_trading_enabled"] else "OFF")
    c3.metric("Private Key", "Present" if status["private_key_configured"] else "Absent")
    c4.metric("Live Guard", "Allowed" if status["live_guard_allowed"] else "Blocked")

    st.markdown("### Safety Checklist")
    dataframe_or_info(service.checklist(), "No checklist available.")
    st.markdown("### Runtime Flags")
    st.json(status)


def render_analytics() -> None:
    st.subheader("Analytics")
    if AnalyticsService is None:
        st.info("Analytics module not installed.")
        return

    service = AnalyticsService()
    summary = service.summary() if hasattr(service, "summary") else {}
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Scans", summary.get("Total Scans", 0))
    c2.metric("Paper Trades", summary.get("Paper Trades", 0))
    c3.metric("Profitable Trades", summary.get("Profitable Trades", 0))
    c4.metric("Win Rate", f'{summary.get("Win Rate %", 0)}%')
    c5.metric("Est. P/L", f'${summary.get("Estimated P/L USD", 0)}')

    if hasattr(service, "recent_paper_trades"):
        st.markdown("### Recent Paper Trades")
        dataframe_or_info(service.recent_paper_trades(), "No paper trades saved.")

    if hasattr(service, "recent_scans"):
        st.markdown("### Recent Scans")
        dataframe_or_info(service.recent_scans(), "No scan history saved.")


def render_registry() -> None:
    st.subheader("Registry")
    token_rows, dex_rows, pair_rows = [], [], []

    for chain_key, chain in SUPPORTED_CHAINS.items():
        for token in get_tokens_for_chain(chain_key):
            token_rows.append(
                {
                    "Chain": chain.name,
                    "Symbol": token.symbol,
                    "Name": token.name,
                    "Address": token.address,
                    "Decimals": token.decimals,
                    "CoinGecko ID": token.coingecko_id,
                }
            )
        for dex in get_dexes_for_chain(chain_key):
            dex_rows.append(
                {
                    "Chain": chain.name,
                    "DEX": dex.name,
                    "Type": dex.dex_type,
                    "Router": dex.router_address or "-",
                    "Notes": dex.notes,
                }
            )
        for pair in get_pairs_for_chain(chain_key):
            pair_rows.append(
                {
                    "Chain": chain.name,
                    "Pair": f"{pair.base_symbol}/{pair.quote_symbol}",
                    "Priority": pair.priority,
                }
            )

    st.markdown("### Tokens")
    dataframe_or_info(token_rows, "No tokens registered.")
    st.markdown("### DEXs")
    dataframe_or_info(dex_rows, "No DEXs registered.")
    st.markdown("### Pairs")
    dataframe_or_info(pair_rows, "No pairs registered.")


def render_roadmap() -> None:
    st.subheader("CryptoAI Roadmap")
    done = [
        "v0.1 — Project setup",
        "v0.2 — Multi-chain RPC",
        "v0.3 — Dashboard foundation",
        "v0.4 — Market data",
        "v0.5 — Connector framework and net estimates",
        "v0.6 — Paper trading simulation",
        "v0.7 — Historical storage and analytics",
        "v0.8 — RPC failover, quote cache, and system health",
        "v0.9 — Fast data layer and latency metrics",
        "v1.0 — Strategy engine",
        "v1.1 — Backtesting engine",
        "v1.2 — AI ranking engine",
        "v1.3 — Risk engine",
        "v1.4 — Portfolio engine",
        "v1.5 — Paper execution",
        "v1.6 — Scheduler",
        "v1.7 — Database-backed state",
        "v1.8 — Portfolio persistence",
        "v1.9 — Trading controls guard",
        "v2.0 — Event bus",
        "v2.1 — Real-time market data foundation",
        "v2.2 — Advanced opportunity engine",
        "v2.3 — Cloud paper autopilot",
        "v2.4 — Cleanup and deploy-ready dashboard",
    ]
    for item in done:
        st.write(f"✅ {item}")

    st.markdown("### Remaining before live trading")
    for item in [
        "v2.5 — Paper ledger with real balances across assets",
        "v2.6 — Slippage/gas/liquidity simulator",
        "v2.7 — Alerts and reports",
        "v2.8 — Month-long paper performance dashboard",
        "v3.0 — Manual-approved live trading prototype only after paper results prove an edge",
    ]:
        st.write(f"🔜 {item}")

    st.warning("Do not connect real funds until paper results are proven over time.")


PAGES = {
    "01 Chain Health": render_chain_health,
    "02 Live Prices": render_live_prices,
    "03 Real-Time Market Data": render_realtime,
    "04 DEX Quotes": render_dex_quotes,
    "05 Opportunity Engine": render_opportunity_engine,
    "06 Gross Opportunities": render_gross_opps,
    "07 Net Estimates": render_net_estimates,
    "08 Strategies": render_strategies,
    "09 AI Ranking": render_ai_ranking,
    "10 Risk": render_risk,
    "11 Portfolio": render_portfolio,
    "12 Paper Execution": render_paper_execution,
    "13 Paper Autopilot": render_autopilot,
    "14 Scheduler": render_scheduler,
    "15 Event Bus": render_event_bus,
    "16 Database": render_database,
    "17 Backtesting": render_backtesting,
    "18 Performance": render_performance,
    "19 System Health": render_system_health,
    "20 Trading Controls": render_trading_controls,
    "21 Analytics": render_analytics,
    "22 Registry": render_registry,
    "23 Roadmap": render_roadmap,
}


render_header()

with st.sidebar:
    st.header("CryptoAI")
    page = st.radio("Navigate", list(PAGES.keys()), index=0)
    st.divider()
    st.caption("Mode: paper trading only")
    if st.button("Clear Streamlit Cache"):
        st.cache_data.clear()
        st.rerun()

PAGES[page]()
