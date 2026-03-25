// Fixture: Insecure random number generation
// Triggers: Check 3 (CWE-330)

import crypto from 'crypto';

// CWE-330: Math.random() for session tokens (Check 3 - Insecure Random)
function generateSessionToken(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let token = '';
  for (let i = 0; i < 32; i++) {
    token += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return token;
}

// CWE-330: Math.random() for OTP codes (Check 3 - Insecure Random)
function generateOTP(): string {
  const otp = Math.floor(Math.random() * 1000000);
  return otp.toString().padStart(6, '0');
}

// CWE-330: Date.now() for password reset token (Check 3 - Insecure Random)
function generateResetToken(userId: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 10);
  return `${userId}-${timestamp}-${random}`;
}

// CORRECT: crypto.randomBytes() for secure token generation
function generateSecureToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

export { generateSessionToken, generateOTP, generateResetToken, generateSecureToken };
