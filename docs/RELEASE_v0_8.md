# CryptoAI v0.8 — Professional Data Engine Foundation

## What this release adds

- RPC fallback support in `RpcClient`
- Comma-separated RPC URL support in `.env`
- Lightweight in-memory TTL quote cache
- Quote Manager request throttling for public RPC safety
- Smaller default quote set to reduce Base public RPC rate limits
- Friendlier Aerodrome error handling and volatile/stable route fallback
- System Health dashboard tab
- Quote provider status and quote error categorization
- Full dashboard refresh with v0.8 roadmap

## Why this matters

Earlier releases proved that CryptoAI could read real on-chain quotes, but public RPC endpoints can return `429 Too Many Requests` or route-specific quote failures. v0.8 makes those conditions visible and less disruptive instead of treating them as unexpected app failures.

## Recommended `.env` update

You can keep your existing `.env`, but v0.8 supports multiple RPC URLs per chain:

```env
BASE_RPC=https://mainnet.base.org,https://base-rpc.publicnode.com
POLYGON_RPC=https://polygon-bor-rpc.publicnode.com,https://polygon-rpc.com
ARBITRUM_RPC=https://arb1.arbitrum.io/rpc,https://arbitrum-one-rpc.publicnode.com
ETHEREUM_RPC=https://ethereum-rpc.publicnode.com,https://rpc.ankr.com/eth
```

A private RPC from Alchemy/Infura/QuickNode/Ankr will be more reliable than public RPCs.

## How to test

```powershell
cd C:\Projects\CryptoAI
.\venv\Scripts\Activate.ps1
python -m streamlit run app/dashboard/main_dashboard.py
```

Then check:

1. Chain Health tab shows `RPC Used`.
2. DEX Quotes tab loads without crashing.
3. System Health tab shows registered providers and quote success rate.
4. Paper Trading and Analytics still work.

## Commit message

```powershell
git add .
git commit -m "v0.8 - Add RPC failover quote cache and system health"
git push
```
