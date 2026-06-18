import { AppShell } from "./AppShell";
import { EmptySection } from "./EmptySection";
import { getDashboardData } from "../lib/api";

export async function SectionPage({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: string[];
}) {
  const [health, readiness, safety] = await getDashboardData();

  return (
    <AppShell health={health} readiness={readiness} safety={safety}>
      <main className="route-page">
        <EmptySection title={title} description={description} items={items} />
      </main>
    </AppShell>
  );
}

