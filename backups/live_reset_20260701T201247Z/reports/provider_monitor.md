# CryptoAI Provider Monitor

Generated: `2026-07-01T20:11:58Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 98.31 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 99.26 |  |
| base | dex | Uniswap V3 | 100 | OK | OK | True | 0 | 96.11 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 92822.52 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 97 | OK | OK | True | 0 | 15.97 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 92822.52 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
