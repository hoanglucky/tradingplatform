"use client";

import type { MarketSymbol, Watchlist } from "@trading-framework/shared";
import { Badge, Panel } from "@trading-framework/ui";
import { ChevronRight, Plus, RefreshCw, Trash2 } from "lucide-react";
import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { availableWatchlistSymbols, watchlistChartHref } from "../lib/watchlist";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function responseError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall through to the status message.
  }
  return `Watchlist request failed (${response.status}).`;
}

export function WatchlistPanel() {
  const [watchlist, setWatchlist] = useState<Watchlist | null>(null);
  const [symbols, setSymbols] = useState<MarketSymbol[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [loading, setLoading] = useState(true);
  const [pendingSymbol, setPendingSymbol] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const availableSymbols = useMemo(
    () => availableWatchlistSymbols(symbols, watchlist?.items ?? []),
    [symbols, watchlist?.items],
  );

  const loadWatchlist = useCallback(async (signal?: AbortSignal) => {
    try {
      const [watchlistResponse, symbolsResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/watchlist`, { signal }),
        fetch(`${apiBaseUrl}/symbols?active_only=true`, { signal }),
      ]);
      if (!watchlistResponse.ok) {
        throw new Error(await responseError(watchlistResponse));
      }
      if (!symbolsResponse.ok) {
        throw new Error(await responseError(symbolsResponse));
      }

      const nextWatchlist = (await watchlistResponse.json()) as Watchlist;
      const nextSymbols = (await symbolsResponse.json()) as MarketSymbol[];
      const nextAvailable = availableWatchlistSymbols(nextSymbols, nextWatchlist.items);
      setError(null);
      setWatchlist(nextWatchlist);
      setSymbols(nextSymbols);
      setSelectedSymbol((current) =>
        nextAvailable.some((symbol) => symbol.symbol === current) ? current : (nextAvailable[0]?.symbol ?? ""),
      );
    } catch (loadError) {
      if (signal?.aborted) {
        return;
      }
      setError(loadError instanceof Error ? loadError.message : "Unable to load watchlist.");
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const request = window.setTimeout(() => void loadWatchlist(controller.signal), 0);
    return () => {
      window.clearTimeout(request);
      controller.abort();
    };
  }, [loadWatchlist]);

  async function addSymbol(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedSymbol || pendingSymbol) {
      return;
    }
    setPendingSymbol(selectedSymbol);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/watchlist/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: selectedSymbol }),
      });
      if (!response.ok) {
        throw new Error(await responseError(response));
      }
      await loadWatchlist();
    } catch (mutationError) {
      setError(mutationError instanceof Error ? mutationError.message : "Unable to add symbol.");
    } finally {
      setPendingSymbol(null);
    }
  }

  function refreshWatchlist() {
    if (loading || pendingSymbol) {
      return;
    }
    setLoading(true);
    void loadWatchlist();
  }

  async function removeSymbol(symbol: string) {
    if (pendingSymbol) {
      return;
    }
    setPendingSymbol(symbol);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/watchlist/items/${encodeURIComponent(symbol)}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(await responseError(response));
      }
      await loadWatchlist();
    } catch (mutationError) {
      setError(mutationError instanceof Error ? mutationError.message : "Unable to remove symbol.");
    } finally {
      setPendingSymbol(null);
    }
  }

  return (
    <Panel className="watchlist-panel">
      <div className="watchlist-header">
        <div>
          <p className="eyebrow">Markets</p>
          <h2>{watchlist?.name ?? "Watchlist"}</h2>
        </div>
        <div className="watchlist-header-actions">
          <Badge tone="neutral">{watchlist?.items.length ?? 0}</Badge>
          <button
            type="button"
            className="watchlist-icon-button"
            aria-label="Refresh watchlist"
            title="Refresh watchlist"
            disabled={loading || pendingSymbol !== null}
            onClick={refreshWatchlist}
          >
            <RefreshCw className={loading ? "is-spinning" : undefined} size={16} aria-hidden="true" />
          </button>
        </div>
      </div>

      <form className="watchlist-add" onSubmit={addSymbol}>
        <label>
          <span>Add symbol</span>
          <select
            value={selectedSymbol}
            onChange={(event) => setSelectedSymbol(event.target.value)}
            disabled={loading || pendingSymbol !== null || availableSymbols.length === 0}
          >
            {availableSymbols.length === 0 ? <option value="">No symbols available</option> : null}
            {availableSymbols.map((symbol) => (
              <option key={symbol.id} value={symbol.symbol}>
                {symbol.symbol} · {symbol.exchange}
              </option>
            ))}
          </select>
        </label>
        <button
          type="submit"
          className="watchlist-icon-button"
          aria-label="Add selected symbol"
          title="Add selected symbol"
          disabled={!selectedSymbol || loading || pendingSymbol !== null}
        >
          <Plus size={17} aria-hidden="true" />
        </button>
      </form>

      {error ? (
        <p className="watchlist-error" role="alert">
          {error}
        </p>
      ) : null}

      {loading && watchlist === null ? (
        <div className="watchlist-state" role="status">
          <span className="chart-spinner" aria-hidden="true" />
          <span>Loading watchlist</span>
        </div>
      ) : error && watchlist === null ? (
        <div className="watchlist-state">
          <strong>Watchlist unavailable</strong>
          <span>Use refresh to try again.</span>
        </div>
      ) : watchlist?.items.length ? (
        <ul className="watchlist-items">
          {watchlist.items.map((item) => (
            <li key={item.id}>
              <Link href={watchlistChartHref(item.symbol)} className="watchlist-symbol-link">
                <span>
                  <strong>{item.symbol}</strong>
                  <small>
                    {item.base_asset} / {item.quote_asset} · {item.exchange}
                  </small>
                </span>
                <ChevronRight size={16} aria-hidden="true" />
              </Link>
              <span className="watchlist-price">
                <strong>—</strong>
                <small>Latest</small>
              </span>
              <button
                type="button"
                className="watchlist-icon-button is-danger"
                aria-label={`Remove ${item.symbol}`}
                title={`Remove ${item.symbol}`}
                disabled={pendingSymbol !== null}
                onClick={() => void removeSymbol(item.symbol)}
              >
                <Trash2 size={16} aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="watchlist-state">
          <strong>No pinned symbols</strong>
          <span>Add a market above.</span>
        </div>
      )}
    </Panel>
  );
}
