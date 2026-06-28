# CryptoAI v0.7 — Historical Storage and Analytics

## What this release adds

- SQLite database persistence at `data/cryptoai.db`
- Historical paper-trade storage
- Analytics service for stored paper-trading results
- Dashboard analytics tab with:
  - total stored rows
  - paper executed count
  - paper skipped count
  - total estimated net P/L
  - average estimated net P/L
  - best/worst estimated net P/L
  - estimated P/L by pair
  - recent stored paper trades

## Files added

- `app/storage/sqlite_store.py`
- `app/analytics/__init__.py`
- `app/analytics/paper_analytics_service.py`
- `docs/RELEASE_v0_7.md`

## Files replaced

- `app/papertrading/paper_service.py`
- `app/dashboard/main_dashboard.py`

## How to test

```powershell
cd C:\Projects\CryptoAI
.\venv\Scripts\Activate.ps1
python -m streamlit run app/dashboard/main_dashboard.py
```

Then:

1. Open the **Paper Trading** tab.
2. Click **Record current paper scan to database + CSV**.
3. Open the **Analytics** tab.
4. Confirm metrics and recent stored rows appear.

## Commit message

```powershell
git add .
git commit -m "v0.7 - Add historical storage and analytics"
git push
```
