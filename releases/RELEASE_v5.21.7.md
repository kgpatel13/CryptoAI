# v5.21.7 - Paper Edge-Probe Threshold

Date: 01-Jul-2026

## Summary

Adds a controlled paper-only edge-probe mode by lowering the strict live-shadow paper BUY threshold from `0.30%` to `0.25%`.

## Guardrails

- Production cost buffer remains `0.30%`.
- Live trading remains disabled.
- The lower paper threshold is valid only when `require_live_shadow_eligible_for_paper=true`.
- Any non-shadow-eligible candidate is still recorded as zero-notional `SKIPPED`, not a profitable paper fill.

## Changes

- Updates the `live_parity_500` paper profile to export `CRYPTOAI_MIN_EDGE_FOR_PAPER_PCT=0.25`.
- Wires opportunity labeling to the runtime paper threshold instead of hardcoded `0.30%`.
- Shows the configured threshold on Mission Control.
- Adds validation coverage proving ordinary paper profiles still require `0.30%`.

## Early Result

The probe successfully surfaced candidates above `0.25%`, but live-shadow enforcement blocked them as `PAPER_ONLY` because execution realism remained `NOT_EXECUTABLE` and stress net edge stayed negative.

## Verification

- `python -m unittest tests.test_paper_settings_service`
- `python -m unittest discover -s tests -p "test_*.py"`

Full regression passed with 154 tests.
