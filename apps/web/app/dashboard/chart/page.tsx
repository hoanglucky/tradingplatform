import { AppShell } from "../../../components/AppShell";
import { ChartWorkspace } from "../../../components/ChartWorkspace";
import { getDashboardData } from "../../../lib/api";

export default async function ChartPage() {
  const [health, readiness, safety] = await getDashboardData();

  return (
    <AppShell health={health} readiness={readiness} safety={safety}>
      <main className="chart-page">
        <ChartWorkspace />
      </main>
    </AppShell>
  );
}
