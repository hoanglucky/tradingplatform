import { SectionPage } from "../../components/SectionPage";

export default function BacktestsPage() {
  return (
    <SectionPage
      title="Backtests"
      description="Historical simulations will be reviewed before paper trading."
      items={["Run form", "Metrics summary", "Equity curve", "Trade list"]}
    />
  );
}

