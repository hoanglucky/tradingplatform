import { SectionPage } from "../../components/SectionPage";

export default function AlertsPage() {
  return (
    <SectionPage
      title="Alerts"
      description="Signal, risk, and system notifications will be configured here."
      items={["Alert rules", "Delivery channels", "Cooldowns", "History"]}
    />
  );
}

