# CryptoAI v6.7.1 `_fmt` Hotfix

Fixes:

```text
AttributeError: 'AtomicArbitrageExecutionService' object has no attribute '_fmt'
```

Apply from project root:

```powershell
Ctrl+C
Expand-Archive -Force C:\path\to\CryptoAI_v6_7_1_fmt_hotfix.zip C:\Temp\CryptoAI_v6_7_1
Copy-Item -Recurse -Force C:\Temp\CryptoAI_v6_7_1\CryptoAI_v6_7_1_fmt_hotfix\app .
python -m compileall -q app tests scripts
```

Then rerun the full env setup and:

```powershell
python -m scripts.reset_live_runtime_state --confirm RESET_LIVE_STATE
python -m app.execution.atomic_arbitrage_execution_service --generate
```
