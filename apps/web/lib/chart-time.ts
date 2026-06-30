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

type ChartTime = number | string | { year: number; month: number; day: number };
type ChartTimeFormat = "axis" | "crosshair";

export function candleCloseTimestampSeconds(timestamp: string, timeframe: string): number {
  const duration = TIMEFRAME_SECONDS[timeframe];
  const openMilliseconds = Date.parse(timestamp);
  if (!duration || !Number.isFinite(openMilliseconds)) {
    throw new Error(`Cannot resolve candle close time for ${timeframe}.`);
  }
  return Math.floor(openMilliseconds / 1000) + duration;
}

export function candleOpenTimestampSeconds(timestamp: string): number {
  const openMilliseconds = Date.parse(timestamp);
  if (!Number.isFinite(openMilliseconds)) {
    throw new Error("Cannot resolve candle open time.");
  }
  return Math.floor(openMilliseconds / 1000);
}

function chartTimeMilliseconds(time: ChartTime): number {
  if (typeof time === "number") return time * 1000;
  if (typeof time === "string") return Date.parse(time);
  return Date.UTC(time.year, time.month - 1, time.day);
}

export function formatChartTime(
  time: ChartTime,
  timezone: string,
  format: ChartTimeFormat,
  locale = "en-GB",
): string {
  const milliseconds = chartTimeMilliseconds(time);
  if (!Number.isFinite(milliseconds)) return "";
  const options: Intl.DateTimeFormatOptions =
    format === "crosshair"
      ? {
          timeZone: timezone,
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hourCycle: "h23",
        }
      : {
          timeZone: timezone,
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hourCycle: "h23",
        };
  return new Intl.DateTimeFormat(locale, options).format(new Date(milliseconds));
}
