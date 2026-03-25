"""Fixture: Hardcoded cryptographic keys and IVs.

Triggers: Check 2 (CWE-321), Check 7 (CWE-329)
"""

from Crypto.Cipher import AES
import base64

# CWE-321: Hardcoded AES key (Check 2 - Hardcoded Key)
AES_KEY = b'SuperSecretKey16'

# CWE-329: Static IV reused across all operations (Check 7 - IV Reuse)
STATIC_IV = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'


def pad(data):
    """PKCS7 padding."""
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)


def encrypt(plaintext):
    """Encrypt using hardcoded key and static IV."""
    # CWE-321, CWE-329: Both key and IV are constants
    cipher = AES.new(AES_KEY, AES.MODE_CBC, STATIC_IV)
    padded = pad(plaintext.encode('utf-8'))
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt(ciphertext_b64):
    """Decrypt using hardcoded key and static IV."""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, STATIC_IV)
    ciphertext = base64.b64decode(ciphertext_b64)
    padded = cipher.decrypt(ciphertext)
    pad_len = padded[-1]
    return padded[:-pad_len].decode('utf-8')
