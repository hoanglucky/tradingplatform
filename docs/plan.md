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
* [ ] Pytest verified in local Python/Docker environment

**Implementation note - 2026-06-18:**

The API skeleton has been hardened with the planned `app/api/routes` structure, central router, logging setup, `/health`, `/health/ready`, `/safety`, and `/modules`. Docker pytest was attempted but did not reach test execution because BuildKit failed resolving `python:3.12-slim` credentials. Retry `docker compose run --rm api pytest` after Docker pull access is fixed.

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

* [ ] Web app runs locally
* [ ] Dashboard layout visible
* [ ] API health status visible

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

* [ ] `docker compose up` works
* [ ] Frontend accessible
* [ ] Backend accessible
* [ ] PostgreSQL starts
* [ ] Redis starts

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

* [ ] Makefile works
* [ ] README updated
* [ ] Local setup is clear

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

* [ ] DB connection works
* [ ] Alembic migration can run
* [ ] Backend still starts

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

* [ ] Migration created
* [ ] Tables created
* [ ] Indexes created

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

* [ ] Repository layer exists
* [ ] Symbol repository tests pass

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

* [ ] Symbol CRUD works
* [ ] Tests pass
* [ ] API docs show symbol endpoints

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

Add Makefile command:
- make seed

Update README.
```

**Done checklist:**

* [ ] Seed script works
* [ ] Symbols visible in API

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

* [ ] Interface created
* [ ] Candle schema created
* [ ] Tests for schema validation

---

### Day 12 — Binance public adapter

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

* [ ] Binance adapter works
* [ ] Mock tests pass
* [ ] No secret required

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

* [ ] `/market/candles` works
* [ ] Test with BTCUSDT works
* [ ] Errors handled cleanly

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

* [ ] Candles stored in DB
* [ ] No duplicate candles
* [ ] Tests pass

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

* [ ] Docs updated
* [ ] API behavior explained

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

* [ ] Chart page exists
* [ ] Mock candles render

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

* [ ] Component reusable
* [ ] Empty state works
* [ ] Resize works

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

* [ ] Symbol selector works
* [ ] Timeframe selector works
* [ ] State updates correctly

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

* [ ] Chart shows backend candles
* [ ] Loading state works
* [ ] Error state works

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

* [ ] Chart page usable
* [ ] Latest price visible
* [ ] Refresh works

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

* [ ] WebSocket connects
* [ ] Subscribe message works
* [ ] Mock updates received

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

* [ ] Realtime candles received
* [ ] Normalized format used
* [ ] Disconnect handled

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

* [ ] Chart updates realtime
* [ ] No duplicated candles
* [ ] Socket cleanup works

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

* [ ] Reconnect works
* [ ] Connection status visible
* [ ] No duplicate subscriptions

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

* [ ] Candle update tests pass
* [ ] Realtime logic stable

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

* [ ] Default user exists
* [ ] Backend can identify MVP user
* [ ] Docs mention mock user mode

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

* [ ] Watchlist API works
* [ ] Duplicate symbol rejected
* [ ] Tests pass

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

* [ ] Watchlist visible
* [ ] Click loads chart
* [ ] Add/remove works

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

* [ ] Settings table/model exists
* [ ] API works
* [ ] Tests pass

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

* [ ] Settings load
* [ ] Settings save
* [ ] Refresh keeps preferences

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
