# CryptoAI Provider Monitor

Generated: `2026-07-02T00:56:14Z`

## Summary

- Mode: `paper`
- Overall status: `OK`
- Providers: `5`
- Alerts: `1`
- Critical alerts: `0`

## Providers

| Chain | Type | Provider | Score | Current | Rolling | Required | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---|---|---:|---:|---|
| base | dex | Aerodrome | 100 | OK | OK | True | 0 | 58.1 |  |
| base | dex | Uniswap V2 | 100 | OK | OK | True | 0 | 59.29 |  |
| base | dex | Uniswap V3 | 99 | OK | OK | True | 0 | 56.02 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 100 | WATCH | OK | False | 0 | 109879.04 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 97 | OK | OK | True | 0 | 15.96 |  |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 109879.04 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
