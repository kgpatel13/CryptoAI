# CryptoAI Architecture

CryptoAI is designed as a modular quantitative trading research and paper-execution platform.

```text
Market Data / Quotes
        |
        v
Opportunity Engine
        |
        v
Strategy Framework
        |
        v
AI Ranking / Signal Ranking
        |
        v
Risk Engine
        |
        v
Paper Execution Engine
        |
        v
Portfolio Accounting
        |
        v
Analytics / Dashboard
```

## Authority Boundaries

- Strategies are advisory only.
- AI ranking is advisory only.
- Risk engine is the final authority before paper execution.
- Live trading remains disabled by default.
- Stale, simulated, degraded, or unsafe data must not trigger live orders.

## v3.6 Change

v3.6 introduces a strategy registry, strategy configuration, ranked strategy signals, strategy-level performance, and a Strategy Center report/dashboard.
