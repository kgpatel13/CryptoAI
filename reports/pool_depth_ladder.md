# CryptoAI Pool Depth Ladder

Generated: `2026-06-30T07:35:00Z`

## Summary

- Overall status: `DEPTH_EVIDENCE_WATCH`
- Confidence: `LOW`
- Requested notional USD: `$1000.0000`
- ETH reference USD: `$1000.0000`
- Quote rows: `30/30`
- Depth-ready routes: `0`

## Routes

| Pair | Status | Confidence | DEXes | Max Usable USD | Requested Impact % | Worst Tested Impact % | Reason |
|---|---|---|---:|---:|---:|---:|---|
| USDC/WETH | DEPTH_WATCH | LOW | 3 | 2000.0000 | 0.1643 | 0.3468 | USDC/WETH has two DEX ladders at requested size, but price impact needs review. |
| WETH/USDC | DEPTH_WATCH | LOW | 3 | 2000.0000 | 0.2605 | 0.5483 | WETH/USDC has two DEX ladders at requested size, but price impact needs review. |

## DEX Detail

| Pair | DEX | OK | Tested | Max Tested USD | Worst Impact % | Liquidity USD |
|---|---|---:|---:|---:|---:|---:|
| USDC/WETH | Aerodrome | 5 | 5 | 2000.0000 | 0.0536 | 0.0000 |
| USDC/WETH | Uniswap V2 | 5 | 5 | 2000.0000 | 0.3468 | 0.0000 |
| USDC/WETH | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0037 | 0.0000 |
| WETH/USDC | Aerodrome | 5 | 5 | 2000.0000 | 0.0850 | 0.0000 |
| WETH/USDC | Uniswap V2 | 5 | 5 | 2000.0000 | 0.5483 | 0.0000 |
| WETH/USDC | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0059 | 0.0000 |

## Findings

| Severity | Message |
|---|---|
| ACTION | No route has medium-confidence depth evidence at requested paper size. |

## Notes

- Pool-depth ladder evidence is research-only and does not change trade thresholds.
- Quote-size ladder impact is measured from provider quotes at increasing notional sizes.
- Live trading remains disabled; DEPTH_READY is not a live-trading approval.
