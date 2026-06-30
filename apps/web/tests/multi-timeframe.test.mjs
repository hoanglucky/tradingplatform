import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_MULTI_TIMEFRAME_WINDOWS,
  DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES,
  MULTI_TIMEFRAME_TIMEFRAMES,
  MULTI_TIMEFRAME_WINDOW_COUNTS,
  clearMultiTimeframeReview,
  createDefaultMultiTimeframeLayout,
  createMultiTimeframeLayout,
  getMultiTimeframeReviewProgress,
  resizeMultiTimeframeLayout,
  resolveMultiTimeframeLayout,
  serializeMultiTimeframeLayout,
  updateMultiTimeframeSymbol,
  updateMultiTimeframeWindow,
  uniqueVisibleMultiTimeframeTimeframes,
  visibleMultiTimeframeWindows,
} from "../lib/multi-timeframe.ts";

test("defines supported multi-timeframe window count presets", () => {
  assert.deepEqual(MULTI_TIMEFRAME_WINDOW_COUNTS, [1, 2, 4, 8]);
});

test("defines extended review timeframe options", () => {
  assert.deepEqual(MULTI_TIMEFRAME_TIMEFRAMES, [
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "45m",
    "1h",
    "2h",
    "3h",
    "4h",
    "1d",
    "2w",
    "1M",
  ]);
});

test("creates the default four-window review layout", () => {
  const layout = createDefaultMultiTimeframeLayout("xauusd");

  assert.equal(layout.symbol, "XAUUSD");
  assert.equal(layout.windowCount, 4);
  assert.deepEqual(
    layout.windows.map((window) => window.timeframe),
    ["4h", "1h", "15m", "5m"],
  );
  assert.ok(layout.windows.every((window) => window.enabled));
  assert.ok(layout.windows.every((window) => !window.reviewChecked));
});

test("creates independent window state for each workspace", () => {
  const first = createDefaultMultiTimeframeLayout("BTCUSDT");
  const second = createDefaultMultiTimeframeLayout("BTCUSDT");

  first.windows[0].reviewChecked = true;

  assert.equal(second.windows[0].reviewChecked, false);
  assert.equal(DEFAULT_MULTI_TIMEFRAME_WINDOWS[0].reviewChecked, false);
});

test("creates the final default timeframe preset for every layout", () => {
  for (const windowCount of MULTI_TIMEFRAME_WINDOW_COUNTS) {
    const layout = createMultiTimeframeLayout("BTCUSDT", windowCount);
    assert.deepEqual(
      layout.windows.map((window) => window.timeframe),
      DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES[windowCount],
    );
  }

  const eightWindowLayout = createMultiTimeframeLayout("BTCUSDT", 8);
  assert.equal(new Set(eightWindowLayout.windows.map((window) => window.timeframe)).size, 8);
});

test("updates the shared symbol without replacing window state", () => {
  const layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout.windows[1].reviewChecked = true;

  const updated = updateMultiTimeframeSymbol(layout, " sp500 ");

  assert.equal(updated.symbol, "SP500");
  assert.equal(updated.windowCount, 4);
  assert.equal(updated.windows[1].reviewChecked, true);
  assert.equal(updated.windows, layout.windows);
});

test("decreasing layout hides extra windows without discarding state", () => {
  const layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout.windows[2].reviewChecked = true;

  const resized = resizeMultiTimeframeLayout(layout, 2);

  assert.equal(resized.windowCount, 2);
  assert.equal(resized.windows.filter((window) => window.enabled).length, 2);
  assert.equal(resized.windows[2].reviewChecked, true);
  assert.equal(resized.windows[2].enabled, false);
});

test("increasing layout restores hidden windows and adds stable defaults", () => {
  const layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout.windows[3].reviewChecked = true;
  const compact = resizeMultiTimeframeLayout(layout, 1);
  const expanded = resizeMultiTimeframeLayout(compact, 8);

  assert.equal(expanded.windowCount, 8);
  assert.equal(expanded.windows.length, 8);
  assert.equal(expanded.windows.filter((window) => window.enabled).length, 8);
  assert.equal(expanded.windows[3].reviewChecked, true);
  assert.equal(new Set(expanded.windows.map((window) => window.id)).size, 8);
});

test("updates one review window without changing its siblings", () => {
  const layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  const updated = updateMultiTimeframeWindow(layout, "w2", {
    timeframe: "1d",
    reviewChecked: true,
  });

  assert.equal(updated.windows[1].timeframe, "1d");
  assert.equal(updated.windows[1].reviewChecked, true);
  assert.equal(updated.windows[0], layout.windows[0]);
  assert.equal(updated.windows[2], layout.windows[2]);
});

test("returns only enabled windows within the selected count", () => {
  const layout = resizeMultiTimeframeLayout(createDefaultMultiTimeframeLayout("BTCUSDT"), 2);

  assert.deepEqual(
    visibleMultiTimeframeWindows(layout).map((window) => window.id),
    ["w1", "w2"],
  );
});

test("returns one realtime subscription per unique visible timeframe", () => {
  let layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout = updateMultiTimeframeWindow(layout, "w2", { timeframe: "4h" });
  layout = resizeMultiTimeframeLayout(layout, 2);

  assert.deepEqual(uniqueVisibleMultiTimeframeTimeframes(layout), ["4h"]);
});

test("calculates review progress from visible enabled windows", () => {
  let layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout = updateMultiTimeframeWindow(layout, "w1", { reviewChecked: true });
  layout = updateMultiTimeframeWindow(layout, "w3", { reviewChecked: true });
  layout = resizeMultiTimeframeLayout(layout, 2);

  assert.deepEqual(getMultiTimeframeReviewProgress(layout), { reviewed: 1, total: 2 });
  assert.equal(layout.windows[2].reviewChecked, true);
});

test("clear review unchecks visible and hidden windows", () => {
  let layout = createDefaultMultiTimeframeLayout("BTCUSDT");
  layout = updateMultiTimeframeWindow(layout, "w1", { reviewChecked: true });
  layout = updateMultiTimeframeWindow(layout, "w4", { reviewChecked: true });
  layout = resizeMultiTimeframeLayout(layout, 1);

  const cleared = clearMultiTimeframeReview(layout);

  assert.ok(cleared.windows.every((window) => !window.reviewChecked));
  assert.deepEqual(getMultiTimeframeReviewProgress(cleared), { reviewed: 0, total: 1 });
});

test("loads a valid persisted layout for the active shared symbol", () => {
  let saved = createDefaultMultiTimeframeLayout("BTCUSDT");
  saved = updateMultiTimeframeWindow(saved, "w2", { reviewChecked: true });
  saved = resizeMultiTimeframeLayout(saved, 2);

  const resolved = resolveMultiTimeframeLayout(saved, "XAUUSD", ["BTCUSDT", "XAUUSD"]);

  assert.equal(resolved.symbol, "XAUUSD");
  assert.equal(resolved.windowCount, 2);
  assert.equal(resolved.windows[1].reviewChecked, true);
  assert.notEqual(resolved.windows, saved.windows);
});

test("falls back safely when a persisted layout is invalid", () => {
  const invalid = {
    symbol: "BTCUSDT",
    windowCount: 2,
    windows: [
      { id: "duplicate", timeframe: "1h", enabled: true, reviewChecked: true },
      { id: "duplicate", timeframe: "15m", enabled: true, reviewChecked: false },
    ],
  };

  const resolved = resolveMultiTimeframeLayout(invalid, "XAUUSD", ["BTCUSDT", "XAUUSD"]);

  assert.equal(resolved.symbol, "XAUUSD");
  assert.equal(resolved.windowCount, 4);
  assert.deepEqual(
    resolved.windows.map((window) => window.timeframe),
    ["4h", "1h", "15m", "5m"],
  );
});

test("serializes layout persistence deterministically", () => {
  const layout = createMultiTimeframeLayout("SP500", 8);

  assert.equal(serializeMultiTimeframeLayout(layout), JSON.stringify(layout));
});
