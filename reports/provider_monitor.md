# CryptoAI Provider Monitor

Generated: `2026-06-29T02:28:53Z`

## Summary

- Mode: `paper`
- Overall status: `CRITICAL`
- Providers: `4`
- Alerts: `4`
- Critical alerts: `3`

## Providers

| Chain | Type | Provider | Score | Status | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | 0 | 25.35 |  |
| base | dex | Aerodrome | 0 | CRITICAL | 4 | 10.5 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 46 | DEGRADED | 2 | 18.0 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | CRITICAL | 2 | 10.5 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| CRITICAL | base | dex | Aerodrome | Provider score 0 is at or below critical threshold. |
| CRITICAL | base | dex | Aerodrome | Provider has 4 consecutive failures. |
| DEGRADED | base | rpc | Base:rpc1:https://base-rpc.publicnode.com | Provider score 46 is below degraded threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider score 0 is at or below critical threshold. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
