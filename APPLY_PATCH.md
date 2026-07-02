# Apply v6.10 Safety / Speed / Observability Patch

This patch can be prepared while your bot is running, but do not overwrite files while the live process is active.

## Safe apply sequence

1. Let the current live run continue if you want.
2. When you are ready to upgrade, stop it with `Ctrl+C`.
3. From `C:\Projects\CryptoAI`, apply the patch:

```powershell
Expand-Archive -Force C:\path\to\CryptoAI_v6_10_safety_speed_observability_patch.zip C:\Temp\CryptoAI_v610
Copy-Item -Recurse -Force C:\Temp\CryptoAI_v610\CryptoAI_v6_10_safety_speed_observability_patch\app .
python -m compileall -q app tests scripts
```

## Recommended env values

```powershell
$env:CRYPTOAI_NEAR_PASS_THRESHOLD_USDC="0.001"
$env:CRYPTOAI_EXECUTOR_CODE_CACHE_TTL_SECONDS="60"
$env:CRYPTOAI_ATOMIC_NOTIONAL_SWEEP_USD="1"
$env:CRYPTOAI_ATOMIC_SWEEP_LEG_SLIPPAGE_BPS_LIST="1"
$env:CRYPTOAI_ATOMIC_ROUTE_SWEEP_VENUES="Uniswap V2,Uniswap V3"
$env:CRYPTOAI_ATOMIC_ROUTE_SWEEP_MAX_ATTEMPTS="12"
$env:CRYPTOAI_ATOMIC_ROUTE_SWEEP_STOP_ON_PASS="true"
```

## Validate

```powershell
python -m app.execution.atomic_arbitrage_execution_service --generate
Get-Content reports\atomic_live_arbitrage.json -Tail 160
```

Look for:

```text
performance_metrics
near_pass
atomic_route_simulation_passed
atomic_eth_call_passed
```

Only run live after the compile and report generation are clean.
