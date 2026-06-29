import { Badge, Panel } from "@trading-framework/ui";
import { AppShell } from "../components/AppShell";
import { EmptySection } from "../components/EmptySection";
import { WatchlistPanel } from "../components/WatchlistPanel";
import { getDashboardData } from "../lib/api";

export default async function Home() {
  const [health, readiness, safety, modules] = await getDashboardData();

  return (
    <AppShell health={health} readiness={readiness} safety={safety}>
      <main className="dashboard-grid">
        <section className="primary-column">
          <EmptySection
            title="Candlestick workspace"
            description="Chart integration starts after the dashboard skeleton is stable."
            items={["Symbol selector", "Timeframe selector", "Realtime status", "Indicator overlays"]}
          />
          <section className="module-grid" aria-label="System modules">
            {modules.map((module) => (
              <Panel key={module.name}>
                <div className="module-header">
                  <h2>{module.name}</h2>
                  <Badge tone={module.status === "read_only" ? "success" : "neutral"}>{module.status}</Badge>
                </div>
                <p>{module.role}</p>
              </Panel>
            ))}
          </section>
        </section>

        <aside className="side-column" aria-label="Dashboard side panels">
          <Panel className="status-panel">
            <div className="status-row">
              <span>Live trading</span>
              <Badge tone={safety.live_trading_enabled ? "danger" : "success"}>
                {safety.live_trading_enabled ? "enabled" : "disabled"}
              </Badge>
            </div>
            <div className="status-row">
              <span>Exchange writes</span>
              <Badge tone={safety.exchange_writes_allowed ? "danger" : "success"}>
                {safety.exchange_writes_allowed ? "allowed" : "blocked"}
              </Badge>
            </div>
            <div className="status-row">
              <span>Adapter mode</span>
              <Badge tone="neutral">{safety.exchange_adapter_mode}</Badge>
            </div>
          </Panel>
          <WatchlistPanel />
          <EmptySection
            title="Latest signals"
            description="Strategy signals will stay paper-only in the MVP."
            items={["Signal table", "Confidence", "Generated time"]}
          />
        </aside>
      </main>
    </AppShell>
  );
}
