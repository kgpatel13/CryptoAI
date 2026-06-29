# CryptoAI Paper Trading Settings

Generated: `2026-06-29T23:16:13Z`

## Summary

- Status: `VALID`
- Mode: `paper`
- Paper capital USD: `3500.00`
- Errors: `0`
- Warnings: `0`
- Launch command: `python -m app.automation.paper_autopilot --loop --use-settings`

## Launch Profile

- Asset focus: `ETH`
- Chains: `base`
- Routes: `WETH/USDC, USDC/WETH`
- DEXs: `Uniswap V2, Aerodrome`
- Initial paper capital ETH: `1.0`
- Max notional per trade USD: `100`
- Production buffer %: `0.30`
- Research candidate buffer %: `0.20`
- Paper BUY threshold %: `0.30`

## Findings

| Severity | Field | Message |
|---|---|---|
| OK | - | Settings are valid for paper-mode launch. |

## Notes

- Paper settings are launch controls for continuous simulation only.
- Live trading remains disabled until live-readiness gates pass.
- The 0.20% buffer is research-only; production and paper BUY gates remain at 0.30%.
- One ETH is treated as a paper capital profile and future live ceiling, not an all-in per-trade size.
