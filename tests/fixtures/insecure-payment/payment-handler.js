/**
 * Payment Handler — Deliberately insecure for PCI-DSS audit testing.
 *
 * Violations:
 *   - PAN logged in plaintext (CWE-532 / Req 3.4)
 *   - Card data in URL parameters (CWE-598 / Req 4.2)
 *   - Weak "encryption" with Base64/MD5 (CWE-327 / Req 3.5)
 *   - No audit trail on payment operations (CWE-778 / Req 10.2)
 *   - Hardcoded gateway credentials (CWE-798 / Req 8.6)
 *   - No input validation on card numbers (CWE-20 / Req 6.2)
 */

const express = require('express');
const crypto = require('crypto');
const fetch = require('node-fetch');
const router = express.Router();

// VIOLATION: Hardcoded payment gateway credentials (CWE-798)
const STRIPE_SECRET_KEY = 'HARDCODED_STRIPE_KEY_DO_NOT_USE';
const MERCHANT_ID = 'merchant_prod_98765';
const GATEWAY_PASSWORD = 'GatewayP@ss2024!';

// VIOLATION: No authentication middleware on payment routes (CWE-862)
router.post('/api/payments/charge', async (req, res) => {
  const { cardNumber, cvv, expiry, amount } = req.body;

  // VIOLATION: No input validation on card number (CWE-20)
  // Accepts any string — no format check, no Luhn validation

  // VIOLATION: Full PAN logged in plaintext (CWE-532)
  console.log(`Processing payment: card=${cardNumber}, cvv=${cvv}, amount=${amount}`);
  console.log('Card details received: ' + JSON.stringify({ cardNumber, cvv, expiry }));

  try {
    // VIOLATION: Weak "encryption" — Base64 is encoding, not encryption (CWE-327)
    const encodedCard = Buffer.from(cardNumber).toString('base64');

    // VIOLATION: MD5 hash of card — trivially reversible for 16-digit space (CWE-327)
    const cardHash = crypto.createHash('md5').update(cardNumber).digest('hex');

    // VIOLATION: No audit trail — no structured logging of who, what, when (CWE-778)
    const result = await chargeGateway(cardNumber, cvv, amount);

    // VIOLATION: Storing CVV alongside card data (CWE-257 / Req 3.3.2)
    await saveToDatabase({
      cardNumber: encodedCard,
      cardHash,
      cvv,
      expiry,
      amount,
      status: result.status,
    });

    res.json({ success: true, transactionId: result.id });
  } catch (err) {
    // VIOLATION: Card number in error message (CWE-209)
    res.status(500).json({
      error: `Payment failed for card ${cardNumber}: ${err.message}`,
    });
  }
});

// VIOLATION: Card data sent via URL/query parameters (CWE-598)
router.get('/api/payments/verify', async (req, res) => {
  const { cardNumber, expiry } = req.query;
  console.log(`Verifying card: ${cardNumber}`);
  const valid = cardNumber && cardNumber.length >= 13;
  res.json({ valid });
});

router.post('/api/payments/refund', async (req, res) => {
  const { transactionId, amount } = req.body;
  // VIOLATION: No audit logging for refund operation (CWE-778)
  // VIOLATION: No authorization check — anyone can issue refunds (CWE-862)
  const result = await refundGateway(transactionId, amount);
  res.json(result);
});

async function chargeGateway(cardNumber, cvv, amount) {
  // VIOLATION: HTTP instead of HTTPS for payment gateway (CWE-319)
  const response = await fetch('http://gateway.example.com/v1/charges', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
      'X-Merchant-Id': MERCHANT_ID,
    },
    body: JSON.stringify({ card: cardNumber, cvv, amount }),
  });
  return response.json();
}

async function refundGateway(transactionId, amount) {
  const response = await fetch('http://gateway.example.com/v1/refunds', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${STRIPE_SECRET_KEY}` },
    body: JSON.stringify({ transactionId, amount }),
  });
  return response.json();
}

async function saveToDatabase(record) {
  // Simulated DB save — in production this writes plaintext + CVV to the database
  global.db = global.db || [];
  global.db.push(record);
}

module.exports = router;
