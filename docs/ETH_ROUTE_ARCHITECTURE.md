# CryptoAI ETH Route Architecture

## Purpose

ETH Route Architecture focuses the system on one chain and one core ETH route before broader expansion:

- Chain: Base
- Routes: `WETH/USDC` and `USDC/WETH`
- Active venues: Uniswap V2-compatible router, Aerodrome, and Uniswap V3
- Next evidence target: sustained three-venue Base ETH route diagnostics

The report compares the unchanged `0.30%` production buffer against a `0.20%` research candidate. It does not change production settings.

## Why Base First

Base is the current focus because it has implemented quote providers for Uniswap V2, Aerodrome, and Uniswap V3, with route evidence still required before any live-readiness decision.

Ethereum, Arbitrum, and Polygon remain useful future surfaces, but they should not become active trade targets until router metadata, quote providers, route diagnostics, and provider health evidence are implemented.

## Buffer Rule

`0.20%` may remain a research candidate when replay shows more positive signals than `0.30%`.

It should not become the production buffer until all promotion gates pass:

- execution-cost confidence is high
- filled paper slippage sample is at least 30
- quote OK rate is at least 90%
- Base `WETH/USDC` has active two-DEX quote evidence
- provider status is not critical or degraded
- report audit is clean
- `0.20%` candidate has at least 30 positive-after-buffer replay signals
- average candidate net edge is at least 0.03%

## Real-Money Architecture

Future live execution should follow this gated path:

1. Quote fanout across trusted Base venues.
2. Opportunity and cost gate with fresh quotes, net-edge checks, and replay evidence.
3. Risk gate for sizing, cooldowns, exposure, daily loss, and kill switch controls.
4. Transaction preflight with allowance caps, exact calldata simulation, `amountOutMin`, deadline, and nonce control.
5. Execution and reconciliation with receipt verification, gas attribution, balance checks, and automatic halt on mismatch.

## Command

```bash
python -m app.research.eth_route_architecture_service
```

## Outputs

- `reports/eth_route_architecture.json`
- `reports/eth_route_architecture.md`

## References

- [Uniswap v3 Base deployments](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-base-deployments)
- [Uniswap deployments guidance](https://developers.uniswap.org/docs/protocols/v3/deployments)
- [Aerodrome documentation](https://aerodrome.finance/docs)
