import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_TIMEFRAME_FAVORITES,
  normalizeChartTimeframe,
  parseStoredTimeframeFavorites,
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

test("uses polling only when a provider has no direct realtime timeframe", () => {
  assert.equal(supportsRealtimeTimeframe("XAUUSD", "3m"), false);
  assert.equal(supportsRealtimeTimeframe("XAUUSD", "5m"), true);
  assert.equal(supportsRealtimeTimeframe("BTCUSDT", "3m"), true);
  assert.equal(supportsRealtimeTimeframe("BTCUSDT", "45m"), false);
});
