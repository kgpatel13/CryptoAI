# CryptoAI Event Model

CryptoAI already has an internal event bus and SQLite event table. v4.0 starts using events as part of the research platform.

## Target event types

- QuoteReceived
- QuoteRejected
- OpportunityDetected
- SignalGenerated
- RiskApproved
- RiskRejected
- OrderSubmitted
- OrderFilled
- PositionOpened
- PositionClosed
- PnLUpdated
- AnalyticsUpdated
- FeatureStoreUpdated

## Design rule

Events should be immutable facts. Derived state can be rebuilt from event history, but historical events should not be mutated.
