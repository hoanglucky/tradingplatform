import type {
  MultiTimeframeLayout,
  MultiTimeframeTimeframe,
  MultiTimeframeWindow,
  MultiTimeframeWindowCount,
} from "@trading-framework/shared";

export type {
  MultiTimeframeLayout,
  MultiTimeframeTimeframe,
  MultiTimeframeWindow,
  MultiTimeframeWindowCount,
} from "@trading-framework/shared";

export const MULTI_TIMEFRAME_WINDOW_COUNTS = [1, 2, 4, 8] as const;
export const MULTI_TIMEFRAME_TIMEFRAMES = [
  "1m",
  "5m",
  "15m",
  "30m",
  "1h",
  "2h",
  "4h",
  "1d",
] as const;

export type MultiTimeframeReviewProgress = {
  reviewed: number;
  total: number;
};

export const DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES: Record<
  MultiTimeframeWindowCount,
  readonly MultiTimeframeTimeframe[]
> = {
  1: ["15m"],
  2: ["1h", "15m"],
  4: ["4h", "1h", "15m", "5m"],
  8: ["1d", "4h", "2h", "1h", "30m", "15m", "5m", "1m"],
};

export const DEFAULT_MULTI_TIMEFRAME_WINDOWS: readonly MultiTimeframeWindow[] =
  DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES[4].map((timeframe, index) => ({
    id: `w${index + 1}`,
    timeframe,
    enabled: true,
    reviewChecked: false,
  }));

function createWindow(index: number, windowCount: MultiTimeframeWindowCount): MultiTimeframeWindow {
  return {
    id: `w${index + 1}`,
    timeframe: DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES[windowCount][index],
    enabled: true,
    reviewChecked: false,
  };
}

export function createMultiTimeframeLayout(
  symbol: string,
  windowCount: MultiTimeframeWindowCount,
): MultiTimeframeLayout {
  return {
    symbol: symbol.trim().toUpperCase(),
    windowCount,
    windows: DEFAULT_MULTI_TIMEFRAME_LAYOUT_TIMEFRAMES[windowCount].map((_, index) =>
      createWindow(index, windowCount),
    ),
  };
}

export function createDefaultMultiTimeframeLayout(symbol: string): MultiTimeframeLayout {
  return createMultiTimeframeLayout(symbol, 4);
}

export function updateMultiTimeframeSymbol(
  layout: MultiTimeframeLayout,
  symbol: string,
): MultiTimeframeLayout {
  const normalizedSymbol = symbol.trim().toUpperCase();
  return normalizedSymbol === layout.symbol ? layout : { ...layout, symbol: normalizedSymbol };
}

export function resizeMultiTimeframeLayout(
  layout: MultiTimeframeLayout,
  windowCount: MultiTimeframeWindowCount,
): MultiTimeframeLayout {
  const windows = layout.windows.map((window, index) => ({
    ...window,
    enabled: index < windowCount,
  }));
  while (windows.length < windowCount) {
    windows.push(createWindow(windows.length, windowCount));
  }
  return { ...layout, windowCount, windows };
}

export function updateMultiTimeframeWindow(
  layout: MultiTimeframeLayout,
  windowId: string,
  changes: Partial<Pick<MultiTimeframeWindow, "timeframe" | "enabled" | "reviewChecked">>,
): MultiTimeframeLayout {
  let found = false;
  const windows = layout.windows.map((window) => {
    if (window.id !== windowId) {
      return window;
    }
    found = true;
    return { ...window, ...changes };
  });
  return found ? { ...layout, windows } : layout;
}

export function visibleMultiTimeframeWindows(layout: MultiTimeframeLayout): MultiTimeframeWindow[] {
  return layout.windows.filter((window) => window.enabled).slice(0, layout.windowCount);
}

export function uniqueVisibleMultiTimeframeTimeframes(
  layout: MultiTimeframeLayout,
): MultiTimeframeTimeframe[] {
  return [...new Set(visibleMultiTimeframeWindows(layout).map((window) => window.timeframe))];
}

export function getMultiTimeframeReviewProgress(
  layout: MultiTimeframeLayout,
): MultiTimeframeReviewProgress {
  const visibleWindows = visibleMultiTimeframeWindows(layout);
  return {
    reviewed: visibleWindows.filter((window) => window.reviewChecked).length,
    total: visibleWindows.length,
  };
}

export function clearMultiTimeframeReview(layout: MultiTimeframeLayout): MultiTimeframeLayout {
  if (!layout.windows.some((window) => window.reviewChecked)) {
    return layout;
  }
  return {
    ...layout,
    windows: layout.windows.map((window) =>
      window.reviewChecked ? { ...window, reviewChecked: false } : window,
    ),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function resolveMultiTimeframeLayout(
  value: unknown,
  activeSymbol: string,
  supportedSymbols: readonly string[],
): MultiTimeframeLayout {
  const fallback = createDefaultMultiTimeframeLayout(activeSymbol);
  if (!isRecord(value)) {
    return fallback;
  }
  const symbol = typeof value.symbol === "string" ? value.symbol.trim().toUpperCase() : "";
  const windowCount = value.windowCount;
  const windows = value.windows;
  if (
    !supportedSymbols.includes(symbol) ||
    !MULTI_TIMEFRAME_WINDOW_COUNTS.some((count) => count === windowCount) ||
    !Array.isArray(windows) ||
    windows.length < Number(windowCount) ||
    windows.length > 8
  ) {
    return fallback;
  }

  const normalizedWindows: MultiTimeframeWindow[] = [];
  const ids = new Set<string>();
  for (const window of windows) {
    if (!isRecord(window)) {
      return fallback;
    }
    const id = typeof window.id === "string" ? window.id.trim() : "";
    if (
      !id ||
      ids.has(id) ||
      !MULTI_TIMEFRAME_TIMEFRAMES.some((timeframe) => timeframe === window.timeframe) ||
      typeof window.enabled !== "boolean" ||
      typeof window.reviewChecked !== "boolean"
    ) {
      return fallback;
    }
    ids.add(id);
    normalizedWindows.push({
      id,
      timeframe: window.timeframe as MultiTimeframeTimeframe,
      enabled: window.enabled,
      reviewChecked: window.reviewChecked,
    });
  }

  if (normalizedWindows.filter((window) => window.enabled).length !== windowCount) {
    return fallback;
  }
  return {
    symbol: activeSymbol.trim().toUpperCase(),
    windowCount: windowCount as MultiTimeframeWindowCount,
    windows: normalizedWindows,
  };
}

export function serializeMultiTimeframeLayout(layout: MultiTimeframeLayout): string {
  return JSON.stringify(layout);
}
