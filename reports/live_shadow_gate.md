# Live Shadow Gate

Generated: `2026-07-01T06:04:40Z`
- Overall status: `SHADOW_ELIGIBLE_EVIDENCE`
- Recent orders: `200`
- Shadow eligible: `19`
- Paper only: `181`

## Latest Decisions

| Order | Pair | Paper Status | Shadow Decision | Stress Net % | Reason |
|---|---|---|---|---:|---|
| 4b67770e | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 709b3604 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| f911d905 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 3d83ece9 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| d6847f29 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 89246f2c | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3136 | Paper order passed live-style shadow gates. |
| 42c8c195 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| aec84dd4 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 3d56fd8a | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| ae7b90e3 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 5a084b4c | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| ec1ec01a | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 4f9c0c87 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| b8ea6656 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| d55ff005 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 8901f436 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 62a50ba4 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| cf8470c5 | USDC/WETH | CLOSED | SHADOW_ELIGIBLE | 0.3136 | Paper order passed live-style shadow gates. |
| 1d6d9e82 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 0fd04aec | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 5edbebcb | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| f927ddd1 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| f4b27762 | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |
| 14b2d7d9 | USDC/WETH | RISK_REJECTED | PAPER_ONLY | 0.3136 | Paper status is RISK_REJECTED. |
| 53cf1d0e | WETH/USDC | SKIPPED | PAPER_ONLY | -0.0779 | Paper status is SKIPPED.; Realism status is NEGATIVE_AFTER_STRESS.; Stress net edge is -0.0779%. |

## Notes

- Live Shadow Gate is paper evidence only; it does not approve live trading.
- SHADOW_ELIGIBLE means the paper trade passed live-style evidence gates before wallet/transaction simulation.
- Full live trading still requires wallet preflight, exact calldata, eth_call simulation, live safety, and the reviewed live execution adapter.
