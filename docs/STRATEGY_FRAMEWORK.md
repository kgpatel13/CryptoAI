# Strategy Framework

The Strategy Framework lets CryptoAI support multiple strategies without changing the execution engine.

## Strategy Contract

Each strategy implements:

```python
class BaseStrategy:
    name: str
    def generate_signals(self) -> list[StrategySignal]: ...
```

Signals are advisory. They do not execute trades.

## Config

Strategy enablement lives in:

```text
config/strategies.json
```

Only `arbitrage` is enabled by default. Momentum, mean reversion, breakout, and AI-ranked strategies are visible as research placeholders but disabled.

## Signal Flow

```text
Strategy Registry
      |
      v
Enabled Strategies
      |
      v
Strategy Signals
      |
      v
Ranked Signals
      |
      v
AI Ranking
      |
      v
Risk Engine
      |
      v
Execution Engine
```

## Safety

Adding a strategy should never bypass risk controls. The risk engine and live safety gates remain mandatory.
