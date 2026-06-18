import { Panel } from "@trading-framework/ui";

export function EmptySection({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: string[];
}) {
  return (
    <Panel className="empty-section">
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </Panel>
  );
}

