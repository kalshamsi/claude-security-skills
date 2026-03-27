import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

/// Configuration and network service for the Acme Flutter app.
/// Handles API configuration, HTTP client setup, and logging.

// --- M1: Hardcoded API keys in static class ---
// Subtle: organized in a "Config" class that looks like it should be
// loaded from environment, but values are actually hardcoded in source
class AppConfig {
  // These will be in the compiled Dart snapshot — extractable via reverse engineering
  static const String apiKey = 'HARDCODED_FLUTTER_API_KEY_DO_NOT_USE';
  static const String apiSecret = 'HARDCODED_FLUTTER_SECRET_DO_NOT_USE';
  static const String analyticsKey = 'HARDCODED_ANALYTICS_KEY_EXAMPLE';
  static const String baseUrl = 'https://api.acme.com/v2';

  // Firebase config — should be loaded from google-services.json at runtime
  static const String firebaseApiKey = 'HARDCODED_FIREBASE_KEY_EXAMPLE';
  static const String firebaseProjectId = 'acme-prod-12345';
}

// --- M2: Inadequate Supply Chain Security ---
// Note: In pubspec.yaml, this app would have:
// dependencies:
//   flutter:
//     sdk: flutter
//   http: any                    # Wildcard version — no pinning
//   sketchy_analytics: ^1.0.0   # Unvetted third-party package
//   untrusted_crypto:            # Git dependency from random user
//     git:
//       url: https://github.com/random-user/untrusted_crypto.git

// --- M5: Insecure Communication — disabled certificate verification ---
// Subtle: method named "initSecureHttp" sounds safe but actually DISABLES verification
class SecureHttpClient {
  static HttpClient? _client;

  /// Initialize the "secure" HTTP client.
  ///
  /// PROBLEM: This method's name implies security but it creates an HttpClient
  /// that accepts ALL certificates, including self-signed and expired ones.
  /// An attacker performing MITM can intercept all traffic.
  static HttpClient initSecureHttp() {
    _client ??= HttpClient()
      ..badCertificateCallback = (X509Certificate cert, String host, int port) {
        // Developer added this "for testing" and forgot to remove it
        // Accepts ANY certificate — completely disables TLS verification
        if (kDebugMode) {
          debugPrint('Certificate check for $host: allowing');
        }
        return true;  // <-- Always returns true, even in production
      };
    return _client!;
  }

  /// Make an API request using the "secure" client.
  static Future<Map<String, dynamic>> apiRequest(
    String endpoint, {
    String method = 'GET',
    Map<String, dynamic>? body,
  }) async {
    final client = initSecureHttp();
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');

    HttpClientRequest request;
    if (method == 'POST') {
      request = await client.postUrl(url);
      request.headers.contentType = ContentType.json;
      request.write(jsonEncode(body));
    } else {
      request = await client.getUrl(url);
    }

    request.headers.set('X-API-Key', AppConfig.apiKey);

    final response = await request.close();
    final responseBody = await response.transform(utf8.decoder).join();
    return jsonDecode(responseBody);
  }
}

// --- M8: Insufficient Privacy Controls — verbose debug logging ---
// Subtle: developer wraps logging in kDebugMode check, but kDebugMode is
// controlled by the Dart compiler flag and may be true in staging/beta builds
class AppLogger {
  /// Log an event with full context.
  ///
  /// PROBLEM: Logs user tokens, PII, and request bodies in "debug" mode.
  /// kDebugMode can be true in non-production builds distributed to testers.
  /// Even in "release" mode, these strings exist in the compiled snapshot.
  static void logEvent(String event, {Map<String, dynamic>? context}) {
    if (kDebugMode) {
      // Full context including tokens and PII logged to console
      debugPrint('[$event] ${DateTime.now().toIso8601String()}');
      if (context != null) {
        debugPrint('  Context: ${jsonEncode(context)}');
      }
    }

    // Even without kDebugMode, the event name is still logged to analytics
    // with the hardcoded analytics key
    _sendToAnalytics(event, context);
  }

  static void logUserAction(String action, String userId, {String? token}) {
    logEvent('user_action', context: {
      'action': action,
      'user_id': userId,
      'auth_token': token ?? 'none',  // <-- Token in log context
      'device_info': Platform.operatingSystem,
    });
  }

  static Future<void> _sendToAnalytics(
    String event,
    Map<String, dynamic>? context,
  ) async {
    try {
      await http.post(
        Uri.parse('https://analytics.acme.com/events'),
        headers: {'X-Analytics-Key': AppConfig.analyticsKey},
        body: jsonEncode({
          'event': event,
          'context': context,  // Sending full context including tokens to analytics
          'timestamp': DateTime.now().millisecondsSinceEpoch,
        }),
      );
    } catch (e) {
      // Silently fail — analytics errors shouldn't crash the app
    }
  }
}
