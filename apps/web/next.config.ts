import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* ---- Images ---- */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "fdn2.gsmarena.com",
        pathname: "/vv/bigpic/**",
      },
      {
        protocol: "https",
        hostname: "fdn.gsmarena.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "m.media-amazon.com",
        pathname: "/images/**",
      },
      {
        protocol: "https",
        hostname: "rukminim2.flixcart.com",
        pathname: "/**",
      },
    ],
  },

  /* ---- Environment Variables ---- */
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  /* ---- Headers ---- */
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
        ],
      },
    ];
  },

  /* ---- Redirects ---- */
  async redirects() {
    return [
      {
        source: "/quiz",
        destination: "/easy",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
