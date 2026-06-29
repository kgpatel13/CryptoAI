# CryptoAI v4.4 - Provider Health Hardening

## Executive Summary

v4.4 hardens provider-health evidence before the next development phase. It fixes stale Provider Monitor sequencing, separates current provider status from rolling score recovery, prevents unhealthy optional backup RPCs from creating false critical blockers when required RPC coverage is healthy, and archives legacy paper rows from clean evidence.

Live trading remains disabled.

## Key Changes

- Paper autopilot now generates Provider Monitor and Market Intelligence after the quote/workflow refresh.
- Provider Monitor exposes `current_status`, `rolling_status`, and `required_for_overall`.
- Optional backup RPC failures are WATCH when required same-chain RPC coverage is fresh and healthy.
- Aerodrome-style fresh-success recovery is WATCH while the rolling score rebuilds.
- Experiment evidence treats provider WATCH as WARN instead of PASS.
- Legacy paper rows can be reviewed and archived with `app.reporting.legacy_paper_archive`.

## Validation Snapshot

- Paper autopilot once: `OK`, 4 quote rows refreshed, 0 filled orders because current edge remained below risk threshold.
- Provider Monitor: `WATCH`, 0 critical alerts, 0 degraded alerts.
- Quote Diagnostics: 4 OK, 0 errors.
- Report Audit: 23 reports, 0 missing, 0 stale, 0 findings.
- Paper Report: 45 total orders, 12 filled orders, 0 legacy accounting warnings.
- Portfolio Analytics: total PnL `$2.8220`, total return `0.0282%`.
- Experiment Evidence: 3 pass / 1 warn / 1 fail; default replay remains the only hard failure.

## Commands

```bash
python -m app.diagnostics.quote_diagnostics
python -m app.automation.paper_autopilot --once
python -m app.operations.provider_monitor
python -m app.reporting.legacy_paper_archive --dry-run
python -m app.reporting.report_audit
python -m app.backtesting.experiment_service
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v4.4 - Harden provider health and clean evidence gates
```

## Rollback Instructions

```bash
git revert <v4.4-commit-sha>
```

Generated report artifacts can be regenerated from the commands above. Archived local paper rows remain available in `data/paper_orders_legacy_archive.jsonl`.
