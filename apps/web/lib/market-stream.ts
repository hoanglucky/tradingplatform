import type { Candle } from "@trading-framework/shared";

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === "object" && value !== null;
}

export function getReconnectDelay(attempt: number, baseDelayMs: number, maxDelayMs: number): number {
  const normalizedAttempt = Math.max(0, Math.floor(attempt));
  return Math.min(baseDelayMs * 2 ** normalizedAttempt, maxDelayMs);
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
    updated[existingIndex] = nextCandle;
    return updated;
  }

  const latestTimestamp = candles.length > 0 ? Date.parse(candles[candles.length - 1].timestamp) : -Infinity;
  if (nextTimestamp <= latestTimestamp) {
    return candles;
  }
  return [...candles, nextCandle].slice(-limit);
}

export function synchronizeLatestCandlePrice(candles: Candle[], price: number): Candle[] {
  if (candles.length === 0 || !Number.isFinite(price) || price <= 0) {
    return candles;
  }
  const latest = candles[candles.length - 1];
  const synchronized = {
    ...latest,
    high: Math.max(latest.high, price),
    low: Math.min(latest.low, price),
    close: price,
  };
  return [...candles.slice(0, -1), synchronized];
}
