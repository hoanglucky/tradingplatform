import { SectionPage } from "../../components/SectionPage";

export default function StrategiesPage() {
  return (
    <SectionPage
      title="Strategies"
      description="Strategy configuration will generate paper-only signals."
      items={["Strategy registry", "Parameter forms", "Signal preview", "Risk prechecks"]}
    />
  );
}

