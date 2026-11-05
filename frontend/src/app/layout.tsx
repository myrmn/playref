import type { Metadata, Viewport } from "next";
import { Inter, Cairo } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const cairo = Cairo({
  variable: "--font-cairo",
  subsets: ["arabic", "latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "PlayRef | Football Laws of the Game Assistant",
  description: "AI football assistant grounded in official IFAB Laws of the Game with verifiable citations and rule interpretations.",
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${cairo.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
