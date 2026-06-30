"use client";

import type { Candle, MultiTimeframeWindow } from "@trading-framework/shared";
import { useEffect, useRef, useState } from "react";
import {
  MULTI_TIMEFRAME_TIMEFRAMES,
  type MultiTimeframeLayout,
  type MultiTimeframeTimeframe,
  uniqueVisibleMultiTimeframeTimeframes,
  visibleMultiTimeframeWindows,
} from "../lib/multi-timeframe";
import { fetchMarketCandles, recentCandleRequest } from "../lib/market-candles";
import {
  createHeartbeatPong,
  getReconnectDelay,
  mergeRealtimeCandle,
  normalizeRealtimeCandle,
  synchronizeLatestCandlePrice,
} from "../lib/market-stream";
import { CandlestickChart } from "./CandlestickChart";

const marketDataBaseUrl = process.env.NEXT_PUBLIC_MARKET_DATA_BASE_URL ?? "http://localhost:8101";
const marketWebSocketUrl = process.env.NEXT_PUBLIC_MARKET_WS_URL ?? "ws://localhost:8000/ws/market";

function positiveNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

const reconnectBaseMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_RECONNECT_MS, 1000);
const reconnectMaxMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_MAX_RECONNECT_MS, 15000);

type RealtimeStatus = "connecting" | "connected" | "reconnecting" | "source-reconnecting" | "error";

type MultiTimeframeGridProps = {
  layout: MultiTimeframeLayout;
  timezone: string;
  refreshVersion: number;
  onLatestPriceChange: (price: number | null) => void;
  onTimeframeChange: (windowId: string, timeframe: MultiTimeframeTimeframe) => void;
  onReviewChange: (windowId: string, reviewChecked: boolean) => void;
};

type MultiTimeframeChartWindowProps = {
  symbol: string;
  timezone: string;
  reviewWindow: MultiTimeframeWindow;
  refreshVersion: number;
  realtimeCandle?: Candle;
  realtimeStatus: RealtimeStatus;
  sharedLatestPrice: number | null;
  chartHeight: number;
  onTimeframeChange: (windowId: string, timeframe: MultiTimeframeTimeframe) => void;
  onReviewChange: (windowId: string, reviewChecked: boolean) => void;
};

function realtimeStatusLabel(status: RealtimeStatus): string {
  if (status === "connected") return "Live";
  if (status === "reconnecting" || status === "source-reconnecting") return "Reconnecting";
  if (status === "error") return "Stream unavailable";
  return "Connecting";
}

function MultiTimeframeChartWindow({
  symbol,
  timezone,
  reviewWindow,
  refreshVersion,
  realtimeCandle,
  realtimeStatus,
  sharedLatestPrice,
  chartHeight,
  onTimeframeChange,
  onReviewChange,
}: MultiTimeframeChartWindowProps) {
  const [historicalCandles, setHistoricalCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const realtimeCandleRef = useRef(realtimeCandle);

  useEffect(() => {
    realtimeCandleRef.current = realtimeCandle;
  }, [realtimeCandle]);

  const timeframeCandles = realtimeCandle
    ? mergeRealtimeCandle(historicalCandles, realtimeCandle)
    : historicalCandles;
  const candles =
    realtimeCandle && sharedLatestPrice !== null
      ? synchronizeLatestCandlePrice(timeframeCandles, sharedLatestPrice)
      : timeframeCandles;
  const visibleError = realtimeCandle ? null : error;

  useEffect(() => {
    const controller = new AbortController();

    async function loadCandles() {
      setLoading(true);
      setError(null);
      setHistoricalCandles([]);
      try {
        const historical = await fetchMarketCandles(
          marketDataBaseUrl,
          recentCandleRequest(symbol, reviewWindow.timeframe),
          controller.signal,
        );
        const currentRealtime = realtimeCandleRef.current;
        setHistoricalCandles(
          currentRealtime ? mergeRealtimeCandle(historical, currentRealtime) : historical,
        );
      } catch (requestError: unknown) {
        if (!controller.signal.aborted) {
          setError(requestError instanceof Error ? requestError.message : "Unable to load market data.");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadCandles();
    return () => controller.abort();
  }, [refreshVersion, reviewWindow.timeframe, symbol]);

  return (
    <article className="multi-timeframe-window" data-window-id={reviewWindow.id}>
      <header className="multi-timeframe-window-header">
        <div className="multi-timeframe-window-identity">
          <span>{symbol}</span>
          <strong>{reviewWindow.timeframe}</strong>
        </div>
        <div className="multi-timeframe-live-price">
          <span className={realtimeStatus === "connected" ? "is-live" : undefined}>
            {realtimeStatusLabel(realtimeStatus)}
          </span>
          <strong>
            {sharedLatestPrice === null
              ? "—"
              : sharedLatestPrice.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 5,
                })}
          </strong>
        </div>
        <label className="review-window-check">
          <input
            type="checkbox"
            checked={reviewWindow.reviewChecked}
            onChange={(event) => onReviewChange(reviewWindow.id, event.target.checked)}
          />
          <span>Reviewed</span>
        </label>
      </header>
      <label className="review-window-timeframe">
        <span>Timeframe</span>
        <select
          value={reviewWindow.timeframe}
          onChange={(event) =>
            onTimeframeChange(reviewWindow.id, event.target.value as MultiTimeframeTimeframe)
          }
        >
          {MULTI_TIMEFRAME_TIMEFRAMES.map((timeframe) => (
            <option value={timeframe} key={timeframe}>
              {timeframe}
            </option>
          ))}
        </select>
      </label>
      <CandlestickChart
        candles={candles}
        symbol={symbol}
        timeframe={reviewWindow.timeframe}
        timezone={timezone}
        height={chartHeight}
        loading={loading && candles.length === 0}
        error={visibleError}
      />
    </article>
  );
}

export function MultiTimeframeGrid({
  layout,
  timezone,
  refreshVersion,
  onLatestPriceChange,
  onTimeframeChange,
  onReviewChange,
}: MultiTimeframeGridProps) {
  const visibleWindows = visibleMultiTimeframeWindows(layout);
  const realtimeTimeframes = uniqueVisibleMultiTimeframeTimeframes(layout);
  const realtimeKey = realtimeTimeframes.join(",");
  const [realtimeCandles, setRealtimeCandles] = useState<Record<string, Candle>>({});
  const [realtimeStatuses, setRealtimeStatuses] = useState<Record<string, RealtimeStatus>>({});
  const [sharedQuote, setSharedQuote] = useState<{ symbol: string; price: number } | null>(null);
  const latestPriceChangeRef = useRef(onLatestPriceChange);
  const sharedLatestPrice = sharedQuote?.symbol === layout.symbol ? sharedQuote.price : null;

  useEffect(() => {
    latestPriceChangeRef.current = onLatestPriceChange;
  }, [onLatestPriceChange]);

  useEffect(() => {
    const timeframes = realtimeKey.split(",").filter(Boolean) as MultiTimeframeTimeframe[];
    const sockets = new Map<MultiTimeframeTimeframe, WebSocket>();
    const reconnectTimers = new Map<MultiTimeframeTimeframe, number>();
    const reconnectAttempts = new Map<MultiTimeframeTimeframe, number>();
    let disposed = false;

    function updateStatus(timeframe: MultiTimeframeTimeframe, status: RealtimeStatus) {
      setRealtimeStatuses((current) => ({
        ...current,
        [`${layout.symbol}:${timeframe}`]: status,
      }));
    }

    function scheduleReconnect(timeframe: MultiTimeframeTimeframe) {
      if (disposed || reconnectTimers.has(timeframe)) return;
      const attempt = reconnectAttempts.get(timeframe) ?? 0;
      const delay = getReconnectDelay(attempt, reconnectBaseMs, reconnectMaxMs);
      reconnectAttempts.set(timeframe, attempt + 1);
      updateStatus(timeframe, "reconnecting");
      reconnectTimers.set(
        timeframe,
        window.setTimeout(() => {
          reconnectTimers.delete(timeframe);
          connect(timeframe);
        }, delay),
      );
    }

    function connect(timeframe: MultiTimeframeTimeframe) {
      if (disposed) return;
      updateStatus(timeframe, "connecting");
      let socket: WebSocket;
      try {
        socket = new WebSocket(marketWebSocketUrl);
      } catch {
        scheduleReconnect(timeframe);
        return;
      }
      sockets.set(timeframe, socket);

      socket.addEventListener("open", () => {
        if (!disposed) {
          socket.send(JSON.stringify({ type: "subscribe", symbol: layout.symbol, timeframe }));
        }
      });
      socket.addEventListener("message", (event) => {
        if (disposed) return;
        try {
          const payload = JSON.parse(String(event.data)) as { type?: unknown; code?: unknown };
          const pong = createHeartbeatPong(payload);
          if (pong) {
            socket.send(JSON.stringify(pong));
            return;
          }
          if (payload.type === "subscribed") {
            reconnectAttempts.set(timeframe, 0);
            updateStatus(timeframe, "connected");
            return;
          }
          if (payload.type === "error") {
            updateStatus(timeframe, payload.code === "market_stream_reconnecting" ? "source-reconnecting" : "error");
            return;
          }
          const candle = normalizeRealtimeCandle(payload, layout.symbol, timeframe);
          if (candle) {
            setRealtimeCandles((current) => ({
              ...current,
              [`${layout.symbol}:${timeframe}`]: candle,
            }));
            setSharedQuote({ symbol: layout.symbol, price: candle.close });
            latestPriceChangeRef.current(candle.close);
            updateStatus(timeframe, "connected");
          }
        } catch {
          updateStatus(timeframe, "error");
        }
      });
      socket.addEventListener("error", () => socket.close());
      socket.addEventListener("close", () => {
        sockets.delete(timeframe);
        scheduleReconnect(timeframe);
      });
    }

    timeframes.forEach(connect);
    return () => {
      disposed = true;
      reconnectTimers.forEach((timer) => window.clearTimeout(timer));
      sockets.forEach((socket) => socket.close(1000, "Workspace subscription changed"));
    };
  }, [layout.symbol, realtimeKey]);

  return (
    <section
      className={`multi-timeframe-grid is-layout-${layout.windowCount}`}
      aria-label={`${layout.symbol} multi-timeframe review windows`}
    >
      {visibleWindows.map((reviewWindow) => (
        <MultiTimeframeChartWindow
          key={reviewWindow.id}
          symbol={layout.symbol}
          timezone={timezone}
          reviewWindow={reviewWindow}
          refreshVersion={refreshVersion}
          realtimeCandle={realtimeCandles[`${layout.symbol}:${reviewWindow.timeframe}`]}
          realtimeStatus={realtimeStatuses[`${layout.symbol}:${reviewWindow.timeframe}`] ?? "connecting"}
          sharedLatestPrice={sharedLatestPrice}
          chartHeight={layout.windowCount === 1 ? 460 : 260}
          onTimeframeChange={onTimeframeChange}
          onReviewChange={onReviewChange}
        />
      ))}
    </section>
  );
}
