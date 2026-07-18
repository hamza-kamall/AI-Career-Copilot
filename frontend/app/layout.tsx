import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BootCamp.AI",
  description: "Personalized career guidance with mentor matching and verified learning resources.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
