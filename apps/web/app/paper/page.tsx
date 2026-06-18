import { SectionPage } from "../../components/SectionPage";

export default function PaperPage() {
  return (
    <SectionPage
      title="Paper trading"
      description="Simulated orders and portfolio state live here."
      items={["Paper account", "Simulated orders", "Positions", "PnL"]}
    />
  );
}

