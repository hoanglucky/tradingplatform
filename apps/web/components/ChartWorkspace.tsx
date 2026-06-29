"use client";

import type { Candle } from "@trading-framework/shared";
import { RefreshCw } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import {
  createHeartbeatPong,
  getReconnectDelay,
  mergeRealtimeCandle,
  normalizeRealtimeCandle,
} from "../lib/market-stream";
import { CandlestickChart } from "./CandlestickChart";
import { HISTORY_RANGES, historyStartSeconds, type HistoryRange } from "../lib/chart-history";
import {
  MULTI_TIMEFRAME_WINDOW_COUNTS,
  createDefaultMultiTimeframeLayout,
  resizeMultiTimeframeLayout,
  updateMultiTimeframeSymbol,
  updateMultiTimeframeWindow,
  type MultiTimeframeTimeframe,
} from "../lib/multi-timeframe";
import {
  getUserSettings,
  patchUserSettings,
  resolveChartPreferences,
  type ChartPreferences,
  type UserSettingsPatch,
} from "../lib/user-settings";
import { MultiTimeframeGrid } from "./MultiTimeframeGrid";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const marketDataBaseUrl = process.env.NEXT_PUBLIC_MARKET_DATA_BASE_URL ?? "http://localhost:8101";
const marketWebSocketUrl = process.env.NEXT_PUBLIC_MARKET_WS_URL ?? "ws://localhost:8000/ws/market";

function positiveNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

const reconnectBaseMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_RECONNECT_MS, 1000);
const reconnectMaxMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_MAX_RECONNECT_MS, 15000);

const SYMBOLS = [
  { value: "BTCUSDT", label: "BTC / USDT", provider: "Binance" },
  { value: "ETHUSDT", label: "ETH / USDT", provider: "Binance" },
  { value: "SOLUSDT", label: "SOL / USDT", provider: "Binance" },
  { value: "BNBUSDT", label: "BNB / USDT", provider: "Binance" },
  { value: "XRPUSDT", label: "XRP / USDT", provider: "Binance" },
  { value: "XAUUSD", label: "XAU / USD", provider: "Oanda" },
  { value: "SP500", label: "S&P 500", provider: "Oanda" },
  { value: "US100", label: "US 100", provider: "Oanda" },
] as const;

const TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"] as const;
type Timeframe = (typeof TIMEFRAMES)[number];
type PreferenceStatus = "loading" | "ready" | "saving" | "error";
type RealtimeStatus =
  | "disabled"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "source-reconnecting"
  | "error";

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

function getRealtimeStatusLabel(status: RealtimeStatus, retryDelayMs: number | null): string {
  switch (status) {
    case "disabled":
      return "Historical data";
    case "connected":
      return "Realtime";
    case "reconnecting":
      return retryDelayMs ? `Retrying in ${Math.ceil(retryDelayMs / 1000)}s` : "Reconnecting";
    case "source-reconnecting":
      return "Market source reconnecting";
    case "error":
      return "Stream unavailable";
    default:
      return "Connecting stream";
  }
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

export function ChartWorkspace({ initialSymbol }: { initialSymbol?: string }) {
  const normalizedInitialSymbol = SYMBOLS.some((item) => item.value === initialSymbol?.toUpperCase())
    ? initialSymbol?.toUpperCase() ?? "BTCUSDT"
    : "BTCUSDT";
  const initialProvider = SYMBOLS.find((item) => item.value === normalizedInitialSymbol)?.provider;
  const [symbol, setSymbol] = useState(normalizedInitialSymbol);
  const [timeframe, setTimeframe] = useState<Timeframe>("15m");
  const [historyRange, setHistoryRange] = useState<HistoryRange>(initialProvider === "Oanda" ? "30d" : "1d");
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [realtimeStatus, setRealtimeStatus] = useState<RealtimeStatus>("connecting");
  const [retryDelayMs, setRetryDelayMs] = useState<number | null>(null);
  const [preferencesReady, setPreferencesReady] = useState(false);
  const [preferenceStatus, setPreferenceStatus] = useState<PreferenceStatus>("loading");
  const [multiTimeframeLayout, setMultiTimeframeLayout] = useState(() =>
    createDefaultMultiTimeframeLayout(normalizedInitialSymbol),
  );
  const connectionVersionRef = useRef(0);
  const persistedPreferencesRef = useRef<ChartPreferences>({
    symbol: normalizedInitialSymbol,
    timeframe: "15m",
  });
  const settingsSaveQueueRef = useRef<Promise<void>>(Promise.resolve());
  const settingsSaveVersionRef = useRef(0);
  const selectedSymbol = SYMBOLS.find((item) => item.value === symbol) ?? SYMBOLS[0];
  const latest = candles.at(-1)?.close;
  const first = candles[0]?.open;
  const change = latest !== undefined && first !== undefined ? ((latest - first) / first) * 100 : null;

  useEffect(() => {
    const controller = new AbortController();

    void getUserSettings(apiBaseUrl, controller.signal)
      .then((settings) => {
        const supportedSymbols = SYMBOLS.map((item) => item.value);
        const storedPreferences = resolveChartPreferences(
          settings,
          undefined,
          supportedSymbols,
          TIMEFRAMES,
        );
        const effectivePreferences = resolveChartPreferences(
          settings,
          initialSymbol,
          supportedSymbols,
          TIMEFRAMES,
        );
        persistedPreferencesRef.current = storedPreferences;
        setSymbol(effectivePreferences.symbol);
        setMultiTimeframeLayout((current) =>
          updateMultiTimeframeSymbol(current, effectivePreferences.symbol),
        );
        setTimeframe(effectivePreferences.timeframe as Timeframe);
        const provider = SYMBOLS.find((item) => item.value === effectivePreferences.symbol)?.provider;
        setHistoryRange(provider === "Oanda" ? "30d" : "1d");
        setPreferenceStatus("ready");
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setPreferenceStatus("error");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setPreferencesReady(true);
        }
      });

    return () => controller.abort();
  }, [initialSymbol]);

  useEffect(() => {
    if (!preferencesReady) {
      return;
    }
    const persisted = persistedPreferencesRef.current;
    const patch: UserSettingsPatch = {};
    if (symbol !== persisted.symbol) {
      patch.default_symbol = symbol;
    }
    if (timeframe !== persisted.timeframe) {
      patch.default_timeframe = timeframe;
    }
    if (Object.keys(patch).length === 0) {
      return;
    }

    const saveVersion = ++settingsSaveVersionRef.current;
    const operation = settingsSaveQueueRef.current
      .catch(() => undefined)
      .then(async () => {
        if (settingsSaveVersionRef.current === saveVersion) {
          setPreferenceStatus("saving");
        }
        const updated = await patchUserSettings(apiBaseUrl, patch);
        persistedPreferencesRef.current = {
          symbol: updated.default_symbol,
          timeframe: updated.default_timeframe,
        };
      });
    settingsSaveQueueRef.current = operation;
    void operation.then(
      () => {
        if (settingsSaveVersionRef.current === saveVersion) {
          setPreferenceStatus("ready");
        }
      },
      () => {
        if (settingsSaveVersionRef.current === saveVersion) {
          setPreferenceStatus("error");
        }
      },
    );
  }, [preferencesReady, symbol, timeframe]);

  useEffect(() => {
    if (!preferencesReady) {
      return;
    }
    const controller = new AbortController();

    async function loadCandles() {
      setLoading(true);
      setError(null);

      const interval = TIMEFRAME_SECONDS[timeframe];
      const endSeconds = Math.floor(Date.now() / 1000 / interval) * interval;
      const startSeconds = historyStartSeconds(endSeconds, historyRange);
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
  }, [historyRange, preferencesReady, refreshVersion, symbol, timeframe]);

  useEffect(() => {
    const connectionVersion = ++connectionVersionRef.current;
    if (loading) {
      return;
    }

    let disposed = false;
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let reconnectAttempt = 0;

    function isCurrentConnection() {
      return !disposed && connectionVersionRef.current === connectionVersion;
    }

    function scheduleReconnect() {
      if (!isCurrentConnection() || reconnectTimer !== null) {
        return;
      }
      const delay = getReconnectDelay(reconnectAttempt, reconnectBaseMs, reconnectMaxMs);
      reconnectAttempt += 1;
      setRealtimeStatus("reconnecting");
      setRetryDelayMs(delay);
      reconnectTimer = window.setTimeout(() => {
        reconnectTimer = null;
        if (!isCurrentConnection()) {
          return;
        }
        setRealtimeStatus("connecting");
        setRetryDelayMs(null);
        connect();
      }, delay);
    }

    function connect() {
      if (!isCurrentConnection()) {
        return;
      }
      let activeSocket: WebSocket;
      try {
        activeSocket = new WebSocket(marketWebSocketUrl);
      } catch {
        window.setTimeout(scheduleReconnect, 0);
        return;
      }
      socket = activeSocket;
      let subscriptionSent = false;

      activeSocket.addEventListener("open", () => {
        if (!isCurrentConnection() || subscriptionSent) {
          return;
        }
        subscriptionSent = true;
        activeSocket.send(JSON.stringify({ type: "subscribe", symbol, timeframe }));
      });
      activeSocket.addEventListener("message", (event) => {
        if (!isCurrentConnection()) {
          return;
        }
        try {
          const payload = JSON.parse(String(event.data)) as { type?: unknown; code?: unknown };
          const pong = createHeartbeatPong(payload);
          if (pong) {
            activeSocket.send(JSON.stringify(pong));
            return;
          }
          if (payload.type === "subscribed") {
            reconnectAttempt = 0;
            setRetryDelayMs(null);
            setRealtimeStatus("connected");
            return;
          }
          if (payload.type === "error") {
            setRealtimeStatus(payload.code === "market_stream_reconnecting" ? "source-reconnecting" : "error");
            return;
          }
          const candle = normalizeRealtimeCandle(payload, symbol, timeframe);
          if (candle) {
            setCandles((current) => mergeRealtimeCandle(current, candle));
            setError(null);
            setLastUpdated(new Date());
            setRealtimeStatus("connected");
          }
        } catch {
          setRealtimeStatus("error");
        }
      });
      activeSocket.addEventListener("error", () => {
        if (isCurrentConnection()) {
          activeSocket.close();
        }
      });
      activeSocket.addEventListener("close", () => {
        if (isCurrentConnection()) {
          scheduleReconnect();
        }
      });
    }

    connect();

    return () => {
      disposed = true;
      connectionVersionRef.current += 1;
      if (reconnectTimer !== null) {
        window.clearTimeout(reconnectTimer);
      }
      socket?.close(1000, "Subscription changed");
    };
  }, [loading, selectedSymbol.provider, symbol, timeframe]);

  function selectSymbol(nextSymbol: string) {
    connectionVersionRef.current += 1;
    const nextProvider = SYMBOLS.find((item) => item.value === nextSymbol)?.provider;
    setRealtimeStatus(nextProvider ? "connecting" : "disabled");
    setRetryDelayMs(null);
    setCandles([]);
    setLastUpdated(null);
    setHistoryRange(nextProvider === "Oanda" ? "30d" : "1d");
    setMultiTimeframeLayout((current) => updateMultiTimeframeSymbol(current, nextSymbol));
    setSymbol(nextSymbol);
  }

  function selectHistoryRange(nextRange: HistoryRange) {
    if (nextRange === historyRange) {
      return;
    }
    setCandles([]);
    setLastUpdated(null);
    setHistoryRange(nextRange);
  }

  function selectReviewWindowCount(windowCount: (typeof MULTI_TIMEFRAME_WINDOW_COUNTS)[number]) {
    setMultiTimeframeLayout((current) => resizeMultiTimeframeLayout(current, windowCount));
  }

  function selectReviewTimeframe(windowId: string, nextTimeframe: MultiTimeframeTimeframe) {
    setMultiTimeframeLayout((current) =>
      updateMultiTimeframeWindow(current, windowId, { timeframe: nextTimeframe }),
    );
  }

  function setReviewChecked(windowId: string, reviewChecked: boolean) {
    setMultiTimeframeLayout((current) =>
      updateMultiTimeframeWindow(current, windowId, { reviewChecked }),
    );
  }

  function selectTimeframe(nextTimeframe: Timeframe) {
    if (nextTimeframe === timeframe) {
      return;
    }
    connectionVersionRef.current += 1;
    setRealtimeStatus("connecting");
    setRetryDelayMs(null);
    setCandles([]);
    setLastUpdated(null);
    setTimeframe(nextTimeframe);
  }

  return (
    <>
      <header
        className="chart-toolbar"
        data-review-symbol={multiTimeframeLayout.symbol}
        data-review-window-count={multiTimeframeLayout.windowCount}
        data-review-enabled-windows={multiTimeframeLayout.windows.filter((window) => window.enabled).length}
      >
        <label className="chart-symbol-control">
          <span>Symbol</span>
          <select value={symbol} onChange={(event) => selectSymbol(event.target.value)}>
            {SYMBOLS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.value}
              </option>
            ))}
          </select>
          <small>
            {selectedSymbol.provider} · read-only
            {preferenceStatus === "saving"
              ? " · saving"
              : preferenceStatus === "error"
                ? " · settings unavailable"
                : ""}
          </small>
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
        <div className="chart-ranges" aria-label="History range">
          {HISTORY_RANGES.map((item) => (
            <button
              key={item.value}
              type="button"
              className={historyRange === item.value ? "is-active" : undefined}
              aria-pressed={historyRange === item.value}
              onClick={() => selectHistoryRange(item.value)}
            >
              {item.label}
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
            onClick={() => {
              if (selectedSymbol.provider === "Binance") {
                setRealtimeStatus("connecting");
                setRetryDelayMs(null);
              }
              setRefreshVersion((version) => version + 1);
            }}
          >
            <RefreshCw className={loading ? "is-spinning" : undefined} aria-hidden="true" size={17} />
          </button>
        </div>
      </header>

      <section className="review-workspace-toolbar" aria-label="Multi-timeframe review layout">
        <div className="review-workspace-title">
          <span>Review layout</span>
          <strong>{multiTimeframeLayout.symbol}</strong>
        </div>
        <div className="review-layout-selector" aria-label="Window count">
          {MULTI_TIMEFRAME_WINDOW_COUNTS.map((windowCount) => (
            <button
              key={windowCount}
              type="button"
              className={multiTimeframeLayout.windowCount === windowCount ? "is-active" : undefined}
              aria-pressed={multiTimeframeLayout.windowCount === windowCount}
              aria-label={`${windowCount} chart ${windowCount === 1 ? "window" : "windows"}`}
              onClick={() => selectReviewWindowCount(windowCount)}
            >
              {windowCount}
            </button>
          ))}
        </div>
        <small>{multiTimeframeLayout.windowCount} windows · shared symbol</small>
      </section>

      <MultiTimeframeGrid
        layout={multiTimeframeLayout}
        onTimeframeChange={selectReviewTimeframe}
        onReviewChange={setReviewChecked}
      />

      <section className="chart-workspace" aria-labelledby="chart-heading">
        <div className="chart-heading-row">
          <div>
            <p className="eyebrow">Price chart</p>
            <h2 id="chart-heading">
              {selectedSymbol.label} · {timeframe} · {HISTORY_RANGES.find((item) => item.value === historyRange)?.label}
            </h2>
          </div>
          <div className="chart-data-meta">
            <span
              className={`data-status ${error || realtimeStatus === "error" ? "is-error" : realtimeStatus === "connected" ? "is-live" : "is-loading"}`}
              aria-live="polite"
            >
              {error
                ? "Unavailable"
                : loading
                  ? candles.length > 0
                    ? "Refreshing"
                    : "Loading"
                  : getRealtimeStatusLabel(realtimeStatus, retryDelayMs)}
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
