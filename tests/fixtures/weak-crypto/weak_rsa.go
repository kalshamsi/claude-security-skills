// Fixture: Weak RSA key size, disabled TLS verification, deprecated TLS version
// Triggers: Check 4 (CWE-326), Check 8 (CWE-295), Check 10 (CWE-327)

package weakcrypto

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"net/http"
)

// CWE-326: 1024-bit RSA key is factorable (Check 4 - Weak Key Size)
func GenerateWeakKey() (*rsa.PrivateKey, error) {
	key, err := rsa.GenerateKey(rand.Reader, 1024)
	if err != nil {
		return nil, fmt.Errorf("key generation failed: %w", err)
	}
	return key, nil
}

// CWE-295: Disabled TLS certificate verification (Check 8 - Improper Cert Validation)
func CreateInsecureClient() *http.Client {
	tlsConfig := &tls.Config{
		InsecureSkipVerify: true,
	}
	transport := &http.Transport{TLSClientConfig: tlsConfig}
	return &http.Client{Transport: transport}
}

// CWE-327: Deprecated TLS 1.0 (Check 10 - Deprecated TLS)
func CreateWeakTLSConfig() *tls.Config {
	return &tls.Config{
		MinVersion: tls.VersionTLS10,
		MaxVersion: tls.VersionTLS11,
	}
}

// SignData signs data with a weak RSA key
func SignData(key *rsa.PrivateKey, data []byte) ([]byte, error) {
	hashed := sha256Sum(data)
	return rsa.SignPKCS1v15(rand.Reader, key, 0, hashed)
}

func sha256Sum(data []byte) []byte {
	h := make([]byte, 32)
	copy(h, data[:min(32, len(data))])
	return h
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
