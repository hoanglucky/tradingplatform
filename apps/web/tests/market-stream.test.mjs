import assert from "node:assert/strict";
import test from "node:test";

import {
  createHeartbeatPong,
  getReconnectDelay,
  mergeRealtimeCandle,
  normalizeRealtimeCandle,
  reconcileContiguousOpen,
  shouldResumeMarketData,
} from "../lib/market-stream.ts";

const historicalCandle = {
  symbol: "BTCUSDT",
  timeframe: "1m",
  timestamp: "2026-06-29T08:00:00+00:00",
  open: 100,
  high: 102,
  low: 99,
  close: 101,
  volume: 10,
};

test("normalizes a matching realtime candle", () => {
  const normalized = normalizeRealtimeCandle(
    {
      type: "candle",
      symbol: "BTCUSDT",
      timeframe: "1m",
      timestamp: "2026-06-29T08:00:00Z",
      open: 100,
      high: 103,
      low: 99,
      close: 102,
      volume: 12,
    },
    "BTCUSDT",
    "1m",
  );

  assert.equal(normalized?.close, 102);
});

test("updates an existing candle by epoch without creating a duplicate", () => {
  const realtimeCandle = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:00:00Z",
    close: 102,
  };
  const merged = mergeRealtimeCandle([historicalCandle], realtimeCandle);

  assert.equal(merged.length, 1);
  assert.equal(merged[0].close, 102);
  assert.equal(historicalCandle.close, 101);
});

test("appends a newer candle", () => {
  const newerCandle = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:01:00Z",
  };
  const candles = mergeRealtimeCandle([historicalCandle], newerCandle);

  assert.equal(candles.length, 2);
  assert.equal(candles[1].open, historicalCandle.close);
  assert.equal(candles[1].timestamp, newerCandle.timestamp);
});

test("retains consecutive realtime candles in a bounded stream buffer", () => {
  const second = {...historicalCandle, timestamp: "2026-06-29T08:01:00Z"};
  const third = {...historicalCandle, timestamp: "2026-06-29T08:02:00Z"};
  const buffered = [historicalCandle, second, third].reduce(
    (candles, candle) => mergeRealtimeCandle(candles, candle),
    [],
  );

  assert.deepEqual(buffered.map((candle) => candle.timestamp), [
    historicalCandle.timestamp,
    second.timestamp,
    third.timestamp,
  ]);
});

test("ignores an older unknown candle", () => {
  const newerCandle = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:01:00Z",
  };
  const candles = [historicalCandle, newerCandle];
  const olderCandle = {
    ...historicalCandle,
    timestamp: "2026-06-29T07:59:00Z",
  };

  assert.strictEqual(mergeRealtimeCandle(candles, olderCandle), candles);
});

test("replaces a duplicate timestamp without changing candle order", () => {
  const secondCandle = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:01:00Z",
  };
  const replacement = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:00:00Z",
    close: 101.5,
  };
  const merged = mergeRealtimeCandle([historicalCandle, secondCandle], replacement);

  assert.equal(merged.length, 2);
  assert.strictEqual(merged[0], replacement);
  assert.strictEqual(merged[1], secondCandle);
});

test("adds the first realtime candle to an empty chart", () => {
  const merged = mergeRealtimeCandle([], historicalCandle);

  assert.deepEqual(merged, [historicalCandle]);
});

test("uses the previous close as open for contiguous realtime candles", () => {
  const next = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:01:00Z",
    open: 102,
    high: 104,
    low: 102,
  };
  const reconciled = reconcileContiguousOpen(historicalCandle, next);

  assert.equal(reconciled.open, historicalCandle.close);
  assert.equal(reconciled.low, historicalCandle.close);
  assert.equal(reconciled.high, 104);
});

test("preserves provider open across a real market gap", () => {
  const next = {
    ...historicalCandle,
    timestamp: "2026-06-29T08:03:00Z",
    open: 104,
    high: 105,
    low: 103,
  };

  assert.strictEqual(reconcileContiguousOpen(historicalCandle, next), next);
});

test("reconciles contiguous opens across standard timeframes", () => {
  for (const [timeframe, previousTimestamp, nextTimestamp] of [
    ["1m", "2026-06-29T08:00:00Z", "2026-06-29T08:01:00Z"],
    ["5m", "2026-06-29T08:00:00Z", "2026-06-29T08:05:00Z"],
    ["1h", "2026-06-29T08:00:00Z", "2026-06-29T09:00:00Z"],
    ["1d", "2026-06-29T00:00:00Z", "2026-06-30T00:00:00Z"],
  ]) {
    const previous = {...historicalCandle, timeframe, timestamp: previousTimestamp, close: 101};
    const next = {...historicalCandle, timeframe, timestamp: nextTimestamp, open: 103, high: 104, low: 102};
    assert.equal(reconcileContiguousOpen(previous, next).open, 101);
  }
});

test("rejects inconsistent realtime OHLC values", () => {
  assert.throws(
    () =>
      normalizeRealtimeCandle(
        {
          type: "candle",
          symbol: "BTCUSDT",
          timeframe: "1m",
          timestamp: "2026-06-29T08:00:00Z",
          open: 100,
          high: 98,
          low: 99,
          close: 101,
          volume: 12,
        },
        "BTCUSDT",
        "1m",
      ),
    /inconsistent OHLCV/,
  );
});

test("calculates bounded exponential reconnect delays", () => {
  assert.equal(getReconnectDelay(0, 1000, 15000), 1000);
  assert.equal(getReconnectDelay(3, 1000, 15000), 8000);
  assert.equal(getReconnectDelay(8, 1000, 15000), 15000);
});

test("resynchronizes once when a paused chart becomes visible", () => {
  assert.equal(shouldResumeMarketData("hidden", 1_000, 5_000), false);
  assert.equal(shouldResumeMarketData("visible", 1_000, 1_999), false);
  assert.equal(shouldResumeMarketData("visible", 1_000, 2_000), true);
});

test("creates pong responses only for valid heartbeat messages", () => {
  assert.deepEqual(createHeartbeatPong({ type: "heartbeat", id: 7 }), { type: "pong", id: 7 });
  assert.equal(createHeartbeatPong({ type: "heartbeat", id: 0 }), null);
  assert.equal(createHeartbeatPong({ type: "candle", id: 7 }), null);
});
