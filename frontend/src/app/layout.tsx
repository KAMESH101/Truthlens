// src/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TruthLens — AI Review Detector",
  description: "Detect fake reviews and manipulated ratings on any e-commerce product with AI.",
  openGraph: {
    title: "TruthLens — AI Review Detector",
    description: "We don't just detect fake reviews — we explain them.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
