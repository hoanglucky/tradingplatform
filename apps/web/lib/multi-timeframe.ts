export const MULTI_TIMEFRAME_WINDOW_COUNTS = [1, 2, 4, 8] as const;
export const MULTI_TIMEFRAME_TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"] as const;

export type MultiTimeframeWindowCount = (typeof MULTI_TIMEFRAME_WINDOW_COUNTS)[number];
export type MultiTimeframeTimeframe = "1m" | "5m" | "15m" | "1h" | "4h" | "1d";

export type MultiTimeframeWindow = {
  id: string;
  timeframe: MultiTimeframeTimeframe;
  enabled: boolean;
  reviewChecked: boolean;
};

export type MultiTimeframeLayout = {
  symbol: string;
  windowCount: MultiTimeframeWindowCount;
  windows: MultiTimeframeWindow[];
};

export const DEFAULT_MULTI_TIMEFRAME_WINDOWS: readonly MultiTimeframeWindow[] = [
  { id: "w1", timeframe: "4h", enabled: true, reviewChecked: false },
  { id: "w2", timeframe: "1h", enabled: true, reviewChecked: false },
  { id: "w3", timeframe: "15m", enabled: true, reviewChecked: false },
  { id: "w4", timeframe: "5m", enabled: true, reviewChecked: false },
];

const ADDITIONAL_WINDOW_TIMEFRAMES: readonly MultiTimeframeTimeframe[] = [
  "1d",
  "1m",
  "4h",
  "15m",
];

function createWindow(index: number): MultiTimeframeWindow {
  const defaultWindow = DEFAULT_MULTI_TIMEFRAME_WINDOWS[index];
  return defaultWindow
    ? { ...defaultWindow }
    : {
        id: `w${index + 1}`,
        timeframe: ADDITIONAL_WINDOW_TIMEFRAMES[
          (index - DEFAULT_MULTI_TIMEFRAME_WINDOWS.length) % ADDITIONAL_WINDOW_TIMEFRAMES.length
        ],
        enabled: true,
        reviewChecked: false,
      };
}

export function createDefaultMultiTimeframeLayout(symbol: string): MultiTimeframeLayout {
  return {
    symbol: symbol.trim().toUpperCase(),
    windowCount: 4,
    windows: DEFAULT_MULTI_TIMEFRAME_WINDOWS.map((window) => ({ ...window })),
  };
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
    windows.push(createWindow(windows.length));
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
