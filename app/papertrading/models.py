from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal


@dataclass(frozen=True)
class PaperTrade:
    timestamp_utc: str
    chain: str
    pair: str
    buy_dex: str
    sell_dex: str
    trade_size_usd: Decimal
    estimated_net_profit_usd: Decimal
    estimated_net_profit_pct: Decimal
    status: str
    reason: str

    @staticmethod
    def now(
        chain: str,
        pair: str,
        buy_dex: str,
        sell_dex: str,
        trade_size_usd: Decimal,
        estimated_net_profit_usd: Decimal,
        estimated_net_profit_pct: Decimal,
        status: str,
        reason: str,
    ) -> "PaperTrade":
        return PaperTrade(
            timestamp_utc=datetime.now(UTC).isoformat(timespec="seconds"),
            chain=chain,
            pair=pair,
            buy_dex=buy_dex,
            sell_dex=sell_dex,
            trade_size_usd=trade_size_usd,
            estimated_net_profit_usd=estimated_net_profit_usd,
            estimated_net_profit_pct=estimated_net_profit_pct,
            status=status,
            reason=reason,
        )
