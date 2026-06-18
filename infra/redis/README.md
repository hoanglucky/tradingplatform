# Redis

Redis is used as the initial local event backbone and cache layer.

Recommended early channels:

- `market-data.candles`
- `indicators.updated`
- `strategies.signals`
- `paper-trading.orders`
- `alerts.dispatch`

For production, replace ad hoc channel names with versioned event schemas and add durable replay where required.

