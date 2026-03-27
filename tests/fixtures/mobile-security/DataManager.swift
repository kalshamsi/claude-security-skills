import Foundation
import LocalAuthentication
import Security

/// Manages user data, authentication, and network communication for the Acme iOS app.
class DataManager {

    // --- M1: Hardcoded credentials in source ---
    // Subtle: looks like a configuration struct but contains production credentials
    private struct Config {
        static let apiKey = "HARDCODED_IOS_API_KEY_DO_NOT_USE"
        static let apiSecret = "HARDCODED_IOS_SECRET_DO_NOT_USE"
        static let analyticsToken = "HARDCODED_ANALYTICS_TOKEN_EXAMPLE"
        static let baseURL = "https://api.acme.com/v2"
    }

    // --- M9: Insecure Data Storage — UserDefaults instead of Keychain ---
    // Subtle: UserDefaults is NOT encrypted and is backed up to iCloud
    // Developer used UserDefaults for convenience instead of Keychain

    func saveAuthToken(_ token: String) {
        // UserDefaults is stored in a plist file, unencrypted
        // Accessible via device backup, jailbreak, or forensic extraction
        UserDefaults.standard.set(token, forKey: "auth_token")
        UserDefaults.standard.set(Date(), forKey: "token_date")
    }

    func saveUserCredentials(username: String, passwordHash: String) {
        // Credentials in UserDefaults — should be in Keychain with kSecAttrAccessible
        UserDefaults.standard.set(username, forKey: "saved_username")
        UserDefaults.standard.set(passwordHash, forKey: "saved_password_hash")
        UserDefaults.standard.synchronize()
    }

    func getUserToken() -> String? {
        return UserDefaults.standard.string(forKey: "auth_token")
    }

    // --- M3: Biometric auth with client-only verification ---
    // Subtle: uses LAContext (correct!) but the success path just sets a local flag
    // No cryptographic proof or server-side verification of biometric result
    func authenticateWithBiometrics(completion: @escaping (Bool) -> Void) {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            completion(false)
            return
        }

        context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Authenticate to access your account"
        ) { success, error in
            if success {
                // Problem: just sets a UserDefaults flag — no server-side verification
                // An attacker can set this flag directly without biometric auth
                UserDefaults.standard.set(true, forKey: "biometric_authenticated")
                UserDefaults.standard.set(Date(), forKey: "biometric_auth_date")
                completion(true)
            } else {
                completion(false)
            }
        }
    }

    // --- M5: Disabled App Transport Security (ATS) ---
    // Note: In a real app, this would be in Info.plist:
    // <key>NSAppTransportSecurity</key>
    // <dict>
    //   <key>NSAllowsArbitraryLoads</key>
    //   <true/>  <!-- Disables ATS entirely — allows HTTP and weak TLS -->
    // </dict>

    // --- M5: No certificate pinning on network requests ---
    // Subtle: uses URLSession (correct!) but with default configuration (no pinning)
    func makeAPIRequest(endpoint: String, completion: @escaping (Data?, Error?) -> Void) {
        let url = URL(string: "\(Config.baseURL)\(endpoint)")!
        var request = URLRequest(url: url)
        request.setValue(Config.apiKey, forHTTPHeaderField: "X-API-Key")

        // Default URLSession — no certificate pinning
        // Vulnerable to MITM with a rogue CA cert (common on corporate/school networks)
        let session = URLSession.shared
        let task = session.dataTask(with: request) { data, response, error in
            completion(data, error)
        }
        task.resume()
    }

    // --- M9: Caching sensitive data without encryption ---
    func cacheSensitiveData(accounts: [[String: Any]]) {
        // Writing sensitive financial data to a plist file in Documents directory
        // No encryption, no data protection attributes
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        let cacheFile = documentsPath.appendingPathComponent("account_cache.plist")

        let data = try? NSKeyedArchiver.archivedData(
            withRootObject: accounts,
            requiringSecureCoding: false  // insecure coding allowed
        )
        try? data?.write(to: cacheFile)
        // No NSFileProtectionComplete attribute set — file accessible when device locked
    }

    // --- M10: Incomplete Jailbreak Detection ---
    // Subtle: jailbreak detection EXISTS but checks are trivially bypassable
    // Only checks for common file paths — doesn't check for Cydia URL scheme,
    // sandbox integrity, fork() behavior, or dyld loaded libraries
    func isDeviceJailbroken() -> Bool {
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt"
        ]

        // Only checks file existence — trivially bypassable by:
        // 1. Hooking NSFileManager.fileExists to return false
        // 2. Using a jailbreak that doesn't install these files (rootless jailbreaks)
        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        // Missing checks:
        // - canOpenURL for cydia:// scheme
        // - Write test to /private (sandbox escape)
        // - Check for suspicious dylibs (frida, substrate)
        // - Verify code signing integrity
        // - Check symlink behavior

        return false
    }

    // --- M9: Logging sensitive data ---
    // Subtle: uses NSLog which persists to device console logs
    // On older iOS versions, syslog is accessible without jailbreak
    func logUserActivity(action: String, details: [String: String]) {
        // NSLog writes to syslog — accessible via Console.app or device logs
        NSLog("User action: \(action), details: \(details)")
        // If details contain tokens, PII, or financial data, they're now in syslog
    }
}
