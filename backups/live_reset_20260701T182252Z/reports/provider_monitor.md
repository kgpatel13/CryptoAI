# CryptoAI Provider Monitor

Generated: `2026-07-01T18:22:29Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 268.85 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 269.81 |  |
| base | dex | Uniswap V3 | 100 | OK | OK | True | 0 | 266.84 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 86253.67 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 97 | OK | OK | True | 0 | 15.79 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 86253.67 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
