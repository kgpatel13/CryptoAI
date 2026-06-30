# CryptoAI ETH Market Coverage

Generated: `2026-06-30T03:09:37Z`

## Summary

- Asset focus: `ETH`
- Coverage model: `ETH_GOLDEN_PATH`
- Overall score: `53`
- Overall status: `ETH_COVERAGE_EARLY`
- Target chains: `5`
- Configured target chains: `4`
- Target DEXs: `14`
- Configured target DEXs: `11`
- Quote-ready routes: `2`

## Chain Coverage

| Chain | Stage | Score | Status | Tokens | DEXs | Quote Routes | Providers | Next Action |
|---|---|---:|---|---:|---:|---:|---:|---|
| Base | reference | 83 | DEVELOPING | 2/4 | 3/3 | 2 | 4 | Improve sustained three-venue quote OK rate and paper execution samples before expanding beyond Base ETH. |
| Ethereum | planned | 19 | TARGET_ONLY | 2/4 | 3/4 | 0 | 0 | Add verified token metadata for ethereum: USDT, DAI. |
| Arbitrum One | planned | 23 | TARGET_ONLY | 2/4 | 3/3 | 0 | 0 | Add verified token metadata for arbitrum: USDT, DAI. |
| Optimism | planned_next | 0 | TARGET_ONLY | 0/4 | 0/2 | 0 | 0 | Add verified token metadata for optimism: WETH, USDC, USDT, DAI. |
| Polygon | planned | 23 | TARGET_ONLY | 2/4 | 2/2 | 0 | 0 | Add verified token metadata for polygon: USDT, DAI. |

## Next Actions

- Keep ETH Golden Path on Base until coverage score reaches reference-ready maturity.
- Collect sustained Base Uniswap V3 quote diagnostics before adding a new asset class.
- Add Optimism registry metadata only after official token/DEX/router addresses are verified.
- Do not expand to BTC or blue chips until ETH coverage KPIs are stable.

## Findings

- `INFO` ETH Golden Path overall coverage score is 53.
- `ACTION` Base reference coverage score is 83 with status DEVELOPING.
- `ACTION` 4 target chain(s) still have target-only or near-empty evidence coverage.

## Notes

- ETH Market Coverage scores target-vs-evidence maturity before adding BTC, blue chips, or long-tail tokens.
- A target chain or DEX is not treated as active coverage until registry metadata, quote providers, route diagnostics, and provider health exist.
- This report does not change production buffers, risk thresholds, or live-trading eligibility.
