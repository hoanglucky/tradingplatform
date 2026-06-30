"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { LucideIcon } from "lucide-react";
import {
  Bell,
  ChartCandlestick,
  FlaskConical,
  History,
  LayoutDashboard,
  List,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  WalletCards,
} from "lucide-react";
import type { ReactNode } from "react";
import { Badge, Panel } from "@trading-framework/ui";
import type { HealthStatus, ReadinessStatus, SafetyStatus } from "@trading-framework/shared";
import { useStoredCollapse } from "../lib/collapsible-layout";

const SIDEBAR_STORAGE_KEY = "trading-framework:sidebar-collapsed";

const navItems: Array<{ href: string; label: string; icon: LucideIcon }> = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/markets", label: "Markets", icon: List },
  { href: "/dashboard/chart", label: "Chart", icon: ChartCandlestick },
  { href: "/strategies", label: "Strategies", icon: FlaskConical },
  { href: "/backtests", label: "Backtests", icon: History },
  { href: "/paper", label: "Paper", icon: WalletCards },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
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
  const pathname = usePathname();
  const [sidebarCollapsed, toggleSidebar] = useStoredCollapse(SIDEBAR_STORAGE_KEY);

  return (
    <div className={`app-frame${sidebarCollapsed ? " is-sidebar-collapsed" : ""}`}>
      <aside className={`sidebar${sidebarCollapsed ? " is-collapsed" : ""}`} aria-label="Primary navigation">
        <div className="brand-block">
          <span className="brand-mark">TF</span>
          <div className="brand-copy">
            <strong>Trading Framework</strong>
            <span>Paper MVP</span>
          </div>
        </div>
        <button
          type="button"
          className="sidebar-toggle"
          aria-label={sidebarCollapsed ? "Expand navigation" : "Collapse navigation"}
          title={sidebarCollapsed ? "Expand navigation" : "Collapse navigation"}
          onClick={toggleSidebar}
        >
          {sidebarCollapsed ? (
            <PanelLeftOpen size={18} aria-hidden="true" />
          ) : (
            <PanelLeftClose size={18} aria-hidden="true" />
          )}
        </button>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={active ? "is-active" : undefined}
                aria-current={active ? "page" : undefined}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </Link>
            );
          })}
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
