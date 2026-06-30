from __future__ import annotations

import pandas as pd
import streamlit as st

from app.dashboard.time_format import localize_timestamps
from app.realtime.market_data_service import RealtimeMarketDataService


def render_realtime_market_panel() -> None:
    service = RealtimeMarketDataService()

    st.caption("Fetches one public WebSocket trade tick. This is safe and read-only.")

    symbol = st.selectbox(
        "Symbol",
        ["ethusdt", "btcusdt", "solusdt", "bnbusdt"],
        index=0,
    )

    if st.button("Fetch One Live Tick"):
        snapshot = service.snapshot(symbol=symbol)
        c1, c2, c3 = st.columns(3)
        c1.metric("Connected", "Yes" if snapshot["connected"] else "No")
        c2.metric("Symbol", snapshot["symbol"])
        c3.metric("Price USD", snapshot["price_usd"] or "-")
        st.write(snapshot["message"])

    st.markdown("### Recent Stored Ticks")
    rows = service.recent_ticks()
    if rows:
        st.dataframe(pd.DataFrame(localize_timestamps(rows)), use_container_width=True)
    else:
        st.info("No stored real-time ticks yet.")
