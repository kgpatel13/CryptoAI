import streamlit as st
import pandas as pd

from app.blockchain.chains import SUPPORTED_CHAINS
from app.services.chain_health_service import ChainHealthService
from app.registry.tokens import get_tokens_for_chain
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain
from app.marketdata.market_service import MarketDataService
from app.quotes.quote_service import QuoteService
from app.services.system_health_service import SystemHealthService

try:
    from app.strategy.strategy_service import StrategyService
except Exception:
    StrategyService = None

try:
    from app.scanner.opportunity_scanner import OpportunityScanner
except Exception:
    OpportunityScanner = None

try:
    from app.scanner.net_opportunity_scanner import NetOpportunityScanner
except Exception:
    NetOpportunityScanner = None

try:
    from app.paper.paper_trading_service import PaperTradingService
except Exception:
    PaperTradingService = None

try:
    from app.analytics.analytics_service import AnalyticsService
except Exception:
    AnalyticsService = None


st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 CryptoAI Quant Trading Dashboard")
st.caption("Multi-chain crypto research platform — scanner first, no wallet, no live trading yet.")


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


def dataframe_or_info(rows, message: str):
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(message)


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(
    [
        "🌐 Chain Health",
        "💵 Live Prices",
        "🔁 DEX Quotes",
        "🚨 Gross Opps",
        "🧮 Net Estimates",
        "🧠 Strategies",
        "⚡ Performance",
        "💉 System Health",
        "🧪 Paper Trading",
        "📊 Analytics",
        "🪙 Assets",
        "📈 Roadmap",
    ]
)

with tab1:
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

with tab2:
    st.subheader("Live Market Prices")
    try:
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    except Exception as exc:
        st.error(f"Failed to load market prices: {exc}")

with tab3:
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
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

with tab4:
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
    dataframe_or_info(rows, "No gross opportunities detected right now.")

with tab5:
    st.subheader("Net Opportunity Estimates")
    rows = []
    for opp in load_net_estimates():
        d = opp.__dict__ if hasattr(opp, "__dict__") else {}
        rows.append({k: str(v) for k, v in d.items()})
    dataframe_or_info(rows, "Net opportunity engine is available when v0.5+ scanner classes are present.")
    st.warning("Still read-only. These estimates are not trade instructions.")

with tab6:
    st.subheader("Strategy Engine")
    st.caption("v1.0 adds standardized strategy signals. No live execution.")

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

    dataframe_or_info(rows, "No strategy signals available right now.")
    st.warning("READY_FOR_PAPER means simulation only. It does not mean execute real trades.")

with tab7:
    st.subheader("Performance Metrics")
    service = SystemHealthService()
    dataframe_or_info(service.get_metric_rows(), "Metrics will populate after quote/chain calls complete.")
    st.markdown("### Cache Stats")
    st.json(service.get_cache_stats())

with tab8:
    st.subheader("System Health & Latency Budget")
    service = SystemHealthService()
    budget_rows = []
    for item in service.get_latency_budget():
        budget_rows.append(
            {
                "Stage": item.stage,
                "Target ms": item.target_ms,
                "Current ms": item.current_ms,
                "Status": item.status,
            }
        )
    st.dataframe(pd.DataFrame(budget_rows), use_container_width=True)
    st.info("For future autopilot trading, signal → decision → execution must stay inside a strict latency budget.")

with tab9:
    st.subheader("Paper Trading")
    if PaperTradingService is None:
        st.info("Paper trading module not found in this install.")
    else:
        try:
            service = PaperTradingService()
            result = service.run_once() if hasattr(service, "run_once") else None
            st.write(result)
        except Exception as exc:
            st.error(f"Paper trading failed: {exc}")

with tab10:
    st.subheader("Analytics")

    if AnalyticsService is None:
        st.info("Analytics module not found in this install.")
    else:
        try:
            service = AnalyticsService()
            summary = service.summary() if hasattr(service, "summary") else {}

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Scans", summary.get("Total Scans", 0))
            c2.metric("Paper Trades", summary.get("Paper Trades", 0))
            c3.metric("Profitable Trades", summary.get("Profitable Trades", 0))
            c4.metric("Win Rate", f'{summary.get("Win Rate %", 0)}%')
            c5.metric("Est. P/L", f'${summary.get("Estimated P/L USD", 0)}')

            st.caption(f'Last updated: {summary.get("Last Updated", "-")}')

            st.markdown("### Recent Paper Trades")
            paper_rows = service.recent_paper_trades() if hasattr(service, "recent_paper_trades") else []
            dataframe_or_info(paper_rows, "No paper trades saved yet.")

            st.markdown("### Recent Scans")
            scan_rows = service.recent_scans() if hasattr(service, "recent_scans") else []
            dataframe_or_info(scan_rows, "No scan history saved yet.")

            st.markdown("### Live Scanner Snapshot")
            live_rows = service.live_scanner_snapshot() if hasattr(service, "live_scanner_snapshot") else []
            dataframe_or_info(live_rows, "No live scanner opportunities detected right now.")

        except Exception as exc:
            st.error(f"Analytics failed: {exc}")

with tab11:
    st.subheader("Assets, DEXs, and Pairs")
    token_rows = []
    dex_rows = []
    pair_rows = []

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
    st.dataframe(pd.DataFrame(token_rows), use_container_width=True)
    st.markdown("### DEXs")
    st.dataframe(pd.DataFrame(dex_rows), use_container_width=True)
    st.markdown("### Pairs")
    st.dataframe(pd.DataFrame(pair_rows), use_container_width=True)

with tab12:
    st.subheader("CryptoAI Roadmap")
    st.markdown(
        """
        ✅ v0.1 — Project setup  
        ✅ v0.2 — Multi-chain RPC  
        ✅ v0.3 — Dashboard foundation  
        ✅ v0.4 — Market data  
        ✅ v0.5 — Connector framework and net estimates  
        ✅ v0.6 — Paper trading simulation  
        ✅ v0.7 — Historical storage and analytics  
        ✅ v0.8 — RPC failover, quote cache, and system health  
        ✅ v0.9 — Fast data layer and latency metrics  
        ✅ v0.9.1 — Analytics and provider compatibility hotfix  
        ✅ v0.9.2 — Analytics dashboard UI restore  
        🔄 v1.0 — Strategy engine framework  
        🔜 v1.1 — Backtesting engine  
        🔜 v1.2 — AI ranking engine  
        🔜 v2.0 — Live trading controls with strict risk limits  
        """
    )
    st.warning("Live trading remains disabled until scanner, backtesting, and paper trading prove an edge.")
