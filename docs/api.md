# API

Base URL in local development:

```txt
http://localhost:8000
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

