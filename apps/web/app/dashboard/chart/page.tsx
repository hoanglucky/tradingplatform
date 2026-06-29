import { AppShell } from "../../../components/AppShell";
import { ChartWorkspace } from "../../../components/ChartWorkspace";
import { WatchlistPanel } from "../../../components/WatchlistPanel";
import { getDashboardData } from "../../../lib/api";

export default async function ChartPage({
  searchParams,
}: {
  searchParams: Promise<{ symbol?: string | string[] }>;
}) {
  const params = await searchParams;
  const initialSymbol = Array.isArray(params.symbol) ? params.symbol[0] : params.symbol;
  const [health, readiness, safety] = await getDashboardData();

  return (
    <AppShell health={health} readiness={readiness} safety={safety}>
      <main className="chart-page">
        <div className="chart-main-column">
          <ChartWorkspace key={initialSymbol ?? "settings-default"} initialSymbol={initialSymbol} />
        </div>
        <aside className="chart-watchlist-column" aria-label="Chart watchlist">
          <WatchlistPanel />
        </aside>
      </main>
    </AppShell>
  );
}
