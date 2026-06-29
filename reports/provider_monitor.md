# CryptoAI Provider Monitor

Generated: `2026-06-29T02:34:44Z`

## Summary

- Mode: `paper`
- Overall status: `CRITICAL`
- Providers: `4`
- Alerts: `4`
- Critical alerts: `4`

## Providers

| Chain | Type | Provider | Score | Status | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | 0 | 17.97 |  |
| base | dex | Aerodrome | 0 | CRITICAL | 8 | 9.45 | Aerodrome quote unavailable for this route/RPC. Provider kept registered; scanner will skip this row |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 75 | OK | 0 | 8.78 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | CRITICAL | 4 | 9.45 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| CRITICAL | base | dex | Aerodrome | Provider score 0 is at or below critical threshold. |
| CRITICAL | base | dex | Aerodrome | Provider has 8 consecutive failures. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider score 0 is at or below critical threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider has 4 consecutive failures. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
