"use client";

import type { Candle, MultiTimeframeWindow } from "@trading-framework/shared";
import { useEffect, useRef, useState } from "react";
import {
  type MultiTimeframeLayout,
  type MultiTimeframeTimeframe,
  uniqueVisibleMultiTimeframeTimeframes,
  visibleMultiTimeframeWindows,
} from "../lib/multi-timeframe";
import {
  fetchMarketCandleResult,
  recentCandleRequest,
  type CandleQueryMetadata,
} from "../lib/market-candles";
import {
  createHeartbeatPong,
  getReconnectDelay,
  mergeRealtimeCandle,
  normalizeRealtimeCandle,
  shouldResumeMarketData,
} from "../lib/market-stream";
import { CandlestickChart } from "./CandlestickChart";
import { supportsRealtimeTimeframe } from "../lib/timeframe-options";

const marketDataBaseUrl = process.env.NEXT_PUBLIC_MARKET_DATA_BASE_URL ?? "http://localhost:8101";
const marketWebSocketUrl = process.env.NEXT_PUBLIC_MARKET_WS_URL ?? "ws://localhost:8000/ws/market";

function positiveNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

const reconnectBaseMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_RECONNECT_MS, 1000);
const reconnectMaxMs = positiveNumber(process.env.NEXT_PUBLIC_MARKET_WS_MAX_RECONNECT_MS, 15000);

type RealtimeStatus = "connecting" | "connected" | "reconnecting" | "source-reconnecting" | "polling" | "error";

type MultiTimeframeGridProps = {
  layout: MultiTimeframeLayout;
  timeframeOptions: string[];
  timezone: string;
  refreshVersion: number;
  activeWindowId: string;
  onActiveWindowChange: (windowId: string) => void;
  onTimeframeChange: (windowId: string, timeframe: MultiTimeframeTimeframe) => void;
  onReviewChange: (windowId: string, reviewChecked: boolean) => void;
};

type MultiTimeframeChartWindowProps = {
  symbol: string;
  timezone: string;
  reviewWindow: MultiTimeframeWindow;
  timeframeOptions: string[];
  refreshVersion: number;
  resumeVersion: number;
  realtimeCandles?: Candle[];
  realtimeStatus: RealtimeStatus;
  chartHeight: number;
  active: boolean;
  onActivate: () => void;
  onTimeframeChange: (windowId: string, timeframe: MultiTimeframeTimeframe) => void;
  onReviewChange: (windowId: string, reviewChecked: boolean) => void;
};

function realtimeStatusLabel(status: RealtimeStatus): string {
  if (status === "connected") return "Live";
  if (status === "reconnecting" || status === "source-reconnecting") return "Reconnecting";
  if (status === "error") return "Stream unavailable";
  if (status === "polling") return "Auto sync";
  return "Connecting";
}

function MultiTimeframeChartWindow({
  symbol,
  timezone,
  reviewWindow,
  timeframeOptions,
  refreshVersion,
  resumeVersion,
  realtimeCandles,
  realtimeStatus,
  chartHeight,
  active,
  onActivate,
  onTimeframeChange,
  onReviewChange,
}: MultiTimeframeChartWindowProps) {
  const [historicalCandles, setHistoricalCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<CandleQueryMetadata | null>(null);
  const realtimeCandlesRef = useRef(realtimeCandles);
  const requestIdentityRef = useRef(`${symbol}:${reviewWindow.timeframe}`);

  useEffect(() => {
    realtimeCandlesRef.current = realtimeCandles;
  }, [realtimeCandles]);

  const candles = (realtimeCandles ?? []).reduce(
    (current, candle) => mergeRealtimeCandle(current, candle),
    historicalCandles,
  );
  const visibleError = realtimeCandles?.length ? null : error;

  useEffect(() => {
    const controller = new AbortController();

    async function loadCandles() {
      const requestIdentity = `${symbol}:${reviewWindow.timeframe}`;
      const identityChanged = requestIdentityRef.current !== requestIdentity;
      requestIdentityRef.current = requestIdentity;
      setLoading(true);
      setError(null);
      if (identityChanged) setHistoricalCandles([]);
      try {
        const result = await fetchMarketCandleResult(
          marketDataBaseUrl,
          recentCandleRequest(symbol, reviewWindow.timeframe),
          controller.signal,
        );
        const historical = result.candles;
        setMetadata(result.metadata);
        const currentRealtime = realtimeCandlesRef.current ?? [];
        setHistoricalCandles(
          currentRealtime.reduce(
            (current, candle) => mergeRealtimeCandle(current, candle),
            historical,
          ),
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
  }, [refreshVersion, resumeVersion, reviewWindow.timeframe, symbol]);

  return (
    <article
      className={`multi-timeframe-window${active ? " is-active" : ""}`}
      data-window-id={reviewWindow.id}
      onPointerDown={onActivate}
      onFocusCapture={onActivate}
    >
      <header className="multi-timeframe-window-header">
        <div className="multi-timeframe-window-identity">
          <span>{symbol}</span>
          <strong>{reviewWindow.timeframe}</strong>
          <span className={`window-stream-status${realtimeStatus === "connected" ? " is-live" : ""}`}>
            {realtimeStatusLabel(realtimeStatus)}
          </span>
          {metadata ? (
            <span
              className="window-source-label"
              title={`Provider: ${metadata.source_provider}; market: ${metadata.source_market_type}; cache: ${metadata.cache_hit ? "hit" : "miss"}; fetched ranges: ${metadata.missing_ranges_fetched}`}
            >
              {metadata.aggregation_used
                ? `Aggregated from ${metadata.base_timeframe}`
                : `${metadata.source_provider} · Direct`}
            </span>
          ) : null}
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
          {!timeframeOptions.includes(reviewWindow.timeframe) ? (
            <option value={reviewWindow.timeframe}>{reviewWindow.timeframe}</option>
          ) : null}
          {timeframeOptions.map((timeframe) => (
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
  timeframeOptions,
  timezone,
  refreshVersion,
  activeWindowId,
  onActiveWindowChange,
  onTimeframeChange,
  onReviewChange,
}: MultiTimeframeGridProps) {
  const visibleWindows = visibleMultiTimeframeWindows(layout);
  const realtimeTimeframes = uniqueVisibleMultiTimeframeTimeframes(layout);
  const directRealtimeTimeframes = realtimeTimeframes.filter((timeframe) =>
    supportsRealtimeTimeframe(layout.symbol, timeframe),
  );
  const realtimeKey = directRealtimeTimeframes.join(",");
  const hasPollingTimeframes = directRealtimeTimeframes.length !== realtimeTimeframes.length;
  const [realtimeCandles, setRealtimeCandles] = useState<Record<string, Candle[]>>({});
  const [realtimeStatuses, setRealtimeStatuses] = useState<Record<string, RealtimeStatus>>({});
  const [resumeVersion, setResumeVersion] = useState(0);
  const [pollVersion, setPollVersion] = useState(0);

  useEffect(() => {
    let lastResumeAt = 0;

    function resynchronizeAfterPause() {
      const now = Date.now();
      if (!shouldResumeMarketData(document.visibilityState, lastResumeAt, now)) return;
      lastResumeAt = now;
      setResumeVersion((version) => version + 1);
    }

    document.addEventListener("visibilitychange", resynchronizeAfterPause);
    window.addEventListener("focus", resynchronizeAfterPause);
    window.addEventListener("online", resynchronizeAfterPause);
    return () => {
      document.removeEventListener("visibilitychange", resynchronizeAfterPause);
      window.removeEventListener("focus", resynchronizeAfterPause);
      window.removeEventListener("online", resynchronizeAfterPause);
    };
  }, []);

  useEffect(() => {
    if (!hasPollingTimeframes) return;
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        setPollVersion((version) => version + 1);
      }
    }, 10_000);
    return () => window.clearInterval(timer);
  }, [hasPollingTimeframes]);

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
              [`${layout.symbol}:${timeframe}`]: mergeRealtimeCandle(
                current[`${layout.symbol}:${timeframe}`] ?? [],
                candle,
              ),
            }));
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
  }, [layout.symbol, realtimeKey, resumeVersion]);

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
          timeframeOptions={timeframeOptions}
          refreshVersion={refreshVersion}
          resumeVersion={resumeVersion + pollVersion}
          realtimeCandles={realtimeCandles[`${layout.symbol}:${reviewWindow.timeframe}`]}
          realtimeStatus={
            supportsRealtimeTimeframe(layout.symbol, reviewWindow.timeframe)
              ? realtimeStatuses[`${layout.symbol}:${reviewWindow.timeframe}`] ?? "connecting"
              : "polling"
          }
          chartHeight={layout.windowCount === 1 ? 460 : 260}
          active={reviewWindow.id === activeWindowId}
          onActivate={() => onActiveWindowChange(reviewWindow.id)}
          onTimeframeChange={onTimeframeChange}
          onReviewChange={onReviewChange}
        />
      ))}
    </section>
  );
}
