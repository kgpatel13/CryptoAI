from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.portfolio.accounting import PaperAccounting


@dataclass(frozen=True)
class PortfolioRiskDecision:
    approved: bool
    notional_usd: Decimal
    reason: str


@dataclass(frozen=True)
class PositionMonitorResult:
    monitored_positions: int
    closed_positions: int
    realized_pnl_usd: Decimal
    events: list[dict[str, Any]]


class PortfolioRiskService:
    """Stateful paper-portfolio risk controls and v3.4 position lifecycle.

    The service remains file-backed and deterministic so it works in GitHub Actions,
    Streamlit Cloud, and local paper trading without external infrastructure.
    """

    def __init__(self, state_path: str | Path | None = None) -> None:
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.state_path = Path(state_path) if state_path else self.data_dir / "paper_portfolio_state.json"

        self.initial_cash_usd = self._env_decimal("CRYPTOAI_PAPER_INITIAL_CASH_USD", "10000")
        self.max_trade_notional_usd = self._env_decimal("CRYPTOAI_MAX_PAPER_NOTIONAL_USD", "250")
        self.min_trade_notional_usd = self._env_decimal("CRYPTOAI_MIN_PAPER_NOTIONAL_USD", "25")
        self.risk_per_trade_pct = self._env_decimal("CRYPTOAI_PAPER_RISK_PER_TRADE_PCT", "1.00")
        self.max_cash_usage_pct = self._env_decimal("CRYPTOAI_PAPER_MAX_CASH_USAGE_PCT", "10.00")
        self.max_token_exposure_pct = self._env_decimal("CRYPTOAI_MAX_TOKEN_EXPOSURE_PCT", "25.00")
        self.max_chain_exposure_pct = self._env_decimal("CRYPTOAI_MAX_CHAIN_EXPOSURE_PCT", "50.00")
        self.max_open_positions = self._env_int("CRYPTOAI_MAX_OPEN_POSITIONS", 8)
        self.max_daily_trades = self._env_int("CRYPTOAI_MAX_DAILY_PAPER_TRADES", 8)
        self.cooldown_seconds = self._env_int("CRYPTOAI_TRADE_COOLDOWN_SECONDS", 900)
        self.duplicate_window_seconds = self._env_int("CRYPTOAI_DUPLICATE_SIGNAL_WINDOW_SECONDS", 900)
        self.block_same_pair_open_position = self._env_bool("CRYPTOAI_BLOCK_SAME_PAIR_OPEN_POSITION", True)
        self.max_daily_loss_usd = self._env_decimal("CRYPTOAI_MAX_DAILY_LOSS_USD", "0")

        self.take_profit_pct = self._env_decimal("CRYPTOAI_PAPER_TAKE_PROFIT_PCT", "0.50")
        self.stop_loss_pct = self._env_decimal("CRYPTOAI_PAPER_STOP_LOSS_PCT", "0.35")
        self.max_hold_seconds = self._env_int("CRYPTOAI_PAPER_MAX_HOLD_SECONDS", 3600)

    def assess(self, *, chain: str, pair: str, side: str, requested_notional_usd: Decimal, expected_edge_pct: Decimal | None = None, now: str | None = None) -> PortfolioRiskDecision:
        timestamp = now or self._utc_now()
        state = self.load_state()
        self._reset_daily_counters_if_needed(state, timestamp)

        if requested_notional_usd <= 0:
            return PortfolioRiskDecision(False, Decimal("0"), "Portfolio risk rejected: requested notional is zero.")

        if self.max_daily_loss_usd > 0 and self._decimal(state.get("daily_realized_pnl_usd", "0")) <= -self.max_daily_loss_usd:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: daily loss guard reached ${self.max_daily_loss_usd}.")

        if int(state.get("daily_filled_trades", 0)) >= self.max_daily_trades:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: max daily paper trades reached ({self.max_daily_trades}).")

        open_positions = self._open_positions(state)
        if len(open_positions) >= self.max_open_positions:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: max open positions reached ({self.max_open_positions}).")

        normalized_pair = self._normalize_pair(pair)
        normalized_side = side.upper()

        existing = self._same_open_position(open_positions, normalized_pair, normalized_side)
        if existing is not None and self.block_same_pair_open_position:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: existing open {normalized_side} position for {normalized_pair}; reuse/monitor the open position instead of adding duplicate exposure.")

        duplicate = self._recent_duplicate(open_positions, normalized_pair, normalized_side, timestamp)
        if duplicate is not None:
            age = self._age_seconds(duplicate.get("opened_at"), timestamp)
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: duplicate {normalized_side} signal for {normalized_pair} within {self.duplicate_window_seconds}s window (age {age}s).")

        cooldown = self._cooldown_active(state, normalized_pair, normalized_side, timestamp)
        if cooldown is not None:
            age = self._age_seconds(cooldown, timestamp)
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: cooldown active for {normalized_pair} {normalized_side} ({age}s/{self.cooldown_seconds}s).")

        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        if cash < self.min_trade_notional_usd:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: cash ${cash} below minimum trade notional ${self.min_trade_notional_usd}.")

        portfolio_value = self._portfolio_value(state)
        dynamic_by_risk = portfolio_value * self.risk_per_trade_pct / Decimal("100")
        dynamic_by_cash = cash * self.max_cash_usage_pct / Decimal("100")
        notional = min(requested_notional_usd, self.max_trade_notional_usd, dynamic_by_risk, dynamic_by_cash, cash)
        notional = self._quantize_usd(notional)

        if notional < self.min_trade_notional_usd:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: computed notional ${notional} below minimum ${self.min_trade_notional_usd}.")

        base_symbol, _quote_symbol = self._split_pair(normalized_pair)
        token_exposure_after = self._exposure_for(open_positions, token=base_symbol) + notional
        chain_exposure_after = self._exposure_for(open_positions, chain=chain) + notional
        max_token_exposure = portfolio_value * self.max_token_exposure_pct / Decimal("100")
        max_chain_exposure = portfolio_value * self.max_chain_exposure_pct / Decimal("100")

        if token_exposure_after > max_token_exposure:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: {base_symbol} exposure ${self._quantize_usd(token_exposure_after)} would exceed limit ${self._quantize_usd(max_token_exposure)}.")

        if chain_exposure_after > max_chain_exposure:
            return PortfolioRiskDecision(False, Decimal("0"), f"Portfolio risk rejected: {chain} exposure ${self._quantize_usd(chain_exposure_after)} would exceed limit ${self._quantize_usd(max_chain_exposure)}.")

        return PortfolioRiskDecision(True, notional, f"Portfolio risk approved: notional ${notional}, cash ${cash}, open positions {len(open_positions)}/{self.max_open_positions}.")

    def record_filled_order(self, *, order_id: str, timestamp: str, strategy_name: str, chain: str, pair: str, side: str, notional_usd: Decimal, fill_price_usd: Decimal, quantity: Decimal, estimated_edge_pct: Decimal | None = None, slippage_bps: Decimal | None = None, latency_ms: int | None = None, execution_quality: str | None = None) -> dict[str, Any]:
        state = self.load_state()
        self._reset_daily_counters_if_needed(state, timestamp)

        normalized_pair = self._normalize_pair(pair)
        base_symbol, quote_symbol = self._split_pair(normalized_pair)
        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        canonical = PaperAccounting.canonical_entry(pair=normalized_pair, raw_price=fill_price_usd, notional_usd=notional_usd)
        fill_price_usd = canonical.price_usd
        quantity = canonical.quantity
        state["cash_usd"] = str(self._quantize_usd(max(Decimal("0"), cash - canonical.notional_usd)))
        state["daily_filled_trades"] = int(state.get("daily_filled_trades", 0)) + 1
        state["updated_at"] = timestamp
        state.setdefault("positions", []).append({
            "position_id": order_id,
            "order_id": order_id,
            "strategy_name": strategy_name,
            "chain": chain,
            "pair": normalized_pair,
            "side": side.upper(),
            "base_symbol": canonical.base_symbol,
            "quote_symbol": canonical.quote_symbol,
            "quantity": str(canonical.quantity),
            "entry_price_usd": str(canonical.price_usd),
            "current_price_usd": str(canonical.price_usd),
            "notional_usd": str(canonical.notional_usd),
            "estimated_edge_pct": str(estimated_edge_pct) if estimated_edge_pct is not None else None,
            "slippage_bps": str(slippage_bps) if slippage_bps is not None else None,
            "latency_ms": latency_ms,
            "execution_quality": execution_quality,
            "take_profit_price_usd": str(self._exit_price(fill_price_usd, side, self.take_profit_pct, True)),
            "stop_loss_price_usd": str(self._exit_price(fill_price_usd, side, self.stop_loss_pct, False)),
            "max_hold_seconds": self.max_hold_seconds,
            "status": "OPEN",
            "lifecycle_status": "MONITORING",
            "opened_at": timestamp,
            "updated_at": timestamp,
        })
        state.setdefault("signal_history", []).append({
            "pair": normalized_pair,
            "side": side.upper(),
            "chain": chain,
            "timestamp": timestamp,
            "order_id": order_id,
            "status": "FILLED",
        })
        state["signal_history"] = state["signal_history"][-500:]
        self.save_state(state)
        return state

    def monitor_positions(self, *, prices: dict[str, Decimal] | None = None, now: str | None = None) -> PositionMonitorResult:
        timestamp = now or self._utc_now()
        prices = prices or {}
        state = self.load_state()
        self._reset_daily_counters_if_needed(state, timestamp)
        events: list[dict[str, Any]] = []
        closed = 0
        realized = Decimal("0")

        for pos in state.get("positions", []):
            if str(pos.get("status", "OPEN")).upper() != "OPEN":
                continue
            pair = str(pos.get("pair", "-/USDC"))
            base_symbol, _quote_symbol = self._split_pair(pair)
            current_price = PaperAccounting.mark_price_usd(pair=pair, prices=prices, fallback=pos.get("current_price_usd") or pos.get("entry_price_usd"))
            if current_price <= 0:
                continue
            pos["current_price_usd"] = str(current_price)
            pos["updated_at"] = timestamp
            pos["lifecycle_status"] = "MONITORING"

            exit_reason = self._exit_reason(pos, current_price, timestamp)
            if exit_reason is None:
                continue

            pnl = self._close_position(state, pos, current_price, timestamp, exit_reason)
            realized += pnl
            closed += 1
            events.append({"timestamp": timestamp, "position_id": pos.get("position_id"), "pair": pair, "exit_reason": exit_reason, "realized_pnl_usd": str(pnl)})

        if closed:
            state["daily_realized_pnl_usd"] = str(self._decimal(state.get("daily_realized_pnl_usd", "0")) + realized)
            state["realized_pnl_usd"] = str(self._decimal(state.get("realized_pnl_usd", "0")) + realized)
            state["updated_at"] = timestamp
            self.save_state(state)
        else:
            self.save_state(state)
        return PositionMonitorResult(len(self._open_positions(state)) + closed, closed, realized, events)

    def summary(self) -> dict[str, Any]:
        state = self.load_state()
        open_positions = self._open_positions(state)
        closed_positions = [p for p in state.get("positions", []) if str(p.get("status", "")).upper() == "CLOSED"]
        exposure_by_chain: dict[str, str] = {}
        exposure_by_token: dict[str, str] = {}
        unrealized = Decimal("0")
        for pos in open_positions:
            notional = self._decimal(pos.get("notional_usd", "0"))
            chain = str(pos.get("chain", "-"))
            token = str(pos.get("base_symbol") or self._split_pair(str(pos.get("pair", "-/USDC")))[0])
            exposure_by_chain[chain] = str(self._decimal(exposure_by_chain.get(chain, "0")) + notional)
            exposure_by_token[token] = str(self._decimal(exposure_by_token.get(token, "0")) + notional)
            unrealized += self._unrealized_pnl(pos)
        return {
            "cash_usd": state.get("cash_usd", str(self.initial_cash_usd)),
            "initial_cash_usd": state.get("initial_cash_usd", str(self.initial_cash_usd)),
            "open_positions": len(open_positions),
            "closed_positions": len(closed_positions),
            "daily_filled_trades": state.get("daily_filled_trades", 0),
            "daily_realized_pnl_usd": state.get("daily_realized_pnl_usd", "0"),
            "realized_pnl_usd": state.get("realized_pnl_usd", "0"),
            "unrealized_pnl_usd": str(self._quantize_usd(unrealized)),
            "exposure_by_chain": exposure_by_chain,
            "exposure_by_token": exposure_by_token,
            "limits": {
                "max_open_positions": self.max_open_positions,
                "max_daily_trades": self.max_daily_trades,
                "trade_cooldown_seconds": self.cooldown_seconds,
                "duplicate_signal_window_seconds": self.duplicate_window_seconds,
                "block_same_pair_open_position": self.block_same_pair_open_position,
                "max_trade_notional_usd": str(self.max_trade_notional_usd),
                "risk_per_trade_pct": str(self.risk_per_trade_pct),
                "max_cash_usage_pct": str(self.max_cash_usage_pct),
                "take_profit_pct": str(self.take_profit_pct),
                "stop_loss_pct": str(self.stop_loss_pct),
                "max_hold_seconds": self.max_hold_seconds,
            },
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
        }

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            state = self._initial_state()
            self.save_state(state)
            return state
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8", errors="replace"))
            if not isinstance(raw, dict):
                raise ValueError("state is not an object")
            upgraded = self._upgrade_state(raw)
            if upgraded != raw or str(upgraded.get("version")) == "3.4.1":
                self.save_state(upgraded)
            return upgraded
        except Exception:
            state = self._initial_state()
            self.save_state(state)
            return state

    def save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    def _initial_state(self) -> dict[str, Any]:
        now = self._utc_now()
        return {
            "version": "3.4.1",
            "portfolio_name": "CryptoAI Paper Portfolio",
            "initial_cash_usd": str(self.initial_cash_usd),
            "cash_usd": str(self.initial_cash_usd),
            "daily_date": now[:10],
            "daily_filled_trades": 0,
            "daily_realized_pnl_usd": "0",
            "realized_pnl_usd": "0",
            "positions": [],
            "signal_history": [],
            "created_at": now,
            "updated_at": now,
        }

    def _upgrade_state(self, state: dict[str, Any]) -> dict[str, Any]:
        original_version = str(state.get("version", ""))
        state["version"] = "3.4.1"
        state.setdefault("portfolio_name", "CryptoAI Paper Portfolio")
        state.setdefault("initial_cash_usd", str(self.initial_cash_usd))
        state.setdefault("cash_usd", str(self.initial_cash_usd))
        state.setdefault("daily_date", self._utc_now()[:10])
        state.setdefault("daily_filled_trades", 0)
        state.setdefault("daily_realized_pnl_usd", "0")
        state.setdefault("realized_pnl_usd", "0")
        state.setdefault("positions", [])
        state.setdefault("signal_history", [])
        state.setdefault("created_at", self._utc_now())
        state.setdefault("updated_at", state.get("created_at"))
        for pos in state.get("positions", []):
            self._normalize_position_accounting(pos)
            if str(pos.get("status", "OPEN")).upper() == "OPEN":
                pos.setdefault("lifecycle_status", "MONITORING")
                entry = self._decimal(pos.get("entry_price_usd", "0"))
                side = str(pos.get("side", "BUY"))
                pos.setdefault("take_profit_price_usd", str(self._exit_price(entry, side, self.take_profit_pct, True)))
                pos.setdefault("stop_loss_price_usd", str(self._exit_price(entry, side, self.stop_loss_pct, False)))
                pos.setdefault("max_hold_seconds", self.max_hold_seconds)
        if original_version != "3.4.1" or self._state_has_accounting_anomaly(state):
            self._rebuild_cash_from_positions(state)
        return state

    def _reset_daily_counters_if_needed(self, state: dict[str, Any], timestamp: str) -> None:
        today = timestamp[:10]
        if state.get("daily_date") != today:
            state["daily_date"] = today
            state["daily_filled_trades"] = 0
            state["daily_realized_pnl_usd"] = "0"
            state["updated_at"] = timestamp

    def _close_position(self, state: dict[str, Any], pos: dict[str, Any], exit_price: Decimal, timestamp: str, reason: str) -> Decimal:
        self._normalize_position_accounting(pos)
        qty = self._decimal(pos.get("quantity", "0"))
        notional = self._decimal(pos.get("notional_usd", "0"))
        exit_value = PaperAccounting.market_value_usd(quantity=qty, price_usd=exit_price)
        pnl = PaperAccounting.realized_pnl_usd(notional_usd=notional, exit_value_usd=exit_value)
        state["cash_usd"] = str(self._quantize_usd(self._decimal(state.get("cash_usd", "0")) + exit_value))
        pos["status"] = "CLOSED"
        pos["lifecycle_status"] = "CLOSED"
        pos["exit_price_usd"] = str(exit_price)
        pos["exit_value_usd"] = str(exit_value)
        pos["realized_pnl_usd"] = str(pnl)
        pos["closed_at"] = timestamp
        pos["exit_reason"] = reason
        pos["updated_at"] = timestamp
        return pnl

    def _exit_reason(self, pos: dict[str, Any], current_price: Decimal, timestamp: str) -> str | None:
        side = str(pos.get("side", "BUY")).upper()
        take_profit = self._decimal(pos.get("take_profit_price_usd", "0"))
        stop_loss = self._decimal(pos.get("stop_loss_price_usd", "0"))
        if side == "BUY":
            if take_profit > 0 and current_price >= take_profit:
                return "TAKE_PROFIT"
            if stop_loss > 0 and current_price <= stop_loss:
                return "STOP_LOSS"
        age = self._age_seconds(pos.get("opened_at"), timestamp)
        if age >= int(pos.get("max_hold_seconds", self.max_hold_seconds)):
            return "MAX_HOLD_TIME"
        return None

    def _unrealized_pnl(self, pos: dict[str, Any]) -> Decimal:
        qty = self._decimal(pos.get("quantity", "0"))
        current = self._decimal(pos.get("current_price_usd", pos.get("entry_price_usd", "0")))
        notional = self._decimal(pos.get("notional_usd", "0"))
        return PaperAccounting.realized_pnl_usd(notional_usd=notional, exit_value_usd=PaperAccounting.market_value_usd(quantity=qty, price_usd=current))

    def _portfolio_value(self, state: dict[str, Any]) -> Decimal:
        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        open_notional = sum((self._decimal(pos.get("notional_usd", "0")) for pos in self._open_positions(state)), Decimal("0"))
        return max(self.initial_cash_usd, cash + open_notional)

    def _normalize_position_accounting(self, pos: dict[str, Any]) -> None:
        pair = self._normalize_pair(str(pos.get("pair", "-/USDC")))
        base_symbol, quote_symbol = self._split_pair(pair)
        notional = self._decimal(pos.get("notional_usd", "0"))
        entry = self._decimal(pos.get("entry_price_usd", "0"))
        quantity = self._decimal(pos.get("quantity", "0"))

        # Legacy v3.4 inverse-pair positions could store quote-token price
        # and enormous quantity (for example USDC/WETH at 0.00063). Convert
        # all positions to USD price per base token and quantity = notional / USD price.
        if not PaperAccounting.is_stable(quote_symbol):
            canonical_price = PaperAccounting.price_for_symbol(base_symbol, {})
            if canonical_price <= 0 and PaperAccounting.is_stable(base_symbol):
                canonical_price = Decimal("1")
            if canonical_price > 0 and (entry <= Decimal("0.01") or quantity * canonical_price > notional * Decimal("5")):
                entry = canonical_price
                quantity = PaperAccounting.quantity_from_notional(notional_usd=notional, price_usd=entry)
                pos["entry_price_usd"] = str(entry)
                pos["current_price_usd"] = str(entry)
                pos["quantity"] = str(quantity)

        pos["pair"] = pair
        pos["base_symbol"] = base_symbol
        pos["quote_symbol"] = quote_symbol

    def _state_has_accounting_anomaly(self, state: dict[str, Any]) -> bool:
        initial = self._decimal(state.get("initial_cash_usd", self.initial_cash_usd))
        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        realized = self._decimal(state.get("realized_pnl_usd", "0"))
        if initial > 0 and (cash > initial * Decimal("5") or cash < Decimal("0")):
            return True
        total_traded = sum((self._decimal(p.get("notional_usd", "0")) for p in state.get("positions", [])), Decimal("0"))
        if total_traded > 0 and abs(realized) > total_traded:
            return True
        return False

    def _rebuild_cash_from_positions(self, state: dict[str, Any]) -> None:
        initial = self._decimal(state.get("initial_cash_usd", self.initial_cash_usd))
        cash = initial
        realized_total = Decimal("0")
        daily_realized = Decimal("0")
        daily_date = str(state.get("daily_date", self._utc_now()[:10]))
        for pos in state.get("positions", []):
            self._normalize_position_accounting(pos)
            notional = self._decimal(pos.get("notional_usd", "0"))
            status = str(pos.get("status", "OPEN")).upper()
            cash -= notional
            if status == "OPEN":
                continue
            stored_pnl = self._decimal(pos.get("realized_pnl_usd", "0"))
            edge = self._decimal(pos.get("estimated_edge_pct", "0"))
            pnl = PaperAccounting.reasonable_closed_pnl(notional_usd=notional, stored_pnl=stored_pnl, estimated_edge_pct=edge)
            exit_value = self._quantize_usd(notional + pnl)
            pos["realized_pnl_usd"] = str(pnl)
            pos["exit_value_usd"] = str(exit_value)
            cash += exit_value
            realized_total += pnl
            if str(pos.get("closed_at", ""))[:10] == daily_date:
                daily_realized += pnl
        state["cash_usd"] = str(self._quantize_usd(max(Decimal("0"), cash)))
        state["realized_pnl_usd"] = str(self._quantize_usd(realized_total))
        state["daily_realized_pnl_usd"] = str(self._quantize_usd(daily_realized))
        state["updated_at"] = self._utc_now()

    @staticmethod
    def _open_positions(state: dict[str, Any]) -> list[dict[str, Any]]:
        return [p for p in state.get("positions", []) if str(p.get("status", "OPEN")).upper() == "OPEN"]

    @staticmethod
    def _same_open_position(open_positions: list[dict[str, Any]], pair: str, side: str) -> dict[str, Any] | None:
        for pos in reversed(open_positions):
            if str(pos.get("pair")) == pair and str(pos.get("side", "BUY")).upper() == side:
                return pos
        return None

    def _recent_duplicate(self, open_positions: list[dict[str, Any]], pair: str, side: str, now: str) -> dict[str, Any] | None:
        for pos in reversed(open_positions):
            if str(pos.get("pair")) == pair and str(pos.get("side", "BUY")).upper() == side:
                age = self._age_seconds(pos.get("opened_at"), now)
                if age <= self.duplicate_window_seconds:
                    return pos
        return None

    def _cooldown_active(self, state: dict[str, Any], pair: str, side: str, now: str) -> str | None:
        for row in reversed(state.get("signal_history", [])):
            if str(row.get("pair")) == pair and str(row.get("side", "BUY")).upper() == side:
                ts = str(row.get("timestamp", ""))
                if self._age_seconds(ts, now) <= self.cooldown_seconds:
                    return ts
        return None

    def _exposure_for(self, open_positions: list[dict[str, Any]], *, token: str | None = None, chain: str | None = None) -> Decimal:
        total = Decimal("0")
        for pos in open_positions:
            if token is not None:
                pos_token = str(pos.get("base_symbol") or self._split_pair(str(pos.get("pair", "-/USDC")))[0]).upper()
                if pos_token != token.upper():
                    continue
            if chain is not None and str(pos.get("chain", "")).lower() != chain.lower():
                continue
            total += self._decimal(pos.get("notional_usd", "0"))
        return total

    @staticmethod
    def _exit_price(entry: Decimal, side: str, pct: Decimal, favorable: bool) -> Decimal:
        if entry <= 0:
            return Decimal("0")
        delta = pct / Decimal("100")
        if side.upper() == "BUY":
            return (entry * (Decimal("1") + delta if favorable else Decimal("1") - delta)).quantize(Decimal("0.000000000000000001"))
        return (entry * (Decimal("1") - delta if favorable else Decimal("1") + delta)).quantize(Decimal("0.000000000000000001"))

    @staticmethod
    def _normalize_pair(pair: str) -> str:
        return str(pair or "-").strip().upper()

    @staticmethod
    def _split_pair(pair: str) -> tuple[str, str]:
        if "/" in pair:
            left, right = pair.split("/", 1)
            return left.upper(), right.upper()
        return pair.upper(), "USDC"

    @staticmethod
    def _age_seconds(then: Any, now: str) -> int:
        try:
            then_dt = datetime.fromisoformat(str(then).replace("Z", "+00:00"))
            now_dt = datetime.fromisoformat(str(now).replace("Z", "+00:00"))
            return max(0, int((now_dt - then_dt).total_seconds()))
        except Exception:
            return 10**9

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _quantize_usd(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.0001"))

    @staticmethod
    def _env_decimal(name: str, default: str) -> Decimal:
        try:
            return Decimal(os.getenv(name, default))
        except Exception:
            return Decimal(default)

    @staticmethod
    def _env_int(name: str, default: int) -> int:
        try:
            return int(os.getenv(name, str(default)))
        except Exception:
            return default

    @staticmethod
    def _env_bool(name: str, default: bool) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
