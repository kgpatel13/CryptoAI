# CryptoAI Paper Trading Settings

Generated: `2026-06-30T07:34:52Z`

## Summary

- Status: `VALID`
- Mode: `paper`
- Paper profile: `unbounded_paper_lab`
- Paper capital USD: `1000.00`
- Errors: `0`
- Warnings: `0`
- Launch command: `python -m app.automation.paper_autopilot --loop --use-settings`

## Launch Profile

- Asset focus: `ETH`
- Chains: `base`
- Routes: `WETH/USDC, USDC/WETH`
- DEXs: `Uniswap V2, Aerodrome, Uniswap V3`
- Loop interval seconds: `0`
- Initial paper capital ETH: `1.0`
- Max notional per trade USD: `1000`
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
- Unbounded paper lab removes paper-only throttles for stress testing; live trading remains disabled.
- Full available cash sizing lets approved paper trades request the configured max trade size, then portfolio cash caps the actual fill.
- Arbitrage paper trades close atomically and must not create long-lived open positions.
