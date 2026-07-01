# Live Shadow Gate

Generated: `2026-07-01T03:54:27Z`
- Overall status: `NO_SHADOW_ELIGIBLE_TRADES`
- Recent orders: `200`
- Shadow eligible: `0`
- Paper only: `200`

## Latest Decisions

| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |
|---|---|---|---|---:|---|
| f59e1d52 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| fb62f0aa | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 78af94a4 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| a48b4c46 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 69007df1 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 9d4bc237 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| bcdef217 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 142a976d | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| cdf7e1f6 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 4d019bd9 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 0ab0b051 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| c026b53c | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 935954d0 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| b0d31d56 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| e8928f14 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 28ff24e7 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 5cf60889 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| eee2e5f6 | USDC/WETH | SKIPPED | PAPER_ONLY | 0.0513 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 24af3f0d | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| fa8e360b | USDC/WETH | CLOSED | PAPER_ONLY | 0.0513 | Realism status is WATCH_ONLY. |
| c5445511 | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| d0abeb40 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.0513 | Paper status is RISK_REJECTED.; Realism status is WATCH_ONLY. |
| 263a626f | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |
| 5b063ad6 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.0513 | Paper status is RISK_REJECTED.; Realism status is WATCH_ONLY. |
| 5d35d42e | WETH/USDC | SKIPPED | PAPER_ONLY | 0.1683 | Paper status is SKIPPED.; Realism status is WATCH_ONLY. |

## Notes

- Live Shadow Gate is paper evidence only; it does not approve live trading.
- SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.
- Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.
