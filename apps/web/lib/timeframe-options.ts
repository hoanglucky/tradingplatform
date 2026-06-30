export const TIMEFRAME_GROUPS = [
  { label: "Minutes", values: ["1m", "3m", "5m", "15m", "30m", "45m"] },
  { label: "Hours", values: ["1h", "2h", "3h", "4h"] },
  { label: "Long range", values: ["1d", "2w", "1M"] },
] as const;

export const DEFAULT_TIMEFRAME_FAVORITES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"];

export function normalizeChartTimeframe(value: string): string | null {
  const candidate = value.trim();
  if (candidate === "1M") return candidate;
  const match = /^([1-9][0-9]*)([mhdw])$/i.exec(candidate);
  if (!match) return null;
  const amount = Number(match[1]);
  const unit = match[2].toLowerCase();
  const durationDays = amount * ({ m: 1 / 1440, h: 1 / 24, d: 1, w: 7 }[unit] ?? Infinity);
  return durationDays <= 31 ? `${amount}${unit}` : null;
}

export function chartTimeframeDurationMilliseconds(timeframe: string): number {
  if (timeframe === "1M") return 31 * 86_400_000;
  const match = /^([1-9][0-9]*)([mhdw])$/.exec(timeframe);
  if (!match) return Number.POSITIVE_INFINITY;
  const multiplier = { m: 60_000, h: 3_600_000, d: 86_400_000, w: 604_800_000 }[
    match[2] as "m" | "h" | "d" | "w"
  ];
  return Number(match[1]) * multiplier;
}

export function sortChartTimeframes(timeframes: readonly string[]): string[] {
  return [...new Set(timeframes)].sort((left, right) => {
    const durationDifference =
      chartTimeframeDurationMilliseconds(left) - chartTimeframeDurationMilliseconds(right);
    return durationDifference || left.localeCompare(right);
  });
}

export function parseStoredTimeframeFavorites(value: string | null): string[] {
  if (!value) return DEFAULT_TIMEFRAME_FAVORITES;
  try {
    const parsed = JSON.parse(value);
    if (!Array.isArray(parsed)) return DEFAULT_TIMEFRAME_FAVORITES;
    const normalized = parsed
      .map((item) => (typeof item === "string" ? normalizeChartTimeframe(item) : null))
      .filter((item): item is string => item !== null);
    return sortChartTimeframes(normalized);
  } catch {
    return DEFAULT_TIMEFRAME_FAVORITES;
  }
}

const OANDA_SYMBOLS = new Set(["XAUUSD", "SP500", "US100"]);
const OANDA_REALTIME_TIMEFRAMES = new Set(["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"]);
const BINANCE_REALTIME_TIMEFRAMES = new Set(["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1M"]);

export function supportsRealtimeTimeframe(symbol: string, timeframe: string): boolean {
  return (OANDA_SYMBOLS.has(symbol) ? OANDA_REALTIME_TIMEFRAMES : BINANCE_REALTIME_TIMEFRAMES).has(
    timeframe,
  );
}

export function realtimeSourceTimeframe(symbol: string, timeframe: string): string {
  if (OANDA_SYMBOLS.has(symbol)) return "1m";
  return supportsRealtimeTimeframe(symbol, timeframe) ? timeframe : "1m";
}
