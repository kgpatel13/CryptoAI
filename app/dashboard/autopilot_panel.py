from __future__ import annotations

import pandas as pd
import streamlit as st

from app.automation.paper_autopilot import PaperAutopilot


def render_autopilot_panel() -> None:
    st.caption("Runs one safe paper autopilot cycle from the dashboard.")

    enable_paper = st.checkbox("Enable paper execution", value=True)

    if st.button("Run Paper Autopilot Once"):
        result = PaperAutopilot(enable_paper_execution=enable_paper).run_once()

        c1, c2, c3 = st.columns(3)
        c1.metric("Status", result.get("status", "-"))
        c2.metric("Run ID", result.get("run_id", "-"))
        c3.metric("Latency ms", result.get("total_latency_ms", "-"))

        steps = result.get("steps", [])
        if steps:
            st.dataframe(pd.DataFrame(steps), use_container_width=True)

        st.json(result)

    st.warning("This panel is paper-only. It refuses to run if live trading is enabled.")
