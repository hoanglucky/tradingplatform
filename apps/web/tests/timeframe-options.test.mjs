import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_TIMEFRAME_FAVORITES,
  normalizeChartTimeframe,
  parseStoredTimeframeFavorites,
  realtimeSourceTimeframe,
  sortChartTimeframes,
  supportsRealtimeTimeframe,
} from "../lib/timeframe-options.ts";

test("normalizes custom minute, hour, week, and month timeframes", () => {
  assert.equal(normalizeChartTimeframe(" 7M "), "7m");
  assert.equal(normalizeChartTimeframe("3H"), "3h");
  assert.equal(normalizeChartTimeframe("2w"), "2w");
  assert.equal(normalizeChartTimeframe("1M"), "1M");
  assert.equal(normalizeChartTimeframe("0m"), null);
  assert.equal(normalizeChartTimeframe("5w"), null);
});

test("loads unique valid timeframe favorites", () => {
  assert.deepEqual(parseStoredTimeframeFavorites('["3m","3m","45m","bad"]'), ["3m", "45m"]);
  assert.deepEqual(parseStoredTimeframeFavorites("bad json"), DEFAULT_TIMEFRAME_FAVORITES);
});

test("sorts preset and custom favorites by timeframe duration", () => {
  assert.deepEqual(sortChartTimeframes(["1h", "15m", "6m", "5m", "1M", "2w"]), [
    "5m",
    "6m",
    "15m",
    "1h",
    "2w",
    "1M",
  ]);
});

test("uses a one-minute live source when a provider has no direct realtime timeframe", () => {
  assert.equal(supportsRealtimeTimeframe("XAUUSD", "3m"), false);
  assert.equal(supportsRealtimeTimeframe("XAUUSD", "5m"), true);
  assert.equal(supportsRealtimeTimeframe("BTCUSDT", "3m"), true);
  assert.equal(supportsRealtimeTimeframe("BTCUSDT", "45m"), false);
  assert.equal(realtimeSourceTimeframe("XAUUSD", "3m"), "1m");
  assert.equal(realtimeSourceTimeframe("XAUUSD", "5m"), "1m");
  assert.equal(realtimeSourceTimeframe("XAUUSD", "1h"), "1m");
  assert.equal(realtimeSourceTimeframe("BTCUSDT", "45m"), "1m");
});
