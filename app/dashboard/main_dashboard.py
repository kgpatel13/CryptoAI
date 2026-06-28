import streamlit as st
import pandas as pd

from app.blockchain.chains import SUPPORTED_CHAINS
from app.services.chain_health_service import ChainHealthService
from app.registry.tokens import get_tokens_for_chain
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain
from app.marketdata.market_service import MarketDataService
from app.quotes.quote_service import QuoteService
from app.scanner.opportunity_scanner import OpportunityScanner


st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 CryptoAI Quant Trading Dashboard")
st.caption(
    "Multi-chain crypto research platform — scanner first, no wallet, no live trading yet."
)


@st.cache_data(ttl=30)
def load_chain_health():
    return ChainHealthService().check_all_chains()


@st.cache_data(ttl=60)
def load_market_prices():
    return MarketDataService().get_registered_asset_prices()


@st.cache_data(ttl=20)
def load_dex_quotes():
    return QuoteService().get_base_quotes()


@st.cache_data(ttl=20)
def load_gross_opportunities():
    return OpportunityScanner().scan_base_gross_opportunities()


@st.cache_data(ttl=20)
def load_net_opportunities():
    return OpportunityScanner().scan_base_net_estimates()


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "🌐 Chain Health",
        "💵 Live Prices",
        "🔁 DEX Quotes",
        "🚨 Gross Opportunities",
        "🧮 Net Estimates",
        "🪙 Assets",
        "🏦 DEX Registry",
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
                "Gas Gwei": float(result.gas_price_gwei)
                if result.gas_price_gwei
                else None,
                "Error": result.error or "",
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.info("This confirms CryptoAI can read live blockchain data from multiple networks.")


with tab2:
    st.subheader("Live Market Prices")

    try:
        price_rows = []

        for price in load_market_prices():
            price_rows.append(
                {
                    "Asset": price.name,
                    "Symbol": price.symbol,
                    "CoinGecko ID": price.coingecko_id,
                    "USD Price": float(price.usd_price)
                    if price.usd_price
                    else None,
                    "24h Change %": float(price.change_24h_pct)
                    if price.change_24h_pct
                    else None,
                    "24h Volume": float(price.volume_24h)
                    if price.volume_24h
                    else None,
                    "Market Cap": float(price.market_cap)
                    if price.market_cap
                    else None,
                }
            )

        st.dataframe(pd.DataFrame(price_rows), use_container_width=True)
        st.success("Live market data loaded successfully.")

    except Exception as exc:
        st.error(f"Failed to load market prices: {exc}")


with tab3:
    st.subheader("Live DEX Quotes")

    try:
        quote_rows = []

        for quote in load_dex_quotes():
            quote_rows.append(
                {
                    "Chain": quote.chain,
                    "DEX": quote.dex,
                    "Token In": quote.token_in,
                    "Token Out": quote.token_out,
                    "Amount In": float(quote.amount_in),
                    "Amount Out": float(quote.amount_out)
                    if quote.amount_out
                    else None,
                    "Price": float(quote.price) if quote.price else None,
                    "Error": quote.error or "",
                }
            )

        st.dataframe(pd.DataFrame(quote_rows), use_container_width=True)
        st.info("These are live on-chain quotes through the new Quote Manager framework.")

    except Exception as exc:
        st.error(f"Failed to load DEX quotes: {exc}")


with tab4:
    st.subheader("Gross Opportunity Scanner")

    try:
        rows = []

        for opp in load_gross_opportunities():
            rows.append(
                {
                    "Chain": opp.chain,
                    "Pair": opp.pair,
                    "Buy DEX": opp.best_buy_dex,
                    "Sell DEX": opp.best_sell_dex,
                    "Buy Price": float(opp.buy_price),
                    "Sell Price": float(opp.sell_price),
                    "Gross Spread %": float(opp.gross_spread_pct),
                }
            )

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.warning(
            "Gross spread only. This does NOT include gas, slippage, MEV, DEX fees, or execution risk yet."
        )

    except Exception as exc:
        st.error(f"Failed to scan gross opportunities: {exc}")


with tab5:
    st.subheader("Estimated Net Opportunity Scanner")

    try:
        rows = []

        for opp in load_net_opportunities():
            rows.append(
                {
                    "Chain": opp.chain,
                    "Pair": opp.pair,
                    "Buy DEX": opp.buy_dex,
                    "Sell DEX": opp.sell_dex,
                    "Notional USD": float(opp.notional_usd),
                    "Gross Spread %": float(opp.gross_spread_pct),
                    "Gross Profit USD": float(opp.estimated_gross_profit_usd),
                    "Estimated Costs USD": float(opp.estimated_total_cost_usd),
                    "Estimated Net USD": float(opp.estimated_net_profit_usd),
                    "Estimated Net %": float(opp.estimated_net_profit_pct),
                    "Decision": opp.decision,
                    "Reason": opp.reason,
                }
            )

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.warning(
            "Research estimate only. Costs use conservative placeholders; no live execution signal yet."
        )

    except Exception as exc:
        st.error(f"Failed to scan net opportunities: {exc}")


with tab6:
    st.subheader("Token Registry")

    token_rows = []
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
                    "Coingecko ID": token.coingecko_id,
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

    st.markdown("### Supported Tokens")
    st.dataframe(pd.DataFrame(token_rows), use_container_width=True)

    st.markdown("### Supported Trading Pairs")
    st.dataframe(pd.DataFrame(pair_rows), use_container_width=True)


with tab7:
    st.subheader("DEX Registry")

    dex_rows = []

    for chain_key, chain in SUPPORTED_CHAINS.items():
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

    st.dataframe(pd.DataFrame(dex_rows), use_container_width=True)


with tab8:
    st.subheader("CryptoAI Roadmap")

    st.markdown(
        """
        ✅ M0 — Development environment  
        ✅ M1 — Multi-chain RPC connections  
        ✅ M2 — Token, DEX, and pair registry  
        ✅ M3 — Streamlit dashboard foundation  
        ✅ M4 — Live market data engine  
        ✅ M5 — Live DEX quote engine  
        ✅ M6 — Gross opportunity scanner  
        🔄 v0.5 — Connector framework + estimated net opportunity scanner  
        🔜 v0.6 — Real gas/slippage/risk engine  
        🔜 v0.7 — AI ranking engine  
        🔜 v0.8 — Paper trading  
        🔜 v0.9 — Backtesting  
        🔜 v1.0 — Live trading controls  
        """
    )

    st.warning(
        "Live trading remains disabled until scanner, backtesting, and paper trading prove an edge."
    )
