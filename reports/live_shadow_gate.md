# Live Shadow Gate

Generated: `2026-07-01T01:29:58Z`
- Overall status: `SHADOW_ELIGIBLE_EVIDENCE`
- Recent orders: `200`
- Shadow eligible: `35`
- Paper only: `165`

## Latest Decisions

| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |
|---|---|---|---|---:|---|
| 4fa319fd | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 7c22a874 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 98f8f258 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 95a04849 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 573bf1e3 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| e343171d | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 6cedd225 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 77932773 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 49c905bb | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 17fc2d5c | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 765fe4a1 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 000d9005 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 047c37d6 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| f0b6a1c4 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| d2eff728 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 93f2cc94 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 82fa297d | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 4cca9c81 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| dd7f2690 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 455e4ae4 | WETH/USDC | RISK_REJECTED | PAPER_ONLY | 0.3429 | Paper status is RISK_REJECTED. |
| 0e8ccda9 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| f1f9ea04 | WETH/USDC | CLOSED | SHADOW_ELIGIBLE | 0.3429 | Paper order passed live-style shadow gates. |
| 80bf5739 | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |
| 580b1901 | WETH/USDC | RISK_REJECTED | PAPER_ONLY | 0.3429 | Paper status is RISK_REJECTED. |
| ec5cc75f | USDC/WETH | SKIPPED | PAPER_ONLY | -0.1227 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.1227%. |

## Notes

- Live Shadow Gate is paper evidence only; it does not approve live trading.
- SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.
- Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.
