# CryptoAI Provider Monitor

Generated: `2026-06-29T12:47:53Z`

## Summary

- Mode: `paper`
- Overall status: `CRITICAL`
- Providers: `4`
- Alerts: `4`
- Critical alerts: `2`

## Providers

| Chain | Type | Provider | Score | Status | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | 0 | 39.85 |  |
| base | dex | Aerodrome | 50 | DEGRADED | 0 | 38.93 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 93 | OK | 0 | 38.93 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | CRITICAL | 4 | 36797.93 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| DEGRADED | base | dex | Aerodrome | Provider score 50 is below degraded threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider score 0 is at or below critical threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider has 4 consecutive failures. |
| WATCH | base | rpc | Base:rpc2:https://mainnet.base.org | Provider observation is stale at 36797.93 seconds old. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
