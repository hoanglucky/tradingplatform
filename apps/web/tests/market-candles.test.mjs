import assert from "node:assert/strict";
import test from "node:test";

import { fetchMarketCandles, recentCandleRequest } from "../lib/market-candles.ts";

test("builds an aligned recent candle range for extended timeframes", () => {
  const now = Date.UTC(2026, 5, 30, 10, 45);
  const request = recentCandleRequest("XAUUSD", "2h", now, 120);

  assert.equal(request.end.toISOString(), "2026-06-30T10:00:00.000Z");
  assert.equal(request.end.getTime() - request.start.getTime(), 120 * 2 * 60 * 60 * 1000);
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
