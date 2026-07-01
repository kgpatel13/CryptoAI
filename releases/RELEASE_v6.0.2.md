# v6.0.2 - Enable Base Uniswap V2 Atomic Route Selection

## Summary

Fixes the atomic route selection gap where Base `Uniswap V2 -> Uniswap V3` shadow-ready routes were visible in execution realism but excluded from live transaction simulation.

## Changes

- Added Uniswap V2 to the approved Base live/atomic DEX scope.
- Updated transaction simulation to select Uniswap V2 two-leg candidates instead of falling back to one-leg smoke mode.
- Updated live guard and feature-flag defaults to include Uniswap V2.
- Added decoded atomic executor custom errors, including `ProfitTooLow`.

## Current Behavior

The latest atomic route now builds calldata and reaches the deployed executor in `eth_call`. The executor correctly rejects the route when simulated final USDC output is below the required profitable output.

## Suggested Commit Message

`v6.0.2 - Enable Uniswap V2 atomic route selection`
