import os
import hashlib
import hmac
import logging
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)
logger = logging.getLogger(__name__)

# --- Check 9: Weak Tokenization (predictable HMAC with static key) ---
# Subtle: Uses HMAC (sounds secure!) but the key is hardcoded in source code
# and the token is deterministic — same card always produces same token
TOKENIZATION_SECRET = "hmac-signing-key-for-card-tokens"  # <-- Static key in source


def tokenize_card(card_number: str) -> str:
    """Generate a 'secure' token for a card number.

    Problem: deterministic HMAC with a static key means:
    1. Same card number always produces the same token (no randomness)
    2. An attacker with the source code can reverse-engineer tokens
    3. Token collision = card number collision (breaks unlinkability)
    """
    return hmac.new(
        TOKENIZATION_SECRET.encode(),
        card_number.encode(),
        hashlib.sha256
    ).hexdigest()


# --- Check 10: No Key Rotation Mechanism ---
# Subtle: encryption key loading exists but there's no rotation, versioning, or expiry
# PCI-DSS Req 3.6 requires key management including rotation
class CardEncryption:
    """Handles card data encryption.

    Problem: Single static key with no rotation mechanism.
    PCI requires: key versioning, periodic rotation, split knowledge,
    and documented key management procedures.
    """

    def __init__(self):
        # Key loaded from env (good!) but never rotated (bad!)
        # No key version tracking, no rotation schedule, no split knowledge
        self._key = os.environ.get('CARD_KEY', 'fallback-dev-key-not-for-prod')
        # No key creation date, no expiry, no rotation check

    def encrypt(self, card_number: str) -> str:
        """Encrypt a card number. No key version is stored with the ciphertext,
        making future key rotation impossible without re-encrypting everything."""
        h = hashlib.sha256(self._key.encode() + card_number.encode()).hexdigest()
        return h  # This is a hash, not reversible encryption — can't decrypt for display


card_encryption = CardEncryption()


# --- Check 6 variant: Minimal Input Validation ---
# Subtle: validation exists but is too permissive (allows non-numeric, wrong lengths)
@app.route('/api/billing/add-card', methods=['POST'])
def add_card():
    data = request.get_json()
    card_number = data.get('card_number', '')

    # "Validation" that's too loose — only checks it's not empty
    # No Luhn check, no length validation, no format check
    if not card_number or len(card_number) < 8:
        return jsonify({'error': 'Invalid card number'}), 400

    token = tokenize_card(card_number)

    # Store token (good!) but no audit trail of who added it (bad — Check 4 overlap)
    return jsonify({'token': token, 'last_four': card_number[-4:]})


# --- Card Data in Error Messages (CWE-209, PCI-DSS Req 6.2) ---
# Subtle: error handler returns card data in the error response to the client
# Developer included debug info to help users troubleshoot payment failures
@app.route('/api/billing/charge', methods=['POST'])
def charge_recurring():
    data = request.get_json()
    card_number = data.get('card_number', '')
    amount = data.get('amount', 0)

    try:
        # Process payment...
        if amount <= 0:
            raise ValueError("Invalid amount")

        token = tokenize_card(card_number)
        # ... gateway charge logic would go here ...
        return jsonify({'status': 'charged', 'token': token})

    except Exception as e:
        # Error response includes the card number for "debugging"
        # This exposes PAN data to the client and any monitoring/logging system
        return jsonify({
            'error': 'Payment failed',
            'details': {
                'card': card_number,  # <-- Full PAN in error response
                'amount': amount,
                'reason': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 400


# --- Overly Broad Database Permissions ---
# Subtle: connection string uses a superuser account for the app
# PCI-DSS Req 7.1 requires least-privilege access
DB_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/payments'  # <-- superuser 'postgres'
)
# The app connects as 'postgres' (superuser) instead of a restricted app-specific user
# This violates least-privilege: the app can DROP tables, access other schemas, etc.
engine = create_engine(DB_URL)


# --- Missing MFA Check Before Card Display ---
# Subtle: displays saved cards without requiring step-up authentication
# PCI-DSS Req 8.4 requires MFA for non-console administrative access
@app.route('/api/billing/cards', methods=['GET'])
def list_saved_cards():
    user_id = request.headers.get('X-User-Id')

    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    # No MFA/step-up authentication before showing saved card data
    # User just needs a valid session — no re-authentication or 2FA challenge
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT token, last_four, expiry FROM saved_cards WHERE user_id = :uid"),
            {'uid': user_id}
        )
        cards = [dict(row._mapping) for row in result]

    return jsonify({'cards': cards})


if __name__ == '__main__':
    app.run(debug=False, port=5001)
