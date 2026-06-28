# CryptoAI v0.5 - Connector Framework + Estimated Net Opportunities

## What changed

This milestone introduces a cleaner quote-provider architecture:

- `QuoteProvider` interface
- `QuoteManager` to coordinate providers
- Updated Aerodrome and Uniswap providers
- Updated `QuoteService`
- Estimated net opportunity scanner
- Dashboard tab for estimated net opportunities

## Important safety note

The net opportunity scanner still uses conservative placeholder costs. It is for research only.
It is not a live trading signal and does not connect to a wallet.

## Run

```powershell
cd C:\Projects\CryptoAI
.\venv\Scripts\Activate.ps1
python -m streamlit run app/dashboard/main_dashboard.py
```

## Commit

```powershell
git add .
git commit -m "v0.5 - Add connector framework and net opportunity estimates"
git push
```
