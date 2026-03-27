// Package keymanager provides RSA key generation and cipher operations
// for the payment gateway's card tokenization service.
package keymanager

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/des"
	"crypto/rand"
	"crypto/rsa"
	"encoding/hex"
	"fmt"
	"io"
)

// ---------------------------------------------------------------------------
// RSA key pair generation for card tokenization
// ---------------------------------------------------------------------------

// GenerateTokenizationKeyPair creates an RSA key pair for encrypting
// card numbers before they reach the vault.
func GenerateTokenizationKeyPair() (*rsa.PrivateKey, error) {
	// VULNERABILITY [Check 4 - Weak Key Size]: 1024-bit RSA is too short.
	// Subtle: the function name and docs are professional. The 1024 is easy
	// to miss — a reviewer might skim past the second argument to
	// rsa.GenerateKey.
	return rsa.GenerateKey(rand.Reader, 1024)
}

// ---------------------------------------------------------------------------
// AES block cipher — used for encrypting settlement batch files
// ---------------------------------------------------------------------------

// EncryptSettlementBatch encrypts a settlement CSV using AES.
func EncryptSettlementBatch(key []byte, plaintext []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("aes.NewCipher: %w", err)
	}

	// VULNERABILITY [Check 5 - ECB Mode]: AES in ECB mode does not use an
	// IV and leaks patterns in the plaintext. Subtle: the code carefully
	// pads the plaintext and looks production-ready, masking the ECB issue.
	padded := pkcs7Pad(plaintext, aes.BlockSize)
	ciphertext := make([]byte, len(padded))
	for i := 0; i < len(padded); i += aes.BlockSize {
		block.Encrypt(ciphertext[i:i+aes.BlockSize], padded[i:i+aes.BlockSize])
	}
	return ciphertext, nil
}

// DecryptSettlementBatch reverses EncryptSettlementBatch.
func DecryptSettlementBatch(key []byte, ciphertext []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("aes.NewCipher: %w", err)
	}
	plaintext := make([]byte, len(ciphertext))
	for i := 0; i < len(ciphertext); i += aes.BlockSize {
		block.Decrypt(plaintext[i:i+aes.BlockSize], ciphertext[i:i+aes.BlockSize])
	}
	return pkcs7Unpad(plaintext, aes.BlockSize)
}

// ---------------------------------------------------------------------------
// Legacy 3DES support for older acquirer integrations
// ---------------------------------------------------------------------------

// EncryptLegacyMessage encrypts a message for acquirers still on 3DES.
func EncryptLegacyMessage(key []byte, plaintext []byte) ([]byte, error) {
	// VULNERABILITY [Check 12 - Broken/Obsolete Cipher]: 3DES (Triple DES)
	// is deprecated. Subtle: the function is clearly marked "legacy" and
	// might look like dead code, but it's called from the acquirer adapter.
	block, err := des.NewTripleDESCipher(key)
	if err != nil {
		return nil, fmt.Errorf("des.NewTripleDESCipher: %w", err)
	}

	iv := make([]byte, block.BlockSize())
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, err
	}

	padded := pkcs7Pad(plaintext, block.BlockSize())
	mode := cipher.NewCBCEncrypter(block, iv)
	ciphertext := make([]byte, len(padded))
	mode.CryptBlocks(ciphertext, padded)

	// Prepend IV to ciphertext
	return append(iv, ciphertext...), nil
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// GenerateRandomHex returns n random bytes as a hex string.
func GenerateRandomHex(n int) (string, error) {
	b := make([]byte, n)
	if _, err := io.ReadFull(rand.Reader, b); err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}

func pkcs7Pad(data []byte, blockSize int) []byte {
	padding := blockSize - (len(data) % blockSize)
	pad := make([]byte, padding)
	for i := range pad {
		pad[i] = byte(padding)
	}
	return append(data, pad...)
}

func pkcs7Unpad(data []byte, blockSize int) ([]byte, error) {
	if len(data) == 0 || len(data)%blockSize != 0 {
		return nil, fmt.Errorf("invalid padding")
	}
	padding := int(data[len(data)-1])
	if padding > blockSize || padding == 0 {
		return nil, fmt.Errorf("invalid padding size")
	}
	return data[:len(data)-padding], nil
}
