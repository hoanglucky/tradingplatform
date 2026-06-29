"use client";

import {
  MULTI_TIMEFRAME_TIMEFRAMES,
  type MultiTimeframeLayout,
  type MultiTimeframeTimeframe,
  visibleMultiTimeframeWindows,
} from "../lib/multi-timeframe";

type MultiTimeframeGridProps = {
  layout: MultiTimeframeLayout;
  onTimeframeChange: (windowId: string, timeframe: MultiTimeframeTimeframe) => void;
  onReviewChange: (windowId: string, reviewChecked: boolean) => void;
};

export function MultiTimeframeGrid({
  layout,
  onTimeframeChange,
  onReviewChange,
}: MultiTimeframeGridProps) {
  const visibleWindows = visibleMultiTimeframeWindows(layout);

  return (
    <section
      className={`multi-timeframe-grid is-layout-${layout.windowCount}`}
      aria-label={`${layout.symbol} multi-timeframe review windows`}
    >
      {visibleWindows.map((window) => (
        <article className="multi-timeframe-window" key={window.id} data-window-id={window.id}>
          <header className="multi-timeframe-window-header">
            <div>
              <span>{layout.symbol}</span>
              <strong>{window.timeframe}</strong>
            </div>
            <label className="review-window-check">
              <input
                type="checkbox"
                checked={window.reviewChecked}
                onChange={(event) => onReviewChange(window.id, event.target.checked)}
              />
              <span>Reviewed</span>
            </label>
          </header>
          <label className="review-window-timeframe">
            <span>Timeframe</span>
            <select
              value={window.timeframe}
              onChange={(event) =>
                onTimeframeChange(window.id, event.target.value as MultiTimeframeTimeframe)
              }
            >
              {MULTI_TIMEFRAME_TIMEFRAMES.map((timeframe) => (
                <option value={timeframe} key={timeframe}>
                  {timeframe}
                </option>
              ))}
            </select>
          </label>
          <div
            className="review-window-placeholder"
            role="img"
            aria-label={`${layout.symbol} ${window.timeframe} chart placeholder`}
          >
            <span>{layout.symbol}</span>
            <strong>{window.timeframe}</strong>
          </div>
        </article>
      ))}
    </section>
  );
}
