import streamlit as st
import pandas as pd

from app.blockchain.chains import SUPPORTED_CHAINS
from app.services.chain_health_service import ChainHealthService
from app.registry.tokens import get_tokens_for_chain
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain


st.set_page_config(
    page_title="CryptoAI Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 CryptoAI Quant Trading Dashboard")
st.caption("Multi-chain crypto research platform — scanner first, no wallet, no live trading yet.")


@st.cache_data(ttl=30)
def load_chain_health():
    service = ChainHealthService()
    return service.check_all_chains()


tab1, tab2, tab3, tab4 = st.tabs(
    ["🌐 Chain Health", "🪙 Assets", "🏦 DEX Registry", "📈 Roadmap"]
)

with tab1:
    st.subheader("Multi-Chain RPC Health")

    results = load_chain_health()

    rows = []
    for result in results:
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

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.info("This confirms our platform can read live blockchain data from multiple networks.")

with tab2:
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

with tab3:
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

with tab4:
    st.subheader("CryptoAI Roadmap")

    st.markdown(
        """
        ✅ M0 — Development environment  
        ✅ M1 — Multi-chain RPC connections  
        ✅ M2 — Token, DEX, and pair registry  
        🔜 M3 — Live quote engine  
        🔜 M4 — Opportunity scanner  
        🔜 M5 — AI ranking engine  
        🔜 M6 — Paper trading  
        🔜 M7 — Backtesting  
        🔜 M8 — Live trading controls  
        """
    )

    st.warning("Live trading will stay disabled until scanner, backtesting, and paper trading prove an edge.")