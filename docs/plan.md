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

**Implementation note - 2026-06-29:**

The chart now loads settings before requesting candles, applies the stored default symbol and timeframe, and serializes preference PATCH requests after selection changes. A valid URL/watchlist symbol overrides the stored symbol and is then persisted as the new default. API failures keep usable local fallbacks and expose a compact settings status beside the read-only provider label.



# Multi-timeframe Review Workspace — Day 30.x Extension

## 1. Mục tiêu

Bổ sung cụm task sau **Day 30 — Persist frontend settings** để tạo một màn hình review đa khung thời gian cho web trading framework.

Mục tiêu của tính năng này:

- Một symbol chính dùng chung cho toàn bộ workspace.
- User có thể chọn layout gồm **1 / 2 / 4 / 8 cửa sổ chart**.
- Mỗi cửa sổ chart có timeframe riêng.
- Mỗi cửa sổ có checkbox **Reviewed** để tick khi đã xem xong khung đó.
- Có bộ đếm tiến độ review, ví dụ: `Reviewed 2/4 timeframes`.
- Có thể lưu layout, timeframe và trạng thái review vào settings.
- Sau đó có thể nối từng cửa sổ với `/market/candles` để lấy nến riêng theo timeframe.

Tính năng này phục vụ workflow phân tích thủ công đa khung thời gian:

```txt
1D  -> xem xu hướng lớn
4H  -> xem vùng chính
1H  -> xem cấu trúc/setup
15M -> xem vùng entry
5M  -> timing
1M  -> timing chi tiết
```

---

## 2. Nguyên tắc triển khai

### Bắt buộc

- Chỉ dùng **một symbol chung** cho toàn bộ layout.
- Không tạo symbol riêng cho từng cửa sổ.
- Mỗi cửa sổ chỉ được chọn timeframe riêng.
- Không implement live trading.
- Không coi checkbox review là tín hiệu giao dịch.
- Không hardcode dữ liệu chart.
- Không làm candle aggregation trong Day 30.x.
- Không phá flow single-chart cũ.
- Mỗi task nhỏ phải có test hoặc manual verification rõ ràng.

### Chưa làm ở cụm Day 30.x

- Không tự build nến 5m/15m/1h từ nến 1m.
- Không implement strategy đa khung.
- Không implement signal confirmation đa khung.
- Không thêm live order.
- Không thêm AI prediction.

---

## 3. Data structure đề xuất

```ts
export type ReviewTimeframe =
  | "1m"
  | "5m"
  | "15m"
  | "30m"
  | "1h"
  | "2h"
  | "4h"
  | "1d";

export type MultiTimeframeWindow = {
  id: string;
  timeframe: ReviewTimeframe;
  enabled: boolean;
  reviewChecked: boolean;
};

export type MultiTimeframeLayout = {
  symbol: string;
  windowCount: 1 | 2 | 4 | 8;
  windows: MultiTimeframeWindow[];
};
```

---

## 4. Default layout

### 1 window

```txt
15m
```

### 2 windows

```txt
1h
15m
```

### 4 windows

```txt
4h
1h
15m
5m
```

### 8 windows

```txt
1d
4h
2h
1h
30m
15m
5m
1m
```

---

# Day 30.1 — Multi-timeframe workspace model

## Goal

Chuẩn bị state/type cho màn review đa khung thời gian.

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Add multi-timeframe workspace state for the chart page.

Context:
The app already has symbol/timeframe selection and user settings persistence.
We now need to prepare a multi-timeframe review workspace for one selected symbol.

Requirements:
- Create TypeScript types for MultiTimeframeWindow and MultiTimeframeLayout.
- One workspace uses one shared symbol.
- Support window count presets: 1, 2, 4, 8.
- Each window has:
  - id
  - timeframe
  - enabled
  - reviewChecked
- Default symbol should use current selected symbol.
- Default window count: 4.
- Default 4-window layout:
  - 4h
  - 1h
  - 15m
  - 5m
- Do not connect API yet.
- Do not change backend.
- Keep old single-chart behavior working.

Output:
1. Implement the types and default layout helpers.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[x] MultiTimeframeLayout type exists
[x] MultiTimeframeWindow type exists
[x] Default 4-window config exists
[x] State updates without breaking old chart
[x] Old single-chart behavior still works
```

**Implementation note - 2026-06-29:**

Added typed window-count presets, `MultiTimeframeLayout`, `MultiTimeframeWindow`, immutable default-layout helpers, and shared-symbol updates. `ChartWorkspace` now owns a prepared four-window review state synchronized with settings and manual symbol changes; no multi-window UI, API request, backend change, or candle aggregation was introduced.

---

# Day 30.2 — Layout selector 1 / 2 / 4 / 8

## Goal

Cho phép user chọn số cửa sổ chart muốn xem.

## UI concept

```txt
Layout: [1] [2] [4] [8]
Symbol: BTCUSDT
Review mode: ON/OFF
```

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Create layout selector for multi-timeframe chart workspace.

Context:
The app needs a manual multi-timeframe review workspace.
The workspace uses one shared symbol and multiple timeframe windows.

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
- Keep old single-chart behavior working.

Output:
1. Implement layout selector UI.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[x] User can select 1 window
[x] User can select 2 windows
[x] User can select 4 windows
[x] User can select 8 windows
[x] Active layout is visible
[x] Existing state is preserved where possible
[x] One shared symbol is used for all windows
```

**Implementation note - 2026-06-29:**

Added an accessible segmented selector for 1, 2, 4, and 8 review windows. Resizing marks extra windows disabled instead of deleting them, restores hidden timeframe/review state when expanding, and appends stable default windows when needed. The selector displays the single shared workspace symbol while the existing single chart remains active below it.

---

# Day 30.3 — Multi-timeframe grid UI

## Goal

Hiển thị nhiều chart theo layout đã chọn.

## Layout concept

### 1 window

```txt
[ chart ]
```

### 2 windows

```txt
[ chart ][ chart ]
```

### 4 windows

```txt
[ chart ][ chart ]
[ chart ][ chart ]
```

### 8 windows

```txt
[ chart ][ chart ][ chart ][ chart ]
[ chart ][ chart ][ chart ][ chart ]
```

Với màn nhỏ, layout có thể responsive thành 1 hoặc 2 cột.

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Create MultiTimeframeGrid component.

Context:
The user needs a review workspace with 1, 2, 4, or 8 chart windows for the same symbol.

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
- Keep old single-chart behavior working.

Output:
1. Implement MultiTimeframeGrid component.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[x] MultiTimeframeGrid component exists
[x] 1-window layout renders
[x] 2-window layout renders
[x] 4-window layout renders
[x] 8-window layout renders
[x] Each window has timeframe selector
[x] Each window has review checkbox
[x] Responsive layout works
```

**Implementation note - 2026-06-29:**

Added a controlled `MultiTimeframeGrid` that renders only visible/enabled windows for the selected layout. Each repeated window shows the shared symbol, its own timeframe selector, a Reviewed checkbox, and a stable placeholder area. Window updates are keyed by ID, the grid responds from four to two to one column, and the existing live single chart remains unchanged below it.

---

# Day 30.4 — Extended timeframe presets

## Goal

Mở rộng timeframe để layout 8 cửa sổ có đủ khung khác nhau.

## Final supported review timeframes

```txt
1m
5m
15m
30m
1h
2h
4h
1d
```

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Extend timeframe options for multi-timeframe review mode.

Context:
The existing chart selector supports basic timeframes.
The multi-timeframe workspace needs enough distinct timeframes for 8 windows.

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
- The backend should still request candles directly by selected timeframe.
- Keep old single-chart selector working.

Output:
1. Implement the extended timeframe options.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[ ] 30m option exists
[ ] 2h option exists
[ ] 8-window default has 8 different timeframes
[ ] Old single-chart timeframe selector still works
[ ] No candle aggregation added in this task
```

---

# Day 30.5 — Review checkbox per window

## Goal

Mỗi khung có checkbox để đánh dấu đã review.

## Example

```txt
[✓] 1D reviewed
[✓] 4H reviewed
[ ] 1H reviewed
[ ] 15M reviewed
```

## Review progress

```txt
Reviewed 2/4 timeframes
```

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Add review checkbox behavior for each multi-timeframe window.

Context:
The multi-timeframe workspace is for manual review.
The checkbox is only a user workflow aid, not a trading signal.

Requirements:
- Each chart window has a checkbox labeled "Reviewed".
- Ticking checkbox updates reviewChecked for that window only.
- Add a review progress indicator:
  - Example: Reviewed 2/4 timeframes
- Add a "Clear review" button.
- Clear review should uncheck all visible/enabled windows.
- Do not store review as trading signal.
- Do not trigger strategy or paper trading from review checkbox.
- This is only for manual review workflow.

Output:
1. Implement review checkbox behavior.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[ ] Each window has Reviewed checkbox
[ ] Checkbox updates correct window
[ ] Review progress visible
[ ] Clear review works
[ ] Review checkbox does not create trading signal
[ ] Review checkbox does not trigger paper order
```

---

# Day 30.6 — Persist multi-timeframe layout

## Goal

Reload lại web vẫn giữ layout đang xem.

## Settings payload example

```json
{
  "default_symbol": "BTCUSDT",
  "default_timeframe": "15m",
  "selected_indicators": [],
  "theme": "dark",
  "multi_timeframe_layout": {
    "symbol": "BTCUSDT",
    "windowCount": 4,
    "windows": [
      {
        "id": "w1",
        "timeframe": "4h",
        "enabled": true,
        "reviewChecked": false
      },
      {
        "id": "w2",
        "timeframe": "1h",
        "enabled": true,
        "reviewChecked": false
      },
      {
        "id": "w3",
        "timeframe": "15m",
        "enabled": true,
        "reviewChecked": false
      },
      {
        "id": "w4",
        "timeframe": "5m",
        "enabled": true,
        "reviewChecked": false
      }
    ]
  }
}
```

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Persist multi-timeframe layout in user settings.

Context:
Day 30 already persists frontend settings.
Now extend settings to include the multi-timeframe review layout.

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
- Do not hardcode user-specific values.

Output:
1. Implement settings persistence for multi-timeframe layout.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[ ] Layout saves
[ ] Layout reloads after refresh
[ ] Invalid saved layout falls back safely
[ ] Existing settings still work
[ ] Existing default_symbol still works
[ ] Existing default_timeframe still works
```

---

# Day 30.7 — Connect multi-window charts to candles API

## Goal

Mỗi cửa sổ chart lấy nến riêng theo timeframe của nó.

## API behavior

Một symbol chung, nhiều request theo timeframe:

```txt
GET /market/candles?symbol=BTCUSDT&timeframe=4h
GET /market/candles?symbol=BTCUSDT&timeframe=1h
GET /market/candles?symbol=BTCUSDT&timeframe=15m
GET /market/candles?symbol=BTCUSDT&timeframe=5m
```

## Important decision

Ở task này vẫn lấy nến trực tiếp theo timeframe từ backend/provider.
Không tự build timeframe lớn từ nến 1m.

## Codex task

```txt
You are working inside the trading-framework repo.

Task:
Connect multi-timeframe windows to market candles API.

Context:
The app already has a market candles endpoint:
GET /market/candles

The multi-timeframe workspace uses one shared symbol and multiple chart windows.
Each enabled window should load its own timeframe independently.

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
- Do not hardcode candles.
- Keep old single-chart behavior working.

Output:
1. Connect multi-window charts to the candles API.
2. Add tests or manual verification steps.
3. Explain changed files.
4. Mention how to run and verify.
```

## Done checklist

```txt
[ ] Each window loads candles
[ ] Different timeframes show independently
[ ] Loading state works per window
[ ] Error state works per window
[ ] One failed window does not crash whole page
[ ] Existing CandlestickChart component is reused
[ ] No candle aggregation added in this task
```

---

# 5. Suggested implementation order

```txt
30.1 State/type
30.2 Layout selector
30.3 Grid UI
30.4 Timeframe presets
30.5 Review checkbox
30.6 Persist settings
30.7 Fetch candles
```

Không nên nhảy thẳng vào fetch nhiều chart ngay từ đầu. Nên làm UI/state trước để dễ debug, sau đó mới nối API.

---

# 6. Manual verification checklist

Sau khi hoàn thành cụm Day 30.x, kiểm tra theo flow:

```txt
1. Mở chart page.
2. Chọn symbol BTCUSDT.
3. Chọn layout 1 window.
4. Đổi timeframe trong window.
5. Chọn layout 2 windows.
6. Chọn layout 4 windows.
7. Chọn layout 8 windows.
8. Tick Reviewed ở từng window.
9. Kiểm tra progress Reviewed x/y.
10. Bấm Clear review.
11. Reload page.
12. Kiểm tra layout/timeframe/review state được load lại.
13. Nếu đã làm Day 30.7, kiểm tra mỗi window gọi đúng /market/candles theo timeframe riêng.
14. Kiểm tra lỗi một timeframe không làm crash toàn bộ workspace.
```

---

# 7. Notes for backend/provider

Hiện tại MVP nên lấy nến trực tiếp theo timeframe user chọn:

```txt
Chart request timeframe nào -> backend/provider lấy timeframe đó -> cache vào DB.
```

Ví dụ:

```txt
BTCUSDT 1m  -> provider 1m  -> DB candles timeframe=1m
BTCUSDT 5m  -> provider 5m  -> DB candles timeframe=5m
BTCUSDT 15m -> provider 15m -> DB candles timeframe=15m
BTCUSDT 1h  -> provider 1h  -> DB candles timeframe=1h
```

Chưa nên bắt buộc lấy nến 1m rồi tự build mọi timeframe trong cụm Day 30.x.

Candle aggregation nên để task riêng sau này:

```txt
services/market-data/candle_aggregator.py
```

Quy tắc aggregation sau này:

```txt
open   = open của cây đầu tiên
high   = max high trong nhóm
low    = min low trong nhóm
close  = close của cây cuối cùng
volume = sum volume
timestamp = thời điểm mở bucket
```

---

# 8. Definition of done

Tính năng multi-timeframe review workspace được xem là xong khi:

```txt
[ ] User chọn được 1 / 2 / 4 / 8 cửa sổ.
[ ] Tất cả cửa sổ dùng chung một symbol.
[ ] Mỗi cửa sổ chọn được timeframe riêng.
[ ] Mỗi cửa sổ có checkbox Reviewed.
[ ] Có progress Reviewed x/y.
[ ] Có Clear review.
[ ] Layout được lưu vào settings.
[ ] Reload page không mất layout.
[ ] Khi nối API, từng cửa sổ lấy candles độc lập.
[ ] Một cửa sổ lỗi không làm lỗi toàn bộ workspace.
[ ] Không có live trading code.
[ ] Không có candle aggregation trong Day 30.x.
```

---

# 9. Commit message suggestions

```txt
feature: add multi-timeframe workspace types
feature: add multi-timeframe layout selector
feature: add multi-timeframe chart grid
feature: add review checklist for timeframe windows
feature: persist multi-timeframe layout settings
feature: connect multi-timeframe charts to market candles api
fix: preserve multi-timeframe state when changing layout
```
---

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
