from __future__ import annotations

import pandas as pd
import streamlit as st

from app.dashboard.time_format import localize_timestamps
from app.execution.trading_controls_service import TradingControlsService


def render_trading_controls_panel() -> None:
    """Reusable trading controls panel for future dashboard refactor."""

    service = TradingControlsService()
    status = service.get_status()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Trading", "ON" if status["live_trading_enabled"] else "OFF")
    c2.metric("Paper Trading", "ON" if status["paper_trading_enabled"] else "OFF")
    c3.metric("Private Key", "Present" if status["private_key_configured"] else "Absent")
    c4.metric("Live Guard", "Allowed" if status["live_guard_allowed"] else "Blocked")

    st.markdown("### Safety Checklist")
    st.dataframe(pd.DataFrame(localize_timestamps(service.checklist())), use_container_width=True)

    st.markdown("### Runtime Flags")
    st.json(localize_timestamps(status))

    st.warning(
        "Live trading must remain blocked until scanner, backtesting, paper execution, "
        "risk controls, and wallet transaction code are reviewed together."
    )
