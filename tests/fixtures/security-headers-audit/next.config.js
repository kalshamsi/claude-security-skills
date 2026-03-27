/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // ---------------------------------------------------------------------------
  // Security headers for the Next.js frontend
  // ---------------------------------------------------------------------------
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          // VULNERABILITY [Check 7 - Overly Permissive Permissions-Policy]:
          // Grants access to camera, microphone, and geolocation to self AND
          // any dashboard.io subdomain. A SaaS dashboard rarely needs camera
          // or microphone access. Subtle: the syntax is correct and looks
          // intentional, but the permissions granted are excessive.
          {
            key: "Permissions-Policy",
            value:
              "camera=(self https://*.dashboard.io), " +
              "microphone=(self https://*.dashboard.io), " +
              "geolocation=(self), " +
              "payment=(self)",
          },
        ],
      },
      {
        // API routes served by Next.js API routes (BFF layer)
        source: "/api/:path*",
        headers: [
          // VULNERABILITY [Check 10 - Missing HSTS on API responses]:
          // The main Nginx config sets HSTS for the frontend, but Next.js
          // API routes (served via a different path) don't get HSTS when
          // accessed directly during development or via internal routing.
          // (No Strict-Transport-Security header here)

          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
        ],
      },
    ];
  },

  // ---------------------------------------------------------------------------
  // VULNERABILITY [Check 11 - Missing COOP/COEP]:
  // No Cross-Origin-Opener-Policy or Cross-Origin-Embedder-Policy headers
  // are set anywhere. The dashboard loads third-party analytics scripts,
  // which could exploit Spectre-type side-channels without cross-origin
  // isolation. Subtle: COOP/COEP are relatively new and many teams skip them.
  // ---------------------------------------------------------------------------

  // Standard Next.js configuration
  images: {
    domains: ["avatars.dashboard.io", "cdn.dashboard.io"],
  },

  experimental: {
    serverActions: { bodySizeLimit: "2mb" },
  },
};

module.exports = nextConfig;
