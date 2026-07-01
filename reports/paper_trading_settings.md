# CryptoAI Paper Trading Settings

Generated: `2026-07-01T01:32:11Z`

## Summary

- Status: `VALID`
- Mode: `paper`
- Paper profile: `live_parity_500`
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
- Min notional per trade USD: `500`
- Paper sizing mode: `full_available_cash`
- Max daily paper trades: `0`
- Max open positions: `1`
- Duplicate position block: `True`
- Cooldown seconds: `0`
- Arbitrage signal fingerprint window seconds: `60`
- Max daily loss USD: `5`
- Production buffer %: `0.30`
- Research candidate buffer %: `0.20`
- Paper BUY threshold %: `0.25`
- Require live-shadow eligible paper fills: `True`

## Findings

| Severity | Field | Message |
|---|---|---|
| OK | - | Settings are valid for paper-mode launch. |

## Notes

- Limit value `0` means continuous, unlimited, or disabled for loop interval, daily trades, open positions, cooldown, and daily-loss stop.
- Paper settings are launch controls for continuous simulation only.
- Live trading remains disabled until live-readiness gates pass.
- The 0.20% buffer is research-only; production buffer remains at 0.30%.
- One ETH is treated as a paper capital profile and future live ceiling, not an all-in per-trade size.
- Live parity 500 profile is running a paper-only $500 notional probe against a $500 wallet ceiling; live trading remains disabled.
- Paper fills require live-shadow eligibility in this profile, so paper profit means more than paper-only edge.
- Paper BUY threshold is temporarily set to 0.25% for edge-probe testing only; live-shadow gates still block non-executable fills.
- $500 paper notional is an experiment to measure gas percentage, price impact, and stress net edge at full paper-wallet size.
- A 60-second arbitrage signal fingerprint guard blocks repeated identical route/price snapshots while allowing continuous scanning.
- This profile is still paper-only and does not approve live trading.
