# CryptoAI Paper Trading Settings

Generated: `2026-06-30T08:03:41Z`

## Summary

- Status: `VALID`
- Mode: `paper`
- Paper profile: `shadow_500`
- Paper capital USD: `500.00`
- Errors: `0`
- Warnings: `0`
- Launch command: `python -m app.automation.paper_autopilot --loop --use-settings`

## Launch Profile

- Asset focus: `ETH`
- Chains: `base`
- Routes: `WETH/USDC, USDC/WETH`
- DEXs: `Uniswap V2, Aerodrome, Uniswap V3`
- Loop interval seconds: `0`
- Initial paper capital ETH: `0.5`
- Max notional per trade USD: `500`
- Paper sizing mode: `full_available_cash`
- Max daily paper trades: `0`
- Max open positions: `1`
- Duplicate position block: `True`
- Cooldown seconds: `0`
- Max daily loss USD: `0`
- Production buffer %: `0.30`
- Research candidate buffer %: `0.20`
- Paper BUY threshold %: `0.30`

## Findings

| Severity | Field | Message |
|---|---|---|
| OK | - | Settings are valid for paper-mode launch. |

## Notes

- Limit value `0` means continuous, unlimited, or disabled for loop interval, daily trades, open positions, cooldown, and daily-loss stop.
- Paper settings are launch controls for continuous simulation only.
- Live trading remains disabled until live-readiness gates pass.
- The 0.20% buffer is research-only; production and paper BUY gates remain at 0.30%.
- Shadow 500 profile uses a $500 production-like paper capital ceiling for multi-day validation; live trading remains disabled.
- Full available cash sizing lets approved paper trades request the configured max trade size, then portfolio cash caps the actual fill.
- Arbitrage paper trades close atomically and must not create long-lived open positions.
