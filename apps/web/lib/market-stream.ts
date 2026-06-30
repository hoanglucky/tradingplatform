import type { Candle } from "@trading-framework/shared";

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === "object" && value !== null;
}

export function getReconnectDelay(attempt: number, baseDelayMs: number, maxDelayMs: number): number {
  const normalizedAttempt = Math.max(0, Math.floor(attempt));
  return Math.min(baseDelayMs * 2 ** normalizedAttempt, maxDelayMs);
}

export function shouldResumeMarketData(
  visibilityState: DocumentVisibilityState,
  lastResumeAt: number,
  now: number,
  minimumIntervalMs = 1000,
): boolean {
  return visibilityState === "visible" && now - lastResumeAt >= minimumIntervalMs;
}

export function createHeartbeatPong(payload: unknown): { type: "pong"; id: number } | null {
  if (
    !isRecord(payload) ||
    payload.type !== "heartbeat" ||
    typeof payload.id !== "number" ||
    !Number.isInteger(payload.id) ||
    payload.id < 1
  ) {
    return null;
  }
  return { type: "pong", id: payload.id };
}

export function normalizeRealtimeCandle(
  payload: unknown,
  expectedSymbol: string,
  expectedTimeframe: string,
): Candle | null {
  if (!isRecord(payload) || payload.type !== "candle") {
    return null;
  }

  const candle = {
    symbol: payload.symbol,
    timeframe: payload.timeframe,
    timestamp: payload.timestamp,
    open: payload.open,
    high: payload.high,
    low: payload.low,
    close: payload.close,
    volume: payload.volume,
  };
  if (
    candle.symbol !== expectedSymbol ||
    candle.timeframe !== expectedTimeframe ||
    typeof candle.timestamp !== "string" ||
    !Number.isFinite(Date.parse(candle.timestamp)) ||
    ![candle.open, candle.high, candle.low, candle.close, candle.volume].every(
      (value) => typeof value === "number" && Number.isFinite(value),
    )
  ) {
    throw new Error("Market stream returned an invalid candle.");
  }

  const normalized = candle as Candle;
  if (
    normalized.open <= 0 ||
    normalized.high <= 0 ||
    normalized.low <= 0 ||
    normalized.close <= 0 ||
    normalized.volume < 0 ||
    normalized.low > Math.min(normalized.open, normalized.close) ||
    normalized.high < Math.max(normalized.open, normalized.close)
  ) {
    throw new Error("Market stream returned inconsistent OHLCV values.");
  }
  return normalized;
}

export function mergeRealtimeCandle(candles: Candle[], nextCandle: Candle, limit = 500): Candle[] {
  const nextTimestamp = Date.parse(nextCandle.timestamp);
  const existingIndex = candles.findIndex((candle) => Date.parse(candle.timestamp) === nextTimestamp);

  if (existingIndex >= 0) {
    const updated = candles.slice();
    updated[existingIndex] = reconcileContiguousOpen(candles[existingIndex - 1], nextCandle);
    return updated;
  }

  const latestTimestamp = candles.length > 0 ? Date.parse(candles[candles.length - 1].timestamp) : -Infinity;
  if (nextTimestamp <= latestTimestamp) {
    return candles;
  }
  return [...candles, reconcileContiguousOpen(candles[candles.length - 1], nextCandle)].slice(-limit);
}

function timeframeDurationMilliseconds(timeframe: string, timestamp: number): number | null {
  if (timeframe === "1M") {
    const open = new Date(timestamp);
    return (
      Date.UTC(open.getUTCFullYear(), open.getUTCMonth() + 1, 1) -
      Date.UTC(open.getUTCFullYear(), open.getUTCMonth(), 1)
    );
  }
  const match = /^([1-9][0-9]*)([mhdw])$/i.exec(timeframe);
  if (!match) return null;
  const multiplier = { m: 60_000, h: 3_600_000, d: 86_400_000, w: 604_800_000 }[
    match[2].toLowerCase() as "m" | "h" | "d" | "w"
  ];
  return Number(match[1]) * multiplier;
}

export function reconcileContiguousOpen(previous: Candle | undefined, next: Candle): Candle {
  if (!previous || previous.symbol !== next.symbol || previous.timeframe !== next.timeframe) return next;
  const previousTimestamp = Date.parse(previous.timestamp);
  const nextTimestamp = Date.parse(next.timestamp);
  const duration = timeframeDurationMilliseconds(next.timeframe, previousTimestamp);
  if (!duration || nextTimestamp !== previousTimestamp + duration || next.open === previous.close) return next;
  return {
    ...next,
    open: previous.close,
    high: Math.max(next.high, previous.close),
    low: Math.min(next.low, previous.close),
  };
}
