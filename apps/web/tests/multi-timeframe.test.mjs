import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_MULTI_TIMEFRAME_WINDOWS,
  MULTI_TIMEFRAME_WINDOW_COUNTS,
  createDefaultMultiTimeframeLayout,
  resizeMultiTimeframeLayout,
  updateMultiTimeframeSymbol,
  updateMultiTimeframeWindow,
  visibleMultiTimeframeWindows,
} from "../lib/multi-timeframe.ts";

test("defines supported multi-timeframe window count presets", () => {
  assert.deepEqual(MULTI_TIMEFRAME_WINDOW_COUNTS, [1, 2, 4, 8]);
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
