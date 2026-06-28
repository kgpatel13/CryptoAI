# CryptoAI Deployment and Paper-Test Plan

## What is remaining before live trading

CryptoAI still needs these before real money:

1. More reliable real-time market-data workers.
2. Proper paper portfolio ledger with persistent balances.
3. More realistic slippage, gas, and fee model.
4. Multi-day/month paper performance reports.
5. Alerting when strategy quality drops.
6. Manual approval workflow.
7. Exchange/wallet integration only after paper trading proves edge.
8. Security review before any private key is used.

## Recommended paper-testing path

### Phase A — Local
Run:

```powershell
python -m app.automation.paper_autopilot --loop --interval-seconds 300 --max-cycles 3
```

### Phase B — GitHub Actions scheduled paper checks
Use `.github/workflows/paper-autopilot.yml`.

This is free for many GitHub accounts/public repos and good for periodic paper checks. It is not true high-frequency trading.

### Phase C — Dashboard deployment
Use Streamlit Community Cloud for dashboard only.

Main file:

```text
app/dashboard/main_dashboard.py
```

### Phase D — Always-on worker
For real always-on paper trading, use a paid or persistent worker host. Free services often sleep.

## 1 ETH paper mode

Do not use real ETH yet. Treat 1 ETH as a simulated notional amount. The current engine mostly tracks USD notional; multi-asset ledger is next.
