/**
 * FIXTURE: Insecure Express.js application
 *
 * This file intentionally contains HTTP security header misconfigurations
 * for use by the security-headers-audit skill test suite.
 *
 * Issues present (do NOT use in production):
 *   - No Helmet.js — all default header protections absent
 *   - Permissive CORS: origin '*' on all routes
 *   - No Content-Security-Policy header
 *   - X-Powered-By header exposed (Express default)
 *   - No X-Content-Type-Options header
 *   - No X-Frame-Options header
 *   - No Strict-Transport-Security header
 *   - No Referrer-Policy header
 *   - Sensitive endpoint returns user data with no Cache-Control
 *   - No Permissions-Policy header
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// ----------------------------------------------------------------
// ISSUE 1: Permissive CORS — wildcard origin on all routes
// CWE-942 | A05:2021 — any website can make credentialed requests
// ----------------------------------------------------------------
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Origin', 'X-Requested-With', 'Content-Type', 'Accept', 'Authorization'],
}));

app.use(express.json());

// ----------------------------------------------------------------
// ISSUE 2: No Helmet.js — no security headers applied
// This means: X-Content-Type-Options, X-Frame-Options, HSTS,
//             Referrer-Policy, and X-DNS-Prefetch-Control are all absent
// CWE-693, CWE-16, CWE-319, CWE-1021, CWE-200 | A05:2021
// ----------------------------------------------------------------
// Missing: app.use(require('helmet')());

// ----------------------------------------------------------------
// ISSUE 3: X-Powered-By exposed
// Express sets this header by default: "X-Powered-By: Express"
// CWE-200 | A05:2021 — reveals server technology stack
// Missing: app.disable('x-powered-by');
// ----------------------------------------------------------------

// Simple in-memory user store for demonstration
const users = {
  1: { id: 1, email: 'alice@example.com', creditCard: '4111-1111-1111-1111', ssn: '123-45-6789' },
  2: { id: 2, email: 'bob@example.com', creditCard: '5500-0000-0000-0004', ssn: '987-65-4321' },
};

// ----------------------------------------------------------------
// ISSUE 4: Sensitive data endpoint with no Cache-Control
// User profile including PII returned without any caching directives
// CWE-524 | A04:2021 — response may be cached by browser or proxy
// ----------------------------------------------------------------
app.get('/api/user/:id', (req, res) => {
  const user = users[req.params.id];
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  // No Cache-Control, Pragma, or Expires headers — sensitive data cacheable
  res.json(user);
});

// ----------------------------------------------------------------
// ISSUE 5: Financial data endpoint with no Cache-Control or CORS restriction
// CWE-524, CWE-942 | A04:2021, A05:2021
// ----------------------------------------------------------------
app.get('/api/user/:id/payment', (req, res) => {
  const user = users[req.params.id];
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  // Payment data with no cache prevention and no origin restriction
  res.json({ creditCard: user.creditCard });
});

// ----------------------------------------------------------------
// ISSUE 6: No Content-Security-Policy set anywhere
// The HTML response below has inline scripts that would be blocked by a proper CSP
// but there is no CSP at all, so XSS has unrestricted execution
// CWE-693 | A05:2021
// ----------------------------------------------------------------
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head><title>Example App</title></head>
      <body>
        <h1>Welcome</h1>
        <!-- No Content-Security-Policy in response headers -->
        <!-- Inline script runs freely — XSS amplification risk -->
        <script>
          const user = "${req.query.name || 'guest'}";
          document.write("Hello, " + user);
        </script>
      </body>
    </html>
  `);
  // Response headers sent:
  //   X-Powered-By: Express           (info disclosure)
  //   (no Content-Security-Policy)    (missing)
  //   (no X-Content-Type-Options)     (missing)
  //   (no X-Frame-Options)            (missing)
  //   (no Strict-Transport-Security)  (missing)
  //   (no Referrer-Policy)            (missing)
});

// ----------------------------------------------------------------
// ISSUE 7: Manual CORS header setting with wildcard on a specific route
// Duplicates the global cors() misconfiguration for clarity
// CWE-942 | A05:2021
// ----------------------------------------------------------------
app.get('/api/public/data', (req, res) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Credentials', 'true'); // DANGEROUS: wildcard + credentials
  res.json({ data: 'public information' });
});

// ----------------------------------------------------------------
// ISSUE 8: No rate limiting headers (X-RateLimit-*) on authentication endpoint
// Not a header security issue per CWE but aids credential stuffing attacks
// ----------------------------------------------------------------
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  // No rate limiting, no CSRF protection headers
  const user = Object.values(users).find(u => u.email === email);
  if (user && password === 'password123') {
    res.json({ token: 'fake-jwt-token-' + user.id });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
