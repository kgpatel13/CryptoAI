# CryptoAI Pool Depth Ladder

Generated: `2026-07-01T01:29:16Z`

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
| USDC/WETH | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0114 | 0.0735 | 0.3491 | USDC/WETH has at least two healthy DEX ladders at requested size with worst impact 0.0114%. |
| WETH/USDC | DEPTH_READY | MEDIUM | 3 | 2000.0000 | 0.0178 | 0.1149 | 0.5436 | WETH/USDC has at least two healthy DEX ladders at requested size with worst impact 0.0178%. |

## DEX Detail

| Pair | DEX | OK | Tested | Max Tested USD | Worst Impact % | Liquidity USD |
|---|---|---:|---:|---:|---:|---:|
| USDC/WETH | Aerodrome | 5 | 5 | 2000.0000 | 0.0539 | 0.0000 |
| USDC/WETH | Uniswap V2 | 5 | 5 | 2000.0000 | 0.3491 | 0.0000 |
| USDC/WETH | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0039 | 0.0000 |
| WETH/USDC | Aerodrome | 5 | 5 | 2000.0000 | 0.0844 | 0.0000 |
| WETH/USDC | Uniswap V2 | 5 | 5 | 2000.0000 | 0.5436 | 0.0000 |
| WETH/USDC | Uniswap V3 | 5 | 5 | 2000.0000 | 0.0061 | 0.0000 |

## Findings

| Severity | Message |
|---|---|
| OK | No pool-depth ladder findings. |

## Notes

- Pool-depth ladder evidence is research-only and does not change trade thresholds.
- Quote-size ladder impact is measured from provider quotes at increasing notional sizes.
- Live trading remains disabled; DEPTH_READY is not a live-trading approval.
