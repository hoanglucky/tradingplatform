import Link from "next/link";
import type { ReactNode } from "react";
import { Badge, Panel } from "@trading-framework/ui";
import type { HealthStatus, ReadinessStatus, SafetyStatus } from "@trading-framework/shared";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/markets", label: "Markets" },
  { href: "/dashboard/chart", label: "Chart" },
  { href: "/strategies", label: "Strategies" },
  { href: "/backtests", label: "Backtests" },
  { href: "/paper", label: "Paper" },
  { href: "/alerts", label: "Alerts" },
  { href: "/settings", label: "Settings" },
];

export function AppShell({
  children,
  health,
  readiness,
  safety,
}: {
  children: ReactNode;
  health: HealthStatus;
  readiness: ReadinessStatus;
  safety: SafetyStatus;
}) {
  const apiTone = readiness.status === "ready" ? "success" : "danger";

  return (
    <div className="app-frame">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand-block">
          <span className="brand-mark">TF</span>
          <div>
            <strong>Trading Framework</strong>
            <span>Paper MVP</span>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations</p>
            <h1>Trading dashboard</h1>
          </div>
          <div className="topbar-status" aria-label="System status">
            <Badge tone={apiTone}>{readiness.status}</Badge>
            <Badge tone={safety.exchange_writes_allowed ? "danger" : "success"}>writes blocked</Badge>
          </div>
        </header>

        <section className="system-strip" aria-label="API health">
          <Panel>
            <span>API</span>
            <strong>{health.service}</strong>
            <small>{health.environment}</small>
          </Panel>
          <Panel>
            <span>Trading mode</span>
            <strong>{safety.default_trading_mode}</strong>
            <small>{health.trading_mode}</small>
          </Panel>
          <Panel>
            <span>Dependencies</span>
            <strong>{readiness.status}</strong>
            <small>{readiness.dependencies.map((dependency) => `${dependency.name}:${dependency.status}`).join(" · ")}</small>
          </Panel>
        </section>

        {children}
      </div>
    </div>
  );
}
