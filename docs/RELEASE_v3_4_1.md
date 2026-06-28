# CryptoAI v3.4.1 — Paper Accounting & Execution Integrity Hotfix

## Objective

This maintenance release fixes paper portfolio accounting after the v3.4 professional execution engine release.

The main issue was inverse-pair accounting for routes such as `USDC/WETH`. A raw DEX quote for `USDC/WETH` is expressed as WETH per USDC, not USD per USDC. v3.4 could incorrectly treat that raw quote as a USD price, creating unrealistic token quantities and impossible paper PnL.

## Fixes

- Added canonical paper accounting utilities.
- Normalized all paper positions to USD-denominated accounting.
- Fixed inverse-pair quantity calculation for `USDC/WETH`.
- Fixed position close/PnL math to use notional USD and market value USD.
- Added automatic legacy state repair for corrupted v3.4 paper portfolio state.
- Added `python -m app.portfolio.repair_portfolio` utility.
- Added regression tests for WETH/USDC, USDC/WETH, legacy repair, and PnL clamping.

## Safety

- Paper trading only.
- Live trading remains disabled.
- This release changes accounting correctness only; it does not enable live execution.

## New command

Repair existing paper state:

```bash
python -m app.portfolio.repair_portfolio
```

Reset paper portfolio state for clean validation:

```bash
python -m app.portfolio.repair_portfolio --reset
```

## Validation

```bash
python -m compileall -q app
python -m unittest discover -s tests -v
python -m app.portfolio.repair_portfolio
python -m app.reporting.paper_report
```

Then run the standard paper pipeline:

```bash
python -m app.diagnostics.quote_diagnostics
python -m app.opportunities.multi_dex_opportunity_engine
python -m app.opportunities.opportunity_explorer
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
```

## Expected result

Paper portfolio cash should remain close to the configured initial cash plus/minus realistic paper PnL. It should no longer jump from `$10,000` to six figures due to inverse-pair quantity math.

## Rollback

```bash
git log --oneline
git revert <v3.4.1_commit_hash>
git push
```
