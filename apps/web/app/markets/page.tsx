import { SectionPage } from "../../components/SectionPage";

export default function MarketsPage() {
  return (
    <SectionPage
      title="Markets"
      description="Read-only market data views will start here."
      items={["Symbol search", "Latest candles", "Provider status", "No exchange writes"]}
    />
  );
}

