import assert from "node:assert/strict";
import test from "node:test";

import {
  candleCloseTimestampSeconds,
  candleOpenTimestampSeconds,
  formatCandleTimeRange,
  formatChartTime,
} from "../lib/chart-time.ts";

test("keeps the provider open timestamp as the chart coordinate", () => {
  const open = "2026-06-30T07:55:00Z";

  assert.equal(candleOpenTimestampSeconds(open), Date.parse(open) / 1000);
  assert.equal(
    formatChartTime(candleOpenTimestampSeconds(open), "Asia/Bangkok", "axis"),
    "14:55",
  );
});

test("formats explicit candle ranges for every chart timeframe", () => {
  const open = Date.parse("2026-06-30T08:00:00Z") / 1000;

  assert.equal(formatCandleTimeRange(open, "1m", "Asia/Bangkok"), "1m 15:00 - 15:01");
  assert.equal(formatCandleTimeRange(open, "5m", "Asia/Bangkok"), "5m 15:00 - 15:05");
  assert.equal(formatCandleTimeRange(open, "15m", "Asia/Bangkok"), "15m 15:00 - 15:15");
  assert.equal(formatCandleTimeRange(open, "1h", "Asia/Bangkok"), "1h 15:00 - 16:00");
});

test("calculates close timestamps for every preset timeframe", () => {
  const open = "2026-06-30T03:20:00Z";

  assert.equal(candleCloseTimestampSeconds(open, "1m"), Date.parse("2026-06-30T03:21:00Z") / 1000);
  assert.equal(candleCloseTimestampSeconds(open, "5m"), Date.parse("2026-06-30T03:25:00Z") / 1000);
  assert.equal(candleCloseTimestampSeconds(open, "2h"), Date.parse("2026-06-30T05:20:00Z") / 1000);
  assert.equal(candleCloseTimestampSeconds(open, "1d"), Date.parse("2026-07-01T03:20:00Z") / 1000);
});

test("formats the same close instant in UTC and Bangkok", () => {
  const close = Date.parse("2026-06-30T03:21:00Z") / 1000;

  assert.equal(formatChartTime(close, "UTC", "axis"), "03:21");
  assert.equal(formatChartTime(close, "Asia/Bangkok", "axis"), "10:21");
});

test("calculates custom and calendar-month close timestamps", () => {
  assert.equal(
    candleCloseTimestampSeconds("2026-06-30T03:20:00Z", "7m"),
    Date.parse("2026-06-30T03:27:00Z") / 1000,
  );
  assert.equal(
    candleCloseTimestampSeconds("2026-06-01T00:00:00Z", "1M"),
    Date.parse("2026-07-01T00:00:00Z") / 1000,
  );
  assert.throws(() => candleCloseTimestampSeconds("2026-06-30T03:20:00Z", "1x"));
});

test("rejects invalid candle open timestamps", () => {
  assert.throws(() => candleOpenTimestampSeconds("invalid"), /Cannot resolve candle open time/);
});
