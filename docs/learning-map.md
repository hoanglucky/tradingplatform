# Learning Map

This document maps common algorithmic trading course concepts into the current Trading Framework architecture.

## Module mapping

### `market-data`

Relevant concepts:

- OHLCV candles
- Tickers and symbols
- Timeframes
- Historical data loading
- Data normalization
- Missing candle handling
- Timestamp alignment

MVP scope:

- Normalize market data into shared candle contracts.
- Store historical candles in PostgreSQL.
- Publish market data events through Redis.

Do not add yet:

- Paid data provider abstraction
- Complex order book reconstruction
- Multi-exchange symbol mapping beyond one read-only adapter

### `indicator-engine`

Relevant concepts:

- Moving averages
- RSI
- MACD
- Bollinger Bands
- Rolling windows
- Warm-up periods
- Indicator parameterization

MVP scope:

- Compute deterministic indicators from normalized candles.
- Keep indicator inputs and outputs serializable.
- Make indicator calculations testable without exchange access.

Do not add yet:

- Machine learning indicators
- Auto-generated indicator strategies
- Optimized vector engine before correctness is proven

### `strategy-engine`

Relevant concepts:

- Entry rules
- Exit rules
- Signal generation
- Position sizing constraints
- Risk filters
- Strategy parameter sets

MVP scope:

- Convert market and indicator data into `buy`, `sell`, or `hold` signals.
- Keep strategy output separate from execution.
- Send signals only to backtesting or paper trading.

Do not add yet:

- Live order execution
- Leverage
- Margin logic
- Copy trading
- Strategy marketplace

### `backtest-engine`

Relevant concepts:

- Historical replay
- Slippage
- Fees
- Equity curve
- Drawdown
- Win rate
- Sharpe ratio
- Benchmark comparison

MVP scope:

- Run deterministic strategy simulations against historical candles.
- Store backtest runs and metrics in PostgreSQL.
- Surface results through API and web dashboard.

Do not add yet:

- Hyperparameter optimization at scale
- Multi-asset portfolio optimizer
- Walk-forward automation before base simulation is trusted

### `paper-trading`

Relevant concepts:

- Simulated orders
- Simulated fills
- Positions
- Balances
- PnL
- Trade journal

MVP scope:

- Simulate orders and fills without touching an exchange.
- Track paper positions and portfolio state.
- Use strategy signals as inputs.

Do not add yet:

- Real broker or exchange execution
- Real account balance mutation
- Withdrawal, deposit, or transfer features

### `alert-engine`

Relevant concepts:

- Signal alerts
- Risk alerts
- System health alerts
- Notification throttling
- Alert routing

MVP scope:

- Send notifications for paper signals, backtest completion, and service failures.
- Support webhook and email configuration through environment variables.

Do not add yet:

- Paid notification channels
- User-configurable automation that can place live trades

### `exchange-adapters`

Relevant concepts:

- Exchange REST APIs
- Exchange WebSocket feeds
- API credentials
- Rate limits
- Symbol metadata
- Read-only account data

MVP scope:

- Implement read-only market data and optional read-only account snapshots.
- Keep credentials out of source code.
- Block write operations by default.

Do not add yet:

- Live order placement
- Cancel/replace real orders
- Margin, futures, leverage, or withdrawals

## Security and risk constraints

- Never hardcode API keys, secrets, or tokens.
- Keep `.env.example` safe and non-secret.
- Keep `ENABLE_LIVE_TRADING=false` by default.
- Keep `ENABLE_EXCHANGE_WRITES=false` by default.
- Keep `EXCHANGE_ADAPTER_MODE=read_only` by default.
- Treat all strategy output as advisory until it passes through paper trading and risk checks.
- Require explicit future design review before any exchange write path is added.
