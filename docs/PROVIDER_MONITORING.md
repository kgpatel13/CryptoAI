# CryptoAI Provider Monitoring

## Purpose

Provider Monitoring is a v4.1 operations report that classifies observed provider health into operational statuses for Mission Control.

It reads existing provider-health observations and does not make network calls.

## Inputs

- `data/provider_health.json`

Provider observations are produced by the quote and RPC layers as they record successes, failures, latency, scores, and recent errors.

## Outputs

- `reports/provider_monitor.json`
- `reports/provider_monitor.md`

## Statuses

- `OK` - provider score and freshness are acceptable.
- `WATCH` - observations are stale or incomplete.
- `DEGRADED` - provider score is below the degraded threshold.
- `CRITICAL` - provider score is critically low or consecutive failures exceed the configured threshold.
- `NEEDS_DATA` - no provider observations exist yet.

## Configuration

Environment variables:

- `CRYPTOAI_PROVIDER_STALE_AFTER_SECONDS` default `900`
- `CRYPTOAI_PROVIDER_DEGRADED_SCORE` default `70`
- `CRYPTOAI_PROVIDER_CRITICAL_SCORE` default `40`
- `CRYPTOAI_PROVIDER_FAILURE_THRESHOLD` default `3`

## Command

```bash
python -m app.operations.provider_monitor
```

## Safety

Provider Monitoring is observational only. It does not approve trades, does not bypass Risk Engine, and does not enable live execution.
