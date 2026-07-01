# Live Shadow Gate

Generated: `2026-07-01T05:30:11Z`
- Overall status: `SHADOW_ELIGIBLE_EVIDENCE`
- Recent orders: `200`
- Shadow eligible: `14`
- Paper only: `186`

## Latest Decisions

| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |
|---|---|---|---|---:|---|
| 7bbda71a | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 27ecdf9c | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| ce581af8 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 2a56f48c | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| 6d971576 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| e7786675 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| cb8e9c58 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| bef9935f | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| af03b889 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 7b3f179f | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3058 | Paper order passed live-style shadow gates. |
| f1760fa6 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| c08a4b84 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| b5a0cecc | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 452c613d | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| 1cd01741 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 8e76ef24 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| f4dd3b1a | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 2f3cefe3 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| 1a0094c2 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| e5100624 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| d486d5b1 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| b5e77f38 | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3058 | Paper order passed live-style shadow gates. |
| 9b9ff07b | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |
| 94be2efb | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3058 | Paper status is RISK_REJECTED. |
| f455fe65 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0842 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0842%. |

## Notes

- Live Shadow Gate is paper evidence only; it does not approve live trading.
- SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.
- Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.
