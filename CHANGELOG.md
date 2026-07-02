# CryptoAI v6.10 Safety / Speed / Observability Patch

Builds on v6.9.1 executor V2 Python support.

## Added

- Near-pass detection for routes whose exact atomic shortfall is within `CRYPTOAI_NEAR_PASS_THRESHOLD_USDC` (default `0.001`).
- `performance_metrics` in `reports/atomic_live_arbitrage.json` and markdown output.
- `elapsed_ms` on Base `eth_call` results for latency visibility.
- Short TTL cache for executor bytecode lookup via `CRYPTOAI_EXECUTOR_CODE_CACHE_TTL_SECONDS` (default `60`).
- Better markdown summary fields for near-pass and elapsed time.

## Safety

- Does not relax the executor profit guard.
- Does not change min profit logic.
- Does not sign or broadcast from the atomic report service.
- `atomic_eth_call_passed` is still the final gate.
