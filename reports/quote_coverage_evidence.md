# CryptoAI Quote Coverage Evidence

Generated: `2026-06-30T07:46:45Z`

## Summary

- Implemented providers: `3`
- Configured pairs: `8`
- Active quoted pairs: `1`
- Provider gap pairs: `6`
- Quote-test gap pairs: `1`
- Provider status: `OK` with `0` alert(s)

## Pair Coverage

| Status | Chain | Pair | Score | DEXs | Implemented | Direct OK | Next Action |
|---|---|---|---:|---:|---:|---:|---|
| ACTIVE_QUOTED | base | WETH/USDC | 100 | 3 | 3 | 3 | Keep collecting quote, opportunity, and execution-cost evidence. |
| NEEDS_QUOTE_TEST | base | CBBTC/USDC | 65 | 3 | 3 | 0 | Run targeted quote diagnostics for base CBBTC/USDC across implemented providers. |
| ROUTER_OR_PROVIDER_GAP | ethereum | WETH/USDC | 25 | 3 | 0 | 0 | Add verified router metadata and quote providers for ethereum WETH/USDC. |
| ROUTER_OR_PROVIDER_GAP | arbitrum | WETH/USDC | 25 | 3 | 0 | 0 | Add verified router metadata and quote providers for arbitrum WETH/USDC. |
| ROUTER_OR_PROVIDER_GAP | polygon | WETH/USDC | 20 | 2 | 0 | 0 | Add verified router metadata and quote providers for polygon WETH/USDC. |
| ROUTER_OR_PROVIDER_GAP | ethereum | WBTC/USDC | 15 | 3 | 0 | 0 | Add verified router metadata and quote providers for ethereum WBTC/USDC. |
| ROUTER_OR_PROVIDER_GAP | arbitrum | WBTC/USDC | 15 | 3 | 0 | 0 | Add verified router metadata and quote providers for arbitrum WBTC/USDC. |
| ROUTER_OR_PROVIDER_GAP | polygon | WBTC/USDC | 10 | 2 | 0 | 0 | Add verified router metadata and quote providers for polygon WBTC/USDC. |

## Next Provider Targets

- `base CBBTC/USDC` NEEDS_QUOTE_TEST: Run targeted quote diagnostics for base CBBTC/USDC across implemented providers.
- `ethereum WETH/USDC` ROUTER_OR_PROVIDER_GAP: Add verified router metadata and quote providers for ethereum WETH/USDC.
- `arbitrum WETH/USDC` ROUTER_OR_PROVIDER_GAP: Add verified router metadata and quote providers for arbitrum WETH/USDC.
- `polygon WETH/USDC` ROUTER_OR_PROVIDER_GAP: Add verified router metadata and quote providers for polygon WETH/USDC.
- `ethereum WBTC/USDC` ROUTER_OR_PROVIDER_GAP: Add verified router metadata and quote providers for ethereum WBTC/USDC.

## Findings

- `INFO` 1 configured pair(s) have active two-DEX quote evidence.
- `ACTION` 7 configured pair(s) still need quote coverage before expansion.
- `ACTION` Next targeted quote test: base CBBTC/USDC.

## Notes

- Quote Coverage Evidence is paper-mode expansion planning.
- A configured pair is not tradeable evidence until at least two DEXes have recent OK quotes for the same route.
- This report does not add live trading, change thresholds, or approve new production venues.
