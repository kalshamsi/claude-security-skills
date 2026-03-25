// Fixture: AES in ECB mode with weak key size and MD5 hashing
// Triggers: Check 5 (CWE-327), Check 1 (CWE-328), Check 4 (CWE-326)

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;
import java.util.Base64;

public class InsecureCrypto {

    // CWE-326: 128-bit key is minimum; should use 256-bit (Check 4 - Weak Key Size)
    private static final byte[] KEY = "ShortKey12345678".getBytes();

    // CWE-327: AES in ECB mode leaks patterns (Check 5 - AES ECB)
    public static String encrypt(String plaintext) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(KEY, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);
        byte[] encrypted = cipher.doFinal(plaintext.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encrypted);
    }

    // CWE-327: ECB mode decryption (Check 5)
    public static String decrypt(String ciphertext) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(KEY, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, keySpec);
        byte[] decoded = Base64.getDecoder().decode(ciphertext);
        return new String(cipher.doFinal(decoded), "UTF-8");
    }

    // CWE-328: MD5 for hashing (Check 1 - Weak Hash)
    public static String hashData(String data) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(data.getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
