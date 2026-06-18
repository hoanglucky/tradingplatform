import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./ui.css";
import "./styles.css";

export const metadata: Metadata = {
  title: "Trading Framework",
  description: "Paper-first modular trading MVP foundation.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
