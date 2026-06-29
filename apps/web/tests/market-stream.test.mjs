import assert from "node:assert/strict";
import test from "node:test";

import {
  createHeartbeatPong,
  getReconnectDelay,
  mergeRealtimeCandle,
  normalizeRealtimeCandle,
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
  assert.strictEqual(candles[1], newerCandle);
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

test("creates pong responses only for valid heartbeat messages", () => {
  assert.deepEqual(createHeartbeatPong({ type: "heartbeat", id: 7 }), { type: "pong", id: 7 });
  assert.equal(createHeartbeatPong({ type: "heartbeat", id: 0 }), null);
  assert.equal(createHeartbeatPong({ type: "candle", id: 7 }), null);
});
