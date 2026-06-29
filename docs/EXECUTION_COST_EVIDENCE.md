# CryptoAI Execution Cost Evidence

## Purpose

Execution Cost Evidence measures whether the current `0.30%` production cost buffer is conservative, accurate, too high, too low, or not yet supported by enough evidence.

It does not change production cost buffers, paper thresholds, risk thresholds, or live-trading eligibility.

## Inputs

- `data/paper_orders.jsonl`
- `data/opportunity_decisions.jsonl`
- `data/multi_dex_opportunities.jsonl`
- `data/quote_diagnostics.jsonl`
- `data/provider_health.json`

## Outputs

- `reports/execution_cost_evidence.json`
- `reports/execution_cost_evidence.md`

## Interpretation

The report treats paper slippage plus configured gas buffer as a measured lower bound. It does not claim that lower-bound evidence is a complete live execution-cost estimate, because real gas, pool fee, route depth, and live fill behavior still need stronger evidence.

`TOO_HIGH` requires high-confidence evidence plus replay signals that are profitable under observed lower-bound costs but blocked by the current production buffer. Low-confidence evidence remains `CONSERVATIVE` rather than recommending a threshold change.

## Command

```bash
python -m app.execution.execution_cost_evidence_service
```

## Safety

The correct v5.2 action is evidence collection. Do not lower the production `0.30%` buffer until execution-cost evidence is high-confidence and reviewed with replay, provider, and paper PnL reports.
