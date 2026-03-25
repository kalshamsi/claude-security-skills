// Vulnerable Express.js Application — FOR SECURITY TESTING ONLY
// Each endpoint contains a deliberate vulnerability for use with security-test-generator skill

const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// In-memory config store (simulates application state)
let appConfig = { debug: false, maintenance: false };

// --- CWE-89: SQL Injection ---
// Vulnerable: User input concatenated directly into SQL query string
// The query parameter is interpolated without parameterization
app.get('/api/users', (req, res) => {
  const search = req.query.search;
  // VULNERABLE: String concatenation in SQL query
  const query = "SELECT * FROM users WHERE name LIKE '%" + search + "%'";
  // In a real app this would execute against a database:
  // const results = db.prepare(query).all();
  res.json({ query: query, results: [] });
});

// --- CWE-79: Cross-Site Scripting (Reflected XSS) ---
// Vulnerable: User input reflected directly in HTML response without escaping
app.get('/api/profile', (req, res) => {
  const name = req.query.name;
  // VULNERABLE: Unescaped user input in HTML response
  res.send('<h1>Welcome ' + name + '</h1><p>Your profile page</p>');
});

// --- CWE-22: Path Traversal ---
// Vulnerable: User-controlled filename passed to fs.readFileSync without sanitization
app.get('/api/files', (req, res) => {
  const filename = req.query.name;
  try {
    // VULNERABLE: No path sanitization — allows ../../etc/passwd
    const content = fs.readFileSync(path.join('/uploads', filename), 'utf8');
    res.send(content);
  } catch (err) {
    res.status(404).json({ error: 'File not found' });
  }
});

// --- CWE-287: Authentication Bypass ---
// Vulnerable: Admin endpoint with no authentication middleware
app.post('/api/admin/config', (req, res) => {
  // VULNERABLE: No authentication check — any unauthenticated user can modify config
  const { setting, value } = req.body;
  appConfig[setting] = value;
  res.json({ message: 'Config updated', config: appConfig });
});

// --- CWE-352: Cross-Site Request Forgery ---
// Vulnerable: State-changing POST endpoint with no CSRF token validation
app.post('/api/transfer', (req, res) => {
  const { from, to, amount } = req.body;
  // VULNERABLE: No CSRF token check — request could be forged from another site
  // In a real app this would transfer funds between accounts
  res.json({ message: 'Transfer complete', from, to, amount });
});

module.exports = app;
