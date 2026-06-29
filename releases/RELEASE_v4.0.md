# CryptoAI v4.0 — Quant Research Platform

## Executive Summary

v4.0 promotes CryptoAI from a paper trading platform into a quantitative research platform. The release adds the Feature Store, Research Dashboard, Mission Control, explainability helpers, and research exports for future backtesting and AI ranking.

## Added

- Feature vector model.
- Feature Store service.
- SQLite `feature_vectors` table.
- JSONL and CSV feature exports.
- Research Dashboard report.
- Mission Control dashboard page.
- Research Dashboard dashboard page.
- Decision Explainability helper.
- Documentation for feature store, event model, research platform, and explainability.
- Regression tests for feature vectors, feature exports, and explainability.

## Validation

```bash
python -m compileall -q app tests
python -m unittest discover -s tests -v
python -m app.research.feature_store
python -m app.research.research_report
python -m app.reporting.paper_report
```

## Safety

This release does not enable live trading. Feature vectors are research records only and must not be interpreted as live-trade approvals.

## Rollback

```bash
git checkout v3.6
```
