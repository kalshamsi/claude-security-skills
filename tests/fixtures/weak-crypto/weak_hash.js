// Fixture: Weak hash algorithms for security purposes
// Triggers: Check 1 (CWE-328), Check 3 (CWE-330), Check 11 (CWE-916)

const crypto = require('crypto');

// CWE-328: MD5 used for password hashing (Check 1 - Weak Hash)
function hashPassword(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}

// CWE-328: SHA1 used for token generation (Check 1 - Weak Hash)
function generateAuthToken(userId) {
  return crypto.createHash('sha1').update(userId + Date.now()).digest('hex');
}

// CWE-330: Math.random() for session ID (Check 3 - Insecure Random)
function generateSessionId() {
  return Math.random().toString(36).substring(2) +
         Math.random().toString(36).substring(2);
}

// CWE-916: SHA-256 for password storage without salt/stretching (Check 11)
function storePassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

// Usage
const hash = hashPassword('user-password');
const token = generateAuthToken('user-123');
const session = generateSessionId();
const stored = storePassword('admin-pass');

module.exports = { hashPassword, generateAuthToken, generateSessionId, storePassword };
