import "./src/env.mjs";
import { config } from "@eda/config";
import { withSentryConfig } from "@sentry/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@eda/supabase"],
  experimental: {
    instrumentationHook: process.env.NODE_ENV === "production",
  },
  webpack: (config, { isServer }) => {
    // Handle node: protocol imports
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
      };
    }
    return config;
  },
};

export default withSentryConfig(nextConfig, {
  silent: !process.env.CI,
  telemetry: false,
  widenClientFileUpload: true,
  hideSourceMaps: true,
  disableLogger: true,
  tunnelRoute: "/monitoring",
  authToken: config.api_keys.sentry.auth_token,
});
