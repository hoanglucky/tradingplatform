import { Badge, Panel } from "@trading-framework/ui";
import type { ModuleStatus, SafetyStatus } from "@trading-framework/shared";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, { next: { revalidate: 5 } });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export default async function Home() {
  const [modules, safety] = await Promise.all([
    fetchJson<ModuleStatus[]>("/modules", []),
    fetchJson<SafetyStatus>("/safety", {
      default_trading_mode: "paper",
      live_trading_enabled: false,
      exchange_writes_allowed: false,
      exchange_adapter_mode: "read_only",
    }),
  ]);

  return (
    <main className="shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">Trading Framework</p>
          <h1>Paper-first trading MVP foundation</h1>
          <p className="lede">
            A modular starter for market data, indicators, strategies, backtests, simulated execution,
            alerts, and read-only exchange connectivity.
          </p>
        </div>
        <Panel className="status-panel">
          <div className="status-row">
            <span>Mode</span>
            <Badge tone="success">{safety.default_trading_mode}</Badge>
          </div>
          <div className="status-row">
            <span>Live trading</span>
            <Badge tone={safety.live_trading_enabled ? "danger" : "neutral"}>
              {safety.live_trading_enabled ? "enabled" : "disabled"}
            </Badge>
          </div>
          <div className="status-row">
            <span>Exchange writes</span>
            <Badge tone={safety.exchange_writes_allowed ? "danger" : "neutral"}>
              {safety.exchange_writes_allowed ? "allowed" : "blocked"}
            </Badge>
          </div>
        </Panel>
      </section>

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
    </main>
  );
}

