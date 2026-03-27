import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, Linking } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { WebView } from 'react-native-webview';

// --- M4: Insufficient Input/Output Validation ---
// Subtle: WebView has URL restrictions but uses startsWith (bypassable)
const TRUSTED_DOMAINS = ['https://app.acme.com', 'https://auth.acme.com'];

function isUrlAllowed(url: string): boolean {
  // Bypassable: attacker can use https://app.acme.com.evil.com/phishing
  // startsWith doesn't validate the domain boundary
  return TRUSTED_DOMAINS.some(domain => url.startsWith(domain));
}

// --- M1: Improper Credential Usage ---
// Subtle: wrapper class named "SecureStore" that just delegates to AsyncStorage
// Developer thought the name makes it secure — it doesn't
class SecureStore {
  // This is just AsyncStorage with a fancy name
  // AsyncStorage is unencrypted plaintext on both iOS and Android
  static async setItem(key: string, value: string): Promise<void> {
    await AsyncStorage.setItem(key, value);
  }

  static async getItem(key: string): Promise<string | null> {
    return await AsyncStorage.getItem(key);
  }

  static async removeItem(key: string): Promise<void> {
    await AsyncStorage.removeItem(key);
  }
}

// --- M5: Insecure Communication ---
// No certificate pinning on API calls
// Developer relies on HTTPS alone without pinning
const API_BASE = 'https://api.acme.com/v2';

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  // Standard fetch with no certificate pinning configuration
  // Vulnerable to MITM with a compromised or rogue CA certificate
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return response.json();
}

// --- Main App Component ---
export default function App() {
  const [user, setUser] = useState<any>(null);
  const [webViewUrl, setWebViewUrl] = useState('https://app.acme.com/dashboard');

  useEffect(() => {
    loadUserSession();
    setupDeepLinkHandler();
  }, []);

  // --- M1: Storing auth tokens in plaintext AsyncStorage ---
  async function loadUserSession() {
    const token = await SecureStore.getItem('auth_token');
    const refreshToken = await SecureStore.getItem('refresh_token');
    const userProfile = await SecureStore.getItem('user_profile');

    if (token && userProfile) {
      setUser(JSON.parse(userProfile));
    }
  }

  async function handleLogin(username: string, password: string) {
    try {
      const result = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      // Storing sensitive tokens in unencrypted AsyncStorage
      await SecureStore.setItem('auth_token', result.accessToken);
      await SecureStore.setItem('refresh_token', result.refreshToken);
      await SecureStore.setItem('user_profile', JSON.stringify(result.user));

      // Also storing the raw password hash for "remember me" (M1 violation)
      if (result.rememberMe) {
        await SecureStore.setItem('saved_credentials', JSON.stringify({
          username,
          passwordHash: result.passwordHash,
        }));
      }

      setUser(result.user);
    } catch (error) {
      console.error('Login failed:', error);
    }
  }

  // --- M9: Insecure Data Storage ---
  // Subtle: caches sensitive financial data in AsyncStorage for "offline access"
  async function cacheAccountData(accounts: any[]) {
    // Financial account data cached in unencrypted storage
    // Available to any app with root/jailbreak access
    await SecureStore.setItem('cached_accounts', JSON.stringify(accounts));
    await SecureStore.setItem('cache_timestamp', new Date().toISOString());
  }

  // --- M7: Poor Binary Protections ---
  // Subtle: Deep link handler with no validation of incoming URL parameters
  // Attacker can craft deep links that navigate to arbitrary internal screens
  function setupDeepLinkHandler() {
    Linking.addEventListener('url', (event) => {
      const url = new URL(event.url);
      const screen = url.searchParams.get('screen');
      const token = url.searchParams.get('token');

      // No validation of the screen parameter — attacker can navigate anywhere
      // No verification that the token came from a legitimate source
      if (screen) {
        navigateToScreen(screen, { token });
      }
    });
  }

  function navigateToScreen(screen: string, params: any) {
    // Direct navigation without validating allowed screens
    // Could navigate to admin panels, debug screens, etc.
    console.log(`Navigating to ${screen} with params:`, params);
  }

  // --- M4: WebView with insufficient URL validation ---
  function handleWebViewNavigation(navState: any) {
    const url = navState.url;

    // Uses the bypassable isUrlAllowed check
    if (!isUrlAllowed(url)) {
      console.warn('Blocked navigation to:', url);
      return false;
    }
    return true;
  }

  return (
    <View style={{ flex: 1 }}>
      {user ? (
        <WebView
          source={{ uri: webViewUrl }}
          javaScriptEnabled={true}
          // M4: allowFileAccess enables reading local files from WebView
          allowFileAccess={true}
          // M4: Mixed content allowed — HTTP resources in HTTPS pages
          mixedContentMode="always"
          onShouldStartLoadWithRequest={(request) =>
            handleWebViewNavigation(request)
          }
          // M4: JavaScript bridge exposed to all loaded pages
          injectedJavaScript={`
            window.ReactNativeWebView.postMessage(document.cookie);
          `}
        />
      ) : (
        <LoginScreen onLogin={handleLogin} />
      )}
    </View>
  );
}

function LoginScreen({ onLogin }: { onLogin: (u: string, p: string) => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  return (
    <View style={{ padding: 20 }}>
      <Text>Login</Text>
      <TextInput value={username} onChangeText={setUsername} placeholder="Username" />
      <TextInput value={password} onChangeText={setPassword} placeholder="Password" secureTextEntry />
      <Button title="Login" onPress={() => onLogin(username, password)} />
    </View>
  );
}
