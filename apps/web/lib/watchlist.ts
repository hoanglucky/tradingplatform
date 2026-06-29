import type { MarketSymbol, WatchlistItem } from "@trading-framework/shared";

export function availableWatchlistSymbols(symbols: MarketSymbol[], items: WatchlistItem[]): MarketSymbol[] {
  const pinned = new Set(items.map((item) => item.symbol));
  return symbols.filter((symbol) => symbol.is_active && !pinned.has(symbol.symbol));
}

export function watchlistChartHref(symbol: string): string {
  return `/dashboard/chart?symbol=${encodeURIComponent(symbol)}`;
}
