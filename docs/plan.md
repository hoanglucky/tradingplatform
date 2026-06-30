# Trading Framework MVP — 90-Day Development Plan

## 1. Mục tiêu sản phẩm

Xây dựng một **web trading framework MVP** trong 3 tháng với 1 người phát triển chính và Codex hỗ trợ viết code.

Sản phẩm không phải là sàn giao dịch. Mục tiêu là tạo một trading terminal có:

* Web dashboard
* Realtime candlestick chart
* Watchlist
* Technical indicators
* Strategy signal engine
* Backtest engine
* Paper trading
* Alert system
* Exchange read-only connection
* Deployment-ready codebase

## 2. Nguyên tắc phát triển

### Bắt buộc

* Không implement live trading tiền thật trong MVP.
* Exchange integration chỉ được phép read-only.
* Mỗi ngày chỉ làm 1 task chính.
* Mỗi task phải có test hoặc ít nhất có cách kiểm tra rõ ràng.
* Không hardcode API key, secret, token.
* Mỗi module phải độc lập, dễ refactor.
* Codex viết code, người phát triển review logic.

### Không làm trong MVP

* Live order tiền thật
* Copy trading
* Multi-exchange phức tạp
* AI dự đoán giá
* Mobile app native
* Social trading
* Strategy marketplace
* Leverage trading

---

## 3. Tech stack

```txt
Frontend:
- Next.js
- React
- TypeScript
- TradingView Lightweight Charts

Backend:
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic

Database:
- PostgreSQL
- Redis

Realtime:
- WebSocket

Trading logic:
- Pandas
- NumPy
- Custom strategy engine
- Custom backtest engine

DevOps:
- Docker Compose
- GitHub Actions
- VPS / Railway / Render deployment
```

---

## 4. Cấu trúc repo mục tiêu

```txt
trading-framework/
│
├── apps/
│   ├── web/
│   └── api/
│
├── packages/
│   ├── shared/
│   └── ui/
│
├── services/
│   ├── market-data/
│   ├── indicator-engine/
│   ├── strategy-engine/
│   ├── backtest-engine/
│   ├── paper-trading/
│   ├── alert-engine/
│   └── exchange-adapters/
│
├── infra/
│   ├── docker/
│   ├── nginx/
│   └── deployment/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── learning-map.md
│   └── codex-tasks.md
│
├── docker-compose.yml
├── .env.example
├── README.md
├── Makefile
└── plan.md
```

---

## 5. Prompt mẫu dùng cho Codex mỗi ngày

```txt
You are working inside the trading-framework repo.

Task:
[Write today's task here]

Context:
This is a web trading framework MVP.
The product includes charting, indicators, strategy signals, backtesting, paper trading, alerts, and exchange read-only integration.

Constraints:
- Do not implement real-money live trading.
- Exchange integration must be read-only.
- Keep code modular and testable.
- Add or update tests.
- Update README/docs if needed.
- Do not break existing APIs.
- Do not hardcode secrets.
- Use clear folder structure.

Output:
1. Implement the feature.
2. Add tests or verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

---

# Month 1 — Core Framework, Backend, Frontend, Chart

## Week 1 — Project foundation

### Day 1 — Create monorepo foundation

**Goal:** Create the base repo structure.

**Codex task:**

```txt
Create a production-ready monorepo called trading-framework.

Required folders:
- apps/web
- apps/api
- packages/shared
- packages/ui
- services/market-data
- services/indicator-engine
- services/strategy-engine
- services/backtest-engine
- services/paper-trading
- services/alert-engine
- services/exchange-adapters
- infra
- docs

Also create:
- README.md
- .env.example
- Makefile
- docker-compose.yml placeholder
- docs/architecture.md
- docs/codex-tasks.md

Do not implement live trading.
```

**Done checklist:**

* [x] Repo structure created
* [x] README exists
* [x] `.env.example` exists
* [x] `docs/architecture.md` exists
* [x] `docs/codex-tasks.md` exists

**Implementation note - 2026-06-18:**

Day 1 foundation has been implemented. The scaffold includes Docker Compose, Next.js, FastAPI, PostgreSQL, Redis, shared packages, modular service stubs, and safety defaults that block live trading and exchange writes.

---

### Day 2 — FastAPI backend skeleton

**Goal:** Backend can start and return health check.

**Codex task:**

```txt
Create FastAPI backend skeleton inside apps/api.

Requirements:
- main.py
- app/core/config.py
- app/api/routes/health.py
- app/api/router.py
- app/core/logging.py
- requirements.txt or pyproject.toml
- /health endpoint
- basic CORS setup
- environment config loading

Add a simple test for /health.
```

**Done checklist:**

* [x] API scaffold exists
* [x] `/health` endpoint implemented
* [x] Test for health check added
* [x] `app/api/routes/health.py` exists
* [x] `app/api/router.py` exists
* [x] `app/core/logging.py` exists
* [x] CORS setup exists
* [x] Environment config loading exists
* [x] Backend syntax compile check passed
* [x] Pytest verified in Docker environment

**Implementation note - 2026-06-18:**

The API skeleton has been hardened with the planned `app/api/routes` structure, central router, logging setup, `/health`, `/health/ready`, `/safety`, and `/modules`. Backend pytest now passes in Docker with `docker compose run --rm api pytest`.

---

### Day 3 — Next.js frontend skeleton

**Goal:** Frontend dashboard can start.

**Codex task:**

```txt
Create Next.js frontend inside apps/web.

Requirements:
- TypeScript
- Dashboard layout
- Sidebar
- Topbar
- Main content area
- Basic routing
- Empty dashboard page
- API health check display

Do not add chart yet.
```

**Done checklist:**

* [x] Web app builds successfully
* [x] Dashboard layout visible in implementation
* [x] Sidebar exists
* [x] Topbar exists
* [x] Main content area exists
* [x] Basic routing exists
* [x] Empty dashboard page exists
* [x] API health status visible
* [x] Web app manually verified through local dev server HTTP checks

**Implementation note - 2026-06-18:**

The frontend skeleton has been hardened into an operational dashboard shell with sidebar navigation, topbar status, API health/readiness display, safety posture display, empty chart/watchlist/signal panels, and placeholder routes for markets, strategies, backtests, paper trading, alerts, and settings. Local dev server checks returned HTTP 200 for `/`, `/markets`, and `/settings`.

---

### Day 4 — Docker Compose setup

**Goal:** Run frontend, backend, database, Redis locally.

**Codex task:**

```txt
Create Docker Compose setup for:
- frontend
- backend
- PostgreSQL
- Redis

Add Dockerfile for apps/api.
Add Dockerfile for apps/web.
Update .env.example.
Update README with local setup instructions.
```

**Done checklist:**

* [x] Docker Compose config validates
* [x] API Dockerfile exists
* [x] Web Dockerfile exists
* [x] PostgreSQL healthcheck exists
* [x] Redis healthcheck exists
* [x] API healthcheck exists
* [x] Web healthcheck exists
* [x] Docker build contexts ignore generated/local files
* [x] Domain service stubs isolated behind Compose `services` profile
* [x] `docker compose up` works
* [x] Frontend accessible through full `docker compose up`
* [x] Backend accessible through full `docker compose up`
* [x] PostgreSQL starts during Compose test attempt
* [x] Redis starts during Compose test attempt
* [x] Backend pytest passes through Docker Compose

**Implementation note - 2026-06-18:**

Docker Compose has been hardened with API/web health checks, `.dockerignore` files for root/API/service build contexts, and a `services` profile for domain service stubs. `docker compose config --quiet` validates. `docker pull python:3.12-slim` works, API image build completes, PostgreSQL/Redis start during Compose test runs, backend pytest passes in Docker, and the core Compose stack is accessible at the expected web/API ports.

---

### Day 5 — Developer commands

**Goal:** Make the project easy to run.

**Codex task:**

```txt
Create Makefile commands:
- make dev
- make up
- make down
- make logs
- make api-test
- make web-test
- make lint
- make format

Update README with command usage.
```

**Done checklist:**

* [x] Makefile has `make dev`
* [x] Makefile has `make up`
* [x] Makefile has `make down`
* [x] Makefile has `make logs`
* [x] Makefile has `make api-test`
* [x] Makefile has `make web-test`
* [x] Makefile has `make lint`
* [x] Makefile has `make format`
* [x] npm fallback commands exist for environments without `make`
* [x] README updated
* [x] Local setup is clear

**Implementation note - 2026-06-18:**

Developer commands have been standardized around local npm dev commands and Docker-backed backend checks. Host Python still lacks `pip`/`venv`, so backend test/lint/format commands run through the API Docker image. This environment does not have the `make` binary installed, so equivalent npm commands were added as a fallback.

---

## Week 2 — Database foundation

### Day 6 — Add SQLAlchemy and Alembic

**Goal:** Backend has database migration system.

**Codex task:**

```txt
Add SQLAlchemy and Alembic to FastAPI backend.

Requirements:
- database connection config
- session management
- base model
- Alembic initialized
- first empty migration
- README section for migrations
```

**Done checklist:**

* [x] Database connection utilities exist
* [x] Async SQLAlchemy session management exists
* [x] Shared declarative base model exists
* [x] Alembic initialized
* [x] First empty migration exists
* [x] DB connection works
* [x] Alembic migration can run
* [x] Backend still starts

**Implementation note - 2026-06-18:**

Day 6 database foundation has been added with SQLAlchemy async engine/session utilities, Alembic configuration, and an initial empty migration. `npm run db:upgrade` and `npm run db:current` run successfully against PostgreSQL through Docker. The backend starts and returns `/health`.

---

### Day 7 — Create core database models

**Goal:** Create base models.

**Codex task:**

```txt
Create SQLAlchemy models and Alembic migration for:
- users
- symbols
- candles
- watchlists
- watchlist_items

Rules:
- Use UUID primary keys where suitable.
- Add created_at and updated_at.
- Add index for candles: symbol, timeframe, timestamp.
- Add unique constraint for symbol + timeframe + timestamp.
```

**Done checklist:**

* [x] Models created
* [x] Migration created
* [x] Tables created
* [x] Indexes created
* [x] Unique constraints created

**Implementation note - 2026-06-19:**

Core SQLAlchemy models and migration were added for users, symbols, candles, watchlists, and watchlist items. PostgreSQL verification shows the new tables plus `ix_candles_symbol_timeframe_timestamp`, `uq_candles_symbol_timeframe_timestamp`, and related unique constraints.

---

### Day 8 — Repository layer

**Goal:** Avoid messy direct DB calls.

**Codex task:**

```txt
Create repository layer for:
- users
- symbols
- candles
- watchlists

Each repository should have basic methods:
- create
- get_by_id
- list
- update
- delete where applicable

Add tests for symbol repository.
```

**Done checklist:**

* [x] Repository layer exists
* [x] Symbol repository tests pass

---

### Day 9 — Symbol API

**Goal:** Backend can manage trading symbols.

**Codex task:**

```txt
Create API endpoints for symbols:
- GET /symbols
- GET /symbols/{id}
- POST /symbols
- PATCH /symbols/{id}
- DELETE /symbols/{id}

Add Pydantic schemas.
Add tests.
```

**Done checklist:**

* [x] Symbol CRUD works
* [x] Tests pass
* [x] API docs show symbol endpoints

---

### Day 10 — Seed initial symbols

**Goal:** App has default market symbols.

**Codex task:**

```txt
Create seed script for initial symbols:
- BTCUSDT
- ETHUSDT
- SOLUSDT
- BNBUSDT
- XRPUSDT
- XAUUSD
- SP500
- US100

Add Makefile command:
- make seed

Update README.
```

**Done checklist:**

* [x] Seed script works
* [x] Symbols visible in API

---

## Week 3 — Market data framework

### Day 11 — MarketDataProvider interface

**Goal:** Create standard interface for market data.

**Codex task:**

```txt
Create market-data service.

Define MarketDataProvider interface with:
- get_symbols()
- get_historical_candles(symbol, timeframe, start, end)
- get_latest_price(symbol)

Define Candle schema:
- symbol
- timeframe
- timestamp
- open
- high
- low
- close
- volume
```

**Done checklist:**

* [x] Interface created
* [x] Candle schema created
* [x] Tests for schema validation

---

### Day 12 — Oanda, Binance public adapter

**Goal:** Fetch public candle data.

**Codex task:**

```txt
Implement Binance public market data adapter.

Requirements:
- Fetch historical klines.
- Convert response into internal Candle schema.
- Handle API errors.
- Handle invalid symbol/timeframe.
- Add tests with mocked responses.

No private API keys.
No live trading.
```

**Done checklist:**

* [x] Binance adapter works
* [x] Mock tests pass
* [x] No secret required

---

### Day 13 — Market candles API

**Goal:** Frontend can request candle data.

**Codex task:**

```txt
Create endpoint:
GET /market/candles

Query params:
- symbol
- timeframe
- start
- end

Return internal candle format.
Use Binance adapter for now.
Add tests.
```

**Done checklist:**

* [x] `/market/candles` works
* [x] Test with BTCUSDT works
* [x] Errors handled cleanly

---

### Day 14 — Candle storage

**Goal:** Cache candles in database.

**Codex task:**

```txt
Add logic to save fetched candles into database.

Rules:
- Use upsert based on symbol + timeframe + timestamp.
- Avoid duplicate candles.
- Return candles from DB if already available.
- Fetch missing candles from provider.

Add tests for deduplication.
```

**Done checklist:**

* [x] Candles stored in DB
* [x] No duplicate candles
* [x] Tests pass

---

### Day 15 — Market data docs

**Goal:** Document market data flow.

**Codex task:**

```txt
Update docs/architecture.md and docs/api.md.

Document:
- MarketDataProvider interface
- Binance public adapter
- Candle schema
- /market/candles endpoint
- Candle caching logic
```

**Done checklist:**

* [x] Docs updated
* [x] API behavior explained

---

## Week 4 — Chart frontend

### Day 16 — Install chart library

**Goal:** Add chart package.

**Codex task:**

```txt
Install TradingView Lightweight Charts in apps/web.

Create placeholder Chart page:
- /dashboard/chart
- Empty chart container
- Mock candle data displayed

Do not connect API yet.
```

**Done checklist:**

* [x] Chart page exists
* [x] Mock candles render

---

### Day 17 — CandlestickChart component

**Goal:** Reusable chart component.

**Codex task:**

```txt
Create CandlestickChart component.

Props:
- candles
- symbol
- timeframe
- height
- loading
- error

Requirements:
- Render candlesticks.
- Auto resize.
- Cleanup chart instance on unmount.
- Handle empty data.
```

**Done checklist:**

* [x] Component reusable
* [x] Empty state works
* [x] Resize works

---

### Day 18 — Symbol and timeframe selector

**Goal:** User can select market.

**Codex task:**

```txt
Create UI controls:
- Symbol selector
- Timeframe selector

Default:
- BTCUSDT
- 15m

Supported timeframes:
- 1m
- 5m
- 15m
- 1h
- 4h
- 1d
```

**Done checklist:**

* [x] Symbol selector works
* [x] Timeframe selector works
* [x] State updates correctly

---

### Day 19 — Connect chart to backend

**Goal:** Real candles show on chart.

**Codex task:**

```txt
Connect frontend chart to GET /market/candles.

Requirements:
- Fetch candles when symbol/timeframe changes.
- Show loading state.
- Show error state.
- Transform API data to chart format.
```

**Done checklist:**

* [x] Chart shows backend candles
* [x] Loading state works
* [x] Error state works

---

### Day 20 — UI polish for chart

**Goal:** Make chart usable.

**Codex task:**

```txt
Improve chart page UI.

Add:
- Market header
- Latest close price
- Timeframe buttons
- Refresh button
- Basic responsive layout
```

**Done checklist:**

* [x] Chart page usable
* [x] Latest price visible
* [x] Refresh works

**Implementation note - 2026-06-23:**

The chart workspace now has a responsive market header, a clearly labeled latest close and period change, a manual refresh action, live/loading/error feedback, and a last-updated timestamp. Refresh requests use the existing read-only candle endpoint and retain the current chart while new data is loading.

---

# Month 2 — Realtime, Watchlist, Indicators, Strategy, Backtest

## Week 5 — Realtime WebSocket

### Day 21 — Backend WebSocket endpoint

**Goal:** Backend supports realtime connection.

**Codex task:**

```txt
Create FastAPI WebSocket endpoint:
/ws/market

Support subscribe message:
{
  "type": "subscribe",
  "symbol": "BTCUSDT",
  "timeframe": "1m"
}

For now, send mock candle updates every few seconds.
```

**Done checklist:**

* [x] WebSocket connects
* [x] Subscribe message works
* [x] Mock updates received

**Implementation note - 2026-06-23:**

The FastAPI app now exposes `/ws/market`. Clients can subscribe or resubscribe with a validated symbol and timeframe, receive an acknowledgement, and then receive normalized mock OHLCV candles every `MARKET_WS_INTERVAL_SECONDS`. Invalid messages return a structured error while keeping the connection available for another subscription.

---

### Day 22 — Real market stream service

**Goal:** Stream real market candles.

**Codex task:**

```txt
Create market stream service.

Requirements:
- Connect to Binance public websocket if possible.
- Normalize incoming data into internal Candle format.
- Broadcast to subscribed frontend clients.
- Handle disconnects.
```

**Done checklist:**

* [x] Realtime candles received
* [x] Normalized format used
* [x] Disconnect handled

**Implementation note - 2026-06-23:**

`MarketStreamHub` now opens one Binance public kline stream per active symbol/timeframe and broadcasts normalized candles to every matching frontend subscription. It removes upstream tasks after the final client disconnects, reports transient outages, and reconnects with bounded exponential backoff. Slow-client queues are bounded and retain the newest updates.

---

### Day 23 — Frontend WebSocket subscription

**Goal:** Chart updates realtime.

**Codex task:**

```txt
Connect frontend chart to /ws/market.

Requirements:
- Subscribe to selected symbol/timeframe.
- Update last candle if timestamp matches.
- Append new candle if timestamp is new.
- Cleanup socket on component unmount.
```

**Done checklist:**

* [x] Chart updates realtime
* [x] No duplicated candles
* [x] Socket cleanup works

**Implementation note - 2026-06-29:**

The chart workspace now subscribes to `/ws/market` after its historical Binance candles load. Realtime candles replace an existing epoch-matched bar or append only when newer, preventing duplicates across `Z` and `+00:00` timestamp formats. Selection changes, refreshes, and component unmounts close the old socket. Oanda-only symbols remain on historical HTTP data until a realtime adapter exists.

---

### Day 24 — Reconnect and heartbeat

**Goal:** Improve realtime reliability.

**Codex task:**

```txt
Improve WebSocket reliability.

Add:
- Frontend reconnect with backoff
- Backend heartbeat/ping
- Stale connection cleanup
- Clear connection state in UI
```

**Done checklist:**

* [x] Reconnect works
* [x] Connection status visible
* [x] No duplicate subscriptions

**Implementation note - 2026-06-29:**

The frontend now reconnects closed sockets with exponential backoff bounded between `NEXT_PUBLIC_MARKET_WS_RECONNECT_MS` and `NEXT_PUBLIC_MARKET_WS_MAX_RECONNECT_MS`. The API emits application heartbeat messages, accepts matching pong replies, and closes stale clients after `MARKET_WS_STALE_SECONDS`. The UI distinguishes connecting, retrying, source reconnecting, realtime, unavailable, and historical-only states. Duplicate subscriptions on the same socket are idempotent.

---

### Day 25 — Realtime tests

**Goal:** Prevent candle update bugs.

**Codex task:**

```txt
Add tests for candle update logic.

Test cases:
- update existing candle
- append new candle
- ignore older candle
- handle duplicate timestamp
- handle empty chart state
```

**Done checklist:**

* [x] Candle update tests pass
* [x] Realtime logic stable

**Implementation note - 2026-06-29:**

The frontend realtime suite now covers updating an existing candle, appending a newer candle, ignoring an unknown older candle, replacing duplicate timestamps without reordering, and initializing an empty chart. It also verifies immutable input behavior, invalid OHLC rejection, bounded reconnect delays, and heartbeat pong creation.

---

## Week 6 — Watchlist and user settings

### Day 26 — Mock user mode

**Goal:** App can behave as a single-user MVP.

**Codex task:**

```txt
Create simple mock user mode for MVP.

Requirements:
- Create default local user if none exists.
- Use default user for watchlist and settings.
- Do not implement full auth yet.
- Document this as MVP-only behavior.
```

**Done checklist:**

* [x] Default user exists
* [x] Backend can identify MVP user
* [x] Docs mention mock user mode

**Implementation note - 2026-06-29:**

The API now provides an idempotent `get_mvp_user` dependency backed by a PostgreSQL conflict-safe insert. `GET /users/me` creates the configured local user on first use and returns the same identity afterward with `mode: mvp_local`. Watchlist and settings routes will reuse this dependency in Days 27 and 29. This mode has no credentials or authorization and must be replaced before multi-user deployment.

---

### Day 27 — Watchlist API

**Goal:** User can manage watchlist.

**Codex task:**

```txt
Create watchlist API:
- GET /watchlist
- POST /watchlist/items
- DELETE /watchlist/items/{symbol}

Rules:
- Prevent duplicate symbols.
- Validate symbol exists.
- Use default MVP user.
```

**Done checklist:**

* [x] Watchlist API works
* [x] Duplicate symbol rejected
* [x] Tests pass

**Implementation note - 2026-06-29:**

The API now exposes `GET /watchlist`, `POST /watchlist/items`, and `DELETE /watchlist/items/{symbol}` for the configured MVP user. The default watchlist and items use PostgreSQL conflict-safe inserts, symbols must exist and be active, input symbols normalize to uppercase, duplicates return `409`, and missing symbols/items return `404`.

---

### Day 28 — Watchlist frontend

**Goal:** Watchlist visible in UI.

**Codex task:**

```txt
Create watchlist panel in frontend.

Features:
- Show watchlist symbols
- Click symbol to load chart
- Add symbol
- Remove symbol
- Show latest price placeholder
```

**Done checklist:**

* [x] Watchlist visible
* [x] Click loads chart
* [x] Add/remove works

**Implementation note - 2026-06-29:**

The dashboard now contains a live watchlist panel backed by the Day 27 API. It loads active catalog symbols, filters pinned/inactive choices, supports add, remove, manual refresh, and explicit loading/empty/error states, and shows a latest-price placeholder. Symbol links open `/dashboard/chart?symbol=...`; the chart page validates the query and initializes the matching Binance or Oanda market.

---

### Day 29 — User settings API

**Goal:** Save user preferences.

**Codex task:**

```txt
Create user settings model and API.

Settings:
- default_symbol
- default_timeframe
- selected_indicators
- theme

Endpoints:
- GET /settings
- PATCH /settings
```

**Done checklist:**

* [x] Settings table/model exists
* [x] API works
* [x] Tests pass

**Implementation note - 2026-06-29:**

Added a one-to-one `user_settings` model and migration plus conflict-safe lazy creation. `GET /settings` returns defaults and `PATCH /settings` persists validated active symbol, timeframe, unique indicator slugs, theme, and IANA timezone for the MVP user. Backend suite passes 48 tests.

---

### Day 30 — Persist frontend settings

**Goal:** User preferences survive reload.

**Codex task:**

```txt
Connect frontend to settings API.

Requirements:
- Load default symbol/timeframe on app start.
- Save symbol/timeframe changes.
- Keep UI state after refresh.
```

**Done checklist:**

* [x] Settings load
* [x] Settings save
* [x] Refresh keeps preferences

Week 6.5 — Multi-timeframe, custom timeframe, structure and cross-market data
Ghi chú: Cụm Day 30.x là phần mở rộng sau Day 30. Không đổi số thứ tự Day 31 trở đi trong roadmap gốc. Mục tiêu là hoàn thiện nền tảng review đa khung, tạo custom timeframe, tách sóng swing, định nghĩa các "thế đánh", chuẩn bị nguồn dữ liệu cho vàng/chỉ số/FX, và đưa concept Udemy quant vào một lớp tính toán riêng.

Market focus update
MVP ưu tiên:

Primary markets:
- XAUUSD / Gold
- US100 / NAS100 / Nasdaq index CFD
- US500 / SPX500 / S&P 500 index CFD
- US30 / Dow index CFD
- EURUSD, GBPUSD, USDJPY and major FX pairs

Chart/candle source:
- OANDA / broker CFD / forex-index-gold data provider

Orderflow/volume source:
- CME futures proxy through Databento / dxFeed / CME data

Not primary:
- Crypto-first Binance/CoinGlass flow
Mapping concept:

XAUUSD chart  -> OANDA XAU_USD / broker CFD
Gold flow     -> CME COMEX GC / MGC futures

US100 chart   -> OANDA NAS100_USD / broker CFD
Nasdaq flow   -> CME NQ / MNQ futures

US500 chart   -> OANDA SPX500_USD / broker CFD
S&P flow      -> CME ES / MES futures

EURUSD chart  -> OANDA EUR_USD / spot FX style data
EUR flow      -> CME 6E futures
Additional target service structure
Add these service modules after the current foundation is stable:

services/
  market-data/             # candles and chart data
  data-ingestion/          # provider-specific raw data collectors
  data-engine/             # source registry, symbol mapping, normalization, data quality
  structure-engine/        # swing, wave, trend, BOS/CHOCH, zones
  setup-engine/            # rule-based trading concepts / "thế đánh"
  orderflow-engine/        # big trade, delta, absorption, iceberg suspicion
  liquidity-engine/        # sweep, wick reclaim, futures liquidity zones
  indicator-engine/        # SMA, EMA, RSI, MACD
  strategy-engine/         # convert setup into BUY/SELL/HOLD signal
  backtest-engine/         # validate strategy historically
  paper-trading/           # virtual execution only
Naming convention:

structure-engine = hiểu cấu trúc thị trường
setup-engine     = phát hiện thế đánh
strategy-engine  = signal hóa để backtest/paper trading
data-engine      = chuẩn hóa, mapping source, resample, quality
orderflow-engine = big trade, delta, absorption, iceberg suspect
liquidity-engine = sweep, reclaim, liquidity zones
Day 30.1 — Multi-timeframe workspace model
Goal: Prepare one-symbol multi-timeframe review workspace state.

Codex task:

Create multi-timeframe workspace state for the chart page.

Requirements:
- Create TypeScript types:
  - MultiTimeframeWindow
  - MultiTimeframeLayout
- One workspace uses one shared symbol.
- Support layout presets: 1, 2, 4, 8 windows.
- Each window has:
  - id
  - timeframe
  - enabled
  - reviewChecked
- Default symbol should reuse the current selected symbol.
- Default window count: 4.
- Default 4-window layout:
  - 4h
  - 1h
  - 15m
  - 5m
- Do not connect API yet.
- Do not change backend.
- Keep the old single-chart behavior working.
Done checklist:

[x] MultiTimeframeLayout type exists
[x] MultiTimeframeWindow type exists
[x] Default 4-window config exists
[x] State updates without breaking old chart
Day 30.2 — Layout selector 1 / 2 / 4 / 8
Goal: User can choose the number of chart windows.

Codex task:

Create layout selector for multi-timeframe chart workspace.

Requirements:
- Add UI buttons for layout presets:
  - 1 window
  - 2 windows
  - 4 windows
  - 8 windows
- Selecting a layout updates windowCount.
- When changing layout:
  - Preserve existing window timeframe/reviewChecked state where possible.
  - Add default windows if increasing count.
  - Hide extra windows if decreasing count.
- Keep one shared symbol for all windows.
- Do not create separate symbol per window.
- Add simple visual active state for selected layout.
Done checklist:

[x] User can select 1 window
[x] User can select 2 windows
[x] User can select 4 windows
[x] User can select 8 windows
[x] Active layout is visible
[x] Existing state is preserved where possible
Day 30.3 — Multi-timeframe grid UI
Goal: Render chart windows based on selected layout.

Codex task:

Create MultiTimeframeGrid component.

Requirements:
- Render chart windows based on selected windowCount.
- Support layouts: 1, 2, 4, 8.
- Each chart window should show:
  - symbol
  - timeframe selector
  - review checkbox
  - placeholder chart area for now
- Use same selected symbol for all windows.
- Each window can select its own timeframe.
- Do not fetch candles yet.
- Keep responsive layout.
- Empty/disabled windows should not crash UI.
Done checklist:

[x] MultiTimeframeGrid component exists
[x] 1-window layout renders
[x] 2-window layout renders
[x] 4-window layout renders
[x] 8-window layout renders
[x] Each window has timeframe selector
[x] Each window has review checkbox
Day 30.4 — Extended timeframe presets
Goal: Add enough timeframe options for 8-window review.

Codex task:

Extend timeframe options for multi-timeframe review mode.

Requirements:
- Keep existing supported timeframes:
  - 1m
  - 5m
  - 15m
  - 1h
  - 4h
  - 1d
- Add optional review timeframes:
  - 30m
  - 2h
- Final multi-timeframe options:
  - 1m
  - 5m
  - 15m
  - 30m
  - 1h
  - 2h
  - 4h
  - 1d
- Default layouts:
  - 1 window: 15m
  - 2 windows: 1h, 15m
  - 4 windows: 4h, 1h, 15m, 5m
  - 8 windows: 1d, 4h, 2h, 1h, 30m, 15m, 5m, 1m
- Do not implement candle aggregation.
- Backend should still request candles directly by selected timeframe where provider supports it.
Done checklist:

[x] 30m option exists
[x] 2h option exists
[x] 8-window default has 8 different timeframes
[x] Old single-chart timeframe selector still works

Implementation note — 2026-06-30:

- Review-only presets now include 30m and 2h while the old single-chart selector remains unchanged.
- Default layouts are defined independently for 1, 2, 4, and 8 windows.
- The 8-window preset uses eight distinct timeframes: 1d, 4h, 2h, 1h, 30m, 15m, 5m, and 1m.
- OANDA maps 2h directly to H2; no candle aggregation was added.
- Verification: 27 frontend tests, 32 market-data tests, lint, typecheck, and production build pass.
Day 30.5 — Review checkbox per timeframe
Goal: Each timeframe window can be manually marked as reviewed.

Codex task:

Add review checkbox behavior for each multi-timeframe window.

Requirements:
- Each chart window has a checkbox labeled "Reviewed".
- Ticking checkbox updates reviewChecked for that window only.
- Add a review progress indicator:
  - Example: Reviewed 2/4 timeframes
- Add a "Clear review" button.
- Clear review should uncheck all windows.
- Do not store review as a trading signal.
- This is only for manual review workflow.
Done checklist:

[x] Each window has Reviewed checkbox
[x] Checkbox updates correct window
[x] Review progress visible
[x] Clear review works

Implementation note — 2026-06-30:

- Review progress counts visible/enabled windows only.
- Clear review resets both visible and hidden window state, preventing stale checks from returning after layout expansion.
- Review state remains a manual UI aid and does not call strategy, signal, paper-order, or exchange APIs.
- Verification: 29 frontend tests, lint, typecheck, and production build pass.
Day 30.6 — Persist multi-timeframe layout
Goal: Reloading the app keeps the multi-window layout.

Codex task:

Persist multi-timeframe layout in user settings.

Requirements:
- Extend frontend settings type to include multi_timeframe_layout.
- Extend backend settings schema/model if needed.
- Save:
  - selected symbol
  - windowCount
  - each window timeframe
  - each window enabled state
  - each window reviewChecked state
- Load saved layout on page refresh.
- If saved layout is invalid, fallback to default 4-window layout.
- Do not break existing settings:
  - default_symbol
  - default_timeframe
  - selected_indicators
  - theme
Done checklist:

[x] Layout saves
[x] Layout reloads after refresh
[x] Invalid saved layout falls back safely
[x] Existing settings still work

Implementation note — 2026-06-30:

- Added nullable JSONB `multi_timeframe_layout` under migration `20260630_0005`.
- Backend validates active symbol, 1/2/4/8 count, unique IDs, enabled count, fixed review timeframes, and booleans.
- Frontend loads and clones valid layouts, falls back to the default four-window layout for invalid data, and serializes saves through the existing settings queue.
- Existing symbol, timeframe, indicators, theme, and timezone settings remain compatible.
- Verification: 52 backend tests, Ruff, 33 frontend tests, lint, typecheck, production build, migration, and live persistence smoke test pass.
Day 30.7 — Connect multi-window charts to candles API
Goal: Each chart window fetches candles independently.

Codex task:

Connect multi-timeframe windows to market candles API.

Requirements:
- Each enabled chart window fetches candles from:
  GET /market/candles
- Use same symbol for all windows.
- Use each window's selected timeframe.
- Show loading state per window.
- Show error state per window.
- Do not let one failed timeframe break other windows.
- Use existing CandlestickChart component.
- Do not duplicate chart logic.
- Do not implement candle aggregation here.
Done checklist:

[x] Each window loads candles
[x] Different timeframes show independently
[x] Loading state works per window
[x] Error state works per window
[x] One failed window does not crash whole page

Implementation note — 2026-06-30:

- Extracted one shared candles client used by both the legacy single chart and multi-window charts.
- Each enabled window owns its AbortController, candle state, loading state, and error state.
- Review windows request the latest 120 direct-provider candles for their own timeframe and reuse `CandlestickChart`.
- Hidden/unmounted windows abort old requests; one failed request does not affect sibling windows.
- No candle aggregation or multi-window realtime stream was introduced.
- Verification: 36 frontend tests, lint, typecheck, production build, and direct multi-timeframe API smoke tests pass.
Day 30.8 — Multi-window realtime synchronization
Goal: Show one synchronized current market price across exactly the selected chart windows.

Codex task:

Connect the visible multi-timeframe workspace to realtime candle streams and remove the duplicate legacy chart.

Requirements:
- Render exactly 1, 2, 4, or 8 chart windows for the selected layout.
- Remove the additional single chart below the multi-window grid.
- Open one WebSocket subscription per unique visible timeframe.
- Reuse a subscription when multiple windows select the same timeframe.
- Merge each timeframe's realtime candle into its own historical series.
- Synchronize every active candle close to the latest workspace price while preserving its timeframe bucket.
- Support realtime 30m and 2h subscriptions.
- Keep heartbeat, reconnect, and provider error handling.
- Refresh all visible chart histories with one command.

Done checklist:

[x] Layout renders exactly 1/2/4/8 windows
[x] Duplicate legacy chart removed
[x] Realtime subscriptions are deduplicated by timeframe
[x] Current price is synchronized across windows
[x] 30m and 2h realtime subscriptions work
[x] Tests and production build pass

Implementation note — 2026-06-30:

- Moved realtime ownership into `MultiTimeframeGrid`; each unique symbol/timeframe pair gets one reconnecting WebSocket and duplicate timeframe windows share its update.
- Every window keeps independent history/error/loading state and merges its own realtime candle by timestamp.
- The newest workspace quote synchronizes close/high/low for each active candle, so all visible charts show one current market price without changing their bucket timestamps.
- Removed the separate legacy chart and its standalone timeframe/range controls. Layout 1 uses one full-height chart; layout 2/4/8 renders exactly that many charts.
- Extended the API WebSocket contract and Oanda mappings with 30m/M30 and 2h/H2.
- Verification: 38 frontend tests, lint, typecheck, production build, 56 API tests, Ruff, live XAUUSD multi-stream smoke test, and healthy web/API containers.
Day 30.9 — Right-click chart view reset
Goal: Quickly restore a chart after manual zooming or panning.

Codex task:

Reset the active chart viewport when the user right-clicks its candle canvas.

Requirements:
- Prevent the browser context menu only on a loaded candle chart.
- Fit the complete loaded candle range on the time axis.
- Restore automatic scaling on the right price axis.
- Apply independently to every chart in layouts 1/2/4/8.
- Do not reload candles or reconnect market streams.

Done checklist:

[x] Right-click resets the time scale
[x] Right-click restores price auto-scale
[x] Browser context menu is suppressed on chart canvas
[x] Multi-window charts reset independently
[x] Tests and production build pass

Implementation note — 2026-06-30:

- Added a tested `resetCandlestickChartView` utility that calls `fitContent()` and enables right-price-axis `autoScale`.
- `CandlestickChart` handles `contextmenu`, prevents the browser menu, and resets only its own Lightweight Charts instance.
- Resetting is presentation-only: candle state, history requests, realtime subscriptions, and saved settings are unchanged.
- Verification: 40 frontend tests, lint, typecheck, and production build pass.
Day 30.9.1 — Candle timestamp and chart timezone alignment
Goal: Align every chart candle with TradingView's opening-time convention.

Codex task:

Normalize chart timestamps and timezone formatting without changing provider candle data.

Requirements:
- Treat provider candle timestamps as UTC candle-open instants.
- Plot each candle at its provider opening timestamp, matching TradingView crosshair labels.
- Keep close-time calculation available as derived metadata without shifting the chart coordinate.
- Format the time axis and crosshair in the persisted chart timezone.
- Add UTC and Asia/Bangkok timezone choices and persist selection through `/settings`.
- Apply the same rule to historical and realtime candles in every visible window.
- Do not mutate timestamps stored in PostgreSQL.

Done checklist:

[x] Chart coordinate equals provider candle-open timestamp
[x] Derived close time remains available
[x] UTC and Bangkok axis formatting work
[x] Crosshair displays full candle open time
[x] Timezone selection persists
[x] Tests and production build pass

Implementation note — 2026-06-30:

- Added pure open/close timestamp and timezone formatting utilities.
- `CandlestickChart` places each point at the provider opening instant and uses custom Lightweight Charts axis/crosshair formatters.
- Added a chart timezone selector backed by the existing validated IANA timezone setting.
- Updated the local MVP user's chart timezone to `Asia/Bangkok` for TradingView UTC+7 comparison.
- Historical and realtime payload timestamps remain untouched UTC provider-open instants.
- A correction removed the earlier duration offset that made a 14:55 5m candle appear as 15:00 when selected.
- Lightweight Charts may render sparse axis labels such as 15:00 then 15:05 to prevent overlap; this does not remove intermediate 1m candles.
- Added an on-chart crosshair timestamp label so hovering intermediate bars shows 15:01, 15:02, 15:03, and 15:04 explicitly.
- Crosshair labels now show each timeframe's complete opening-to-closing range, such as `5m 15:00 - 15:05` and `15m 15:00 - 15:15`.
- Verification: 46 frontend tests, lint, typecheck, and production build pass.
Day 30.9.2 — Oanda trailing candle cache repair
Goal: Prevent stale higher-timeframe cache ranges from creating missing chart periods.

Codex task:

Correct Oanda candle cache coverage at the requested range tail.

Requirements:
- Keep weekend tolerance for a missing leading edge before Oanda market opens.
- Do not apply the three-day weekend tolerance to the trailing edge.
- Require the final cached candle plus one timeframe duration to reach the requested end.
- Fetch and upsert the provider range when cached 5m/15m/30m/hourly candles are stale.
- Preserve legitimate Oanda daily-break and weekend gaps.
- Add a regression test for stale trailing cache data.

Done checklist:

[x] Stale Oanda tail triggers provider fetch
[x] Current higher-timeframe candles are backfilled
[x] Leading weekend tolerance remains supported
[x] Legitimate market-closed gaps remain unchanged
[x] Tests pass

Implementation note — 2026-06-30:

- Replaced the shared three-day Oanda edge tolerance with leading-only tolerance.
- Trailing coverage now requires `last candle timestamp + timeframe duration >= requested end`.
- Rebuilt market-data and refetched XAUUSD ranges; 5m, 15m, 30m, 1h, 2h, and 4h tails now reach their latest completed provider bucket.
- Remaining 75/90-minute and weekend gaps match Oanda market closures rather than missing cache rows.
- Verification: 64 market-data tests, live range diagnostics, service health, Ruff, and diff checks pass.
Day 30.9.3 — Chart workspace control layout polish
Goal: Make symbol, timeframe, window-count, and timezone controls easier to scan.

Codex task:

Reorder the chart controls and simplify redundant market information.

Requirements:
- Use one top toolbar ordered as symbol, active-window timeframe, layout count, and actions.
- Clicking or focusing a chart makes it the active window for the top timeframe selector.
- Keep per-window timeframe selectors for direct local editing.
- Remove the global realtime price summary and numeric live price from window headers.
- Move chart timezone to the bottom-right footer.
- Show only hour and minute on time-axis ticks.
- Keep full candle range information in the crosshair overlay.
- Remain responsive for mobile and 1/2/4/8 layouts.

Done checklist:

[x] Top controls follow Symbol → Timeframe → Windows order
[x] Active window timeframe control works
[x] Realtime price summary removed
[x] Timezone is bottom-right
[x] Time axis uses HH:mm only
[x] Responsive build passes

Implementation note — 2026-06-30:

- Consolidated two control rows into one responsive toolbar.
- Added active-window state and a restrained active border so top timeframe buttons target the selected chart.
- Removed global and per-window numeric realtime price text while retaining realtime candle synchronization and compact stream status.
- Moved the persisted timezone selector beside attribution in the chart footer.
- Time-axis formatter now returns only `HH:mm`; the crosshair overlay still shows complete timeframe ranges.
- Verification: 46 frontend tests, lint, typecheck, and production build pass.
Day 30.9.4 — Collapsible chart navigation sidebars
Goal: Maximize chart space while keeping application and market navigation available.

Codex task:

Convert the left application navigation and right market watchlist into independently collapsible sidebars.

Requirements:
- Collapse the primary navigation toward the left edge and retain icon navigation.
- Mark the current primary route and expose labels through tooltips while collapsed.
- Collapse the market watchlist toward the right edge and retain a visible reopen control.
- Expand the chart column into space released by either sidebar.
- Persist both collapse preferences in browser storage.
- Keep keyboard focus states and responsive behavior.

Done checklist:

[x] Left navigation collapses to an icon rail
[x] Right market list collapses to a compact rail
[x] Chart expands with both independent states
[x] Collapse preferences persist
[x] Responsive production build passes

Implementation note — 2026-06-30:

- Added route-aware Lucide icons and active-state styling to the primary navigation.
- Added independent edge controls for the left navigation and right market watchlist.
- Added a shared `useSyncExternalStore` preference hook for hydration-safe local storage and cross-tab updates.
- Changed the chart page grid between a 320px market list and a 44px collapsed rail.
- Verification: frontend lint, 46 tests, typecheck, diff check, and production build pass.
Day 30.9.5 — Automatic chart recovery after browser pause
Goal: Restore every missed candle after a minimized, hidden, suspended, or offline browser session.

Codex task:

Resynchronize historical and realtime data automatically when the chart becomes active again.

Requirements:
- Detect visible-tab, window-focus, and browser-online recovery events.
- Fetch a fresh historical range for every visible chart window.
- Recreate WebSocket subscriptions after recovery.
- Debounce duplicate focus and visibility events.
- Keep existing candles visible while the recovery request is running.
- Require no manual Refresh action.

Done checklist:

[x] Hidden-tab recovery triggers REST backfill
[x] Realtime subscriptions reconnect automatically
[x] Duplicate resume events are debounced
[x] Existing chart remains visible during backfill
[x] Recovery behavior applies to every visible timeframe

Implementation note — 2026-06-30:

- Added one shared resume generation to the multi-timeframe workspace.
- `visibilitychange`, `focus`, and `online` now trigger a debounced resynchronization when the document is visible.
- Every active timeframe reloads its recent authoritative candle range and recreates its WebSocket subscription.
- Historical state is cleared only when symbol or timeframe identity changes, avoiding blank charts during recovery.
- Browser background execution remains best-effort; correctness comes from deterministic REST backfill on resume.
Day 30.9.6 — Realtime candle open continuity repair
Goal: Prevent temporary false gaps while live candles roll into the next bucket.

Codex task:

Keep realtime OHLC isolated per timeframe and reconcile contiguous candle transitions.

Requirements:
- Do not apply one timeframe's latest price to another timeframe's OHLC.
- Retain consecutive realtime candles until REST history catches up.
- For exactly contiguous buckets, use the previous close as the next open.
- Expand high/low only when needed to keep corrected OHLC valid.
- Preserve provider opens across real session, maintenance, and weekend gaps.
- Apply the rule to minute, hour, day, week, and month durations.

Done checklist:

[x] Cross-timeframe OHLC mutation removed
[x] Realtime candles retained in a bounded per-timeframe buffer
[x] Contiguous open equals previous close
[x] Real market gaps remain unchanged
[x] Regression tests pass

Implementation note — 2026-06-30:

- Removed `sharedLatestPrice`, which could temporarily move the previous candle close/high/low using an update from another timeframe.
- Realtime state now stores a bounded candle sequence per symbol/timeframe instead of only the latest snapshot.
- Merge reconciliation adjusts open only when timestamps differ by exactly one timeframe duration.
- Verification: 55 frontend tests, lint, typecheck, and production build pass.
Day 30.10 — Timeframe parser and validation
Goal: Support custom timeframe strings safely.

Codex task:

Create timeframe parser and validation utility.

Requirements:
- Support minute timeframes like:
  - 1m
  - 5m
  - 6m
  - 7m
  - 15m
  - 30m
- Support hour/day timeframes like:
  - 1h
  - 2h
  - 4h
  - 1d
- Normalize API values to internal format.
- Reject invalid values:
  - 0m
  - -5m
  - abc
  - 1x
- Return timeframe duration in milliseconds.
- Add unit tests.
Done checklist:

[x] Parser supports minute/hour/day timeframes
[x] Invalid timeframe rejected
[x] Unit tests pass

Implementation note — 2026-06-30:

- Added a pure market-data timeframe parser for positive integer minute, hour, and day values.
- Inputs normalize whitespace and unit case to canonical lowercase strings.
- Parsed results expose amount, unit, normalized value, and duration milliseconds.
- Invalid syntax, zero/negative values, unsupported units, non-string values, and durations above 31 days are rejected with `TimeframeValidationError`.
- The parser is intentionally not connected to `/market/candles` until Day 30.15.
- Verification: 20 parser cases, 52 total market-data tests, and Ruff pass.
Day 30.11 — CandleAggregator base utility
Goal: Build custom timeframe candles from smaller base candles.

Codex task:

Create CandleAggregator utility.

Requirements:
- Create service in services/market-data or services/data-engine:
  - candle_aggregator.py
- Implement aggregate_candles(candles, target_timeframe).
- Main rule:
  - open = first open in bucket
  - high = max high in bucket
  - low = min low in bucket
  - close = last close in bucket
  - volume = sum volume in bucket
  - timestamp = bucket start time
- Group candles by fixed UTC timestamp buckets.
- Add tests:
  - 1m -> 5m
  - 1m -> 6m
  - 1m -> 7m
  - 1m -> 15m
Done checklist:

[x] CandleAggregator exists
[x] OHLCV aggregation is correct
[x] UTC bucket grouping works
[x] Tests pass

Implementation note — 2026-06-30:

- Added a pure `CandleAggregator` utility and `aggregate_candles` entry point in the market-data service.
- Candles are sorted before grouping into fixed Unix-epoch-aligned UTC buckets.
- Each aggregate uses the first open, maximum high, minimum low, last close, summed volume, and bucket start timestamp.
- Source candles must share one symbol and timeframe; the target must be equal to or larger than the source and an exact duration multiple.
- Tests cover 1m aggregation into 5m, 6m, 7m, and 15m, exact OHLCV values, reversed timezone-aware input, empty input, and invalid source/target combinations.
- Day 30.11 initially returned a final incomplete bucket without lifecycle metadata; Day 30.12 now classifies it explicitly.
- The utility is not connected to providers, storage, or `/market/candles` yet.
- Verification: 11 aggregator tests, 63 total market-data tests, and Ruff pass.
Day 30.12 — Closed vs partial candle handling
Goal: Avoid repainting confirmed historical candles.

Codex task:

Add closed/partial candle handling to CandleAggregator.

Requirements:
- Mark aggregated candles as:
  - closed
  - partial
- Historical completed buckets should be closed.
- Current active bucket should be partial.
- API can optionally include or exclude partial candles.
- Default chart mode may include partial candle.
- Backtest mode must exclude partial candle.
- Add tests for current active bucket.
Done checklist:

[x] Closed candle detection works
[x] Partial candle detection works
[x] Backtest can exclude partial candle
[x] Tests pass

Implementation note — 2026-06-30:

- Added `AggregatedCandle` with complementary `closed` and `partial` flags.
- Bucket lifecycle is evaluated against an optional timezone-aware `as_of`; current UTC time is used for normal chart calls.
- A bucket is closed exactly when its UTC end is less than or equal to `as_of`; the active bucket remains partial.
- `include_partial=True` preserves chart behavior, while `include_partial=False` gives backtest/replay consumers only confirmed candles.
- Naive evaluation datetimes are rejected to prevent ambiguous lifecycle decisions.
- Provider, storage, and `/market/candles` integration remain deferred to Day 30.13–30.15.
- Verification: 15 aggregator tests, 68 total market-data tests, and Ruff pass.
Day 30.13 — Provider capability map
Goal: Know which provider supports which timeframe directly.

Codex task:

Create provider capability map.

Requirements:
- Define provider capabilities for direct candles.
- Example:
  - OANDA supports selected granularities.
  - Binance public can be kept for crypto/dev testing only.
  - Custom 6m/7m should use aggregation fallback if provider does not support it.
- Add source metadata:
  - provider
  - venue
  - market_type
  - data_type
- Add tests for provider capability lookup.
Done checklist:

[x] Provider capability map exists
[x] Unsupported timeframe can be detected
[x] Tests pass

Implementation note — 2026-06-30:

- Added an immutable provider capability registry sourced directly from the adapter timeframe constants.
- Oanda is marked read-only primary CFD/FX market data; Binance is marked read-only spot-crypto development data.
- Each capability exposes provider, venue, market type, data type, intended use, direct timeframes, and read-only state.
- Lookup normalizes provider names and ordinary minute/hour/day timeframe values while preserving Binance's exact monthly `1M` interval.
- Oanda custom 6m, 7m, 45m, and 3h values are identified as aggregate-fallback candidates; malformed values are not considered direct.
- Provider capability lookup remains pure and does not alter provider routing or `/market/candles` until Day 30.14–30.15.
- Verification: 18 capability tests, 86 total market-data tests, and Ruff pass.
Day 30.14 — CandleService aggregate fallback
Goal: Use provider direct timeframe first, then aggregate from smaller candles if needed.

Codex task:

Update CandleService to support aggregate fallback.

Flow:
1. Request symbol/timeframe/range.
2. Check DB cache for exact timeframe.
3. If enough cached data exists, return DB candles.
4. If provider supports timeframe directly, fetch provider candles and upsert DB.
5. If provider does not support timeframe, fetch base timeframe candles, aggregate to target timeframe, upsert result, and return.

Rules:
- Do not duplicate candles.
- Preserve provider/source metadata.
- Do not overwrite spot/CFD candles with futures candles.
- Add tests for direct provider and aggregate fallback.
Done checklist:

[x] Direct timeframe path works
[x] Aggregate fallback works
[x] Cache upsert works
[ ] Source metadata preserved

Implementation note — 2026-06-30:

- Candle storage now validates and normalizes target timeframes before cache lookup.
- Direct provider intervals retain the existing provider/storage path.
- Unsupported intervals select the largest compatible direct base, aggregate OHLCV, and upsert target candles.
- Added fixed week buckets and calendar-month buckets (`1M`).
- Source metadata remains a follow-up because the current candle schema has no source fields.
- Week aggregation is aligned to Monday UTC; month aggregation uses calendar boundaries.
- Verification: 93 market-data tests pass, including Oanda `1m -> 3m` fallback.
Day 30.15 — API support for custom timeframe
Goal: /market/candles accepts custom timeframe values.

Codex task:

Update GET /market/candles to support custom timeframes.

Requirements:
- Accept timeframe values like:
  - 5m
  - 6m
  - 7m
  - 30m
  - 2h
- Validate timeframe through TimeframeParser.
- Return clean 400 error for invalid timeframe.
- Add response metadata:
  - source_provider
  - source_market_type
  - aggregation_used
  - base_timeframe if aggregation was used
- Add tests.
Done checklist:

[x] Custom timeframe accepted
[x] Invalid timeframe rejected cleanly
[x] Response metadata exists
[x] Tests pass

Implementation note — 2026-06-30:

- `/market/candles` accepts normalized minute, hour, day, week, and `1M` values.
- Invalid, zero, malformed, or over-one-month values return HTTP 400.
- The response uses `{ candles, metadata }` and exposes provider, market type, aggregation, base timeframe, cache hit, and fetched-range count.
Day 30.16 — Frontend custom timeframe option
Goal: User can add custom timeframe to a chart window.

Codex task:

Add custom timeframe input to multi-timeframe windows.

Requirements:
- User can select preset timeframe.
- User can type custom timeframe like:
  - 6m
  - 7m
  - 45m
  - 3h
- Validate client-side before API call.
- Show helpful validation error.
- Do not allow invalid values to be saved.
Done checklist:

[x] Custom timeframe input exists
[x] Client validation works
[x] Invalid value not saved

Implementation note — 2026-06-30:

- Added a dropdown grouped into Minutes, Hours, Long range, and Custom input.
- Presets include 1/3/5/15/30/45m, 1/2/3/4h, 1d, 2w, and calendar month `1M`.
- Invalid custom values cannot be applied or favorited.
- Star controls determine which timeframe buttons appear in the main toolbar.
Day 30.17 — Persist custom timeframe layout
Goal: Custom timeframe windows survive reload.

Codex task:

Persist custom timeframe values inside multi_timeframe_layout.

Requirements:
- Save custom timeframe per window.
- Reload custom timeframes after page refresh.
- If saved custom timeframe is invalid, fallback to window default.
- Keep reviewChecked state intact.
Done checklist:

[x] Custom timeframe saves
[x] Custom timeframe reloads
[x] Invalid saved value falls back safely

Implementation note — 2026-06-30:

- API settings validation now accepts safe custom timeframe strings inside each chart window.
- Frontend layout resolution normalizes valid persisted values and rejects invalid layouts.
- Timeframe favorites persist independently in browser-local presentation settings.
Day 30.18 — Connect custom timeframe windows to candles API
Goal: Multi-window chart can display custom aggregated candles.

Codex task:

Connect custom timeframe windows to GET /market/candles.

Requirements:
- Each window sends its selected timeframe.
- If timeframe is custom and backend aggregates it, show a small label:
  - Aggregated from 1m
- Loading/error state remains per window.
- One failed custom timeframe must not crash other windows.
Done checklist:

[x] Custom timeframe chart loads
[x] Aggregation label visible when used
[x] Per-window errors work

Implementation note — 2026-06-30:

- Custom windows send their normalized timeframe to `/market/candles`.
- Provider-native intervals retain WebSocket updates; aggregate-only intervals use visible-tab REST auto-sync every 10 seconds.
- Each window keeps independent loading/error state.
- Window headers now show direct provider or `Aggregated from {base timeframe}` metadata.
Day 30.19 — Aggregation cache verification
Goal: Prevent repeated expensive aggregation.

Codex task:

Add verification for aggregated candle cache.

Requirements:
- Aggregated candles are saved to DB.
- Subsequent same request should return from DB when range is complete.
- Add debug metadata to response:
  - cache_hit
  - aggregation_used
  - missing_ranges_fetched
- Add tests for repeated requests.
Done checklist:

[x] Aggregated candles cached
[x] Repeated request uses cache
[x] Tests pass

Implementation note — 2026-06-30:

- Added a typed candle query envelope with source and cache metadata.
- Exact target-cache coverage returns `cache_hit=true` and performs no provider fetch or upsert.
- Aggregate misses report the compatible base timeframe and propagate provider-range fetch counts.
- Repeated-request tests prove the second request performs no provider call, commit, or re-aggregation.
- Frontend window headers expose source/aggregation labels and cache diagnostics through a tooltip.
- Verification: 94 market-data tests and 56 frontend tests pass.
Day 30.20 — Edge case tests for custom timeframe
Goal: Harden custom timeframe logic.

Codex task:

Add edge case tests for custom timeframe aggregation.

Test cases:
- Missing 1m candles inside bucket.
- Unsorted candles.
- Duplicate candles.
- Partial active bucket.
- Day boundary.
- DST/session boundary where applicable.
- Empty input.
- Invalid timeframe.
Done checklist:

[x] Edge case tests pass
[x] Missing data handled explicitly
[x] Duplicate data does not corrupt OHLCV

Implementation note — 2026-06-30:

- Aggregation deduplicates source candles by timestamp using the latest received value before OHLCV calculation.
- Aggregate lifecycle metadata now includes source, expected, and missing counts plus an explicit completeness flag.
- Missing source intervals are never synthesized; OHLCV remains derived only from observed candles.
- Active partial buckets avoid false missing warnings solely because their target bucket has not closed.
- Added coverage for missing candles, duplicates, unsorted input, partial buckets, UTC day boundaries, DST-local input, empty input, and invalid targets.
- Verification: 98 market-data tests pass.
Day 30.21 — UX polish for custom timeframe
Goal: Make custom timeframe understandable to the user.

Codex task:

Polish multi-timeframe UI for custom timeframe.

Add:
- Source label:
  - Direct provider
  - Aggregated
- Base timeframe label when aggregated.
- Error tooltip for invalid timeframe.
- Small warning if data is partial or missing.
Done checklist:

[x] Source label visible
[x] Aggregated label visible
[x] Partial/missing warning visible

Implementation note — 2026-06-30:

- Favorite timeframe buttons are sorted by normalized duration rather than insertion order.
- Preset and favorited custom values are merged, deduplicated, and sorted in every chart-window selector.
- A custom `6m` favorite therefore appears after `5m` and before `15m` in both toolbar and window dropdowns.
- Added persisted candle quality fields for partial, complete, source, expected, and missing counts.
- API metadata summarizes partial/incomplete buckets and total missing source candles on both cache misses and hits.
- Chart windows show `Missing N` or `Partial` warnings with diagnostic tooltips.
- Trailing partial or incomplete aggregates are no longer trusted as complete cache coverage; they are rebuilt as source candles arrive.
- Polling custom timeframes request the active bucket through the current minute so M3 continues updating before the bucket closes.
- Custom timeframes now consume a shared M1 WebSocket source and update their active UTC bucket on every provider event; REST remains the history and resume reconciliation path.
- One expected open partial candle is hidden while the stream is healthy; genuine missing-source diagnostics remain visible.
- Oanda direct and custom chart windows share one M1 realtime clock, eliminating independently polled M1/M5 phase drift.
- Live rendering updates only the final series item when history is unchanged, avoiding a full chart redraw per event.
- Verification: 99 market-data, 57 API, and 57 frontend tests plus Ruff and production build pass.
Day 30.22 — Custom timeframe documentation
Goal: Document how custom timeframe works.

Codex task:

Update docs/architecture.md and docs/api.md.

Document:
- TimeframeParser.
- CandleAggregator.
- Direct provider vs aggregate fallback.
- Closed vs partial candles.
- Custom timeframe API examples.
- Warning that aggregation is not prediction; it is OHLCV resampling.
Done checklist:

[x] Architecture docs updated
[x] API docs updated
[x] Examples included

Implementation note — 2026-06-30:

- Updated architecture to match the implemented parser, provider routing, aggregation cache, quality persistence, realtime isolation, and frontend source labels.
- Documented the `/market/candles` envelope, custom request examples, metadata fields, validation rules, cache-hit behavior, and quality semantics.
- Explicitly states that aggregation is deterministic OHLCV resampling, not prediction or financial advice.
Day 30.30 — Structure engine base
Goal: Create foundation for market structure analysis.

Codex task:

Create services/structure-engine.

Define:
- Candle input type
- SwingPoint type
- SwingDirection enum
- MarketStructureState type
- StructureConfig type

Rules:
- Do not generate BUY/SELL signal yet.
- This module only analyzes price structure.
- Keep code pure and testable.
Done checklist:

[ ] services/structure-engine exists
[ ] Structure types exist
[ ] Tests for type validation exist
Day 30.31 — Swing high / swing low detector
Goal: Detect swing highs and swing lows from candles.

Codex task:

Implement swing high / swing low detection.

Rules:
- A swing high is a candle whose high is greater than N candles on the left and N candles on the right.
- A swing low is a candle whose low is lower than N candles on the left and N candles on the right.
- Config:
  - left_bars
  - right_bars
  - min_distance
- Return confirmed swing points only.
- Do not repaint confirmed swings.
- Add tests.
Done checklist:

[ ] Swing high detected
[ ] Swing low detected
[ ] Confirmed swings do not repaint
[ ] Tests pass
Day 30.32 — Zigzag swing compression
Goal: Clean raw swing points into readable alternating waves.

Codex task:

Create zigzag swing compression.

Requirements:
- Remove consecutive duplicate swing highs or swing lows.
- If two swing highs appear consecutively, keep the stronger high.
- If two swing lows appear consecutively, keep the stronger low.
- Output alternating structure:
  HIGH -> LOW -> HIGH -> LOW
- Add tests.
Done checklist:

[ ] Consecutive duplicate highs/lows compressed
[ ] Alternating swing sequence returned
[ ] Tests pass
Day 30.33 — Swing wave builder
Goal: Convert swing points into swing waves.

Codex task:

Create SwingWave builder.

Each wave should include:
- start swing
- end swing
- direction: UP or DOWN
- start_time
- end_time
- start_price
- end_price
- length_points
- length_percent
- candle_count
- volume_sum if available

Add tests.
Done checklist:

[ ] Swing waves built from points
[ ] Wave direction calculated
[ ] Wave metrics calculated
[ ] Tests pass
Day 30.34 — Trend classification
Goal: Classify market trend from swing structure.

Codex task:

Implement trend classification.

Rules:
- Uptrend: higher high + higher low
- Downtrend: lower high + lower low
- Range: mixed or unclear structure

Output:
- UP_TREND
- DOWN_TREND
- RANGE
- UNKNOWN

Add tests.
Done checklist:

[ ] Uptrend detected
[ ] Downtrend detected
[ ] Range detected
[ ] Tests pass
Day 30.35 — BOS / CHOCH detection
Goal: Detect break of structure and change of character.

Codex task:

Implement BOS and CHOCH detection.

Definitions:
- BOS bullish: price breaks previous swing high in an uptrend.
- BOS bearish: price breaks previous swing low in a downtrend.
- CHOCH bullish: price breaks previous swing high after downtrend.
- CHOCH bearish: price breaks previous swing low after uptrend.

Return events:
- event_type
- timestamp
- price
- broken_swing_id
- direction
- confidence metadata

Add tests.
Done checklist:

[ ] Bullish BOS detected
[ ] Bearish BOS detected
[ ] Bullish CHOCH detected
[ ] Bearish CHOCH detected
[ ] Tests pass
Day 30.36 — Pullback / retracement analysis
Goal: Analyze pullback depth inside swing waves.

Codex task:

Implement retracement analysis.

Requirements:
- For each active impulse wave, measure pullback percentage.
- Calculate retracement depth:
  - shallow
  - normal
  - deep
- Suggested zones:
  - shallow: < 38.2%
  - normal: 38.2% - 61.8%
  - deep: > 61.8%
- Do not depend on visual chart drawing.
- Add tests.
Done checklist:

[ ] Pullback depth calculated
[ ] Shallow/normal/deep classification works
[ ] Tests pass
Day 30.37 — Key zone detection
Goal: Detect structure zones from swing points.

Codex task:

Implement key zone detection from swing points.

Zones:
- previous swing high zone
- previous swing low zone
- support zone
- resistance zone
- breakout level

Each zone should include:
- price_low
- price_high
- source swing
- timeframe
- strength score

Add tests.
Done checklist:

[ ] Swing high/low zones generated
[ ] Support/resistance zones generated
[ ] Strength score exists
[ ] Tests pass
Day 30.38 — Structure API
Goal: Expose structure analysis to frontend and setup engine.

Codex task:

Create API endpoint:
POST /structure/analyze

Input:
- symbol
- timeframe
- start
- end
- config

Output:
- swings
- waves
- trend
- bos_events
- choch_events
- zones

Rules:
- Do not return BUY/SELL signal.
- This endpoint is for analysis only.
- Add tests.
Done checklist:

[ ] /structure/analyze works
[ ] Swings/waves/trend returned
[ ] No trade signal generated
[ ] Tests pass
Day 30.39 — Draw structure on chart
Goal: Visualize structure analysis on chart windows.

Codex task:

Add frontend overlay for swing points and structure events.

Requirements:
- Show swing high markers.
- Show swing low markers.
- Show BOS marker.
- Show CHOCH marker.
- Allow toggles:
  - Show swings
  - Show structure events
  - Show zones
- Work inside multi-timeframe windows.
Done checklist:

[ ] Swing markers visible
[ ] BOS/CHOCH markers visible
[ ] Structure overlay toggles work
[ ] Multi-window compatible
Day 30.40 — Setup engine base
Goal: Create rule-based setup engine for trading concepts / "thế đánh".

Codex task:

Create services/setup-engine.

Define:
- SetupType enum
- SetupCandidate type
- SetupCondition type
- SetupResult type
- BaseSetupDetector interface
- SetupRegistry

Important:
- Do not place real orders.
- Do not generate final financial advice.
- Only detect rule-based setup candidates for research, paper trading, and backtesting.
Done checklist:

[ ] services/setup-engine exists
[ ] Setup types defined
[ ] Setup registry exists
[ ] Tests pass
Day 30.41 — Trend Pullback setup
Goal: Detect trend pullback setup.

Codex task:

Implement TrendPullbackSetupDetector.

Rules:
- Trend is UP_TREND or DOWN_TREND.
- Latest price pulls back into a structure zone.
- Pullback depth is normal, not too shallow and not too deep.
- No confirmed CHOCH against trend.

Output:
- setup_type = TREND_PULLBACK
- direction
- entry_zone
- invalidation_level
- reason
- confidence_score

Add tests.
Done checklist:

[ ] Bullish trend pullback detected
[ ] Bearish trend pullback detected
[ ] CHOCH invalidation works
[ ] Tests pass
Day 30.42 — Breakout Retest setup
Goal: Detect breakout retest setup.

Codex task:

Implement BreakoutRetestSetupDetector.

Rules:
- BOS detected.
- Price returns to retest broken structure level.
- Retest happens within configurable candle count.
- Retest does not fully invalidate breakout.

Output:
- setup_type = BREAKOUT_RETEST
- direction
- breakout_level
- retest_zone
- invalidation_level
- reason

Add tests.
Done checklist:

[ ] Bullish breakout retest detected
[ ] Bearish breakout retest detected
[ ] Invalidated breakout rejected
[ ] Tests pass
Day 30.43 — Range Reversal setup
Goal: Detect range reversal setup.

Codex task:

Implement RangeReversalSetupDetector.

Rules:
- Structure trend is RANGE.
- Price reaches upper or lower range zone.
- Recent swing rejects zone.
- Setup direction is opposite side of range.

Output:
- setup_type = RANGE_REVERSAL
- direction
- range_high
- range_low
- entry_zone
- invalidation_level
- reason

Add tests.
Done checklist:

[ ] Upper range reversal detected
[ ] Lower range reversal detected
[ ] Non-range market rejected
[ ] Tests pass
Day 30.44 — Liquidity Sweep Reclaim setup
Goal: Detect liquidity sweep and reclaim setup from candle/structure data.

Codex task:

Implement LiquiditySweepReclaimSetupDetector.

Rules:
- Price breaks previous swing high/low.
- Then closes back inside prior range.
- Sweep must happen near a known structure zone.
- Direction is opposite the sweep.

Output:
- setup_type = LIQUIDITY_SWEEP_RECLAIM
- direction
- swept_level
- reclaim_close
- invalidation_level
- reason

Add tests.
Done checklist:

[ ] High sweep reclaim detected
[ ] Low sweep reclaim detected
[ ] Failed reclaim rejected
[ ] Tests pass
Day 30.45 — Setup API
Goal: Expose setup candidates to frontend and strategy engine.

Codex task:

Create endpoint:
POST /setups/detect

Input:
- symbol
- timeframe
- start
- end
- setup_types
- config

Output:
- setup candidates
- structure summary
- reasons
- invalidation levels

Rules:
- Do not execute trades.
- Do not place real orders.
- Add tests.
Done checklist:

[ ] /setups/detect works
[ ] Setup candidates returned
[ ] No real order code
[ ] Tests pass
Day 30.50 — Cross-market data source registry
Goal: Prepare data routing for gold, index, and FX using separate chart and futures flow sources.

Codex task:

Create data source registry in services/data-engine.

Requirements:
- Create source_registry.py.
- Create symbol_mapping.py.
- Each symbol mapping must support:
  - canonical_symbol
  - chart_source
  - orderflow_source
  - liquidity_source
- Add metadata fields:
  - provider
  - venue
  - market_type
  - data_type
  - exchange_symbol
  - canonical_symbol

Initial mappings:
- XAUUSD chart -> OANDA XAU_USD or broker CFD
- XAUUSD orderflow -> CME GC / MGC futures
- US100 chart -> OANDA NAS100_USD or broker CFD
- US100 orderflow -> CME NQ / MNQ futures
- US500 chart -> OANDA SPX500_USD or broker CFD
- US500 orderflow -> CME ES / MES futures
- EURUSD chart -> OANDA EUR_USD
- EURUSD orderflow -> CME 6E futures

Add tests.
Done checklist:

[ ] Source registry exists
[ ] Symbol mapping exists
[ ] Chart source and orderflow source are separate
[ ] Tests pass
Day 30.51 — OANDA chart data adapter
Goal: Add chart/candle data adapter for FX/gold/index CFD-style instruments.

Codex task:

Create OANDA chart data adapter.

Requirements:
- Add provider folder:
  services/data-ingestion/providers/oanda
- Implement candle fetch adapter for chart data.
- Support instruments from symbol mapping.
- Normalize candles into internal Candle schema.
- Include source metadata:
  - provider=oanda
  - market_type=spot_fx or cfd
  - venue=oanda
- Use env variables for token/account config.
- Do not hardcode secrets.
- Add mocked tests.
Done checklist:

[ ] OANDA adapter exists
[ ] Candles normalized
[ ] Secrets from env only
[ ] Mock tests pass
Day 30.52 — CME futures symbol mapping
Goal: Map chart symbols to CME futures proxies.

Codex task:

Create CME futures mapping.

Requirements:
- Add futures proxy mapping for:
  - XAUUSD -> GC / MGC
  - US100 -> NQ / MNQ
  - US500 -> ES / MES
  - US30 -> YM / MYM
  - EURUSD -> 6E
  - GBPUSD -> 6B
  - USDJPY -> 6J
  - AUDUSD -> 6A
- Include fields:
  - exchange
  - dataset
  - primary_contract_root
  - micro_contract_root where available
  - rollover_policy placeholder
- Add tests.
Done checklist:

[ ] CME mapping exists
[ ] Major gold/index/FX symbols mapped
[ ] Tests pass
Day 30.53 — Databento/CME futures adapter base
Goal: Add premium CME futures data adapter foundation.

Codex task:

Create Databento CME adapter base.

Requirements:
- Add provider folder:
  services/data-ingestion/providers/databento_cme
- Create adapter interface for:
  - historical OHLCV
  - historical trades
  - historical depth/orderbook
  - reference data
- Use env variables for API key.
- Do not hardcode secrets.
- Add mocked tests.
- If Databento package is not installed, adapter should fail gracefully with clear error.
Done checklist:

[ ] Databento adapter folder exists
[ ] Adapter interface exists
[ ] Missing dependency handled
[ ] Mock tests pass
Day 30.54 — Futures OHLCV ingestion
Goal: Fetch futures candles for CME proxies.

Codex task:

Implement futures OHLCV ingestion.

Requirements:
- Fetch historical OHLCV for mapped CME futures instrument.
- Normalize into internal Candle schema.
- Include source metadata:
  - provider=databento
  - venue=cme_globex
  - market_type=futures
  - data_type=candle
- Store separately from chart CFD/spot candles.
- Do not overwrite OANDA candles.
- Add tests.
Done checklist:

[ ] CME futures OHLCV normalized
[ ] Separate source metadata preserved
[ ] Does not overwrite chart candles
[ ] Tests pass
Day 30.55 — Futures trade ingestion
Goal: Get raw trade prints for orderflow analysis.

Codex task:

Implement futures trade ingestion.

Requirements:
- Fetch trade/tick data for mapped CME futures instrument.
- Normalize into Trade schema:
  - timestamp
  - price
  - quantity
  - side if available
  - notional
  - provider
  - venue
  - market_type
  - canonical_symbol
  - exchange_symbol
- Add storage/repository layer if needed.
- Add tests with mocked data.
Done checklist:

[ ] Futures trades normalized
[ ] Trade schema exists
[ ] Tests pass
Day 30.56 — Futures depth/orderbook ingestion
Goal: Get market depth/orderbook data for orderflow features.

Codex task:

Implement futures depth/orderbook ingestion.

Requirements:
- Fetch orderbook snapshots or depth updates from provider.
- Normalize into OrderBookSnapshot / OrderBookLevel schema.
- Include bid/ask levels.
- Include source metadata.
- Add tests with mocked depth snapshots.
Done checklist:

[ ] Orderbook schema exists
[ ] Depth data normalized
[ ] Tests pass
Day 30.57 — Big trade detector for CME futures
Goal: Detect unusually large futures trades.

Codex task:

Create services/orderflow-engine.

Implement BigTradeDetector.

Requirements:
- Input: normalized futures trades.
- Config:
  - notional_threshold
  - quantity_threshold
  - rolling_percentile_threshold
- Output event:
  - event_type = BIG_TRADE
  - direction if available
  - price
  - quantity
  - notional
  - timestamp
  - strength_score
- Add tests.
Done checklist:

[ ] orderflow-engine exists
[ ] BigTradeDetector works
[ ] Tests pass
Day 30.58 — Absorption detector
Goal: Detect possible absorption near structure levels.

Codex task:

Implement AbsorptionDetector.

Concept:
- Large traded volume occurs at/near a price zone.
- Price fails to continue in the aggressive direction.

Requirements:
- Input:
  - normalized trades
  - optional structure zones
  - optional candles
- Output:
  - event_type = ABSORPTION_SUSPECTED
  - price_zone
  - direction
  - volume
  - reason
  - confidence_score
- Do not mark as confirmed institutional activity.
- Add tests.
Done checklist:

[ ] Absorption suspected event generated
[ ] Works near structure zone
[ ] Tests pass
Day 30.59 — Iceberg suspicion detector
Goal: Detect possible iceberg/refill behavior from public futures data.

Codex task:

Implement IcebergSuspicionDetector.

Rules:
- Public data cannot confirm real iceberg orders.
- Use event type ICEBERG_SUSPECTED only.

Possible conditions:
- Repeated trades at same price zone.
- Large cumulative volume executed.
- Visible book liquidity appears to refill or not deplete normally.
- Price does not move as expected after large execution.

Output:
- event_type = ICEBERG_SUSPECTED
- price_zone
- cumulative_volume
- evidence
- confidence_score

Add tests with mocked trades/orderbook data.
Done checklist:

[ ] Iceberg suspected event generated
[ ] No false claim of confirmation
[ ] Tests pass
Day 30.60 — Combine chart structure with futures orderflow
Goal: Combine OANDA/CFD chart structure with CME futures orderflow features.

Codex task:

Create cross-source confluence service.

Requirements:
- Input:
  - chart structure from structure-engine
  - futures orderflow events from orderflow-engine
  - symbol mapping from data-engine
- Ensure both sources map to same canonical_symbol.
- Output confluence summary:
  - structure_trend
  - latest_key_zone
  - nearby_big_trade_events
  - nearby_absorption_events
  - nearby_iceberg_suspected_events
  - confidence notes

Rules:
- Do not generate BUY/SELL signal here.
- This is preparation for setup-engine.
- Add tests.
Done checklist:

[ ] Cross-source confluence created
[ ] Source mismatch rejected
[ ] Tests pass
Day 30.61 — Liquidity engine base
Goal: Create liquidity engine for sweep/reclaim and liquidity-zone concepts.

Codex task:

Create services/liquidity-engine.

Define:
- LiquidityEvent type
- LiquidityZone type
- SweepEvent type
- ReclaimEvent type
- LiquidityConfig type

Rules:
- This engine detects liquidity-related events.
- It does not place orders.
- It does not create final trading signals.
Done checklist:

[ ] liquidity-engine exists
[ ] Liquidity types defined
[ ] Tests pass
Day 30.62 — Wick / bóng nến reclaim detector
Goal: Detect sweep and reclaim using candle wicks around structure levels.

Codex task:

Implement WickReclaimDetector.

Rules:
- Price wicks beyond previous swing high/low.
- Candle closes back inside prior range or structure zone.
- Mark event as:
  - SWEEP_HIGH_RECLAIM
  - SWEEP_LOW_RECLAIM

Input:
- candles
- structure zones

Output:
- swept_level
- reclaim_close
- wick_size
- direction
- timestamp
- confidence_score

Add tests.
Done checklist:

[ ] Sweep high reclaim detected
[ ] Sweep low reclaim detected
[ ] Tests pass
Day 30.63 — Resting liquidity zone builder
Goal: Build liquidity zones from repeated swing highs/lows and futures depth when available.

Codex task:

Implement LiquidityZoneBuilder.

Inputs:
- structure swings/zones
- optional futures orderbook depth
- optional volume/orderflow events

Output zones:
- buy-side liquidity zone
- sell-side liquidity zone
- resting liquidity zone

Each zone includes:
- price_low
- price_high
- source
- strength_score
- timeframe

Add tests.
Done checklist:

[ ] Buy-side liquidity zones generated
[ ] Sell-side liquidity zones generated
[ ] Strength score exists
[ ] Tests pass
Day 30.64 — Liquidity API
Goal: Expose liquidity events and zones.

Codex task:

Create endpoint:
POST /liquidity/analyze

Input:
- symbol
- timeframe
- start
- end
- source_config
- config

Output:
- liquidity zones
- sweep events
- wick reclaim events
- source metadata

Add tests.
Done checklist:

[ ] /liquidity/analyze works
[ ] Events/zones returned
[ ] Source metadata included
[ ] Tests pass
Day 30.65 — Frontend liquidity overlay
Goal: Show liquidity events/zones on chart.

Codex task:

Add liquidity overlay to multi-timeframe chart windows.

Requirements:
- Toggle liquidity zones.
- Toggle sweep/reclaim markers.
- Show source label:
  - chart data source
  - futures/orderflow source if used
- Do not clutter chart if disabled.
Done checklist:

[ ] Liquidity overlay visible
[ ] Toggle works
[ ] Source label visible
Day 30.66 — Setup confluence engine
Goal: Allow setups to use structure + orderflow + liquidity together.

Codex task:

Update setup-engine to accept confluence inputs.

Inputs:
- structure summary
- setup detector config
- optional orderflow summary
- optional liquidity summary

Rules:
- Setup should explain which conditions passed/failed.
- Missing orderflow data should not crash the setup detector.
- If orderflow is unavailable, setup can still return but with lower confidence.

Add tests.
Done checklist:

[ ] Setup engine accepts confluence inputs
[ ] Missing orderflow handled
[ ] Tests pass
Day 30.67 — Trend pullback with orderflow confirmation
Goal: Upgrade Trend Pullback setup with futures orderflow confirmation.

Codex task:

Enhance TrendPullbackSetupDetector.

Additional confirmation options:
- Big trade appears near pullback zone.
- Absorption suspected near pullback zone.
- Sweep/reclaim occurs before continuation.

Output:
- base_structure_score
- orderflow_score
- liquidity_score
- final_confidence_score
- reason list

Add tests.
Done checklist:

[ ] Trend pullback uses optional orderflow
[ ] Confidence score split exists
[ ] Tests pass
Day 30.68 — Sweep reclaim with big trade confirmation
Goal: Create stronger liquidity sweep setup.

Codex task:

Enhance LiquiditySweepReclaimSetupDetector.

Additional confirmation options:
- Big trade after reclaim.
- Absorption at swept level.
- Iceberg suspected at swept/reclaim zone.

Output:
- setup candidate with confluence reasons
- invalidation level
- confidence breakdown

Add tests.
Done checklist:

[ ] Sweep reclaim uses big trade confirmation
[ ] Confidence breakdown exists
[ ] Tests pass
Day 30.69 — Breakout retest with absorption confirmation
Goal: Upgrade breakout retest setup with orderflow confirmation.

Codex task:

Enhance BreakoutRetestSetupDetector.

Additional confirmation options:
- Absorption at retest zone.
- Big trade in breakout direction.
- No strong opposite iceberg suspected event.

Add tests.
Done checklist:

[ ] Breakout retest uses absorption
[ ] Opposite evidence can reduce confidence
[ ] Tests pass
Day 30.70 — Cross-source setup UI panel
Goal: Display setup candidates with source explanation.

Codex task:

Create setup review panel in frontend.

Show:
- setup type
- direction
- symbol
- timeframe
- chart source
- orderflow source if used
- structure reason
- orderflow reason
- liquidity reason
- confidence score
- invalidation level

Rules:
- Do not display this as financial advice.
- Label as research/paper trading signal candidate.
Done checklist:

[ ] Setup review panel visible
[ ] Source explanation shown
[ ] Not displayed as financial advice
Day 30.80 — Premium data provider interface
Goal: Standardize paid data provider adapters.

Codex task:

Create premium data provider interface.

Provider types:
- Databento
- dxFeed
- CME direct placeholder
- CQG/Rithmic placeholder

Methods:
- get_historical_candles
- get_historical_trades
- get_orderbook_snapshots
- get_reference_data
- get_available_symbols

Rules:
- Do not hardcode API keys.
- Providers may be disabled if env is missing.
- Add tests for provider registry.
Done checklist:

[ ] Premium provider interface exists
[ ] Provider disabled state works
[ ] Tests pass
Day 30.81 — Provider capability registry
Goal: Know which paid provider supports which data type.

Codex task:

Create provider capability registry.

Capabilities:
- chart_candles
- futures_ohlcv
- futures_trades
- futures_depth
- historical_tick_replay
- reference_data
- realtime_stream

Initial providers:
- oanda
- databento_cme
- dxfeed
- cme_direct_placeholder

Add tests.
Done checklist:

[ ] Capability registry exists
[ ] Data type support can be queried
[ ] Tests pass
Day 30.82 — Source fallback router
Goal: Route requests to available provider or fallback safely.

Codex task:

Create source router.

Requirements:
- Given symbol + data_type, choose provider from source registry.
- If preferred provider is unavailable, use fallback if configured.
- If no source is available, return clear error.
- Do not silently mix unrelated instruments.
- Add tests for source mismatch and missing provider.
Done checklist:

[ ] Source router works
[ ] Missing provider error is clear
[ ] Source mismatch rejected
[ ] Tests pass
Day 30.83 — Data usage limits and cache
Goal: Control paid provider costs.

Codex task:

Add premium data usage and cache controls.

Requirements:
- Cache expensive historical requests.
- Add provider request counter.
- Add optional daily/monthly request limit config.
- Log usage without secrets.
- Add tests for cache hit and usage counting.
Done checklist:

[ ] Paid data cache exists
[ ] Usage counter exists
[ ] Limits configurable
[ ] Tests pass
Day 30.84 — Premium data config UI
Goal: Let user configure data providers safely.

Codex task:

Create settings UI for data providers.

Fields:
- provider name
- enabled / disabled
- API key status only, never reveal secret
- preferred chart source
- preferred futures source

Rules:
- Do not show raw secrets after save.
- Do not require provider config for local mock mode.
Done checklist:

[ ] Provider config UI exists
[ ] Secrets are not displayed
[ ] Local mock mode still works
Day 30.85 — Data source documentation
Goal: Document gold/index/FX source model.

Codex task:

Update docs/architecture.md and docs/data-sources.md.

Document:
- Why chart source and orderflow source are separate.
- XAUUSD -> GC/MGC mapping.
- US100 -> NQ/MNQ mapping.
- US500 -> ES/MES mapping.
- FX spot -> CME FX futures proxy mapping.
- Source metadata fields:
  - provider
  - venue
  - market_type
  - data_type
  - canonical_symbol
- Warning: futures orderflow is a proxy for CFD/spot chart, not the exact same market.
Done checklist:

[ ] Data source docs created
[ ] Symbol mapping explained
[ ] Proxy limitation explained
Day 30.90 — Quant engine base
Goal: Create a dedicated quant layer from Udemy-style algorithmic trading concepts without making Udemy the app architecture.

Position in architecture:

market-data / data-engine
        ↓
structure-engine
        ↓
setup-engine
        ↓
strategy-engine
        ↓
backtest-engine
        ↓
quant-engine for metrics, validation, research reports
Codex task:

Create services/quant-engine.

Context:
The product focuses on gold, indices, and FX trading research.
Udemy algorithmic trading concepts should be used as learning and calculation concepts, not as the app architecture.

Define:
- PriceSeries type
- ReturnSeries type
- TradeSeries type
- EquityCurve type
- QuantMetricResult type

Requirements:
- Use Pandas and NumPy internally where suitable.
- Keep quant-engine independent from frontend.
- Do not fetch provider data inside quant-engine.
- Do not generate BUY/SELL signals here.
- Do not implement live trading.
- Add validation helpers.
- Add unit tests.
Done checklist:

[ ] services/quant-engine exists
[ ] Base types exist
[ ] Validation helpers exist
[ ] Unit tests pass
Day 30.91 — Returns and price transformation
Goal: Implement basic price/return calculations used by backtest and research reports.

Codex task:

Implement return calculation utilities in services/quant-engine.

Functions:
- simple_returns(prices)
- log_returns(prices)
- cumulative_returns(returns)
- percentage_change(prices)
- normalize_price_series(prices, base=100)

Rules:
- Handle empty input safely.
- Handle missing values explicitly.
- Reject invalid zero/negative prices when log returns are requested.
- Return JSON-serializable output where needed.

Add tests for:
- normal price series
- empty data
- missing values
- zero/negative invalid price handling
Done checklist:

[ ] Simple returns work
[ ] Log returns work
[ ] Cumulative returns work
[ ] Edge cases tested
Day 30.92 — Volatility and range metrics
Goal: Add quantitative context for gold/index/FX sessions and setup filtering.

Codex task:

Implement volatility and range metrics in quant-engine.

Metrics:
- rolling volatility
- ATR-like candle range metric
- average candle body size
- average upper wick size
- average lower wick size
- range expansion / contraction flag

Inputs:
- candles with open/high/low/close/volume

Use cases:
- setup filtering
- regime detection
- risk-aware backtest
- gold/index/FX session context

Add tests for normal candles, flat candles, and missing candles.
Done checklist:

[ ] Rolling volatility works
[ ] ATR-like range works
[ ] Wick/body metrics work
[ ] Tests pass
Day 30.93 — Drawdown and equity analysis
Goal: Standardize drawdown calculation for backtest reports.

Codex task:

Implement drawdown utilities in quant-engine.

Functions:
- validate_equity_curve(equity_curve)
- running_peak(equity_curve)
- drawdown_series(equity_curve)
- max_drawdown(equity_curve)
- drawdown_duration(equity_curve)
- recovery_time(equity_curve)

Rules:
- Handle empty equity safely.
- Do not divide by zero.
- Return clear metric names.
- Add tests.
Done checklist:

[ ] Drawdown series works
[ ] Max drawdown works
[ ] Duration/recovery calculated
[ ] Tests pass
Day 30.94 — Trade statistics
Goal: Analyze closed trades from setup/strategy/backtest output.

Codex task:

Implement trade statistics in quant-engine.

Metrics:
- total trades
- winning trades
- losing trades
- win rate
- average win
- average loss
- largest win
- largest loss
- profit factor
- expectancy
- average reward/risk
- consecutive wins
- consecutive losses

Rules:
- Input is closed trade list.
- Do not assume all trades have stop loss.
- Handle no-trade case clearly.
- Add tests.
Done checklist:

[ ] Win rate works
[ ] Profit factor works
[ ] Expectancy works
[ ] No-trade case handled
Day 30.95 — Position sizing helpers
Goal: Add research-only risk sizing helpers for backtest and paper trading.

Codex task:

Create position sizing utilities in quant-engine.

Methods:
- fixed_quantity_size
- fixed_notional_size
- fixed_risk_percent_size
- stop_loss_based_size
- max_risk_per_trade_check

Rules:
- Research and paper trading only.
- Do not connect to live orders.
- Do not place or suggest real trades.
- Validate account balance, risk percent, entry price, stop price.
- Add tests.
Done checklist:

[ ] Fixed quantity sizing works
[ ] Fixed notional sizing works
[ ] Risk-percent sizing works
[ ] Invalid inputs rejected
Day 30.96 — Strategy evaluation report
Goal: Create one standard report format for every setup/strategy/backtest.

Codex task:

Create StrategyEvaluationReport in quant-engine.

Report sections:
- return metrics
- drawdown metrics
- trade statistics
- risk metrics
- setup distribution
- timeframe summary
- source metadata summary

Requirements:
- Output must be JSON serializable.
- Include symbol, timeframe, strategy_name, setup_type if available.
- Include provider/source metadata when available.
- Do not include secrets.
- Add tests.
Done checklist:

[ ] Report type exists
[ ] Report combines metrics
[ ] JSON output works
[ ] Tests pass
Day 30.97 — Walk-forward / forward test split helper
Goal: Prepare forward testing without parameter optimization yet.

Codex task:

Create walk-forward split utilities in quant-engine.

Support:
- fixed train/test split
- rolling windows
- expanding windows

Inputs:
- start date
- end date
- train window length
- test window length
- step size

Rules:
- Do not optimize strategy parameters yet.
- Only split data periods and return metadata.
- Add tests for edge cases.
Done checklist:

[ ] Fixed split works
[ ] Rolling window split works
[ ] Expanding split works
[ ] Tests pass
Day 30.98 — Basic regime detection
Goal: Classify market context for setup filtering.

Codex task:

Implement simple regime detection in quant-engine.

Inputs:
- structure summary
- volatility metrics
- return metrics
- candle range metrics

Output regime labels:
- TRENDING
- RANGING
- HIGH_VOLATILITY
- LOW_VOLATILITY
- UNKNOWN

Output should include:
- regime label
- confidence score
- reasons

Use cases:
- Trend Pullback setup should prefer trending regime.
- Range Reversal setup should prefer ranging regime.
- Backtest report should group results by regime.

Add tests.
Done checklist:

[ ] Regime labels generated
[ ] Reasons included
[ ] Unknown state handled
[ ] Tests pass
Day 30.99 — Quant docs and Udemy concept mapping
Goal: Document how Udemy quant concepts map into the product.

Codex task:

Create docs/quant-concepts.md.

Document:
- Udemy concepts used in MVP
- Which module implements each concept
- What is deliberately not included in MVP
- Why quant-engine is separate from structure/setup/strategy engines
- How quant-engine supports backtest-engine
- Research/paper-trading safety note

Map:
- Python OOP -> base classes and registries
- Pandas/NumPy -> quant-engine, indicator-engine, backtest-engine
- Technical indicators -> indicator-engine
- Strategy rules -> setup-engine and strategy-engine
- Backtesting -> backtest-engine and quant-engine
- Forward testing -> quant-engine/walk_forward.py
- Paper trading -> paper-trading
- Trading costs -> backtest-engine and quant-engine reports
- Broker API architecture -> exchange-adapters and data-ingestion
- Realtime concepts -> market-data and WebSocket services
Done checklist:

[ ] docs/quant-concepts.md exists
[ ] Concept-to-module map exists
[ ] MVP exclusions documented
[ ] Safety note included
## Week 7 — Indicator engine

### Day 31 — Indicator engine base

**Goal:** Create module foundation.

**Codex task:**

```txt
Create services/indicator-engine.

Define:
- Candle input type
- Indicator output type
- Base indicator interface
- Validation helpers

Add tests for validation.
```

**Done checklist:**

* [ ] Module created
* [ ] Types defined
* [ ] Validation tests pass

---

### Day 32 — SMA and EMA

**Goal:** Implement moving averages.

**Codex task:**

```txt
Implement SMA and EMA.

Input:
- candles
- period

Output:
- timestamp-value pairs

Tests:
- normal data
- empty data
- insufficient candles
- invalid period
```

**Done checklist:**

* [ ] SMA works
* [ ] EMA works
* [ ] Tests pass

---

### Day 33 — RSI

**Goal:** Implement RSI.

**Codex task:**

```txt
Implement RSI indicator.

Requirements:
- Default period 14
- Return timestamp-value pairs
- Handle insufficient candles
- Add unit tests
```

**Done checklist:**

* [ ] RSI works
* [ ] Edge cases handled
* [ ] Tests pass

---

### Day 34 — MACD

**Goal:** Implement MACD.

**Codex task:**

```txt
Implement MACD indicator.

Parameters:
- fast_period default 12
- slow_period default 26
- signal_period default 9

Output:
- macd
- signal
- histogram
- timestamp

Add tests.
```

**Done checklist:**

* [ ] MACD works
* [ ] Tests pass

---

### Day 35 — Indicator API

**Goal:** Frontend can request indicator data.

**Codex task:**

```txt
Create endpoint:
POST /indicators/calculate

Input:
- symbol
- timeframe
- indicator name
- params
- start
- end

Output:
- indicator values

Supported:
- SMA
- EMA
- RSI
- MACD
```

**Done checklist:**

* [ ] Indicator API works
* [ ] Tests pass
* [ ] Docs updated

---

## Week 8 — Indicator frontend

### Day 36 — Indicator selector UI

**Goal:** User can choose indicators.

**Codex task:**

```txt
Create indicator selector UI.

Features:
- Toggle SMA
- Toggle EMA
- Toggle RSI
- Toggle MACD
- Configure period values
```

**Done checklist:**

* [ ] Indicator selector visible
* [ ] Toggle works
* [ ] Params editable

---

### Day 37 — Draw SMA/EMA overlay

**Goal:** Overlay indicators on chart.

**Codex task:**

```txt
Draw SMA and EMA lines on candlestick chart.

Requirements:
- Fetch indicator data from backend.
- Add line series to chart.
- Remove line series when indicator disabled.
- Update when symbol/timeframe changes.
```

**Done checklist:**

* [ ] SMA visible
* [ ] EMA visible
* [ ] Toggle remove works

---

### Day 38 — RSI panel

**Goal:** Show RSI separately.

**Codex task:**

```txt
Create RSI panel below main candlestick chart.

Requirements:
- Use backend RSI data.
- Show RSI line.
- Show 70 and 30 reference levels.
- Handle loading and empty state.
```

**Done checklist:**

* [ ] RSI panel visible
* [ ] RSI data loads
* [ ] Empty state works

---

### Day 39 — MACD panel

**Goal:** Show MACD separately.

**Codex task:**

```txt
Create MACD panel below chart.

Requirements:
- Show MACD line
- Show signal line
- Show histogram
- Use backend MACD data
```

**Done checklist:**

* [ ] MACD panel visible
* [ ] MACD values render
* [ ] Toggle works

---

### Day 40 — Save indicator settings

**Goal:** Indicator preferences persist.

**Codex task:**

```txt
Persist selected indicators and params to settings API.

Requirements:
- Save enabled indicators.
- Save indicator periods.
- Reload settings after page refresh.
```

**Done checklist:**

* [ ] Indicator settings save
* [ ] Indicator settings reload
* [ ] No broken chart state

---

## Week 9 — Strategy engine

### Day 41 — Strategy engine base

**Goal:** Create strategy framework.

**Codex task:**

```txt
Create services/strategy-engine.

Define:
- BaseStrategy interface
- Signal type
- Signal enum: BUY, SELL, HOLD
- StrategyInput type
- StrategyResult type

Add tests for base validation.
```

**Done checklist:**

* [ ] Strategy module created
* [ ] Signal types defined
* [ ] Tests pass

---

### Day 42 — EMA crossover strategy

**Goal:** First real strategy.

**Codex task:**

```txt
Implement EMACrossoverStrategy.

Rules:
- BUY when fast EMA crosses above slow EMA.
- SELL when fast EMA crosses below slow EMA.
- HOLD otherwise.

Default:
- fast EMA 9
- slow EMA 21

Signal must include:
- symbol
- timeframe
- timestamp
- price
- reason
- indicator values

Add tests.
```

**Done checklist:**

* [ ] BUY detected
* [ ] SELL detected
* [ ] HOLD detected
* [ ] Tests pass

---

### Day 43 — RSI reversal strategy

**Goal:** Add second strategy.

**Codex task:**

```txt
Implement RSIReversalStrategy.

Rules:
- BUY when RSI crosses up from below 30.
- SELL when RSI crosses down from above 70.
- HOLD otherwise.

Add tests.
```

**Done checklist:**

* [ ] RSI BUY works
* [ ] RSI SELL works
* [ ] Tests pass

---

### Day 44 — Strategy registry

**Goal:** Make strategies pluggable.

**Codex task:**

```txt
Create strategy registry.

Requirements:
- Register strategy by name.
- List available strategies.
- Run strategy by name.
- Validate params.
- Add tests.
```

**Done checklist:**

* [ ] Registry works
* [ ] Strategies listed
* [ ] Invalid strategy handled

---

### Day 45 — Strategy API

**Goal:** Frontend can run strategy.

**Codex task:**

```txt
Create endpoints:
- GET /strategies
- POST /strategies/run

Input:
- symbol
- timeframe
- strategy_name
- params
- start
- end

Output:
- latest signal
- signal history if requested
```

**Done checklist:**

* [ ] Strategy API works
* [ ] Tests pass
* [ ] Docs updated

---

## Week 10 — Signal frontend and storage

### Day 46 — Signal history database

**Goal:** Store generated signals.

**Codex task:**

```txt
Create signal database model and migration.

Fields:
- id
- symbol
- timeframe
- strategy_name
- signal
- price
- timestamp
- reason
- metadata
- created_at

Add repository and tests.
```

**Done checklist:**

* [ ] Signal table exists
* [ ] Repository works
* [ ] Tests pass

---

### Day 47 — Signal history API

**Goal:** Read signal history.

**Codex task:**

```txt
Create endpoints:
- GET /signals
- GET /signals/latest

Filters:
- symbol
- timeframe
- strategy_name
- signal
- start
- end
```

**Done checklist:**

* [ ] Signal history API works
* [ ] Filters work
* [ ] Tests pass

---

### Day 48 — Signal table UI

**Goal:** Display strategy output.

**Codex task:**

```txt
Create signal history table in frontend.

Columns:
- timestamp
- symbol
- timeframe
- strategy
- signal
- price
- reason

Add filters for symbol and strategy.
```

**Done checklist:**

* [ ] Signal table visible
* [ ] Filters work
* [ ] API connected

---

### Day 49 — Chart signal markers

**Goal:** Show BUY/SELL on chart.

**Codex task:**

```txt
Add BUY/SELL markers to candlestick chart.

Requirements:
- BUY marker below candle.
- SELL marker above candle.
- Use signal API.
- Do not hardcode data.
- Update when symbol/timeframe changes.
```

**Done checklist:**

* [ ] BUY marker visible
* [ ] SELL marker visible
* [ ] No hardcoded markers

---

### Day 50 — Strategy selector UI

**Goal:** User can choose active strategy.

**Codex task:**

```txt
Create strategy selector UI.

Features:
- Select EMA crossover
- Select RSI reversal
- Edit strategy params
- Run strategy manually
- Show latest signal
```

**Done checklist:**

* [ ] Strategy selector works
* [ ] Manual run works
* [ ] Latest signal shown

---

## Week 11 — Backtest engine

### Day 51 — Backtest engine base

**Goal:** Create backtest framework.

**Codex task:**

```txt
Create services/backtest-engine.

Define:
- BacktestInput
- BacktestResult
- Trade
- Position
- PortfolioState

Add validation tests.
```

**Done checklist:**

* [ ] Backtest module created
* [ ] Types defined
* [ ] Tests pass

---

### Day 52 — Basic backtest loop

**Goal:** Strategy runs over candles.

**Codex task:**

```txt
Implement basic backtest loop.

Requirements:
- Iterate through historical candles.
- Run selected strategy.
- Open position on BUY.
- Close position on SELL.
- Track balance.
- No leverage.
- Long-only for MVP.
```

**Done checklist:**

* [ ] Backtest loop runs
* [ ] Trades generated
* [ ] Long-only enforced

---

### Day 53 — Trading costs

**Goal:** Make backtest more realistic.

**Codex task:**

```txt
Add trading costs to backtest engine.

Support:
- fee_percent
- spread_percent
- slippage_percent

Apply costs on entry and exit.
Add tests comparing no-cost vs high-cost scenarios.
```

**Done checklist:**

* [ ] Fees applied
* [ ] Spread applied
* [ ] Slippage applied
* [ ] Tests pass

---

### Day 54 — Backtest metrics

**Goal:** Calculate performance.

**Codex task:**

```txt
Implement backtest metrics.

Metrics:
- initial balance
- final balance
- PnL
- PnL percent
- total trades
- winning trades
- losing trades
- win rate
- max drawdown
- equity curve
```

**Done checklist:**

* [ ] Metrics calculated
* [ ] Equity curve generated
* [ ] Tests pass

---

### Day 55 — Backtest API

**Goal:** Frontend can run backtest.

**Codex task:**

```txt
Create endpoint:
POST /backtests/run

Input:
- symbol
- timeframe
- strategy_name
- strategy_params
- start
- end
- initial_balance
- position_size
- fee_percent
- spread_percent
- slippage_percent

Output:
- metrics
- trades
- equity_curve
```

**Done checklist:**

* [ ] Backtest API works
* [ ] Tests pass
* [ ] Docs updated

---

## Week 12 — Backtest frontend

### Day 56 — Backtest page

**Goal:** Create backtest UI.

**Codex task:**

```txt
Create frontend page:
/dashboard/backtest

Add form:
- symbol
- timeframe
- strategy
- date range
- initial balance
- position size
- trading costs
```

**Done checklist:**

* [ ] Backtest page visible
* [ ] Form works
* [ ] Values validated

---

### Day 57 — Run backtest from UI

**Goal:** Connect form to backend.

**Codex task:**

```txt
Connect backtest form to POST /backtests/run.

Requirements:
- Loading state
- Error state
- Success result state
- Preserve last submitted params
```

**Done checklist:**

* [ ] Backtest runs from UI
* [ ] Loading works
* [ ] Error handled

---

### Day 58 — Metrics cards

**Goal:** Show result summary.

**Codex task:**

```txt
Create backtest metrics cards.

Cards:
- Final balance
- PnL
- PnL %
- Win rate
- Max drawdown
- Total trades
```

**Done checklist:**

* [ ] Metrics visible
* [ ] Formatting clear
* [ ] Negative values handled

---

### Day 59 — Trade table

**Goal:** Show backtest trades.

**Codex task:**

```txt
Create backtest trade table.

Columns:
- entry time
- exit time
- entry price
- exit price
- size
- PnL
- PnL %
- reason
```

**Done checklist:**

* [ ] Trade table visible
* [ ] Empty trade state works
* [ ] Table scrolls properly

---

### Day 60 — Equity curve

**Goal:** Visualize performance.

**Codex task:**

```txt
Create equity curve chart for backtest result.

Requirements:
- Use chart library or simple line chart.
- Show account equity over time.
- Handle empty equity curve.
```

**Done checklist:**

* [ ] Equity curve visible
* [ ] Data correct
* [ ] Backtest page complete

---

# Month 3 — Paper Trading, Alerts, Exchange Read-Only, Release

## Week 13 — Paper trading backend

### Day 61 — Paper account model

**Goal:** Create virtual trading account.

**Codex task:**

```txt
Create paper trading models:
- paper_accounts
- paper_orders
- paper_positions
- paper_trades

Paper account fields:
- user_id
- starting_balance
- cash_balance
- equity
- created_at
```

**Done checklist:**

* [ ] Models created
* [ ] Migration created
* [ ] Tests pass

---

### Day 62 — Paper account API

**Goal:** User can create/read demo account.

**Codex task:**

```txt
Create paper account API:
- GET /paper/account
- POST /paper/account/reset

Default starting balance:
- 10000 USDT

Use MVP default user.
```

**Done checklist:**

* [ ] Account API works
* [ ] Reset works
* [ ] Tests pass

---

### Day 63 — Paper order execution

**Goal:** Simulate buy/sell orders.

**Codex task:**

```txt
Implement paper market order execution.

Rules:
- Market BUY uses latest price.
- Market SELL closes or reduces position.
- Prevent insufficient balance.
- No leverage.
- Apply fee_percent.
- Save order and trade history.
```

**Done checklist:**

* [ ] Buy works
* [ ] Sell works
* [ ] Insufficient balance blocked
* [ ] Tests pass

---

### Day 64 — Position tracking

**Goal:** Track open positions.

**Codex task:**

```txt
Implement paper position tracking.

Track:
- symbol
- size
- average entry
- current price
- unrealized PnL
- realized PnL
- status open/closed
```

**Done checklist:**

* [ ] Open position updates
* [ ] PnL calculated
* [ ] Close position works

---

### Day 65 — Paper trading API

**Goal:** Expose paper trading actions.

**Codex task:**

```txt
Create endpoints:
- GET /paper/account
- GET /paper/positions
- GET /paper/trades
- POST /paper/orders

Add tests for full buy/sell flow.
```

**Done checklist:**

* [ ] Paper API works
* [ ] Full flow tested
* [ ] No real order code

---

## Week 14 — Paper trading frontend

### Day 66 — Order panel UI

**Goal:** User can place demo orders.

**Codex task:**

```txt
Create order panel UI.

Fields:
- symbol
- side BUY/SELL
- order type MARKET only
- quantity
- estimated value
- submit button

Connect to paper order API.
```

**Done checklist:**

* [ ] Order panel visible
* [ ] Demo BUY works
* [ ] Demo SELL works

---

### Day 67 — Paper portfolio panel

**Goal:** Show demo account status.

**Codex task:**

```txt
Create paper portfolio panel.

Show:
- starting balance
- cash balance
- equity
- unrealized PnL
- realized PnL
```

**Done checklist:**

* [ ] Portfolio visible
* [ ] Values update after order
* [ ] PnL formatting clear

---

### Day 68 — Open positions UI

**Goal:** Show active demo positions.

**Codex task:**

```txt
Create open positions table.

Columns:
- symbol
- size
- average entry
- current price
- unrealized PnL
- action close
```

**Done checklist:**

* [ ] Positions table visible
* [ ] Close action works
* [ ] Empty state works

---

### Day 69 — Trade history UI

**Goal:** Show paper trades.

**Codex task:**

```txt
Create paper trade history table.

Columns:
- timestamp
- symbol
- side
- price
- quantity
- fee
- realized PnL
```

**Done checklist:**

* [ ] Trade history visible
* [ ] New trades appear
* [ ] Empty state works

---

### Day 70 — Full paper trading flow review

**Goal:** Verify complete demo trading.

**Codex task:**

```txt
Review and fix the full paper trading flow.

Flow:
1. Load chart.
2. Place paper BUY.
3. Position appears.
4. Portfolio updates.
5. Place SELL.
6. Position closes.
7. Trade history updates.
8. Realized PnL updates.

Fix bugs and add missing tests.
```

**Done checklist:**

* [ ] Full flow works
* [ ] Bugs fixed
* [ ] Tests pass

---

## Week 15 — Alert system

### Day 71 — Alert model

**Goal:** Store alert rules.

**Codex task:**

```txt
Create alert models:
- alert_rules
- alert_events

Alert rule fields:
- user_id
- symbol
- timeframe
- strategy_name
- signal_type
- channel
- enabled
- created_at
```

**Done checklist:**

* [ ] Models created
* [ ] Migration created
* [ ] Tests pass

---

### Day 72 — Alert engine

**Goal:** Generate alerts from signals.

**Codex task:**

```txt
Create alert-engine.

Requirements:
- Receive signal.
- Match enabled alert rules.
- Create alert event.
- Avoid duplicate alert for same signal.
- Add tests.
```

**Done checklist:**

* [ ] Alert engine works
* [ ] Duplicate prevention works
* [ ] Tests pass

---

### Day 73 — Web notification

**Goal:** Alert appears in web UI.

**Codex task:**

```txt
Create web notification system.

Requirements:
- Show alert popup when new alert event exists.
- Add alert history panel.
- Mark alert as read.
```

**Done checklist:**

* [ ] Popup visible
* [ ] Alert history visible
* [ ] Mark read works

---

### Day 74 — Telegram alert

**Goal:** Send alert to Telegram.

**Codex task:**

```txt
Add Telegram notification provider.

Requirements:
- Use TELEGRAM_BOT_TOKEN from env.
- Use TELEGRAM_CHAT_ID from user settings or env for MVP.
- Do not hardcode token.
- Add test with mocked HTTP request.
```

**Done checklist:**

* [ ] Telegram provider implemented
* [ ] Env-based config
* [ ] Mock test passes

---

### Day 75 — Alert rate limit

**Goal:** Prevent alert spam.

**Codex task:**

```txt
Add alert rate limiting.

Rules:
- No duplicate alert for same symbol/timeframe/strategy/signal/timestamp.
- Add cooldown setting in minutes.
- Default cooldown: 5 minutes.
```

**Done checklist:**

* [ ] Cooldown works
* [ ] Duplicate alert blocked
* [ ] Tests pass

---

## Week 16 — Exchange read-only

### Day 76 — Exchange adapter interface

**Goal:** Standardize exchange integration.

**Codex task:**

```txt
Create exchange adapter interface.

Methods:
- get_account_balance()
- get_positions()
- get_open_orders()
- get_trade_history()

Do not create place_order.
Do not create cancel_order.
Read-only only.
```

**Done checklist:**

* [ ] Interface exists
* [ ] No live order method
* [ ] Docs mention read-only

---

### Day 77 — Binance read-only adapter

**Goal:** Connect to Binance account read-only.

**Codex task:**

```txt
Implement Binance read-only adapter.

Requirements:
- Read account balance.
- Read open positions if available.
- Read trade history if available.
- Use API key and secret from encrypted storage or env for MVP.
- Never place orders.
- Add mocked tests.
```

**Done checklist:**

* [ ] Balance read works
* [ ] Tests mock private API
* [ ] No order placement exists

---

### Day 78 — API key encryption

**Goal:** Store API credentials safely.

**Codex task:**

```txt
Create API key storage service.

Requirements:
- Encrypt API key and secret before saving.
- Decrypt only when needed.
- Never log secret.
- Add tests for encryption/decryption.
```

**Done checklist:**

* [ ] Encryption works
* [ ] Secret not logged
* [ ] Tests pass

---

### Day 79 — Connect exchange UI

**Goal:** User can enter read-only credentials.

**Codex task:**

```txt
Create connect exchange page.

Fields:
- exchange name
- API key
- API secret
- read-only confirmation checkbox

Show warning:
This MVP does not support live trading.
Only read-only access is used.
```

**Done checklist:**

* [ ] UI visible
* [ ] Save credentials works
* [ ] Warning visible

---

### Day 80 — Exchange account dashboard

**Goal:** Show read-only account info.

**Codex task:**

```txt
Create exchange account dashboard.

Show:
- connected exchange
- balances
- positions if available
- last sync time
- connection status
```

**Done checklist:**

* [ ] Account info visible
* [ ] Sync works
* [ ] Errors handled

---

## Week 17 — Overview dashboard and UX

### Day 81 — Overview dashboard

**Goal:** Create main dashboard summary.

**Codex task:**

```txt
Create dashboard overview page.

Sections:
- Market summary
- Active watchlist
- Latest signals
- Paper portfolio summary
- Backtest shortcut
```

**Done checklist:**

* [ ] Overview page visible
* [ ] Cards connected to APIs
* [ ] Layout clean

---

### Day 82 — Market summary cards

**Goal:** Show market movement.

**Codex task:**

```txt
Create market summary cards.

For each watchlist symbol show:
- latest price
- 24h change if available
- volume if available
```

**Done checklist:**

* [ ] Market cards visible
* [ ] Data updates
* [ ] Empty state works

---

### Day 83 — Strategy performance summary

**Goal:** Summarize strategy results.

**Codex task:**

```txt
Create strategy performance summary widget.

Show:
- selected strategy
- latest signal
- recent signal count
- latest backtest PnL if available
```

**Done checklist:**

* [ ] Strategy widget visible
* [ ] Latest signal shown
* [ ] Backtest summary shown if exists

---

### Day 84 — Paper trading summary

**Goal:** Show demo account performance.

**Codex task:**

```txt
Create paper trading summary widget.

Show:
- equity
- cash
- open positions count
- unrealized PnL
- realized PnL
```

**Done checklist:**

* [ ] Paper summary visible
* [ ] Values update
* [ ] Link to paper trading page

---

### Day 85 — UI refactor

**Goal:** Make the app feel consistent.

**Codex task:**

```txt
Refactor frontend layout.

Requirements:
- Consistent spacing
- Consistent card components
- Shared button/input/table components
- Better mobile responsiveness
- No duplicated UI code where avoidable
```

**Done checklist:**

* [ ] UI consistent
* [ ] Shared components created
* [ ] No major visual bugs

---

## Week 18 — Hardening, testing, deployment

### Day 86 — Backend logging

**Goal:** Improve backend observability.

**Codex task:**

```txt
Improve backend logging.

Add:
- structured logs
- request ID
- error logging
- external API error logs without secrets
- WebSocket connection logs
```

**Done checklist:**

* [ ] Logs readable
* [ ] Secrets not logged
* [ ] Errors easier to debug

---

### Day 87 — Frontend error handling

**Goal:** Prevent blank crashes.

**Codex task:**

```txt
Add frontend error handling.

Requirements:
- Error boundary
- API error display
- WebSocket disconnected state
- Retry button
- Empty states for major pages
```

**Done checklist:**

* [ ] Error boundary works
* [ ] API errors shown
* [ ] Retry available

---

### Day 88 — GitHub Actions CI

**Goal:** Run tests automatically.

**Codex task:**

```txt
Create GitHub Actions workflow.

Run:
- backend tests
- frontend lint
- frontend tests if available
- type check
- basic build check
```

**Done checklist:**

* [ ] CI workflow exists
* [ ] Tests run on PR
* [ ] Build check works

---

### Day 89 — Deployment config

**Goal:** Prepare beta deployment.

**Codex task:**

```txt
Create deployment documentation and config.

Options:
- VPS with Docker Compose
- Railway
- Render

Add:
- production env example
- deploy checklist
- database migration instructions
- security notes
```

**Done checklist:**

* [ ] Deployment docs exist
* [ ] Production env documented
* [ ] Migration steps clear

---

### Day 90 — MVP release documentation

**Goal:** Prepare beta release.

**Codex task:**

```txt
Write MVP beta release docs.

Create:
- docs/beta-release.md
- docs/user-guide.md
- docs/security.md
- docs/known-limitations.md

Mention clearly:
- No real-money live trading
- Paper trading only
- Exchange connection is read-only
- Backtest results are not financial advice
```

**Done checklist:**

* [ ] Beta docs complete
* [ ] User guide complete
* [ ] Limitations clear

---

# 6. Udemy learning map

Use the Udemy algorithmic trading Python course as a learning source, not as direct app architecture.

## Apply immediately

* Python OOP
* Pandas and NumPy data handling
* Technical indicators
* Strategy rules
* Backtesting concepts
* Forward testing concepts
* Paper trading
* Trading costs
* Broker API architecture
* Realtime data concepts

## Apply later

* Machine learning trading
* Deep learning trading
* AWS automation
* Live trading
* Complex multi-broker execution

## How to study daily

```txt
Daily routine:
1. Watch 30–45 minutes of the relevant Udemy section.
2. Write the logic in simple Vietnamese.
3. Convert the logic into a Codex task.
4. Let Codex implement the module.
5. Review code and run tests.
```

---

# 7. Priority if delayed

If the plan is delayed, keep these features:

## Must keep

* Backend skeleton
* Frontend dashboard
* Candle chart
* Market data API
* Watchlist
* Indicators
* Strategy signals
* Backtest
* Paper trading basic

## Can delay

* Telegram alert
* Exchange read-only
* MACD
* Advanced dashboard
* Deployment polish

## Must not add early

* Live trading
* AI prediction
* Multi-exchange
* Copy trading
* Leverage

---

# 8. Final MVP definition

The MVP is considered complete when the user can:

```txt
1. Open the web app.
2. View realtime candlestick chart.
3. Select symbol and timeframe.
4. Manage watchlist.
5. Enable indicators.
6. Run strategy signal.
7. See BUY/SELL markers.
8. Run a backtest.
9. View PnL, win rate, drawdown, and trades.
10. Place paper trading orders.
11. View paper portfolio and trade history.
12. Receive basic alerts.
13. Optionally connect exchange in read-only mode.
```

The MVP is not complete if it places real-money orders.

---

# 9. Daily review checklist

At the end of every day:

```txt
- [ ] Code runs locally
- [ ] No hardcoded secrets
- [ ] No live trading code
- [ ] Main task completed
- [ ] Tests added or manual verification documented
- [ ] README/docs updated if needed
- [ ] Git commit created
- [ ] Bugs written down for later
```

---

# 10. Commit message format

```txt
feature: add market data provider interface
feature: implement Binance public candle adapter
feature: add candlestick chart component
feature: add EMA crossover strategy
feature: add backtest engine
fix: prevent duplicate realtime candles
docs: update architecture for market data flow
test: add backtest cost scenario tests
```

---

# 11. Branch naming

```txt
feature/day-01-monorepo-foundation
feature/day-02-api-skeleton
feature/day-03-web-skeleton
feature/day-11-market-provider
feature/day-21-websocket-market
feature/day-31-indicator-engine
feature/day-41-strategy-engine
feature/day-51-backtest-engine
feature/day-61-paper-trading
feature/day-76-exchange-readonly
```

---

# 12. Important safety note

This framework is for education, research, paper trading, and strategy testing.

Do not use this MVP for real-money automated trading until:

* Security review is completed
* Exchange permissions are restricted
* Live order code is separately reviewed
* Risk controls are added
* Position limits are added
* Kill switch is added
* Audit logs are added
* Manual confirmation flow is added
* Legal and financial compliance are reviewed
