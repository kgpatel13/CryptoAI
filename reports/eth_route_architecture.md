# CryptoAI ETH Route Architecture

Generated: `2026-06-29T22:59:35Z`

## Summary

- Focus chain: `base`
- Focus routes: `WETH/USDC, USDC/WETH`
- Production buffer %: `0.30`
- Research candidate buffer %: `0.20`
- Decision: `KEEP_0_30_PRODUCTION_RESEARCH_0_20`
- Promotion gates: `4/8`

## Trusted Venues

| Venue | Status | Role | Notes |
|---|---|---|---|
| Uniswap V2 | ACTIVE | implemented_quote_provider | Currently producing Base WETH/USDC and USDC/WETH quote evidence. |
| Aerodrome | ACTIVE | implemented_quote_provider | Currently producing Base WETH/USDC and USDC/WETH quote evidence. |
| Uniswap V3 | NOT_IMPLEMENTED | verified_next_provider_target | Official Base deployment exists; quote provider and route tests are still required locally. |

## Route Evidence

| Route | Two-DEX Ready | DEXs | 0.20% Signals | 0.20% PnL | 0.30% Signals | 0.30% PnL | Action |
|---|---|---|---:|---:|---:|---:|---|
| WETH/USDC | True | Aerodrome, Uniswap V2 | 59 | 32.5039 | 9 | 1.1800 | Keep WETH/USDC in 0.20% research replay; production stays at 0.30%. |
| USDC/WETH | True | Aerodrome, Uniswap V2 | 11 | 0.8463 | 0 | 0.0000 | Keep USDC/WETH in 0.20% research replay; production stays at 0.30%. |

## Buffer Promotion Gates

| Gate | Passed | Observed |
|---|---|---|
| execution_cost_confidence_high | False | LOW |
| paper_slippage_samples_30_plus | False | 6 |
| quote_ok_rate_90_plus | False | 65.9091 |
| active_two_dex_eth_route | True | 1 |
| provider_not_critical | True | WATCH |
| report_audit_clean | False | 33 |
| candidate_has_30_plus_signals | True | 70 |
| candidate_avg_net_edge_0_03_plus | True | 0.0476 |

## Real Money Architecture

- `1_quote_fanout`: Fetch fresh WETH/USDC and USDC/WETH quotes from multiple trusted Base venues. Controls: fresh quote TTL, two-venue minimum, stale quote live block, provider health score.
- `2_opportunity_and_cost_gate`: Calculate gross edge, subtract observed cost buffer, and reject low-edge routes. Controls: production buffer gate, minimum net edge gate, gas/slippage lower-bound evidence, replay comparison.
- `3_risk_gate`: Let risk decide before any order can be created. Controls: position size cap, daily loss cap, duplicate exposure block, cooldown, kill switch.
- `4_transaction_preflight`: Before real money, simulate exact calldata and amountOutMin against current state. Controls: allowance cap, nonce control, amountOutMin, deadline, private RPC or MEV-aware submit path.
- `5_execution_and_reconciliation`: Submit only if all gates pass, then reconcile fill, gas, slippage, and balance changes. Controls: tx receipt verification, post-trade accounting, gas attribution, automatic halt on mismatch.

## Findings

- `INFO` 2 ETH route direction(s) have two-DEX quote readiness on Base.
- `WATCH` 0.20% candidate replay has 70 positive signal(s) versus 9 at 0.30%, but promotion decision is KEEP_0_30_PRODUCTION_RESEARCH_0_20.
- `ACTION` Keep production buffer at 0.30%; collect missing evidence before any buffer change.
- `ACTION` Next venue expansion target for this route is a verified Base Uniswap V3 quote provider.

## References

- [Uniswap v3 Base deployments](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-base-deployments) - Verify Base Uniswap v3 deployment before local provider implementation.
- [Uniswap deployments guidance](https://developers.uniswap.org/docs/protocols/v3/deployments) - Do not assume contract addresses are identical across chains.
- [Aerodrome documentation](https://aerodrome.finance/docs) - Base DEX and liquidity hub reference for implemented Aerodrome route evidence.

## Notes

- This report is architecture and paper evidence only.
- It does not change production cost buffers, paper thresholds, risk thresholds, or live eligibility.
- A 0.20% buffer remains research-only until every promotion gate passes and the project owner approves a separate change.
