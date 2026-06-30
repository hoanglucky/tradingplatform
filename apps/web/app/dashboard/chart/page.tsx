import { AppShell } from "../../../components/AppShell";
import { ChartPageLayout } from "../../../components/ChartPageLayout";
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
      <ChartPageLayout initialSymbol={initialSymbol} />
    </AppShell>
  );
}
