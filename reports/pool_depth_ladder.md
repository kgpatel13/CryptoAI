# CryptoAI Pool Depth Ladder

Generated: `2026-06-30T17:37:22Z`

## Summary

- Overall status: `DEPTH_EVIDENCE_READY`
- Confidence: `MEDIUM`
- Requested notional USD: `$50.0000`
- ETH reference USD: `$1000.0000`
- Quote rows: `36/36`
- Depth-ready routes: `2`

## Routes

| Pair | Status | Confidence | DEXes | Max Usable USD | Best-Two Requested Impact % | Worst Requested Impact % | Worst Tested Impact % | Reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| USDC/WETH | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0000 | 0.0000 | 0.3581 | USDC/WETH has at least two healthy DEX ladders at requested size with worst impact 0.0000%. |
| WETH/USDC | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0000 | 0.0000 | 0.5593 | WETH/USDC has at least two healthy DEX ladders at requested size with worst impact 0.0000%. |

## DEX Detail

| Pair | DEX | OK | Tested | Max Tested USD | Worst Impact % | Liquidity USD |
|---|---|---:|---:|---:|---:|---:|
| USDC/WETH | Aerodrome | 6 | 6 | 2000.0000 | 0.0553 | 0.0000 |
| USDC/WETH | Uniswap V2 | 6 | 6 | 2000.0000 | 0.3581 | 0.0000 |
| USDC/WETH | Uniswap V3 | 6 | 6 | 2000.0000 | 0.0040 | 0.0000 |
| WETH/USDC | Aerodrome | 6 | 6 | 2000.0000 | 0.0868 | 0.0000 |
| WETH/USDC | Uniswap V2 | 6 | 6 | 2000.0000 | 0.5593 | 0.0000 |
| WETH/USDC | Uniswap V3 | 6 | 6 | 2000.0000 | 0.0063 | 0.0000 |

## Findings

| Severity | Message |
|---|---|
| OK | No pool-depth ladder findings. |

## Notes

- Pool-depth ladder evidence is research-only and does not change trade thresholds.
- Quote-size ladder impact is measured from provider quotes at increasing notional sizes.
- Live trading remains disabled; DEPTH_READY is not a live-trading approval.
