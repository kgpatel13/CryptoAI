# CryptoAI v3.6 — Strategy Framework & Research Platform Foundation

## Objective

Transform CryptoAI from a single-strategy paper trading bot into a modular strategy platform.

## Added

- Strategy registry.
- Strategy configuration file: `config/strategies.json`.
- Ranked strategy signals.
- Strategy signal persistence.
- Strategy-level performance service.
- Strategy Center report: `reports/strategy_center.md` and `.json`.
- Dashboard Strategy Center page.
- Documentation under `docs/`.
- Tests for strategy registry, ranking, and reporting.

## Safety

- Strategies remain advisory only.
- AI ranking remains advisory only.
- Risk engine remains final authority.
- Live trading remains disabled by default.

## Validation

```bash
python -m compileall -q app
python -m unittest discover -s tests -v
python -m app.strategy.strategy_center
python -m app.automation.paper_autopilot --once
python -m app.reporting.paper_report
```

## Rollback

```bash
git checkout v3.5
```
