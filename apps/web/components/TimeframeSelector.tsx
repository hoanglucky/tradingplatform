"use client";

import { ChevronDown, Star } from "lucide-react";
import { FormEvent, useState } from "react";
import {
  TIMEFRAME_GROUPS,
  normalizeChartTimeframe,
} from "../lib/timeframe-options";

type TimeframeSelectorProps = {
  activeTimeframe: string;
  favorites: string[];
  onSelect: (timeframe: string) => void;
  onToggleFavorite: (timeframe: string) => void;
};

export function TimeframeSelector({
  activeTimeframe,
  favorites,
  onSelect,
  onToggleFavorite,
}: TimeframeSelectorProps) {
  const [customValue, setCustomValue] = useState("");
  const normalizedCustom = normalizeChartTimeframe(customValue);

  function selectCustom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (normalizedCustom) onSelect(normalizedCustom);
  }

  return (
    <div className="workspace-timeframe-selector" aria-label="Active chart timeframe">
      <span>Timeframe</span>
      <div className="timeframe-control-row">
        <div className="timeframe-favorites">
          {favorites.map((timeframe) => (
            <button
              key={timeframe}
              type="button"
              className={activeTimeframe === timeframe ? "is-active" : undefined}
              aria-pressed={activeTimeframe === timeframe}
              onClick={() => onSelect(timeframe)}
            >
              {timeframe}
            </button>
          ))}
        </div>
        <details className="timeframe-menu">
          <summary aria-label="Open timeframe list" title="Timeframe list">
            <ChevronDown size={17} aria-hidden="true" />
          </summary>
          <div className="timeframe-menu-popover">
            {TIMEFRAME_GROUPS.map((group) => (
              <section key={group.label}>
                <strong>{group.label}</strong>
                <div>
                  {group.values.map((timeframe) => {
                    const favorite = favorites.includes(timeframe);
                    return (
                      <span className="timeframe-menu-item" key={timeframe}>
                        <button type="button" onClick={() => onSelect(timeframe)}>
                          {timeframe}
                          {timeframe === "1M" ? <small>month</small> : null}
                        </button>
                        <button
                          type="button"
                          className={favorite ? "is-favorite" : undefined}
                          aria-label={`${favorite ? "Remove" : "Add"} ${timeframe} favorite`}
                          title={`${favorite ? "Remove" : "Add"} favorite`}
                          onClick={() => onToggleFavorite(timeframe)}
                        >
                          <Star size={15} fill={favorite ? "currentColor" : "none"} aria-hidden="true" />
                        </button>
                      </span>
                    );
                  })}
                </div>
              </section>
            ))}
            <form className="timeframe-custom" onSubmit={selectCustom}>
              <label htmlFor="custom-timeframe">Custom</label>
              <div>
                <input
                  id="custom-timeframe"
                  value={customValue}
                  placeholder="e.g. 7m"
                  aria-invalid={customValue.length > 0 && !normalizedCustom}
                  onChange={(event) => setCustomValue(event.target.value)}
                />
                <button type="submit" disabled={!normalizedCustom}>Apply</button>
                <button
                  type="button"
                  disabled={!normalizedCustom}
                  aria-label="Toggle custom timeframe favorite"
                  title="Toggle favorite"
                  onClick={() => normalizedCustom && onToggleFavorite(normalizedCustom)}
                >
                  <Star
                    size={15}
                    fill={normalizedCustom && favorites.includes(normalizedCustom) ? "currentColor" : "none"}
                    aria-hidden="true"
                  />
                </button>
              </div>
              {customValue && !normalizedCustom ? <small>Use 1m–31d, 1–4w, or 1M.</small> : null}
            </form>
          </div>
        </details>
      </div>
    </div>
  );
}
