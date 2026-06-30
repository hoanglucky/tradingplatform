import assert from "node:assert/strict";
import test from "node:test";

import {
  fetchMarketCandleResult,
  fetchMarketCandles,
  recentCandleRequest,
  timeframeSeconds,
} from "../lib/market-candles.ts";

test("builds an aligned recent candle range for extended timeframes", () => {
  const now = Date.UTC(2026, 5, 30, 10, 45);
  const request = recentCandleRequest("XAUUSD", "2h", now, 120);

  assert.equal(request.end.toISOString(), "2026-06-30T10:00:00.000Z");
  assert.equal(request.end.getTime() - request.start.getTime(), 120 * 2 * 60 * 60 * 1000);
});

test("calculates custom week and month timeframe durations", () => {
  assert.equal(timeframeSeconds("45m"), 2700);
  assert.equal(timeframeSeconds("3h"), 10800);
  assert.equal(timeframeSeconds("2w"), 1209600);
  assert.equal(timeframeSeconds("1M"), 2678400);
});

test("aligns week ranges to Monday and month ranges to calendar boundaries", () => {
  const now = Date.parse("2026-06-30T12:34:00Z");
  const weekly = recentCandleRequest("XAUUSD", "2w", now, 2);
  const monthly = recentCandleRequest("XAUUSD", "1M", now, 2);

  assert.equal(weekly.end.getUTCDay(), 1);
  assert.equal(monthly.start.toISOString(), "2026-04-01T00:00:00.000Z");
  assert.equal(monthly.end.toISOString(), "2026-06-30T12:34:00.000Z");
});

test("fetches and normalizes candles through the shared client", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async (url) => {
    const parsed = new URL(String(url));
    assert.equal(parsed.pathname, "/market/candles");
    assert.equal(parsed.searchParams.get("symbol"), "SP500");
    assert.equal(parsed.searchParams.get("timeframe"), "30m");
    return new Response(
      JSON.stringify([
        {
          symbol: "SP500",
          timeframe: "30m",
          timestamp: "2026-06-30T10:00:00Z",
          open: "6100.5",
          high: "6110.0",
          low: "6098.0",
          close: "6108.5",
          volume: "42",
        },
      ]),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  };

  const request = recentCandleRequest("SP500", "30m", Date.UTC(2026, 5, 30, 10, 45));
  const candles = await fetchMarketCandles("http://market.test", request);

  assert.equal(candles.length, 1);
  assert.equal(candles[0].close, 6108.5);
  assert.equal(candles[0].volume, 42);
});

test("returns candle source and aggregation metadata", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        candles: [
          {
            symbol: "XAUUSD",
            timeframe: "45m",
            timestamp: "2026-06-30T10:00:00Z",
            open: "3300",
            high: "3310",
            low: "3290",
            close: "3305",
            volume: "10",
          },
        ],
        metadata: {
          source_provider: "oanda",
          source_market_type: "cfd_fx",
          aggregation_used: true,
          base_timeframe: "15m",
          cache_hit: true,
          missing_ranges_fetched: 0,
        },
      }),
      { headers: { "Content-Type": "application/json" } },
    );

  const result = await fetchMarketCandleResult(
    "http://market.test",
    recentCandleRequest("XAUUSD", "45m", Date.UTC(2026, 5, 30, 10, 45)),
  );

  assert.equal(result.candles.length, 1);
  assert.equal(result.metadata?.aggregation_used, true);
  assert.equal(result.metadata?.base_timeframe, "15m");
  assert.equal(result.metadata?.cache_hit, true);
});

test("surfaces a provider error without returning partial data", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Provider unavailable." }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });

  await assert.rejects(
    fetchMarketCandles(
      "http://market.test",
      recentCandleRequest("US100", "1h", Date.UTC(2026, 5, 30, 10, 45)),
    ),
    /Provider unavailable/,
  );
});
