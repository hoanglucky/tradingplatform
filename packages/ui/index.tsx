import type { HTMLAttributes, ReactNode } from "react";

type BadgeTone = "neutral" | "success" | "danger";

export function Panel({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={["tf-panel", className].filter(Boolean).join(" ")} {...props} />;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: BadgeTone }) {
  return <span className={`tf-badge tf-badge-${tone}`}>{children}</span>;
}

