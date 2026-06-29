import assert from "node:assert/strict";
import test from "node:test";

import {
  getUserSettings,
  patchUserSettings,
  resolveChartPreferences,
} from "../lib/user-settings.ts";

const settings = {
  id: "settings-id",
  user_id: "user-id",
  default_symbol: "XAUUSD",
  default_timeframe: "5m",
  selected_indicators: [],
  theme: "system",
  timezone: "UTC",
  created_at: "2026-06-29T00:00:00Z",
  updated_at: "2026-06-29T00:00:00Z",
};
const symbols = ["BTCUSDT", "XAUUSD", "SP500"];
const timeframes = ["1m", "5m", "15m"];

test("loads stored chart symbol and timeframe", () => {
  assert.deepEqual(resolveChartPreferences(settings, undefined, symbols, timeframes), {
    symbol: "XAUUSD",
    timeframe: "5m",
  });
});

test("URL symbol overrides stored symbol without replacing stored timeframe", () => {
  assert.deepEqual(resolveChartPreferences(settings, "sp500", symbols, timeframes), {
    symbol: "SP500",
    timeframe: "5m",
  });
});

test("falls back when stored preferences are unsupported", () => {
  assert.deepEqual(
    resolveChartPreferences(
      { ...settings, default_symbol: "UNKNOWN", default_timeframe: "2m" },
      undefined,
      symbols,
      timeframes,
    ),
    { symbol: "BTCUSDT", timeframe: "1m" },
  );
});

test("loads settings from the API", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async (url, init) => {
    assert.equal(url, "http://api.test/settings");
    assert.equal(init?.signal, undefined);
    return new Response(JSON.stringify(settings), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  assert.deepEqual(await getUserSettings("http://api.test"), settings);
});

test("patches chart preferences through the API", async (context) => {
  const originalFetch = globalThis.fetch;
  context.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async (url, init) => {
    assert.equal(url, "http://api.test/settings");
    assert.equal(init?.method, "PATCH");
    assert.equal(init?.headers?.["Content-Type"], "application/json");
    assert.deepEqual(JSON.parse(String(init?.body)), {
      default_symbol: "SP500",
      default_timeframe: "1h",
    });
    return new Response(
      JSON.stringify({ ...settings, default_symbol: "SP500", default_timeframe: "1h" }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  };

  const updated = await patchUserSettings("http://api.test", {
    default_symbol: "SP500",
    default_timeframe: "1h",
  });
  assert.equal(updated.default_symbol, "SP500");
  assert.equal(updated.default_timeframe, "1h");
});
