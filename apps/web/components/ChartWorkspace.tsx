"use client";

import { RefreshCw, RotateCcw } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import {
  MULTI_TIMEFRAME_TIMEFRAMES,
  MULTI_TIMEFRAME_WINDOW_COUNTS,
  clearMultiTimeframeReview,
  createDefaultMultiTimeframeLayout,
  getMultiTimeframeReviewProgress,
  resizeMultiTimeframeLayout,
  resolveMultiTimeframeLayout,
  serializeMultiTimeframeLayout,
  updateMultiTimeframeSymbol,
  updateMultiTimeframeWindow,
  type MultiTimeframeTimeframe,
} from "../lib/multi-timeframe";
import {
  getUserSettings,
  patchUserSettings,
  resolveChartPreferences,
  type ChartPreferences,
  type UserSettingsPatch,
} from "../lib/user-settings";
import { MultiTimeframeGrid } from "./MultiTimeframeGrid";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const CHART_TIMEZONES = ["UTC", "Asia/Bangkok"] as const;

const SYMBOLS = [
  { value: "BTCUSDT", label: "BTC / USDT", provider: "Binance" },
  { value: "ETHUSDT", label: "ETH / USDT", provider: "Binance" },
  { value: "SOLUSDT", label: "SOL / USDT", provider: "Binance" },
  { value: "BNBUSDT", label: "BNB / USDT", provider: "Binance" },
  { value: "XRPUSDT", label: "XRP / USDT", provider: "Binance" },
  { value: "XAUUSD", label: "XAU / USD", provider: "Oanda" },
  { value: "SP500", label: "S&P 500", provider: "Oanda" },
  { value: "US100", label: "US 100", provider: "Oanda" },
] as const;

type PreferenceStatus = "loading" | "ready" | "saving" | "error";

export function ChartWorkspace({ initialSymbol }: { initialSymbol?: string }) {
  const normalizedInitialSymbol = SYMBOLS.some((item) => item.value === initialSymbol?.toUpperCase())
    ? initialSymbol?.toUpperCase() ?? "BTCUSDT"
    : "BTCUSDT";
  const [symbol, setSymbol] = useState(normalizedInitialSymbol);
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [latestPrice, setLatestPrice] = useState<number | null>(null);
  const [timezone, setTimezone] = useState<string>("UTC");
  const [preferencesReady, setPreferencesReady] = useState(false);
  const [preferenceStatus, setPreferenceStatus] = useState<PreferenceStatus>("loading");
  const [multiTimeframeLayout, setMultiTimeframeLayout] = useState(() =>
    createDefaultMultiTimeframeLayout(normalizedInitialSymbol),
  );
  const persistedPreferencesRef = useRef<ChartPreferences>({
    symbol: normalizedInitialSymbol,
    timeframe: "15m",
  });
  const persistedMultiTimeframeLayoutRef = useRef<string | null>(
    serializeMultiTimeframeLayout(createDefaultMultiTimeframeLayout(normalizedInitialSymbol)),
  );
  const persistedTimezoneRef = useRef("UTC");
  const settingsSaveQueueRef = useRef<Promise<void>>(Promise.resolve());
  const settingsSaveVersionRef = useRef(0);
  const selectedSymbol = SYMBOLS.find((item) => item.value === symbol) ?? SYMBOLS[0];
  const reviewProgress = getMultiTimeframeReviewProgress(multiTimeframeLayout);

  useEffect(() => {
    const controller = new AbortController();

    void getUserSettings(apiBaseUrl, controller.signal)
      .then((settings) => {
        const supportedSymbols = SYMBOLS.map((item) => item.value);
        const storedPreferences = resolveChartPreferences(
          settings,
          undefined,
          supportedSymbols,
          MULTI_TIMEFRAME_TIMEFRAMES,
        );
        const effectivePreferences = resolveChartPreferences(
          settings,
          initialSymbol,
          supportedSymbols,
          MULTI_TIMEFRAME_TIMEFRAMES,
        );
        persistedPreferencesRef.current = storedPreferences;
        persistedMultiTimeframeLayoutRef.current = settings.multi_timeframe_layout
          ? JSON.stringify(settings.multi_timeframe_layout)
          : null;
        persistedTimezoneRef.current = settings.timezone;
        setSymbol(effectivePreferences.symbol);
        setTimezone(settings.timezone);
        setMultiTimeframeLayout(
          resolveMultiTimeframeLayout(
            settings.multi_timeframe_layout,
            effectivePreferences.symbol,
            supportedSymbols,
          ),
        );
        setPreferenceStatus("ready");
      })
      .catch(() => {
        if (!controller.signal.aborted) setPreferenceStatus("error");
      })
      .finally(() => {
        if (!controller.signal.aborted) setPreferencesReady(true);
      });

    return () => controller.abort();
  }, [initialSymbol]);

  useEffect(() => {
    if (!preferencesReady) return;
    const patch: UserSettingsPatch = {};
    if (symbol !== persistedPreferencesRef.current.symbol) {
      patch.default_symbol = symbol;
    }
    if (timezone !== persistedTimezoneRef.current) {
      patch.timezone = timezone;
    }
    const serializedLayout = serializeMultiTimeframeLayout(multiTimeframeLayout);
    if (serializedLayout !== persistedMultiTimeframeLayoutRef.current) {
      patch.multi_timeframe_layout = multiTimeframeLayout;
    }
    if (Object.keys(patch).length === 0) return;

    const saveVersion = ++settingsSaveVersionRef.current;
    const operation = settingsSaveQueueRef.current
      .catch(() => undefined)
      .then(async () => {
        if (settingsSaveVersionRef.current === saveVersion) setPreferenceStatus("saving");
        const updated = await patchUserSettings(apiBaseUrl, patch);
        persistedPreferencesRef.current = {
          symbol: updated.default_symbol,
          timeframe: updated.default_timeframe,
        };
        persistedMultiTimeframeLayoutRef.current = updated.multi_timeframe_layout
          ? serializeMultiTimeframeLayout(updated.multi_timeframe_layout)
          : null;
        persistedTimezoneRef.current = updated.timezone;
      });
    settingsSaveQueueRef.current = operation;
    void operation.then(
      () => {
        if (settingsSaveVersionRef.current === saveVersion) setPreferenceStatus("ready");
      },
      () => {
        if (settingsSaveVersionRef.current === saveVersion) setPreferenceStatus("error");
      },
    );
  }, [multiTimeframeLayout, preferencesReady, symbol, timezone]);

  function selectSymbol(nextSymbol: string) {
    setLatestPrice(null);
    setMultiTimeframeLayout((current) => updateMultiTimeframeSymbol(current, nextSymbol));
    setSymbol(nextSymbol);
  }

  function selectReviewWindowCount(windowCount: (typeof MULTI_TIMEFRAME_WINDOW_COUNTS)[number]) {
    setMultiTimeframeLayout((current) => resizeMultiTimeframeLayout(current, windowCount));
  }

  function selectReviewTimeframe(windowId: string, nextTimeframe: MultiTimeframeTimeframe) {
    setMultiTimeframeLayout((current) =>
      updateMultiTimeframeWindow(current, windowId, { timeframe: nextTimeframe }),
    );
  }

  function setReviewChecked(windowId: string, reviewChecked: boolean) {
    setMultiTimeframeLayout((current) =>
      updateMultiTimeframeWindow(current, windowId, { reviewChecked }),
    );
  }

  return (
    <>
      <header
        className="chart-toolbar"
        data-review-symbol={multiTimeframeLayout.symbol}
        data-review-window-count={multiTimeframeLayout.windowCount}
        data-review-enabled-windows={multiTimeframeLayout.windows.filter((window) => window.enabled).length}
      >
        <label className="chart-symbol-control">
          <span>Symbol</span>
          <select value={symbol} onChange={(event) => selectSymbol(event.target.value)}>
            {SYMBOLS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.value}
              </option>
            ))}
          </select>
          <small>
            {selectedSymbol.provider} · read-only
            {preferenceStatus === "saving"
              ? " · saving"
              : preferenceStatus === "error"
                ? " · settings unavailable"
                : ""}
          </small>
        </label>
        <label className="chart-timezone-control">
          <span>Chart timezone</span>
          <select value={timezone} onChange={(event) => setTimezone(event.target.value)}>
            {CHART_TIMEZONES.map((item) => (
              <option key={item} value={item}>
                {item === "Asia/Bangkok" ? "Bangkok (UTC+7)" : "UTC"}
              </option>
            ))}
          </select>
          <small>Candle open time</small>
        </label>
        <div className="chart-market-summary">
          <div className="chart-quote">
            <span>Realtime price</span>
            <strong>
              {latestPrice === null
                ? "—"
                : latestPrice.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 5,
                  })}
            </strong>
            <small>{selectedSymbol.label}</small>
          </div>
          <button
            type="button"
            className="chart-refresh-button"
            aria-label="Refresh all chart windows"
            title="Refresh all chart windows"
            onClick={() => setRefreshVersion((version) => version + 1)}
          >
            <RefreshCw aria-hidden="true" size={17} />
          </button>
        </div>
      </header>

      <section className="review-workspace-toolbar" aria-label="Multi-timeframe review layout">
        <div className="review-workspace-title">
          <span>Review layout</span>
          <strong>{multiTimeframeLayout.symbol}</strong>
        </div>
        <div className="review-layout-selector" aria-label="Window count">
          {MULTI_TIMEFRAME_WINDOW_COUNTS.map((windowCount) => (
            <button
              key={windowCount}
              type="button"
              className={multiTimeframeLayout.windowCount === windowCount ? "is-active" : undefined}
              aria-pressed={multiTimeframeLayout.windowCount === windowCount}
              aria-label={`${windowCount} chart ${windowCount === 1 ? "window" : "windows"}`}
              onClick={() => selectReviewWindowCount(windowCount)}
            >
              {windowCount}
            </button>
          ))}
        </div>
        <div className="review-workspace-progress">
          <strong aria-live="polite">
            Reviewed {reviewProgress.reviewed}/{reviewProgress.total} timeframes
          </strong>
          <button
            type="button"
            onClick={() => setMultiTimeframeLayout((current) => clearMultiTimeframeReview(current))}
            disabled={reviewProgress.reviewed === 0}
          >
            <RotateCcw size={14} aria-hidden="true" />
            <span>Clear review</span>
          </button>
        </div>
      </section>

      <MultiTimeframeGrid
        layout={multiTimeframeLayout}
        timezone={timezone}
        refreshVersion={refreshVersion}
        onLatestPriceChange={setLatestPrice}
        onTimeframeChange={selectReviewTimeframe}
        onReviewChange={setReviewChecked}
      />

      <p className="chart-attribution">
        Charts by{" "}
        <a href="https://www.tradingview.com" target="_blank" rel="noreferrer">
          TradingView
        </a>
      </p>
    </>
  );
}
