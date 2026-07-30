import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/v1/:path*',
        destination: 'http://127.0.0.1:8001/v1/:path*',
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:8001/health',
      }
    ];
  },
};

export default nextConfig;
