import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow local network IP access in dev mode so HMR and client chunks aren't blocked
  allowedDevOrigins: [
    "localhost:3000",
    "127.0.0.1:3000",
    "192.168.100.12:3000",
    "192.168.100.12",
  ],
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
