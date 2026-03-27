# mobile-security Test Fixture

Multi-platform mobile application code with subtle security vulnerabilities for testing the mobile-security skill across all 4 supported platforms.

## Files

- `App.tsx` — React Native application (JavaScript/TypeScript)
- `AuthManager.kt` — Android authentication manager (Kotlin)
- `DataManager.swift` — iOS data and auth manager (Swift)
- `config_service.dart` — Flutter configuration and HTTP service (Dart)

## Planted Vulnerabilities by OWASP Mobile Top 10:2024

### M1: Improper Credential Usage
- **App.tsx:** `SecureStore` class wraps AsyncStorage (unencrypted) — name implies security, implementation doesn't deliver
- **AuthManager.kt:** API key hardcoded in companion object; credentials in plain SharedPreferences
- **DataManager.swift:** Hardcoded API keys in Config struct; credentials in UserDefaults
- **config_service.dart:** All API keys hardcoded in AppConfig static class

### M2: Inadequate Supply Chain Security
- **config_service.dart:** References unvetted dependencies with wildcard versions and git sources

### M3: Insecure Authentication/Authorization
- **AuthManager.kt:** Client-side-only auth check (bypassable with Frida); biometric auth sets local flag only
- **DataManager.swift:** Biometric auth success just writes to UserDefaults — no server-side verification

### M4: Insufficient Input/Output Validation
- **App.tsx:** WebView URL check uses `startsWith` (bypassable with `trusted.com.evil.com`); `allowFileAccess` enabled; mixed content allowed; JavaScript bridge exposed

### M5: Insecure Communication
- **App.tsx:** No certificate pinning on fetch calls
- **DataManager.swift:** Disabled ATS; no cert pinning on URLSession
- **config_service.dart:** `initSecureHttp()` method DISABLES certificate verification entirely

### M7: Insufficient Binary Protections
- **App.tsx:** Deep link handler accepts arbitrary screen navigation without validation
- **AuthManager.kt:** Deep link intent handler triggers transfers and PIN resets without re-authentication

### M8: Insufficient Privacy Controls
- **AuthManager.kt:** Log.d logs credentials and tokens (accessible via logcat)
- **config_service.dart:** AppLogger sends full context including auth tokens to analytics service; kDebugMode check is insufficient

### M9: Insecure Data Storage
- **App.tsx:** Financial account data cached in unencrypted AsyncStorage
- **DataManager.swift:** Sensitive data in UserDefaults (unencrypted plist); account cache written without file protection attributes; NSLog for sensitive operations

### M10: Insufficient Binary Protections
- **AuthManager.kt:** Root detection only checks for `su` binary — misses Magisk, KernelSU, test-keys
- **DataManager.swift:** Jailbreak detection checks file paths only — bypassable by hooking NSFileManager or using rootless jailbreaks

## What Makes These Subtle

All vulnerabilities follow the "tried-but-failed" pattern:
- `SecureStore` wrapper that just delegates to AsyncStorage (name implies security)
- `initSecureHttp()` that actually disables certificate verification (method name lies)
- Root/jailbreak detection that exists but is trivially bypassable (incomplete checks)
- Biometric authentication that doesn't verify server-side (client-only)
- URL validation using `startsWith` instead of proper domain parsing (bypassable)
- Debug logging wrapped in `kDebugMode` check (insufficient for privacy)
