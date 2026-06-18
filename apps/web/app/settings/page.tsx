import { SectionPage } from "../../components/SectionPage";

export default function SettingsPage() {
  return (
    <SectionPage
      title="Settings"
      description="MVP settings remain safe-by-default and paper-first."
      items={["Environment status", "Read-only exchange settings", "User preferences", "Audit notes"]}
    />
  );
}

