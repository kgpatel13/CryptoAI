from __future__ import annotations

import pandas as pd
import streamlit as st

from app.dashboard.time_format import localize_timestamps
from app.events.event_service import EventBusService


def render_event_bus_panel() -> None:
    service = EventBusService()

    if st.button("Publish Test Event"):
        service.publish_system_event("dashboard", "Manual test event from dashboard.")

    rows = service.recent_events(limit=100)

    if not rows:
        st.info("No in-memory events yet. Run scheduler once to publish events.")
        return

    display_rows = []
    for row in rows:
        display_rows.append(
            {
                "Time": row["created_at"],
                "Type": row["event_type"],
                "Source": row["source"],
                "Event ID": row["event_id"],
                "Payload": str(row["payload"]),
            }
        )

    st.dataframe(pd.DataFrame(localize_timestamps(display_rows)), use_container_width=True)
