package com.acme.payments.controller;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.io.FileInputStream;
import java.security.KeyStore;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.Base64;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

/**
 * Payment processing controller.
 * Handles card storage, charging, and TLS configuration.
 */
@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    // --- Check 5: Hardcoded Payment Gateway Credentials (CWE-798, PCI-DSS Req 2.2, 8.6) ---
    // Subtle: looks like constants/config but these are actual gateway credentials in source
    // Developer used static finals thinking "it's compiled into bytecode so it's hidden"
    private static final String GATEWAY_API_KEY = "HARDCODED_STRIPE_KEY_EXAMPLE";
    private static final String GATEWAY_SECRET = "HARDCODED_GATEWAY_SECRET_DO_NOT_USE";
    private static final String MERCHANT_ID = "merchant_acme_prod_001";

    // --- Check 6: No Input Validation on Card Numbers (CWE-20, PCI-DSS Req 6.2) ---
    // Subtle: method signature suggests validation ("processValidCard") but body has none
    @PostMapping("/charge")
    public ResponseEntity<?> processPayment(@RequestBody PaymentRequest request) {
        // No Luhn check, no length validation, no format verification
        // Method name and parameter type suggest structure but there's no actual validation
        String cardNumber = request.getCardNumber();
        String cvv = request.getCvv();
        double amount = request.getAmount();

        try {
            String encrypted = encryptCardData(cardNumber);
            saveCardToDatabase(request.getUserId(), encrypted, request.getExpiry());
            // ... charge logic ...
            return ResponseEntity.ok().body(new PaymentResponse("success", "txn_" + System.currentTimeMillis()));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(new ErrorResponse("Payment failed"));
        }
    }

    // --- Check 7: Cardholder Data Stored Without Proper Encryption (CWE-312, PCI-DSS Req 3.4) ---
    // Subtle: encryption method EXISTS and uses AES — but stores the key alongside the data
    // and uses a fixed IV (initialization vector), making it effectively deterministic
    private String encryptCardData(String cardNumber) throws Exception {
        // Fixed key derived from hardcoded string — same key for all cards
        byte[] keyBytes = "AcmePaymentKey16".getBytes("UTF-8");  // 16 bytes = AES-128
        SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");

        // AES/ECB/PKCS5Padding — no IV, deterministic encryption
        // Identical card numbers produce identical ciphertext
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);
        byte[] encrypted = cipher.doFinal(cardNumber.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encrypted);
    }

    private void saveCardToDatabase(long userId, String encryptedCard, String expiry) throws Exception {
        // Card data goes to DB — the encryption above is weak (ECB mode, hardcoded key)
        Connection conn = DriverManager.getConnection(
            "jdbc:postgresql://localhost:5432/payments", "app_user", "app_password"
        );
        PreparedStatement stmt = conn.prepareStatement(
            "INSERT INTO stored_cards (user_id, encrypted_card, expiry, created_at) VALUES (?, ?, ?, NOW())"
        );
        stmt.setLong(1, userId);
        stmt.setString(2, encryptedCard);
        stmt.setString(3, expiry);
        stmt.executeUpdate();
        conn.close();
    }

    // --- Check 11: Insecure Cryptographic Key Storage (CWE-321, PCI-DSS Req 3.6) ---
    // Subtle: DOES use a KeyStore (correct approach!) but with the default password 'changeit'
    // and loads from a predictable filesystem path without integrity verification
    private KeyStore loadPaymentKeyStore() throws Exception {
        KeyStore keyStore = KeyStore.getInstance("JKS");
        // Default password 'changeit' — never changed from Java's default
        // Stored in a predictable path without file permission restrictions
        FileInputStream fis = new FileInputStream("/opt/acme/payment-keys.jks");
        keyStore.load(fis, "changeit".toCharArray());
        fis.close();
        return keyStore;
    }

    // --- Check 12: Missing TLS Enforcement / Weak TLS (CWE-326, PCI-DSS Req 4.1) ---
    // Subtle: TLS IS configured (not missing!) but allows TLSv1.0 and TLSv1.1
    // PCI-DSS v4.0 requires TLSv1.2 minimum for cardholder data transmission
    private SSLContext createPaymentSSLContext() throws Exception {
        KeyStore trustStore = loadPaymentKeyStore();
        TrustManagerFactory tmf = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm()
        );
        tmf.init(trustStore);

        // Allows TLSv1.0 — which has known vulnerabilities (BEAST, POODLE)
        // PCI-DSS v4.0 requires TLSv1.2 as minimum
        SSLContext sslContext = SSLContext.getInstance("TLS");  // <-- Allows TLSv1.0, 1.1
        sslContext.init(null, tmf.getTrustManagers(), null);
        return sslContext;
        // Should be: SSLContext.getInstance("TLSv1.2") or "TLSv1.3"
    }

    // Simple DTOs
    static class PaymentRequest {
        private String cardNumber;
        private String cvv;
        private String expiry;
        private double amount;
        private long userId;
        public String getCardNumber() { return cardNumber; }
        public String getCvv() { return cvv; }
        public String getExpiry() { return expiry; }
        public double getAmount() { return amount; }
        public long getUserId() { return userId; }
    }

    static class PaymentResponse {
        private String status;
        private String transactionId;
        public PaymentResponse(String status, String transactionId) {
            this.status = status;
            this.transactionId = transactionId;
        }
        public String getStatus() { return status; }
        public String getTransactionId() { return transactionId; }
    }

    static class ErrorResponse {
        private String error;
        public ErrorResponse(String error) { this.error = error; }
        public String getError() { return error; }
    }
}
