from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PortfolioRiskDecision:
    approved: bool
    notional_usd: Decimal
    reason: str


class PortfolioRiskService:
    """Stateful paper-portfolio risk controls.

    This service is intentionally file-backed and deterministic so it can run in
    GitHub Actions, Streamlit, and local paper tests without extra services.

    It protects the paper pipeline from unrealistic repeated fills by enforcing:
    - duplicate signal suppression
    - per-pair/direction cooldowns
    - cash and dynamic sizing
    - max open positions
    - max daily trades
    - chain/token exposure caps
    - daily realized-loss guard (foundation for v3.5 PnL)
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
        self.max_daily_loss_usd = self._env_decimal("CRYPTOAI_MAX_DAILY_LOSS_USD", "0")

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

    def record_filled_order(self, *, order_id: str, timestamp: str, strategy_name: str, chain: str, pair: str, side: str, notional_usd: Decimal, fill_price_usd: Decimal, quantity: Decimal, estimated_edge_pct: Decimal | None = None) -> dict[str, Any]:
        state = self.load_state()
        self._reset_daily_counters_if_needed(state, timestamp)

        normalized_pair = self._normalize_pair(pair)
        base_symbol, quote_symbol = self._split_pair(normalized_pair)
        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        state["cash_usd"] = str(self._quantize_usd(max(Decimal("0"), cash - notional_usd)))
        state["daily_filled_trades"] = int(state.get("daily_filled_trades", 0)) + 1
        state["updated_at"] = timestamp
        state.setdefault("positions", []).append({
            "position_id": order_id,
            "order_id": order_id,
            "strategy_name": strategy_name,
            "chain": chain,
            "pair": normalized_pair,
            "side": side.upper(),
            "base_symbol": base_symbol,
            "quote_symbol": quote_symbol,
            "quantity": str(quantity),
            "entry_price_usd": str(fill_price_usd),
            "current_price_usd": str(fill_price_usd),
            "notional_usd": str(notional_usd),
            "estimated_edge_pct": str(estimated_edge_pct) if estimated_edge_pct is not None else None,
            "status": "OPEN",
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

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            state = self._initial_state()
            self.save_state(state)
            return state
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8", errors="replace"))
            if not isinstance(raw, dict):
                raise ValueError("state is not an object")
            return self._upgrade_state(raw)
        except Exception:
            state = self._initial_state()
            self.save_state(state)
            return state

    def save_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    def summary(self) -> dict[str, Any]:
        state = self.load_state()
        open_positions = self._open_positions(state)
        exposure_by_chain: dict[str, str] = {}
        exposure_by_token: dict[str, str] = {}
        for pos in open_positions:
            notional = self._decimal(pos.get("notional_usd", "0"))
            chain = str(pos.get("chain", "-"))
            token = str(pos.get("base_symbol") or self._split_pair(str(pos.get("pair", "-/USDC")))[0])
            exposure_by_chain[chain] = str(self._decimal(exposure_by_chain.get(chain, "0")) + notional)
            exposure_by_token[token] = str(self._decimal(exposure_by_token.get(token, "0")) + notional)
        return {
            "cash_usd": state.get("cash_usd", str(self.initial_cash_usd)),
            "initial_cash_usd": state.get("initial_cash_usd", str(self.initial_cash_usd)),
            "open_positions": len(open_positions),
            "daily_filled_trades": state.get("daily_filled_trades", 0),
            "daily_realized_pnl_usd": state.get("daily_realized_pnl_usd", "0"),
            "exposure_by_chain": exposure_by_chain,
            "exposure_by_token": exposure_by_token,
            "limits": {
                "max_open_positions": self.max_open_positions,
                "max_daily_trades": self.max_daily_trades,
                "trade_cooldown_seconds": self.cooldown_seconds,
                "duplicate_signal_window_seconds": self.duplicate_window_seconds,
                "max_trade_notional_usd": str(self.max_trade_notional_usd),
                "risk_per_trade_pct": str(self.risk_per_trade_pct),
                "max_cash_usage_pct": str(self.max_cash_usage_pct),
                "max_token_exposure_pct": str(self.max_token_exposure_pct),
                "max_chain_exposure_pct": str(self.max_chain_exposure_pct),
            },
            "state_path": str(self.state_path),
            "updated_at": state.get("updated_at"),
        }

    def _initial_state(self) -> dict[str, Any]:
        now = self._utc_now()
        return {
            "version": "3.3",
            "portfolio_name": "CryptoAI Paper Portfolio",
            "initial_cash_usd": str(self.initial_cash_usd),
            "cash_usd": str(self.initial_cash_usd),
            "daily_date": now[:10],
            "daily_filled_trades": 0,
            "daily_realized_pnl_usd": "0",
            "positions": [],
            "signal_history": [],
            "created_at": now,
            "updated_at": now,
        }

    def _upgrade_state(self, state: dict[str, Any]) -> dict[str, Any]:
        state.setdefault("version", "3.3")
        state.setdefault("portfolio_name", "CryptoAI Paper Portfolio")
        state.setdefault("initial_cash_usd", str(self.initial_cash_usd))
        state.setdefault("cash_usd", str(self.initial_cash_usd))
        state.setdefault("daily_date", self._utc_now()[:10])
        state.setdefault("daily_filled_trades", 0)
        state.setdefault("daily_realized_pnl_usd", "0")
        state.setdefault("positions", [])
        state.setdefault("signal_history", [])
        state.setdefault("created_at", self._utc_now())
        state.setdefault("updated_at", state.get("created_at"))
        return state

    def _reset_daily_counters_if_needed(self, state: dict[str, Any], timestamp: str) -> None:
        today = timestamp[:10]
        if state.get("daily_date") != today:
            state["daily_date"] = today
            state["daily_filled_trades"] = 0
            state["daily_realized_pnl_usd"] = "0"
            state["updated_at"] = timestamp

    def _portfolio_value(self, state: dict[str, Any]) -> Decimal:
        cash = self._decimal(state.get("cash_usd", self.initial_cash_usd))
        open_notional = sum((self._decimal(pos.get("notional_usd", "0")) for pos in self._open_positions(state)), Decimal("0"))
        return max(self.initial_cash_usd, cash + open_notional)

    @staticmethod
    def _open_positions(state: dict[str, Any]) -> list[dict[str, Any]]:
        return [p for p in state.get("positions", []) if str(p.get("status", "OPEN")).upper() == "OPEN"]

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
