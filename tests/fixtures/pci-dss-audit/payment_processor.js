const crypto = require('crypto');
const express = require('express');
const router = express.Router();

// Simulated database and payment gateway
const db = require('./db');
const gateway = require('./payment-gateway');

// --- Check 1: PAN Logged in Plaintext (CWE-532, PCI-DSS Req 3.4, 10.3) ---
// Subtle: PAN is logged inside a generic error handler, not a direct console.log
// Developer added error logging for debugging but didn't realize card data flows through it
router.post('/api/checkout', async (req, res) => {
  const { cardNumber, cvv, expiry, amount, userId } = req.body;

  try {
    const token = await tokenizeCard(cardNumber);
    const result = await gateway.charge(token, amount);
    res.json({ transactionId: result.id, status: 'success' });
  } catch (error) {
    // Generic error handler logs the full request context for debugging
    // The card number is in req.body and gets stringified into the log
    console.error('Payment failed:', {
      endpoint: '/api/checkout',
      userId,
      requestBody: req.body,  // <-- Full PAN, CVV logged here
      error: error.message,
      timestamp: new Date().toISOString()
    });
    res.status(500).json({ error: 'Payment processing failed' });
  }
});

// --- Check 2: Cardholder Data in URL Parameters (CWE-598, PCI-DSS Req 4.2) ---
// Subtle: card data is in a redirect URL for 3D Secure verification
// Developer thought HTTPS makes URL params safe (it doesn't — they're logged by proxies/servers)
router.get('/api/verify-card', (req, res) => {
  const { cardNumber, expiry, returnUrl } = req.query;

  // 3D Secure verification redirect — card data in URL will be logged by
  // reverse proxies, CDNs, browser history, and referrer headers
  const verificationUrl = `https://3dsecure.example.com/verify?pan=${cardNumber}&exp=${expiry}&merchant=acme&return=${returnUrl}`;

  res.redirect(302, verificationUrl);
});

// --- Check 3: Weak Encryption of Stored Card Data (CWE-327, PCI-DSS Req 3.5) ---
// Subtle: Uses AES (sounds right!) but in ECB mode (completely wrong)
// Developer chose AES thinking "AES = secure" but picked the wrong mode
function tokenizeCard(cardNumber) {
  // AES-ECB mode — identical plaintext blocks produce identical ciphertext blocks
  // An attacker can detect patterns and potentially recover card numbers
  // ECB is the default when no mode is specified in many crypto libraries
  const key = Buffer.from(process.env.CARD_ENCRYPTION_KEY || 'default-key-for-development-only', 'utf8').slice(0, 16);
  const cipher = crypto.createCipheriv('aes-128-ecb', key, null);
  let encrypted = cipher.update(cardNumber, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

// --- Check 4: Missing Audit Trail for Payment Operations (CWE-778, PCI-DSS Req 10.2) ---
// Subtle: audit logging EXISTS but only logs success, not the operation details
// PCI requires WHO did WHAT to WHICH data WHEN — this only logs that "something happened"
router.post('/api/refund', async (req, res) => {
  const { transactionId, amount, reason } = req.body;

  const result = await gateway.refund(transactionId, amount);

  // Insufficient audit trail — missing: user ID, IP address, card reference,
  // before/after state, and the log goes to console (no tamper-proof storage)
  console.log('Refund processed:', result.success);

  res.json({ refundId: result.id, status: result.success ? 'refunded' : 'failed' });
});

// --- Check 8: CVV/CVC Stored After Authorization (CWE-257, PCI-DSS Req 3.2) ---
// Subtle: CVV is stored in session "temporarily" for multi-step checkout
// PCI prohibits storing CVV after authorization, even encrypted, even "temporarily"
router.post('/api/checkout/step1', (req, res) => {
  const { cardNumber, cvv, expiry } = req.body;

  // "Temporary" session storage of CVV for the multi-step checkout flow
  // Developer thought session storage is OK since it's "not the database"
  req.session.checkoutData = {
    maskedCard: `****${cardNumber.slice(-4)}`,
    cvv: cvv,  // <-- PCI violation: CVV must NEVER be stored post-auth
    expiry: expiry,
    step: 1
  };

  res.json({ step: 1, status: 'card_saved', maskedCard: `****${cardNumber.slice(-4)}` });
});

router.post('/api/checkout/step2', async (req, res) => {
  const { amount, shippingAddress } = req.body;
  const checkoutData = req.session.checkoutData;

  if (!checkoutData || !checkoutData.cvv) {
    return res.status(400).json({ error: 'Start checkout from step 1' });
  }

  // Uses stored CVV from session to complete the charge
  const result = await gateway.charge({
    card: checkoutData.maskedCard,
    cvv: checkoutData.cvv,
    expiry: checkoutData.expiry,
    amount
  });

  // CVV remains in session even after authorization completes
  res.json({ transactionId: result.id, status: 'charged' });
});

module.exports = router;
