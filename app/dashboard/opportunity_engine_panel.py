from __future__ import annotations

import pandas as pd
import streamlit as st

from app.opportunities.opportunity_service import OpportunityService


def render_opportunity_engine_panel() -> None:
    service = OpportunityService()

    if st.button("Run Advanced Opportunity Scan"):
        candidates = service.scan()

        rows = []
        for c in candidates:
            rows.append(
                {
                    "ID": c.opportunity_id,
                    "Type": c.opportunity_type.value,
                    "Chain": c.chain,
                    "Pair": c.pair,
                    "Buy Source": c.source_buy,
                    "Sell Source": c.source_sell,
                    "Buy Price": str(c.buy_price) if c.buy_price is not None else "-",
                    "Sell Price": str(c.sell_price) if c.sell_price is not None else "-",
                    "Gross Spread %": str(c.gross_spread_pct) if c.gross_spread_pct is not None else "-",
                    "Cost Buffer %": str(c.estimated_cost_pct),
                    "Net Edge %": str(c.estimated_net_edge_pct) if c.estimated_net_edge_pct is not None else "-",
                    "Latency": c.latency_sensitivity,
                    "Liquidity": c.liquidity_status,
                    "Status": c.status.value,
                    "Reason": c.reason,
                }
            )

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("No opportunity candidates found right now.")

    st.warning("This panel is read-only. It does not execute trades.")
