# CryptoAI v0.6 — Paper Trading Simulation

## What this release adds

- Quote provider interface and quote manager refresh
- Base Aerodrome + Uniswap V2 quote providers
- Gross opportunity scanner
- Conservative estimated net opportunity scanner
- Paper trading simulation engine
- CSV storage helper
- Dashboard tab for paper trading
- Optional CSV recording to `data/paper_trades.csv`

## Safety status

This release still has:

- No wallet integration
- No private keys
- No transaction signing
- No real trading

Everything is read-only or simulated.

## Install / replace steps

1. Unzip this package.
2. Copy the `app`, `docs`, and `data` folders into your existing `C:\Projects\CryptoAI` folder.
3. Allow Windows to replace files when asked.
4. Run:

```powershell
cd C:\Projects\CryptoAI
.\venv\Scripts\Activate.ps1
python -m streamlit run app/dashboard/main_dashboard.py
```

## Verify

Open the dashboard and check these tabs:

- DEX Quotes
- Gross Opps
- Net Estimates
- Paper Trading

Click **Record current paper scan to CSV** to create or append rows to:

```text
data/paper_trades.csv
```

## Commit

```powershell
git add .
git commit -m "v0.6 - Add paper trading simulation"
git push
```
