# CryptoAI Event Bus

CryptoAI v2.0 introduces an event-driven architecture.

## Why

A quantitative trading platform should not have every module directly calling every other module.

Instead, components publish events:

- QuoteRefreshStarted
- QuoteRefreshCompleted
- StrategySignalsGenerated
- AiRankingCompleted
- RiskAssessmentCompleted
- PaperExecutionCompleted
- SchedulerRunCompleted

## Benefits

- Better audit trail
- Easier debugging
- Cleaner automation loop
- Foundation for real-time dashboards
- Foundation for future workers and queues

## Current implementation

v2.0 uses an in-memory event bus plus SQLite event persistence through the existing `EventStore`.

Future versions can replace the in-memory bus with Redis Streams, Kafka, RabbitMQ, or another queue.
