# Live Shadow Gate

Generated: `2026-07-01T06:24:55Z`
- Overall status: `SHADOW_ELIGIBLE_EVIDENCE`
- Recent orders: `200`
- Shadow eligible: `18`
- Paper only: `182`

## Latest Decisions

| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |
|---|---|---|---|---:|---|
| bd7f9203 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 5a12b400 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 42082fb0 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 3f48793c | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 4dd5bca2 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| c4da2030 | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3268 | Paper order passed live-style shadow gates. |
| d110837a | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| d85fefb6 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| c2b93867 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 7769bce9 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 40bec19b | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| e9082f1a | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 417add4d | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 3bbe1019 | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3268 | Paper order passed live-style shadow gates. |
| 2ce8aa75 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 0e5ab5b1 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 169bc30d | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 96ca5b70 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| a8cf9827 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 638e74c5 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 5a67798f | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 6ce569a2 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 72b76e20 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |
| 2113609b | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3268 | Paper status is RISK_REJECTED. |
| 61463e9d | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0943 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0943%. |

## Notes

- Live Shadow Gate is paper evidence only; it does not approve live trading.
- SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.
- Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.
