import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alkemist — AI-Native Local IDE",
  description:
    "Browser-based IDE with Ollama AI, Docker sandboxes, and iOS build pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-surface-950 text-gray-100 font-mono antialiased">
        {children}
      </body>
    </html>
  );
}
