import assert from "node:assert/strict";
import test from "node:test";

import { resetCandlestickChartView } from "../lib/chart-view.ts";

test("resets time and price scales for a candlestick chart", () => {
  let fitContentCalls = 0;
  const priceScaleCalls = [];
  const chart = {
    timeScale: () => ({
      fitContent: () => {
        fitContentCalls += 1;
      },
    }),
    priceScale: (priceScaleId) => ({
      applyOptions: (options) => priceScaleCalls.push({ priceScaleId, options }),
    }),
  };

  assert.equal(resetCandlestickChartView(chart), true);
  assert.equal(fitContentCalls, 1);
  assert.deepEqual(priceScaleCalls, [
    { priceScaleId: "right", options: { autoScale: true } },
  ]);
});

test("ignores reset before a chart instance exists", () => {
  assert.equal(resetCandlestickChartView(null), false);
});
