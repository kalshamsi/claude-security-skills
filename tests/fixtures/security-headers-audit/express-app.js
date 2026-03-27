/**
 * SaaS Dashboard API — Express backend with Helmet.js security headers.
 * Serves the dashboard API and proxies to internal microservices.
 */

const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const session = require("express-session");

const app = express();

// ---------------------------------------------------------------------------
// Security headers via Helmet
// ---------------------------------------------------------------------------

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        // VULNERABILITY [Check 1 - Weak CSP]: unsafe-eval in script-src-elem
        // allows eval()-based XSS. Subtle: it's on script-src-elem (not the
        // more obvious script-src), and the rest of the CSP looks restrictive.
        scriptSrcElem: ["'self'", "'unsafe-eval'", "https://cdn.dashboard.io"],
        styleSrc: ["'self'", "'unsafe-inline'"],  // unsafe-inline on styles is common/accepted
        imgSrc: ["'self'", "data:", "https://avatars.dashboard.io"],
        connectSrc: ["'self'", "https://api.dashboard.io"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        objectSrc: ["'none'"],
        frameAncestors: ["'self'"],
      },
    },
    // X-Content-Type-Options is enabled by default in helmet (nosniff)
    // X-Frame-Options is enabled by default (SAMEORIGIN via frameAncestors)
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  })
);

// ---------------------------------------------------------------------------
// CORS configuration
// ---------------------------------------------------------------------------

app.use(
  cors({
    // VULNERABILITY [Check 2 - Permissive CORS]: credentials: true with a
    // broad origin list. Subtle: it's not `origin: "*"` (the textbook
    // example). Instead it's a list that includes a wildcard subdomain
    // pattern via a function, combined with credentials: true.
    origin: function (origin, callback) {
      const allowed = [
        "https://app.dashboard.io",
        "https://staging.dashboard.io",
      ];
      // Allow any *.dashboard.io subdomain — but this includes
      // attacker-controlled subdomains if DNS is compromised
      if (!origin || allowed.includes(origin) || /\.dashboard\.io$/.test(origin)) {
        callback(null, true);
      } else {
        callback(new Error("CORS not allowed"));
      }
    },
    credentials: true,
  })
);

// ---------------------------------------------------------------------------
// Session management
// ---------------------------------------------------------------------------

app.use(
  session({
    secret: process.env.SESSION_SECRET || "dashboard-dev-secret",
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === "production",
      httpOnly: true,
      sameSite: "lax",
    },
  })
);

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

app.use(express.json());

// VULNERABILITY [Check 8 - Missing Cache-Control]: Auth-related endpoint
// returns user profile data but doesn't set Cache-Control headers.
// Subtle: other routes might inherit defaults, but this sensitive endpoint
// needs explicit no-store.
app.get("/api/me", (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: "Not authenticated" });
  }
  res.json({
    id: req.session.userId,
    email: req.session.email,
    role: req.session.role,
    apiKey: req.session.apiKey,  // Leaks sensitive data, no cache-control
  });
});

app.get("/api/dashboard/stats", (req, res) => {
  res.set("Cache-Control", "private, no-cache, max-age=60");
  res.json({ activeUsers: 1234, revenue: 56789 });
});

// VULNERABILITY [Check 9 - Exposed Server/X-Powered-By]:
// Helmet removes X-Powered-By by default, but this middleware re-adds it.
// Subtle: it's buried in a "monitoring" middleware, not obvious as a header leak.
app.use((req, res, next) => {
  res.set("X-Request-Id", `req-${Date.now()}`);
  res.set("X-Powered-By", "DashboardAPI/3.2.1");  // Overrides helmet's removal
  next();
});

app.get("/api/health", (req, res) => {
  res.json({ status: "ok", version: "3.2.1" });
});

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------

const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Dashboard API listening on port ${PORT}`);
  });
}

module.exports = app;
