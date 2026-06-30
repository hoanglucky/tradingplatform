import assert from "node:assert/strict";
import test from "node:test";

import {
  candleCloseTimestampSeconds,
  candleOpenTimestampSeconds,
  formatChartTime,
} from "../lib/chart-time.ts";

test("keeps the provider open timestamp as the chart coordinate", () => {
  const open = "2026-06-30T07:55:00Z";

  assert.equal(candleOpenTimestampSeconds(open), Date.parse(open) / 1000);
  assert.equal(
    formatChartTime(candleOpenTimestampSeconds(open), "Asia/Bangkok", "axis"),
    "30/06, 14:55",
  );
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

  assert.equal(formatChartTime(close, "UTC", "axis"), "30/06, 03:21");
  assert.equal(formatChartTime(close, "Asia/Bangkok", "axis"), "30/06, 10:21");
});

test("rejects unsupported timeframe close calculations", () => {
  assert.throws(
    () => candleCloseTimestampSeconds("2026-06-30T03:20:00Z", "7m"),
    /Cannot resolve candle close time/,
  );
});

test("rejects invalid candle open timestamps", () => {
  assert.throws(() => candleOpenTimestampSeconds("invalid"), /Cannot resolve candle open time/);
});
