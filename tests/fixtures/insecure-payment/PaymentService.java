package com.example.payment;

import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

/**
 * PaymentService — Deliberately insecure for PCI-DSS audit testing.
 *
 * Violations:
 *   - Card data stored in plaintext in database (CWE-312 / Req 3.4)
 *   - No access control on payment endpoints (CWE-862 / Req 7.2)
 *   - Insufficient logging (CWE-778 / Req 10.2)
 *   - Weak cryptography for card data (CWE-327 / Req 3.5)
 *   - Card numbers in error messages (CWE-209 / Req 6.2)
 *   - Missing session management (CWE-384 / Req 8.3)
 */
public class PaymentService {

    // VIOLATION: Hardcoded database credentials (CWE-798)
    private static final String DB_URL = "jdbc:mysql://prod-db:3306/payments";
    private static final String DB_USER = "payment_admin";
    private static final String DB_PASS = "Pr0d_Passw0rd!";

    // VIOLATION: Hardcoded encryption key — weak DES key (CWE-321, CWE-327)
    private static final String ENCRYPTION_KEY = "WeakKey8";

    // VIOLATION: No access control — any caller can invoke this (CWE-862)
    public String processPayment(String cardNumber, String cvv, String expiry, double amount) {
        // VIOLATION: No input validation on card number (CWE-20)

        // VIOLATION: Full PAN logged in plaintext (CWE-532)
        System.out.println("Processing payment for card: " + cardNumber + ", CVV: " + cvv);

        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);

            // VIOLATION: Weak DES encryption for card data (CWE-327 / Req 3.5)
            String encryptedCard = weakEncrypt(cardNumber);

            // VIOLATION: Storing CVV in database post-authorization (CWE-257 / Req 3.3.2)
            // VIOLATION: Plaintext card data fields in database (CWE-312 / Req 3.4)
            PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO transactions (card_number, card_encrypted, cvv, expiry, amount, status) " +
                "VALUES (?, ?, ?, ?, ?, ?)"
            );
            stmt.setString(1, cardNumber);     // Plaintext PAN stored directly
            stmt.setString(2, encryptedCard);  // Weak DES "encryption"
            stmt.setString(3, cvv);            // CVV stored — PCI-DSS Req 3.3.2 violation
            stmt.setString(4, expiry);
            stmt.setDouble(5, amount);
            stmt.setString(6, "PENDING");
            stmt.executeUpdate();

            // VIOLATION: No audit logging of payment operation (CWE-778 / Req 10.2)
            // No record of who initiated this, from what IP, at what time

            conn.close();
            return "SUCCESS";

        } catch (Exception e) {
            // VIOLATION: Card number exposed in error message (CWE-209)
            throw new RuntimeException(
                "Payment failed for card " + cardNumber + ": " + e.getMessage()
            );
        }
    }

    // VIOLATION: No authentication or authorization check (CWE-862)
    public String refundPayment(String transactionId, double amount) {
        // VIOLATION: No audit logging for refund (CWE-778)
        System.out.println("Refunding transaction: " + transactionId);
        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            PreparedStatement stmt = conn.prepareStatement(
                "UPDATE transactions SET status = 'REFUNDED', refund_amount = ? WHERE id = ?"
            );
            stmt.setDouble(1, amount);
            stmt.setString(2, transactionId);
            stmt.executeUpdate();
            conn.close();
            return "REFUNDED";
        } catch (Exception e) {
            return "REFUND_FAILED: " + e.getMessage();
        }
    }

    // VIOLATION: DES cipher — 56-bit key, broken algorithm (CWE-327)
    private String weakEncrypt(String data) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(ENCRYPTION_KEY.getBytes(), "DES");
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);
        byte[] encrypted = cipher.doFinal(data.getBytes());
        return Base64.getEncoder().encodeToString(encrypted);
    }

    // VIOLATION: MD5 for card fingerprinting — trivially reversible (CWE-328)
    private String hashCard(String cardNumber) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(cardNumber.getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
