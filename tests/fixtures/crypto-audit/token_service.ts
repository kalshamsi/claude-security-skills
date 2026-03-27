/**
 * Token service for payment gateway SDK.
 * Handles JWT creation, encryption, and webhook signature verification.
 */

import crypto from "crypto";

// ---------------------------------------------------------------------------
// AES encryption for PII fields in transit
// ---------------------------------------------------------------------------

const ALGORITHM = "aes-256-cbc";

class TokenEncryptor {
  private key: Buffer;
  private iv: Buffer;

  constructor(key: string) {
    this.key = Buffer.from(key, "hex");
    // VULNERABILITY [Check 7 - Static IV]: IV is derived once in the
    // constructor and reused for every encrypt() call. Subtle: it's not a
    // hardcoded literal — it's derived from the key, which *looks* reasonable
    // but produces the same IV every time for the same key.
    this.iv = crypto
      .createHash("md5")
      .update(key)
      .digest();
  }

  encrypt(plaintext: string): string {
    const cipher = crypto.createCipheriv(ALGORITHM, this.key, this.iv);
    let encrypted = cipher.update(plaintext, "utf8", "hex");
    encrypted += cipher.final("hex");
    return encrypted;
  }

  decrypt(ciphertext: string): string {
    const decipher = crypto.createDecipheriv(ALGORITHM, this.key, this.iv);
    let decrypted = decipher.update(ciphertext, "hex", "utf8");
    decrypted += decipher.final("utf8");
    return decrypted;
  }
}

// ---------------------------------------------------------------------------
// Webhook signature verification
// ---------------------------------------------------------------------------

function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expected = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");

  // VULNERABILITY [Check 9 - Timing Attack]: Direct string comparison of
  // HMAC digests is vulnerable to timing side-channels. Should use
  // crypto.timingSafeEqual(). Subtle: the HMAC itself is correct — only the
  // comparison is flawed.
  return expected === signature;
}

// ---------------------------------------------------------------------------
// TLS configuration for outbound gateway connections
// ---------------------------------------------------------------------------

interface TlsOptions {
  minVersion: string;
  maxVersion: string;
  ciphers: string;
}

function getGatewayTlsOptions(): TlsOptions {
  // VULNERABILITY [Check 10 - Deprecated TLS]: Allows TLS 1.0 as minimum.
  // Subtle: maxVersion is fine (TLSv1.3), and the ciphers string looks
  // restrictive. The issue is only the minVersion.
  return {
    minVersion: "TLSv1",
    maxVersion: "TLSv1.3",
    ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384",
  };
}

// ---------------------------------------------------------------------------
// HMAC generation (no verification flaw here — this is the "safe" side)
// ---------------------------------------------------------------------------

function signPayload(payload: string, secret: string): string {
  return crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");
}

export { TokenEncryptor, verifyWebhookSignature, getGatewayTlsOptions, signPayload };
