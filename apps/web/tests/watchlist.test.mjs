import assert from "node:assert/strict";
import test from "node:test";

import { availableWatchlistSymbols, watchlistChartHref } from "../lib/watchlist.ts";

const symbols = [
  { id: "1", symbol: "BTCUSDT", exchange: "binance", is_active: true },
  { id: "2", symbol: "ETHUSDT", exchange: "binance", is_active: true },
  { id: "3", symbol: "OLDUSDT", exchange: "binance", is_active: false },
];

test("filters pinned and inactive symbols from watchlist choices", () => {
  const available = availableWatchlistSymbols(symbols, [{ symbol: "BTCUSDT" }]);

  assert.deepEqual(
    available.map((symbol) => symbol.symbol),
    ["ETHUSDT"],
  );
});

test("builds an encoded chart link for a watchlist symbol", () => {
  assert.equal(watchlistChartHref("BTC/USDT"), "/dashboard/chart?symbol=BTC%2FUSDT");
});
