# CryptoAI v5.5 - ETH Route Architecture & Buffer Candidate Evidence

## Executive Summary

v5.5 focuses the next research phase on Base `WETH/USDC` and `USDC/WETH` across trusted swap venues instead of broadening too early.

It also evaluates a `0.20%` cost-buffer candidate against the unchanged `0.30%` production buffer. Current evidence can support research comparison, but not an automatic production-buffer reduction.

Live trading remains disabled.

## Key Changes

- Added `EthRouteArchitectureService`.
- Added `eth_route_architecture.json` and `eth_route_architecture.md`.
- Added route-level evidence for Base `WETH/USDC` and `USDC/WETH`.
- Added trusted-venue planning for Uniswap V2, Aerodrome, and future Base Uniswap V3 quote-provider implementation.
- Added buffer promotion gates for the `0.20%` candidate.
- Added real-money execution architecture stages for future v6 work.
- Integrated ETH Route Architecture into Dashboard, Report Audit, README, Operations docs, roadmap, changelog, and tests.

## Safety

v5.5 does not change:

- production cost buffer
- paper BUY threshold
- risk thresholds
- live-trading eligibility

`0.20%` remains research-only until a separate reviewed paper-buffer change is approved after all gates pass.

## Validation Commands

```bash
python -m app.research.eth_route_architecture_service
python -m app.reporting.report_audit
python -m compileall -q app tests
python -m unittest discover -s tests -v
```

## Git Commit Message

```text
v5.5 - Add ETH route architecture and buffer candidate evidence
```

## Rollback Instructions

```bash
git revert <v5.5-commit-sha>
```

Generated ETH Route Architecture reports can be removed and regenerated safely:

```bash
rm -f reports/eth_route_architecture.json reports/eth_route_architecture.md
```
