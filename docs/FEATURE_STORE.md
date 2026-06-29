# CryptoAI Feature Store

CryptoAI v4.0 introduces a research-grade feature store. Its purpose is to turn market activity, opportunity scans, strategy signals, risk decisions, and execution outcomes into structured records that can later support research, replay, backtesting, and AI-assisted ranking.

## Core principle

A feature vector is not a trading approval. It is a historical research record.

Live trading must still pass quote freshness, provider health, risk controls, execution safety, wallet controls, and live-mode gates.

## Files

- `data/feature_vectors.jsonl` — append/rebuild-friendly feature export.
- `data/feature_vectors.csv` — spreadsheet-friendly research export.
- `reports/feature_store.json` — machine-readable summary.
- `reports/feature_store.md` — human-readable summary.
- SQLite table `feature_vectors` — queryable local research table.

## Current inputs

v4.0 builds features from existing runtime artifacts:

- `data/opportunity_decisions.jsonl`
- `data/multi_dex_opportunities.jsonl`
- `data/paper_orders.jsonl`
- `data/strategy_ranked_signals.jsonl`

## Command

```bash
python -m app.research.feature_store
```

For the complete research dashboard:

```bash
python -m app.research.research_report
```
