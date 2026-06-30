import type { Candle } from "@trading-framework/shared";

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

const TIMEFRAME_SECONDS: Record<string, number> = {
  "1m": 60,
  "5m": 300,
  "15m": 900,
  "30m": 1800,
  "1h": 3600,
  "2h": 7200,
  "4h": 14400,
  "1d": 86400,
};

export type CandleRequest = {
  symbol: string;
  timeframe: string;
  start: Date;
  end: Date;
};

export function normalizeCandles(payload: unknown): Candle[] {
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
      ![normalized.open, normalized.high, normalized.low, normalized.close, normalized.volume].every(
        Number.isFinite,
      )
    ) {
      throw new Error("Market data response contains an invalid candle.");
    }
    return normalized;
  });
}

export function recentCandleRequest(
  symbol: string,
  timeframe: string,
  nowMilliseconds = Date.now(),
  candleCount = 120,
): CandleRequest {
  const interval = TIMEFRAME_SECONDS[timeframe];
  if (!interval) {
    throw new Error(`Unsupported candle timeframe: ${timeframe}`);
  }
  const endSeconds = Math.floor(nowMilliseconds / 1000 / interval) * interval;
  return {
    symbol,
    timeframe,
    start: new Date((endSeconds - interval * candleCount) * 1000),
    end: new Date(endSeconds * 1000),
  };
}

async function marketDataError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Use the status fallback.
  }
  return `Market data request failed (${response.status}).`;
}

export async function fetchMarketCandles(
  marketDataBaseUrl: string,
  request: CandleRequest,
  signal?: AbortSignal,
): Promise<Candle[]> {
  const params = new URLSearchParams({
    symbol: request.symbol,
    timeframe: request.timeframe,
    start: request.start.toISOString(),
    end: request.end.toISOString(),
  });
  const response = await fetch(`${marketDataBaseUrl}/market/candles?${params}`, { signal });
  if (!response.ok) {
    throw new Error(await marketDataError(response));
  }
  return normalizeCandles(await response.json());
}
