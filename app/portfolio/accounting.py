from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

STABLE_USD_SYMBOLS = {"USD", "USDC", "USDT", "DAI"}


@dataclass(frozen=True)
class CanonicalPositionMath:
    pair: str
    base_symbol: str
    quote_symbol: str
    price_usd: Decimal
    quantity: Decimal
    notional_usd: Decimal


class PaperAccounting:
    """Canonical USD accounting for paper positions.

    DEX quote routes can be expressed as WETH/USDC or USDC/WETH.  A raw
    USDC/WETH quote is WETH per USDC, not USD per USDC.  Portfolio accounting
    must always store positions using USD-denominated price, quantity, and
    notional.  This utility keeps execution and portfolio math consistent.
    """

    @classmethod
    def canonical_entry(
        cls,
        *,
        pair: str,
        raw_price: Decimal,
        notional_usd: Decimal,
        prices: dict[str, Decimal] | None = None,
    ) -> CanonicalPositionMath:
        prices = prices or {}
        normalized_pair = cls.normalize_pair(pair)
        base, quote = cls.split_pair(normalized_pair)
        price_usd = cls.raw_pair_price_to_base_usd(
            pair=normalized_pair,
            raw_price=raw_price,
            prices=prices,
        )
        quantity = cls.quantity_from_notional(notional_usd=notional_usd, price_usd=price_usd)
        return CanonicalPositionMath(
            pair=normalized_pair,
            base_symbol=base,
            quote_symbol=quote,
            price_usd=price_usd,
            quantity=quantity,
            notional_usd=cls.quantize_usd(notional_usd),
        )

    @classmethod
    def raw_pair_price_to_base_usd(
        cls,
        *,
        pair: str,
        raw_price: Decimal,
        prices: dict[str, Decimal] | None = None,
    ) -> Decimal:
        prices = prices or {}
        base, quote = cls.split_pair(pair)
        raw_price = cls.decimal(raw_price)
        if raw_price <= 0:
            return Decimal("0")

        # Standard USD-quoted route, e.g. WETH/USDC = USD per WETH.
        if cls.is_stable(quote):
            return raw_price

        # Stable-token base routes such as USDC/WETH are inverse quotes. For
        # accounting, the base token's USD price is the safest canonical price.
        # This avoids treating WETH-per-USDC as USD-per-USDC.
        base_usd = cls.price_for_symbol(base, prices)
        if base_usd > 0 and cls.is_stable(base):
            return base_usd

        # Non-stable inverse route: convert quote units to USD if quote price exists.
        quote_usd = cls.price_for_symbol(quote, prices)
        if quote_usd > 0:
            return raw_price * quote_usd

        if base_usd > 0:
            return base_usd

        return raw_price

    @classmethod
    def mark_price_usd(
        cls,
        *,
        pair: str,
        prices: dict[str, Decimal] | None = None,
        fallback: Any = None,
    ) -> Decimal:
        prices = prices or {}
        base, quote = cls.split_pair(pair)
        pair_price = prices.get(cls.normalize_pair(pair))
        if pair_price is not None and cls.is_stable(quote):
            return cls.decimal(pair_price)
        base_usd = cls.price_for_symbol(base, prices)
        if base_usd > 0:
            return base_usd
        if fallback is not None:
            return cls.decimal(fallback)
        return Decimal("0")

    @classmethod
    def quantity_from_notional(cls, *, notional_usd: Decimal, price_usd: Decimal) -> Decimal:
        notional = cls.decimal(notional_usd)
        price = cls.decimal(price_usd)
        if notional <= 0 or price <= 0:
            return Decimal("0")
        return notional / price

    @classmethod
    def market_value_usd(cls, *, quantity: Decimal, price_usd: Decimal) -> Decimal:
        return cls.quantize_usd(cls.decimal(quantity) * cls.decimal(price_usd))

    @classmethod
    def realized_pnl_usd(cls, *, notional_usd: Decimal, exit_value_usd: Decimal) -> Decimal:
        return cls.quantize_usd(cls.decimal(exit_value_usd) - cls.decimal(notional_usd))

    @classmethod
    def reasonable_closed_pnl(
        cls,
        *,
        notional_usd: Decimal,
        stored_pnl: Decimal,
        estimated_edge_pct: Decimal | None = None,
    ) -> Decimal:
        notional = cls.decimal(notional_usd)
        pnl = cls.decimal(stored_pnl)
        if notional <= 0:
            return Decimal("0.0000")
        # Anything larger than the entire notional in one paper arbitrage round trip
        # is almost certainly a unit/accounting bug.
        if abs(pnl) <= notional:
            return cls.quantize_usd(pnl)
        edge = cls.decimal(estimated_edge_pct) if estimated_edge_pct is not None else Decimal("0")
        if edge > 0:
            return cls.quantize_usd(notional * edge / Decimal("100"))
        return Decimal("0.0000")

    @staticmethod
    def normalize_pair(pair: str) -> str:
        return str(pair or "-").strip().upper()

    @staticmethod
    def split_pair(pair: str) -> tuple[str, str]:
        normalized = str(pair or "-").strip().upper()
        if "/" in normalized:
            left, right = normalized.split("/", 1)
            return left.upper(), right.upper()
        return normalized.upper(), "USDC"

    @staticmethod
    def is_stable(symbol: str) -> bool:
        return str(symbol or "").upper() in STABLE_USD_SYMBOLS

    @classmethod
    def price_for_symbol(cls, symbol: str, prices: dict[str, Decimal]) -> Decimal:
        normalized = str(symbol or "").upper()
        if cls.is_stable(normalized):
            return Decimal("1")
        aliases = {
            "WETH": "ETH",
            "CBETH": "ETH",
            "WBTC": "BTC",
            "CBBTC": "BTC",
        }
        value = prices.get(normalized)
        if value is not None:
            return cls.decimal(value)
        alias = aliases.get(normalized)
        if alias and alias in prices:
            return cls.decimal(prices[alias])
        return Decimal("0")

    @staticmethod
    def decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def quantize_usd(value: Decimal) -> Decimal:
        return Decimal(value).quantize(Decimal("0.0001"))
