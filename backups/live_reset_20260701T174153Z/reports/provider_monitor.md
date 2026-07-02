# CryptoAI Provider Monitor

Generated: `2026-07-01T17:26:33Z`

## Summary

- Mode: `paper`
- Overall status: `WATCH`
- Providers: `5`
- Alerts: `4`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | WATCH | OK | True | 0 | 4277.79 |  |
| base | dex | Uniswap V2 | 100 | WATCH | OK | True | 0 | 4276.16 |  |
| base | dex | Uniswap V3 | 100 | WATCH | OK | True | 0 | 4272.18 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 82898.25 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 98 | OK | OK | True | 0 | 0.96 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | dex | Aerodrome | Provider observation is stale at 4277.79 seconds old. |
| WATCH | base | dex | Uniswap V2 | Provider observation is stale at 4276.16 seconds old. |
| WATCH | base | dex | Uniswap V3 | Provider observation is stale at 4272.18 seconds old. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 82898.25 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
