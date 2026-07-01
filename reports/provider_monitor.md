# CryptoAI Provider Monitor

Generated: `2026-07-01T15:38:44Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 37.4 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 35.67 |  |
| base | dex | Uniswap V3 | 99 | OK | OK | True | 0 | 32.2 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 76429.2 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 99 | OK | OK | True | 0 | 30.53 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 76429.2 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
