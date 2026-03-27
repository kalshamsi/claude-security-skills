const express = require('express');
const sqlite3 = require('sqlite3');
const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const { URL } = require('url');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const db = new sqlite3.Database(':memory:');

// Initialize database
db.serialize(() => {
  db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, role TEXT, password_hash TEXT)");
  db.run("CREATE TABLE profiles (id INTEGER PRIMARY KEY, user_id INTEGER, bio TEXT, avatar_url TEXT, is_admin INTEGER DEFAULT 0)");
  db.run("INSERT INTO users VALUES (1, 'admin', 'admin@example.com', 'admin', 'hashed_pw_1')");
  db.run("INSERT INTO users VALUES (2, 'alice', 'alice@example.com', 'user', 'hashed_pw_2')");
  db.run("INSERT INTO profiles VALUES (1, 1, 'System administrator', '/avatars/admin.png', 1)");
  db.run("INSERT INTO profiles VALUES (2, 2, 'Regular user', '/avatars/alice.png', 0)");
});

// --- Endpoint 1: Search users ---
// Subtle SQLi: template literal interpolation in query, not raw string concat
app.get('/api/users', (req, res) => {
  const search = req.query.search || '';
  const limit = parseInt(req.query.limit) || 20;

  // Developer thought template literals are safe because they "look modern"
  const query = `SELECT id, username, email FROM users WHERE username LIKE '%${search}%' OR email LIKE '%${search}%' LIMIT ${limit}`;

  db.all(query, (err, rows) => {
    if (err) {
      console.error('Search query failed:', err.message);
      return res.status(500).json({ error: 'Search failed' });
    }
    res.json({ results: rows, count: rows.length });
  });
});

// --- Endpoint 2: Login ---
// Subtle timing attack: uses === for token comparison instead of crypto.timingSafeEqual
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required' });
  }

  db.get("SELECT * FROM users WHERE username = ?", [username], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Hash the provided password to compare
    const providedHash = crypto.createHash('sha256').update(password).digest('hex');

    // Timing-vulnerable comparison — === leaks info via timing side channel
    // Should use crypto.timingSafeEqual(Buffer.from(providedHash), Buffer.from(user.password_hash))
    if (providedHash === user.password_hash) {
      const token = crypto.randomBytes(32).toString('hex');
      res.json({ token, userId: user.id });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  });
});

// --- Endpoint 3: File access ---
// Subtle path traversal: sanitizes ../ but only strips it once (not recursively)
app.get('/api/files/:filename', (req, res) => {
  const uploadsDir = '/var/app/uploads';
  let filename = req.params.filename;

  // Developer added sanitization, but it only strips ../ once
  // Attacker can use ....// which becomes ../ after single-pass strip
  filename = filename.replace(/\.\.\//g, '');

  const filePath = `${uploadsDir}/${filename}`;

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.json({ filename, content: data });
  });
});

// --- Endpoint 4: Update profile ---
// Subtle mass assignment: spread operator merges all body fields into DB update
app.put('/api/profile/:userId', (req, res) => {
  const userId = req.params.userId;
  const allowedFields = ['bio', 'avatar_url'];

  // Developer intended to restrict fields but used spread operator on full body
  // req.body could contain { bio: "new bio", is_admin: 1 }
  const updates = { ...req.body };

  // Build SET clause from all provided fields (including is_admin if sent)
  const setClauses = Object.keys(updates).map(key => `${key} = ?`).join(', ');
  const values = Object.values(updates);

  if (setClauses.length === 0) {
    return res.status(400).json({ error: 'No fields to update' });
  }

  db.run(
    `UPDATE profiles SET ${setClauses} WHERE user_id = ?`,
    [...values, userId],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Update failed' });
      }
      res.json({ updated: this.changes > 0 });
    }
  );
});

// --- Endpoint 5: URL proxy/fetch ---
// Subtle SSRF: validates URL scheme but doesn't block internal/private IPs
app.get('/api/proxy', (req, res) => {
  const targetUrl = req.query.url;

  if (!targetUrl) {
    return res.status(400).json({ error: 'URL parameter required' });
  }

  try {
    const parsed = new URL(targetUrl);

    // Developer added scheme validation — but forgot to block internal IPs
    // Allows http://169.254.169.254/latest/meta-data/ (AWS metadata)
    // Allows http://10.0.0.1/admin, http://localhost:8080/internal, etc.
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return res.status(400).json({ error: 'Only HTTP(S) URLs allowed' });
    }

    http.get(targetUrl, (proxyRes) => {
      let data = '';
      proxyRes.on('data', chunk => data += chunk);
      proxyRes.on('end', () => {
        res.json({ status: proxyRes.statusCode, body: data });
      });
    }).on('error', (err) => {
      res.status(502).json({ error: 'Failed to fetch URL' });
    });
  } catch (e) {
    res.status(400).json({ error: 'Invalid URL' });
  }
});

module.exports = app;
