import type { HealthStatus, ModuleStatus, ReadinessStatus, SafetyStatus } from "@trading-framework/shared";

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

export async function getDashboardData() {
  return Promise.all([
    fetchJson<HealthStatus>("/health", {
      status: "ok",
      service: "trading-framework-api",
      environment: "offline",
      trading_mode: "paper",
    }),
    fetchJson<ReadinessStatus>("/health/ready", {
      status: "degraded",
      dependencies: [
        { name: "postgres", status: "error", detail: "unreachable" },
        { name: "redis", status: "error", detail: "unreachable" },
      ],
    }),
    fetchJson<SafetyStatus>("/safety", {
      default_trading_mode: "paper",
      live_trading_enabled: false,
      exchange_writes_allowed: false,
      exchange_adapter_mode: "read_only",
    }),
    fetchJson<ModuleStatus[]>("/modules", []),
  ]);
}

