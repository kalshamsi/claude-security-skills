package com.acme.mobileapp.auth

import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import android.util.Log
import java.io.File

/**
 * Authentication manager for the Acme mobile app.
 * Handles login, session management, and device security checks.
 */
class AuthManager(private val context: Context) {

    companion object {
        private const val TAG = "AuthManager"
        // --- M1: Hardcoded API key in companion object ---
        // Subtle: placed in companion object thinking Kotlin obfuscation hides it
        // Any decompiler (jadx, apktool) extracts this trivially
        private const val API_KEY = "HARDCODED_API_KEY_DO_NOT_USE_IN_PROD"
        private const val API_ENDPOINT = "https://api.acme.com/v2"
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(
        "auth_prefs", Context.MODE_PRIVATE
    )

    // --- M3: Insecure Authentication — client-side only auth check ---
    // Subtle: auth check exists but is entirely client-side (trivially bypassed with Frida)
    fun isAuthenticated(): Boolean {
        // Client-side check only — no server-side token validation
        // An attacker with a debugger can hook this method to always return true
        val token = prefs.getString("auth_token", null)
        val expiry = prefs.getLong("token_expiry", 0)
        return token != null && System.currentTimeMillis() < expiry
    }

    fun login(username: String, password: String): Boolean {
        // --- M1: Credentials stored in plain SharedPreferences ---
        // Subtle: developer used SharedPreferences instead of EncryptedSharedPreferences
        // On rooted devices, SharedPreferences XML files are world-readable
        prefs.edit().apply {
            putString("username", username)
            putString("auth_token", "mock_token_${System.currentTimeMillis()}")
            putLong("token_expiry", System.currentTimeMillis() + 3600000)
            // Storing password hash in SharedPreferences (not Keystore)
            putString("password_hash", username.hashCode().toString())
            apply()
        }

        // --- M8: Insufficient Privacy Controls — logging credentials ---
        // Subtle: uses Log.d (debug) thinking it won't appear in production
        // Android debug logs are accessible via logcat on userdebug builds
        Log.d(TAG, "User logged in: $username with token: ${prefs.getString("auth_token", "")}")

        return true
    }

    fun logout() {
        prefs.edit().clear().apply()
        Log.d(TAG, "User logged out, preferences cleared")
    }

    // --- M3: Biometric auth without server-side verification ---
    // Subtle: biometric prompt exists but success just sets a local flag
    // No cryptographic proof of biometric authentication sent to server
    fun authenticateWithBiometrics(onSuccess: () -> Unit, onFailure: () -> Unit) {
        // In a real implementation, this would use BiometricPrompt
        // Problem: success callback just sets a local boolean — no server round-trip
        // Attacker can call onSuccess() directly via reflection/Frida
        val biometricResult = checkBiometric()
        if (biometricResult) {
            prefs.edit().putBoolean("biometric_verified", true).apply()
            onSuccess()
        } else {
            onFailure()
        }
    }

    private fun checkBiometric(): Boolean {
        // Simulated biometric check — returns true for demo
        return true
    }

    // --- M10: Insufficient Binary Protections ---
    // Subtle: root detection EXISTS but only checks for 'su' binary
    // Magisk, KernelSU, and other modern root solutions hide the su binary
    fun isDeviceSecure(): Boolean {
        // Incomplete root detection — only checks one indicator
        val suPaths = listOf(
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su"
        )

        // Missing checks: Magisk manager, test-keys build, ro.debuggable,
        // /data/local/tmp writability, SELinux status, mounted /system rw
        for (path in suPaths) {
            if (File(path).exists()) {
                Log.w(TAG, "Root detected: su found at $path")
                return false
            }
        }

        return true  // Assumes device is secure if su binary not found
    }

    // --- M7: Insufficient Input Validation on deep links ---
    // Subtle: intent handling with no validation of extras
    fun handleDeepLink(action: String?, data: Map<String, String>?) {
        // Accepts any action and data from intent without validation
        // Attacker can craft intents to trigger internal functionality
        when (action) {
            "com.acme.TRANSFER" -> {
                val amount = data?.get("amount") ?: "0"
                val recipient = data?.get("recipient") ?: ""
                // No validation that this came from a legitimate source
                // No re-authentication before financial action
                initiateTransfer(amount, recipient)
            }
            "com.acme.RESET_PIN" -> {
                // PIN reset triggered via deep link without auth check
                val newPin = data?.get("pin") ?: ""
                resetUserPin(newPin)
            }
        }
    }

    private fun initiateTransfer(amount: String, recipient: String) {
        Log.d(TAG, "Transfer initiated: $amount to $recipient")
    }

    private fun resetUserPin(pin: String) {
        // Stores PIN in SharedPreferences (should be in Android Keystore)
        prefs.edit().putString("user_pin", pin).apply()
        Log.d(TAG, "PIN reset to: $pin")  // M8: logging sensitive data
    }
}
