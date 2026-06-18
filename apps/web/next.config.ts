import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@trading-framework/shared", "@trading-framework/ui"],
};

export default nextConfig;

