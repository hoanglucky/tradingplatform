"use client";

import type { Candle } from "@trading-framework/shared";
import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { CandlestickChart } from "./CandlestickChart";

const marketDataBaseUrl = process.env.NEXT_PUBLIC_MARKET_DATA_BASE_URL ?? "http://localhost:8101";

const SYMBOLS = [
  { value: "BTCUSDT", label: "BTC / USDT", provider: "Binance" },
  { value: "ETHUSDT", label: "ETH / USDT", provider: "Binance" },
  { value: "SOLUSDT", label: "SOL / USDT", provider: "Binance" },
  { value: "XAUUSD", label: "XAU / USD", provider: "Oanda" },
  { value: "SP500", label: "S&P 500", provider: "Oanda" },
  { value: "US100", label: "US 100", provider: "Oanda" },
] as const;

const TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"] as const;
type Timeframe = (typeof TIMEFRAMES)[number];

const TIMEFRAME_SECONDS: Record<Timeframe, number> = {
  "1m": 60,
  "5m": 300,
  "15m": 900,
  "1h": 3600,
  "4h": 14400,
  "1d": 86400,
};

type ApiCandle = {
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: string | number;
  high: string | number;
  low: string | number;
  close: string | number;
  volume: string | number;
};

function normalizeCandles(payload: unknown): Candle[] {
  if (!Array.isArray(payload)) {
    throw new Error("Market data response is not a candle list.");
  }

  return payload.map((item) => {
    const candle = item as ApiCandle;
    const normalized = {
      symbol: String(candle.symbol),
      timeframe: String(candle.timeframe),
      timestamp: String(candle.timestamp),
      open: Number(candle.open),
      high: Number(candle.high),
      low: Number(candle.low),
      close: Number(candle.close),
      volume: Number(candle.volume),
    };
    if (
      !normalized.symbol ||
      !normalized.timeframe ||
      !Number.isFinite(Date.parse(normalized.timestamp)) ||
      ![normalized.open, normalized.high, normalized.low, normalized.close, normalized.volume].every(Number.isFinite)
    ) {
      throw new Error("Market data response contains an invalid candle.");
    }
    return normalized;
  });
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Use the status fallback below.
  }
  return `Market data request failed (${response.status}).`;
}

export function ChartWorkspace() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [timeframe, setTimeframe] = useState<Timeframe>("15m");
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const selectedSymbol = SYMBOLS.find((item) => item.value === symbol) ?? SYMBOLS[0];
  const latest = candles.at(-1)?.close;
  const first = candles[0]?.open;
  const change = latest !== undefined && first !== undefined ? ((latest - first) / first) * 100 : null;

  useEffect(() => {
    const controller = new AbortController();

    async function loadCandles() {
      setLoading(true);
      setError(null);

      const interval = TIMEFRAME_SECONDS[timeframe];
      const endSeconds = Math.floor(Date.now() / 1000 / interval) * interval;
      const startSeconds = endSeconds - interval * 120;
      const params = new URLSearchParams({
        symbol,
        timeframe,
        start: new Date(startSeconds * 1000).toISOString(),
        end: new Date(endSeconds * 1000).toISOString(),
      });

      try {
        const response = await fetch(`${marketDataBaseUrl}/market/candles?${params}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(await getErrorMessage(response));
        }
        setCandles(normalizeCandles(await response.json()));
        setLastUpdated(new Date());
      } catch (requestError) {
        if (controller.signal.aborted) {
          return;
        }
        setError(requestError instanceof Error ? requestError.message : "Unable to load market data.");
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadCandles();
    return () => controller.abort();
  }, [refreshVersion, symbol, timeframe]);

  function selectSymbol(nextSymbol: string) {
    setCandles([]);
    setLastUpdated(null);
    setSymbol(nextSymbol);
  }

  function selectTimeframe(nextTimeframe: Timeframe) {
    if (nextTimeframe === timeframe) {
      return;
    }
    setCandles([]);
    setLastUpdated(null);
    setTimeframe(nextTimeframe);
  }

  return (
    <>
      <header className="chart-toolbar">
        <label className="chart-symbol-control">
          <span>Symbol</span>
          <select value={symbol} onChange={(event) => selectSymbol(event.target.value)}>
            {SYMBOLS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.value}
              </option>
            ))}
          </select>
          <small>{selectedSymbol.provider} · read-only</small>
        </label>
        <div className="chart-timeframes" aria-label="Timeframe">
          {TIMEFRAMES.map((item) => (
            <button
              key={item}
              type="button"
              className={timeframe === item ? "is-active" : undefined}
              aria-pressed={timeframe === item}
              onClick={() => selectTimeframe(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <div className="chart-market-summary">
          <div className="chart-quote">
            <span>Latest close</span>
            <strong>
              {latest === undefined
                ? "—"
                : latest.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </strong>
            <small className={change !== null && change < 0 ? "is-negative" : undefined}>
              {change === null ? "—" : `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`}
            </small>
          </div>
          <button
            type="button"
            className="chart-refresh-button"
            aria-label="Refresh candles"
            title="Refresh candles"
            disabled={loading}
            onClick={() => setRefreshVersion((version) => version + 1)}
          >
            <RefreshCw className={loading ? "is-spinning" : undefined} aria-hidden="true" size={17} />
          </button>
        </div>
      </header>

      <section className="chart-workspace" aria-labelledby="chart-heading">
        <div className="chart-heading-row">
          <div>
            <p className="eyebrow">Price chart</p>
            <h2 id="chart-heading">
              {selectedSymbol.label} · {timeframe}
            </h2>
          </div>
          <div className="chart-data-meta">
            <span className={`data-status ${error ? "is-error" : loading ? "is-loading" : "is-live"}`} aria-live="polite">
              {error ? "Unavailable" : loading ? (candles.length > 0 ? "Refreshing" : "Loading") : "Live data"}
            </span>
            <small>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Awaiting data"}</small>
          </div>
        </div>
        <CandlestickChart
          candles={candles}
          symbol={symbol}
          timeframe={timeframe}
          height={460}
          loading={loading && candles.length === 0}
          error={error}
        />
        <p className="chart-attribution">
          Charts by{" "}
          <a href="https://www.tradingview.com" target="_blank" rel="noreferrer">
            TradingView
          </a>
        </p>
      </section>
    </>
  );
}
