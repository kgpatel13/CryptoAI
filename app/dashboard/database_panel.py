from __future__ import annotations

import pandas as pd
import streamlit as st

from app.database.state_service import StateService


def render_database_panel() -> None:
    """Reusable database panel for future dashboard refactor."""
    service = StateService()
    summary = service.summary()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Events", summary.get("events", 0))
    c2.metric("Scheduler Runs", summary.get("scheduler_runs", 0))
    c3.metric("Paper Orders", summary.get("paper_orders", 0))
    c4.metric("Portfolio Snapshots", summary.get("portfolio_snapshots", 0))

    st.markdown("### Recent Portfolio Snapshots")
    rows = service.recent_portfolio_snapshots()
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No portfolio snapshots saved yet.")
