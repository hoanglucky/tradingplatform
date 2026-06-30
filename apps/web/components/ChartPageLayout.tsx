"use client";

import { PanelRightClose, PanelRightOpen } from "lucide-react";
import { useStoredCollapse } from "../lib/collapsible-layout";
import { ChartWorkspace } from "./ChartWorkspace";
import { WatchlistPanel } from "./WatchlistPanel";

const MARKET_SIDEBAR_STORAGE_KEY = "trading-framework:market-sidebar-collapsed";

export function ChartPageLayout({ initialSymbol }: { initialSymbol?: string }) {
  const [marketSidebarCollapsed, toggleMarketSidebar] = useStoredCollapse(MARKET_SIDEBAR_STORAGE_KEY);

  return (
    <main className={`chart-page${marketSidebarCollapsed ? " is-watchlist-collapsed" : ""}`}>
      <div className="chart-main-column">
        <ChartWorkspace key={initialSymbol ?? "settings-default"} initialSymbol={initialSymbol} />
      </div>
      <aside
        className={`chart-watchlist-column${marketSidebarCollapsed ? " is-collapsed" : ""}`}
        aria-label="Chart watchlist"
      >
        <button
          type="button"
          className="market-sidebar-toggle"
          aria-label={marketSidebarCollapsed ? "Expand markets" : "Collapse markets"}
          title={marketSidebarCollapsed ? "Expand markets" : "Collapse markets"}
          onClick={toggleMarketSidebar}
        >
          {marketSidebarCollapsed ? (
            <PanelRightOpen size={18} aria-hidden="true" />
          ) : (
            <PanelRightClose size={18} aria-hidden="true" />
          )}
        </button>
        {marketSidebarCollapsed ? <span className="market-sidebar-label">Markets</span> : <WatchlistPanel />}
      </aside>
    </main>
  );
}
