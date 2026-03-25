import Foundation
import UIKit
import LocalAuthentication
import CommonCrypto

class AuthManager: NSObject, URLSessionDelegate {

    // FLAW: Hardcoded encryption key (CWE-798, M1)
    private let encryptionKey = "AES256SecretKey!AES256SecretKey!"
    private let apiKey = "HARDCODED_API_KEY_DO_NOT_USE"
    private let hmacSecret = "supersecrethmac1234567890abcdef"

    // FLAW: Storing secrets in UserDefaults (CWE-312, M9)
    func saveCredentials(username: String, password: String, token: String) {
        UserDefaults.standard.set(username, forKey: "username")
        UserDefaults.standard.set(password, forKey: "password")
        UserDefaults.standard.set(token, forKey: "auth_token")
        UserDefaults.standard.set(apiKey, forKey: "api_key")
        UserDefaults.standard.synchronize()
    }

    func loadCredentials() -> (String?, String?) {
        let username = UserDefaults.standard.string(forKey: "username")
        let password = UserDefaults.standard.string(forKey: "password")
        return (username, password)
    }

    // FLAW: Biometric auth without server-side validation (CWE-287, M3)
    func authenticateWithBiometrics(completion: @escaping (Bool) -> Void) {
        let context = LAContext()
        var error: NSError?
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                                   localizedReason: "Authenticate to continue") { success, _ in
                if success {
                    // No server-side token validation -- bypassed with Frida/Objection
                    completion(true)
                } else {
                    completion(false)
                }
            }
        }
    }

    // FLAW: No certificate pinning, accepts all server certs (CWE-295, M5)
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        // Blindly trust any certificate
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        completionHandler(.useCredential, URLCredential(trust: serverTrust))
    }

    // FLAW: MD5 for password hashing (CWE-327, M10)
    func hashPassword(_ password: String) -> String {
        let data = password.data(using: .utf8)!
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))
        data.withUnsafeBytes {
            CC_MD5($0.baseAddress, CC_LONG(data.count), &digest)
        }
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    // FLAW: Sensitive data copied to pasteboard (CWE-200, M9)
    func copyTokenToClipboard() {
        let token = UserDefaults.standard.string(forKey: "auth_token") ?? ""
        UIPasteboard.general.string = token  // Accessible by any app
    }

    func copyPasswordToClipboard() {
        let password = UserDefaults.standard.string(forKey: "password") ?? ""
        UIPasteboard.general.string = password  // Persists in clipboard history
    }

    // FLAW: Insecure encryption with hardcoded key and static IV (CWE-327, M10)
    func encryptData(_ plaintext: String) -> Data? {
        let key = encryptionKey.data(using: .utf8)!
        let iv = Data(repeating: 0, count: kCCBlockSizeAES128)  // Static zero IV
        let data = plaintext.data(using: .utf8)!
        var encryptedData = Data(count: data.count + kCCBlockSizeAES128)
        var numBytesEncrypted: size_t = 0

        let status = key.withUnsafeBytes { keyBytes in
            iv.withUnsafeBytes { ivBytes in
                data.withUnsafeBytes { dataBytes in
                    encryptedData.withUnsafeMutableBytes { encBytes in
                        CCCrypt(CCOperation(kCCEncrypt),
                                CCAlgorithm(kCCAlgorithmAES),
                                CCOptions(kCCOptionPKCS7Padding),
                                keyBytes.baseAddress, key.count,
                                ivBytes.baseAddress,
                                dataBytes.baseAddress, data.count,
                                encBytes.baseAddress, encryptedData.count,
                                &numBytesEncrypted)
                    }
                }
            }
        }
        return status == kCCSuccess ? encryptedData.prefix(numBytesEncrypted) : nil
    }

    // FLAW: No jailbreak detection (CWE-693, M7)
    // Missing: isJailbroken() check
    // Missing: debugger detection
    // Missing: code integrity validation
    func startSecureSession() {
        // App launches without any integrity or environment checks
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
        let url = URL(string: "http://api.example.com/session")!  // Cleartext HTTP (CWE-319)
        let request = URLRequest(url: url)
        session.dataTask(with: request).resume()
    }
}
