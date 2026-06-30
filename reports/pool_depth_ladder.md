# CryptoAI Pool Depth Ladder

Generated: `2026-06-30T08:02:55Z`

## Summary

- Overall status: `DEPTH_EVIDENCE_READY`
- Confidence: `MEDIUM`
- Requested notional USD: `$500.0000`
- ETH reference USD: `$1000.0000`
- Quote rows: `30/30`
- Depth-ready routes: `2`

## Routes

| Pair | Status | Confidence | DEXes | Max Usable USD | Best-Two Requested Impact % | Worst Requested Impact % | Worst Tested Impact % | Reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| USDC/WETH | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0113 | 0.0730 | 0.3468 | USDC/WETH has at least two healthy DEX ladders at requested size with worst impact 0.0113%. |
| WETH/USDC | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0179 | 0.1159 | 0.5482 | WETH/USDC has at least two healthy DEX ladders at requested size with worst impact 0.0179%. |

## DEX Detail

| Pair | DEX | OK | Tested | Max Tested USD | Worst Impact % | Liquidity USD |
|---|---|---:|---:|---:|---:|---:|
| USDC/WETH | Aerodrome | 5 | 5 | 2000.0000 | 0.0535 | 0.0000 |
| USDC/WETH | Uniswap V2 | 5 | 5 | 2000.0000 | 0.3468 | 0.0000 |
| USDC/WETH | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0036 | 0.0000 |
| WETH/USDC | Aerodrome | 5 | 5 | 2000.0000 | 0.0851 | 0.0000 |
| WETH/USDC | Uniswap V2 | 5 | 5 | 2000.0000 | 0.5482 | 0.0000 |
| WETH/USDC | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0058 | 0.0000 |

## Findings

| Severity | Message |
|---|---|
| OK | No pool-depth ladder findings. |

## Notes

- Pool-depth ladder evidence is research-only and does not change trade thresholds.
- Quote-size ladder impact is measured from provider quotes at increasing notional sizes.
- Live trading remains disabled; DEPTH_READY is not a live-trading approval.
