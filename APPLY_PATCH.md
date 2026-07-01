# CryptoAI v6.2 Live Route Refresh Fix

## Purpose
Fix the current live blocker where a stale or previously failed atomic route is reused and where a BUY + SHADOW_READY row can be visible in diagnostics but not selected for current-cycle atomic simulation.

## Files changed

- `app/execution/transaction_simulation_service.py`
- `app/execution/live_execution_engine_service.py`
- `app/execution/atomic_live_adapter.py`

## What changed

1. `transaction_simulation_service` now refreshes the live-route evidence chain before selecting an atomic candidate:
   - quote diagnostics
   - opportunity explorer / multi-DEX opportunity scan
   - pool-depth ladder when available
   - execution realism

2. Candidate selection now has a freshness window:
   - Default: `CRYPTOAI_ATOMIC_MAX_CANDIDATE_AGE_SECONDS=45`
   - stale candidates are rejected with explicit diagnostics instead of being silently reused.

3. `live_execution_engine_service` now regenerates the atomic route report on each live execution readiness cycle instead of reading an old `atomic_live_arbitrage.json`.

4. `atomic_live_adapter` now regenerates the atomic report immediately before send and refuses early if `CRYPTOAI_ATOMIC_EXECUTOR_SEND_ENABLED` is not true.

## Apply

Copy the `app` folder from this patch into your project root and allow overwrite.

## Validation

Use a clean PowerShell terminal for tests first:

```powershell
Remove-Item Env:\CRYPTOAI_PRIVATE_KEY -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_LIVE_TRADING_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_LIVE_KILL_SWITCH_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_LIVE_AUTOPILOT_SEND_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_ATOMIC_EXECUTOR_SEND_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_ATOMIC_EXECUTOR_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_LIVE_EXECUTION_ADAPTER -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_LIVE_WALLET_ADDRESS -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_MAX_LIVE_TRADE_USD -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_MAX_DAILY_LOSS_USD -ErrorAction SilentlyContinue
Remove-Item Env:\CRYPTOAI_MAX_LIVE_WALLET_USD -ErrorAction SilentlyContinue

python -m compileall -q app tests scripts
python -m unittest tests.test_transaction_simulation_service tests.test_atomic_arbitrage_execution_service tests.test_live_execution_engine_service tests.test_atomic_live_adapter tests.test_live_autopilot -v
```

Then in a separate live-readiness terminal:

```powershell
$env:CRYPTOAI_LIVE_TRADING_ENABLED="false"
$env:CRYPTOAI_LIVE_KILL_SWITCH_ENABLED="true"
Remove-Item Env:\CRYPTOAI_PRIVATE_KEY -ErrorAction SilentlyContinue

$env:CRYPTOAI_ATOMIC_EXECUTOR_ENABLED="true"
$env:CRYPTOAI_ATOMIC_EXECUTOR_REVIEWED="true"
$env:CRYPTOAI_ATOMIC_EXECUTOR_ADDRESS="0xf714213aec4d8DD3c95B209f5F5193c8C9ea4508"
$env:CRYPTOAI_LIVE_EXECUTION_ADAPTER="atomic"
$env:CRYPTOAI_LIVE_WALLET_ADDRESS="0x3e4E81ec69A073f157c6945C41e5C36FdA7579a7"
$env:CRYPTOAI_MAX_LIVE_TRADE_USD="19"
$env:CRYPTOAI_MAX_DAILY_LOSS_USD="20"
$env:CRYPTOAI_MAX_LIVE_WALLET_USD="420"
$env:CRYPTOAI_ATOMIC_MAX_CANDIDATE_AGE_SECONDS="45"

python -m app.execution.atomic_arbitrage_execution_service --generate
python -m app.execution.live_execution_engine_service
```

Proceed to a live send only if the current-cycle report shows:

```text
atomic_route_simulation_passed: true
can_run_continuous_live: true
```

For the first send, use:

```powershell
python -m app.execution.live_autopilot --loop --interval-seconds 30 --max-cycles 1
```

## Important

This patch does not force a trade. It fixes stale route reuse and makes the current-cycle simulation authoritative. If the route is unprofitable or no fresh SHADOW_READY candidate exists, live remains blocked.
