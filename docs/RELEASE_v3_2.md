# CryptoAI v3.2 - Production Resilience Layer

## Goal

Strengthen the paper-trading foundation before adding more trading features. This release preserves the v3.1 architecture and adds resilience, observability, and regression tests around external RPC/DEX dependencies.

## Change list

### Added

- `app/resilience/circuit_breaker.py`
  - Per-provider circuit breaker with CLOSED / OPEN / HALF_OPEN states.
- `app/resilience/retry_policy.py`
  - Exponential backoff retry helper with jitter.
- `app/resilience/provider_health.py`
  - Provider success/failure/latency scoring persisted to `data/provider_health.json`.
- `app/resilience/rpc_provider_pool.py`
  - RPC provider pool with failover and circuit-breaker filtering.
- Unit tests:
  - `tests/test_circuit_breaker.py`
  - `tests/test_retry_policy.py`
  - `tests/test_provider_health.py`
  - `tests/test_quote_models.py`

### Changed

- `app/blockchain/rpc_client.py`
  - Replaced simple first-available RPC fallback with a provider pool.
  - Records RPC latency, success, failure, and circuit state.
- `app/quotes/uniswap_v2_quote_provider.py`
  - Uses RPC provider pool, retry policy, and provider-health recording.
- `app/quotes/aerodrome_quote_provider.py`
  - Uses RPC provider pool, retry policy, and provider-health recording.
- `app/quotes/models.py`
  - Adds quote freshness metadata: `source`, `age_seconds`, `is_stale`, and `rpc_provider`.
- `app/quotes/quote_service.py`
  - Keeps stale snapshot fallback for paper mode only.
  - Blocks stale/degraded snapshot usage when live trading is enabled.
- `app/dashboard/main_dashboard.py`
  - System Health now shows provider health and quote snapshot status.
- `.github/workflows/paper-autopilot.yml`
  - Runs unit tests before diagnostics and paper autopilot.

## Safety behavior

- Paper mode may use a recent healthy quote snapshot when live quote calls fail.
- Live mode must not use stale/degraded quote snapshots.
- Failed RPC/DEX calls are isolated, scored, and circuit-broken instead of crashing the pipeline.

## Testing instructions

Run locally:

```bash
python -m unittest discover -s tests -v
python -m compileall -q app
python -m app.diagnostics.quote_diagnostics
python -m app.opportunities.multi_dex_opportunity_engine
python -m app.opportunities.opportunity_explorer
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
```

Dashboard:

```bash
streamlit run streamlit_app.py
```

Open **System Health** and confirm:

- `provider_health.json` exists after diagnostics/autopilot.
- RPC providers show success/failure counts and scores.
- DEX providers show latency and last error/success.
- Quote snapshot is visible.

## Rollback plan

This release is rollback-friendly because it mainly adds new resilience modules and wraps existing quote/RPC calls.

To rollback:

1. Revert the v3.2 commit.
2. Clear runtime artifacts if needed:

```bash
rm -f data/provider_health.json
```

3. Re-run the v3.1 validation commands:

```bash
python -m app.diagnostics.quote_diagnostics
python -m app.reporting.paper_report
```

## Not included yet

- Real execution engine.
- PnL engine.
- Strategy optimization.
- Autonomous live trading.
