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

Supported timeframes are `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, and `1d`. Symbols are normalized to uppercase.

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

It then broadcasts normalized updates from the routed Binance or Oanda source:

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

The API periodically sends an application heartbeat:

```json
{
  "type": "heartbeat",
  "id": 1,
  "timestamp": "2026-06-29T04:00:00Z"
}
```

Clients must respond with the matching id:

```json
{
  "type": "pong",
  "id": 1
}
```

A client that does not return a matching pong before `MARKET_WS_STALE_SECONDS` is closed with WebSocket code `1001`. Sending the same subscription repeatedly only returns another acknowledgement; it does not create a duplicate upstream subscription.

The API shares one upstream source between clients using the same symbol/timeframe. If a provider disconnects, clients receive a `market_stream_reconnecting` error event while the hub retries with bounded exponential backoff. The queue for each client is bounded; when a client cannot keep up, the oldest pending update is replaced by newer market data.

Realtime support includes Binance-listed symbols plus Oanda `XAUUSD`, `SP500`, and `US100`. Oanda maps `30m` to `M30` and `2h` to `H2`, and updates the current read-only instrument candle every two seconds by default because the configured account pricing stream returns `403`.

Configuration:

```env
BINANCE_WS_BASE_URL=wss://data-stream.binance.vision/ws
MARKET_STREAM_RECONNECT_SECONDS=1
MARKET_STREAM_MAX_RECONNECT_SECONDS=30
OANDA_REALTIME_POLL_SECONDS=2
MARKET_WS_HEARTBEAT_SECONDS=10
MARKET_WS_STALE_SECONDS=30
NEXT_PUBLIC_MARKET_WS_RECONNECT_MS=1000
NEXT_PUBLIC_MARKET_WS_MAX_RECONNECT_MS=15000
```

Both realtime paths are read-only. No order action or exchange write operation is available.

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

## MVP User Endpoint

### `GET /users/me`

Returns the configured single local user. The first request creates the user in PostgreSQL; later requests return the same UUID.

```json
{
  "id": "68b41c54-5623-4cdb-81b4-87c64b97b8a1",
  "email": "local@trading-framework.test",
  "display_name": "Local Trader",
  "created_at": "2026-06-29T05:00:00Z",
  "updated_at": "2026-06-29T05:00:00Z",
  "mode": "mvp_local"
}
```

Configuration:

```env
MVP_USER_MODE=true
MVP_USER_EMAIL=local@trading-framework.test
MVP_USER_DISPLAY_NAME=Local Trader
```

When `MVP_USER_MODE=false`, the endpoint returns `503` because real authentication is not implemented. This mode has no password, session, authorization, or user isolation. Watchlist and settings APIs use the same `get_mvp_user` dependency, but full authentication is required before exposing user-specific data publicly.

## Watchlist Endpoints

All watchlist endpoints resolve ownership through the MVP user dependency. They are unavailable when `MVP_USER_MODE=false`.

### `GET /watchlist`

Returns the configured user's default watchlist and creates it on first use.

```json
{
  "id": "d489db73-5f37-4ced-846a-087c285ab50d",
  "user_id": "68b41c54-5623-4cdb-81b4-87c64b97b8a1",
  "name": "Main",
  "items": [
    {
      "id": "f865c561-d747-48d2-bc85-d0c5ae7a2046",
      "symbol_id": "c2c4e1dd-1c45-47bd-989a-1ad671949933",
      "exchange": "binance",
      "symbol": "BTCUSDT",
      "base_asset": "BTC",
      "quote_asset": "USDT",
      "created_at": "2026-06-29T06:00:00Z"
    }
  ]
}
```

### `POST /watchlist/items`

Adds an active symbol from the catalog. Input is whitespace-trimmed and normalized to uppercase.

```json
{
  "symbol": "BTCUSDT"
}
```

Returns `201` on success, `404` when the active symbol does not exist, and `409` when it is already in the watchlist.

### `DELETE /watchlist/items/{symbol}`

Removes a symbol and returns `204`. Returns `404` when the active catalog symbol or watchlist item does not exist.

Configuration:

```env
MVP_WATCHLIST_NAME=Main
```

## User Settings Endpoints

Settings belong to the configured MVP user and are created lazily with `BTCUSDT`, `15m`, no indicators, system theme, and UTC timezone.

### `GET /settings`

Returns the current persisted preferences.

### `PATCH /settings`

Accepts any subset of `default_symbol`, `default_timeframe`, `selected_indicators`, `theme`, and `timezone`. The default symbol must exist in the active catalog; timeframe and theme use fixed choices; indicators use unique lowercase slug names; timezone must be a valid IANA name.

The chart uses `timezone` only to format candle opening times on its axis and crosshair. Provider and database candle timestamps remain UTC opening instants; derived close times do not shift chart coordinates.

It also accepts `multi_timeframe_layout` with one active catalog symbol, `windowCount` of 1/2/4/8, and up to eight uniquely identified windows containing timeframe, enabled, and manual `reviewChecked` state. Invalid nested layouts return `422`; unknown active symbols return `404`.

```json
{
  "default_symbol": "XAUUSD",
  "default_timeframe": "5m",
  "selected_indicators": ["sma", "rsi_14"],
  "theme": "dark",
  "timezone": "Asia/Bangkok"
}
```

## Market Data Endpoints

Market-data endpoints are served by `services/market-data` on port `8101`.

### `GET /market/candles`

Returns normalized candles and request metadata for a symbol and time range.

Required query parameters:

- `symbol`: internal symbol such as `BTCUSDT` or `XAUUSD`
- `timeframe`: native or custom interval such as `1m`, `7m`, `10m`, `45m`, `3h`, `2w`, or `1M`
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

Custom Oanda example (`10m` aggregates from native `5m` candles):

```bash
curl "http://localhost:8101/market/candles?symbol=XAUUSD&timeframe=10m&start=2024-06-19T08:00:00Z&end=2024-06-19T10:00:00Z"
```

Example response:

```json
{
  "candles": [
    {
      "symbol": "XAUUSD",
      "timeframe": "10m",
      "timestamp": "2024-06-19T08:00:00Z",
      "open": "2325.10000000",
      "high": "2327.25000000",
      "low": "2324.90000000",
      "close": "2326.50000000",
      "volume": "123.00000000",
      "partial": false,
      "complete": true,
      "source_count": 2,
      "expected_source_count": 2,
      "missing_source_count": 0
    }
  ],
  "metadata": {
    "source_provider": "oanda",
    "source_market_type": "cfd_fx",
    "aggregation_used": true,
    "base_timeframe": "5m",
    "cache_hit": false,
    "missing_ranges_fetched": 1,
    "partial_candle_count": 0,
    "incomplete_candle_count": 0,
    "missing_source_candle_count": 0
  }
}
```

Timeframe rules:

- Ordinary values use positive integer `m`, `h`, `d`, or `w` units and cannot exceed one month.
- `1m` means one minute; exact `1M` means one calendar month.
- Weeks start Monday UTC. Calendar months start on the first day at `00:00:00Z`.
- The target must be an exact multiple of an available native base timeframe.
- Invalid values such as `0m`, `-5m`, `1x`, or `5w` return `400`.

Provider selection:

- `XAUUSD`, `SP500`, and `US100` use Oanda.
- Other registered symbols currently use Binance.

Cache behavior:

- A fully covered range is returned from PostgreSQL without an external provider request.
- An incomplete range is fetched from the selected provider and upserted into PostgreSQL.
- Duplicate provider rows are collapsed by timestamp before upsert.
- PostgreSQL guarantees uniqueness by symbol, timeframe, and timestamp.
- Aggregate target candles are cached under the requested timeframe.
- A repeated covered request reports `cache_hit=true`, zero fetched ranges, and does not call the provider or aggregate again.

Quality behavior:

- `partial=true` means the aggregate target bucket is still active.
- `complete=false` means one or more expected source candles are absent.
- Missing source intervals are reported and are never filled with invented prices or volume.
- Quality fields persist in PostgreSQL and remain available on cache hits.
- Aggregation is OHLCV resampling only. It does not predict price or produce BUY/SELL advice.

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
