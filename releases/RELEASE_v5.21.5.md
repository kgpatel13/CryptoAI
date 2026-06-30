# v5.21.5 - Live-Style Shadow Gate for Paper Trading

## Summary

Adds the missing bridge between profitable paper fills and live-tradable evidence.

Paper trading now records whether each fill is:

- `PAPER_BUY`: paper simulation filled it.
- `SHADOW_ELIGIBLE`: the same trade passed live-style evidence gates before wallet and transaction simulation.
- `PAPER_ONLY`: paper filled or considered it, but live-style evidence says it should not be used for live readiness.

## Changes

- Adds `app.execution.live_shadow_gate_service`.
- Adds `reports/live_shadow_gate.json` and `reports/live_shadow_gate.md`.
- Adds live-shadow fields to paper orders.
- Updates paper execution to annotate every paper arbitrage order with live-shadow evidence.
- Enables strict live-shadow gating in the `live_parity_500` paper profile:
  - paper max/min trade remains `$20`,
  - paper fills require `SHADOW_ELIGIBLE`,
  - non-eligible opportunities are skipped instead of creating misleading paper profit.
- Adds Live Shadow Gate counts to Paper Report and Paper Run Review.
- Adds dashboard/report-audit visibility for Live Shadow Gate.

## Why

Paper PnL alone does not prove live tradability. The live-parity profile now makes paper behave closer to the live decision path, so we can trust future paper profits as stronger evidence before enabling real-money automation.

## Verification

```powershell
python -m unittest tests.test_live_shadow_gate_service tests.test_paper_settings_service tests.test_arbitrage_execution_engine
python -m unittest discover -s tests
```

## Commit Message

```text
v5.21.5 - Add live-style shadow gate for paper trading
```
