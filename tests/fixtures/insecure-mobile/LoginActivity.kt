package com.example.insecure.ui

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager
import java.security.cert.X509Certificate

class LoginActivity : AppCompatActivity() {

    // FLAW: Hardcoded API keys (CWE-798, M1)
    companion object {
        private const val API_KEY = "HARDCODED_API_KEY_DO_NOT_USE"
        private const val API_SECRET = "HARDCODED_SECRET_DO_NOT_USE"
        private const val FIREBASE_KEY = "HARDCODED_FIREBASE_KEY_DO_NOT_USE"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // FLAW: Logging sensitive data (CWE-359, M6)
        val username = intent.getStringExtra("username") ?: ""
        val password = intent.getStringExtra("password") ?: ""
        Log.d("LOGIN", "Attempting login: user=$username, pass=$password, key=$API_KEY")

        setupInsecureWebView()
        handleDeepLink(intent)
        performLogin(username, password)
    }

    // FLAW: WebView with dangerous settings (CWE-79, M4)
    private fun setupInsecureWebView() {
        val webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.allowFileAccess = true
        webView.settings.allowFileAccessFromFileURLs = true
        webView.settings.allowUniversalAccessFromFileURLs = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()

        // FLAW: Loading arbitrary URL from intent (CWE-79, M4)
        val url = intent.getStringExtra("load_url") ?: "https://example.com"
        webView.loadUrl(url)
    }

    // FLAW: Insecure intent handling -- no validation (CWE-79, M4)
    private fun handleDeepLink(intent: Intent) {
        val data = intent.data
        if (data != null) {
            val action = data.getQueryParameter("action")
            val target = data.getQueryParameter("url")
            // No validation -- attacker can supply arbitrary URLs or actions
            if (action == "open" && target != null) {
                val webView = WebView(this)
                webView.loadUrl(target)
            }
        }
    }

    private fun performLogin(username: String, password: String) {
        // FLAW: Storing credentials in plain SharedPreferences (CWE-312, M9)
        val prefs = getSharedPreferences("user_data", Context.MODE_PRIVATE)
        prefs.edit()
            .putString("username", username)
            .putString("password", password)
            .putString("api_key", API_KEY)
            .putString("session_token", "tok_abc123def456")
            .apply()

        // FLAW: No certificate pinning, trust all certs (CWE-295, M5)
        val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
            override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
            override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
            override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
        })

        val sslContext = SSLContext.getInstance("TLS")
        sslContext.init(null, trustAllCerts, java.security.SecureRandom())

        val url = URL("http://api.example.com/login")  // FLAW: cleartext HTTP (CWE-319, M5)
        val connection = url.openConnection() as HttpsURLConnection
        connection.sslSocketFactory = sslContext.socketFactory
        connection.setRequestProperty("Authorization", "Bearer $API_KEY")
        connection.setRequestProperty("X-Secret", API_SECRET)

        // FLAW: Logging the full response including tokens (CWE-359, M6)
        val response = connection.inputStream.bufferedReader().readText()
        Log.d("LOGIN", "Server response: $response")
        Log.i("LOGIN", "Auth token received for user: $username")

        // FLAW: Storing auth response in plain prefs (CWE-312, M9)
        prefs.edit().putString("auth_response", response).apply()
    }
}
