# API

Base URL in local development:

```txt
http://localhost:8000
```

Market-data service base URL:

```txt
http://localhost:8101
```

## Status endpoints

### `GET /`

Returns the API service identity.

Example response:

```json
{
  "name": "trading-framework-api",
  "status": "ready"
}
```

### `GET /health`

Lightweight liveness endpoint. This endpoint does not check external dependencies.

Example response:

```json
{
  "status": "ok",
  "service": "trading-framework-api",
  "environment": "development",
  "trading_mode": "paper"
}
```

### `GET /health/ready`

Readiness endpoint for dependency checks.

Current dependencies:

- PostgreSQL
- Redis

Example ready response:

```json
{
  "status": "ready",
  "dependencies": [
    {
      "name": "postgres",
      "status": "ok",
      "detail": null
    },
    {
      "name": "redis",
      "status": "ok",
      "detail": null
    }
  ]
}
```

Example degraded response:

```json
{
  "status": "degraded",
  "dependencies": [
    {
      "name": "postgres",
      "status": "error",
      "detail": "ConnectionRefusedError"
    },
    {
      "name": "redis",
      "status": "ok",
      "detail": null
    }
  ]
}
```

## Safety endpoints

### `GET /safety`

Returns the active trading safety posture.

Example response:

```json
{
  "default_trading_mode": "paper",
  "live_trading_enabled": false,
  "exchange_writes_allowed": false,
  "exchange_adapter_mode": "read_only"
}
```

Rules:

- `live_trading_enabled` must remain `false` in the MVP.
- `exchange_writes_allowed` must remain `false` in the MVP.
- Exchange adapters are read-only unless a later task explicitly changes the architecture and safety model.

## Market WebSocket

### `WS /ws/market`

Connect to `ws://localhost:8000/ws/market`, then send a subscription:

```json
{
  "type": "subscribe",
  "symbol": "BTCUSDT",
  "timeframe": "1m"
}
```

Supported timeframes are `1m`, `5m`, `15m`, `1h`, `4h`, and `1d`. Symbols are normalized to uppercase.

The server first acknowledges the active subscription:

```json
{
  "type": "subscribed",
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "source": "binance",
  "mock": false
}
```

It then broadcasts normalized updates from Binance's public kline stream:

```json
{
  "type": "candle",
  "symbol": "BTCUSDT",
  "timeframe": "1m",
  "timestamp": "2026-06-23T08:43:00Z",
  "open": 62418.39,
  "high": 62440.01,
  "low": 62405.88,
  "close": 62440.0,
  "volume": 40.90346,
  "closed": false,
  "source": "binance",
  "mock": false
}
```

Clients may send another valid subscribe message on the same connection. Invalid subscriptions receive an `invalid_subscription` error and can be retried without reconnecting.

The API shares one upstream Binance connection between clients using the same symbol/timeframe. If Binance disconnects, clients receive a `market_stream_reconnecting` error event while the hub retries with bounded exponential backoff. The queue for each client is bounded; when a client cannot keep up, the oldest pending update is replaced by newer market data.

Current realtime support is for Binance-listed symbols. Oanda-only symbols remain available through the historical candle HTTP endpoint and require a future realtime adapter.

Configuration:

```env
BINANCE_WS_BASE_URL=wss://data-stream.binance.vision/ws
MARKET_STREAM_RECONNECT_SECONDS=1
MARKET_STREAM_MAX_RECONNECT_SECONDS=30
```

The Binance stream is public and read-only. No API key, account access, order action, or exchange write operation is used.

## Module endpoints

### `GET /modules`

Returns the current service/module registry for the MVP scaffold.

Example response:

```json
[
  {
    "name": "market-data",
    "role": "Normalize quotes, candles, and order book snapshots.",
    "status": "scaffolded"
  },
  {
    "name": "exchange-adapters",
    "role": "Read-only exchange connectivity until explicitly enabled.",
    "status": "read_only"
  }
]
```

## Symbol endpoints

These endpoints manage the MVP symbol catalog stored in PostgreSQL. They do not place orders and do not connect to exchange write APIs.

### `GET /symbols`

Lists symbols.

Query parameters:

- `limit`: default `100`, max `500`
- `offset`: default `0`
- `active_only`: default `false`

### `GET /symbols/{symbol_id}`

Returns one symbol by UUID. Returns `404` when the symbol does not exist.

### `POST /symbols`

Creates a symbol.

Example request:

```json
{
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "is_active": true
}
```

Returns `409` when the same `exchange + symbol` already exists.

### `PATCH /symbols/{symbol_id}`

Updates one or more symbol fields.

Example request:

```json
{
  "is_active": false
}
```

Returns `404` when the symbol does not exist and `409` when the update would duplicate another symbol.

### `DELETE /symbols/{symbol_id}`

Deletes a symbol. Returns `204` on success or `404` when the symbol does not exist.

## Market Data Endpoints

Market-data endpoints are served by `services/market-data` on port `8101`.

### `GET /market/candles`

Returns normalized candles for a symbol and time range.

Required query parameters:

- `symbol`: internal symbol such as `BTCUSDT` or `XAUUSD`
- `timeframe`: provider-supported timeframe such as `1m`, `5m`, `1h`, or `1d`
- `start`: timezone-aware ISO 8601 datetime
- `end`: timezone-aware ISO 8601 datetime

Binance example:

```bash
curl "http://localhost:8101/market/candles?symbol=BTCUSDT&timeframe=1m&start=2024-06-19T08:00:00Z&end=2024-06-19T09:00:00Z"
```

Oanda example:

```bash
curl "http://localhost:8101/market/candles?symbol=XAUUSD&timeframe=5m&start=2024-06-19T08:00:00Z&end=2024-06-19T09:00:00Z"
```

Example response:

```json
[
  {
    "symbol": "BTCUSDT",
    "timeframe": "1m",
    "timestamp": "2024-06-19T08:00:00Z",
    "open": "65000.10000000",
    "high": "65100.25000000",
    "low": "64950.00000000",
    "close": "65050.50000000",
    "volume": "123.45600000"
  }
]
```

Provider selection:

- `XAUUSD`, `SP500`, and `US100` use Oanda.
- Other registered symbols currently use Binance.

Cache behavior:

- A fully covered range is returned from PostgreSQL without an external provider request.
- An incomplete range is fetched from the selected provider and upserted into PostgreSQL.
- Duplicate provider rows are collapsed by timestamp before upsert.
- PostgreSQL guarantees uniqueness by symbol, timeframe, and timestamp.

Error responses:

- `400`: unsupported timeframe, invalid range, or provider validation error
- `404`: symbol is not registered in the symbol catalog
- `422`: required query parameter is missing or malformed
- `502`: Binance or Oanda upstream request failed
- `503`: required provider configuration, such as `OANDA_API_TOKEN`, is missing

### Market-data configuration

```env
DATABASE_URL=postgresql+asyncpg://trader:trader@postgres:5432/trading_framework
OANDA_API_TOKEN=
OANDA_ACCOUNT_ID=
OANDA_ENVIRONMENT=practice
```

Binance public candle requests require no API key. Oanda credentials must remain outside version control. No market-data endpoint places or modifies orders.

## Day 2 implementation notes

Backend route structure:

```txt
apps/api/app/
├── api/
│   ├── router.py
│   └── routes/
│       ├── health.py
│       ├── modules.py
│       └── safety.py
├── core/
│   ├── config.py
│   └── logging.py
├── main.py
└── schemas/
```

The API currently has no authentication layer. Add auth before introducing user-specific portfolio, watchlist, exchange credential, or account data endpoints.
