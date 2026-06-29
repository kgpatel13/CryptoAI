# CryptoAI Provider Monitor

Generated: `2026-06-29T02:43:22Z`

## Summary

- Mode: `paper`
- Overall status: `CRITICAL`
- Providers: `4`
- Alerts: `3`
- Critical alerts: `3`

## Providers

| Chain | Type | Provider | Score | Status | Consecutive Failures | Age Seconds | Error |
|---|---|---|---:|---|---:|---:|---|
| base | dex | Uniswap V2 | 100 | OK | 0 | 10.57 |  |
| base | dex | Aerodrome | 20 | CRITICAL | 0 | 9.59 |  |
| base | rpc | Base:rpc1:https://base-rpc.publicnode.com | 81 | OK | 0 | 9.59 |  |
| base | rpc | Base:rpc2:https://mainnet.base.org | 0 | CRITICAL | 4 | 526.7 | BadFunctionCallOutput: Could not transact with/call contract function, is contract deployed correctl |

## Alerts

| Severity | Chain | Type | Provider | Message |
|---|---|---|---|---|
| CRITICAL | base | dex | Aerodrome | Provider score 20 is at or below critical threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider score 0 is at or below critical threshold. |
| CRITICAL | base | rpc | Base:rpc2:https://mainnet.base.org | Provider has 4 consecutive failures. |

## Notes

- Provider Monitor summarizes existing provider-health observations.
- It does not make network calls or execute trades.
- Missing provider observations should be treated as incomplete operational evidence.
