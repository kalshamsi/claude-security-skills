/**
 * Deliberately insecure Express.js API server for testing api-security-tester skill.
 *
 * Vulnerabilities:
 *   - BOLA: no ownership checks on resource endpoints
 *   - Broken auth: missing auth middleware on sensitive endpoints
 *   - Excessive data exposure: returns full user objects (including passwords)
 *   - No rate limiting on any endpoint
 *   - Mass assignment: spreads req.body directly into DB update
 *   - SSRF: fetches arbitrary user-supplied URLs
 *   - Missing authorization on admin endpoints
 *   - Permissive CORS and verbose error messages
 */

const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json({ limit: '500mb' })); // Dangerously large body limit

// VULN [API8]: Permissive CORS — allows all origins
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', '*');
  res.setHeader('Access-Control-Allow-Headers', '*');
  next();
});

// Fake in-memory database
const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com', password: 'hashed_s3cret', role: 'user', ssn: '123-45-6789' },
  { id: 2, name: 'Bob', email: 'bob@example.com', password: 'hashed_p@ss', role: 'admin', ssn: '987-65-4321' },
];
const orders = [
  { id: 101, userId: 1, product: 'Widget', total: 29.99 },
  { id: 102, userId: 2, product: 'Gadget', total: 49.99 },
];

// Minimal "auth" that just reads a header — no real verification
function fakeAuth(req, res, next) {
  const userId = parseInt(req.headers['x-user-id']);
  req.user = users.find((u) => u.id === userId) || null;
  next(); // Continues even if user is null
}

// VULN [API1]: BOLA — no ownership check
app.get('/api/orders/:orderId', fakeAuth, (req, res) => {
  const order = orders.find((o) => o.id === parseInt(req.params.orderId));
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order); // Any user can access any order
});

// VULN [API3]: Excessive data exposure — returns password, SSN, role
app.get('/api/users/:id', fakeAuth, (req, res) => {
  const user = users.find((u) => u.id === parseInt(req.params.id));
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user); // Full object with password, ssn, role
});

// VULN [API3]: Mass assignment — spreads all body fields
app.put('/api/users/:id', fakeAuth, (req, res) => {
  const idx = users.findIndex((u) => u.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  users[idx] = { ...users[idx], ...req.body }; // Attacker can set role: "admin"
  res.json(users[idx]);
});

// VULN [API4]: No pagination — returns all records
app.get('/api/users', fakeAuth, (req, res) => {
  res.json(users); // Unbounded, returns everything
});

// VULN [API2 + API5]: No auth at all on admin endpoint
app.delete('/api/admin/users/:id', (req, res) => {
  const idx = users.findIndex((u) => u.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  users.splice(idx, 1);
  res.json({ status: 'deleted' });
});

// VULN [API5]: Admin settings — no role check
app.post('/api/admin/settings', fakeAuth, (req, res) => {
  res.json({ status: 'updated', settings: req.body });
});

// VULN [API7]: SSRF — fetches any user-supplied URL
app.post('/api/fetch-url', fakeAuth, async (req, res) => {
  try {
    const response = await axios.get(req.body.url);
    res.json({ data: response.data });
  } catch (err) {
    res.status(500).json({ error: err.message, stack: err.stack }); // Also leaks stack
  }
});

// VULN [API9]: Debug endpoint left in production
app.get('/api/debug/env', (req, res) => {
  res.json(process.env);
});

// VULN [API8]: Verbose error handler leaking internals
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    path: req.originalUrl,
  });
});

const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => console.log(`Insecure API running on port ${PORT}`));
}

module.exports = app;
