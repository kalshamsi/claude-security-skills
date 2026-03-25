"""
FIXTURE: Insecure Flask application

This file intentionally contains HTTP security header misconfigurations
for use by the security-headers-audit skill test suite.

Issues present (do NOT use in production):
  - No security headers middleware (no flask-talisman, no after_request hooks)
  - Permissive CORS: flask-cors with origins='*'
  - Missing Strict-Transport-Security header on all responses
  - Missing Content-Security-Policy header
  - Missing X-Content-Type-Options header
  - Missing X-Frame-Options header
  - Missing Referrer-Policy header
  - Sensitive data endpoint with no Cache-Control
  - Server header not suppressed (Werkzeug version exposed)
  - No CSRF protection headers
"""

import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

# ----------------------------------------------------------------
# ISSUE 1: Permissive CORS — wildcard origin on all routes
# CWE-942 | A05:2021 — any website can read all API responses
# Fix: CORS(app, origins=['https://app.example.com'])
# ----------------------------------------------------------------
CORS(app)  # Defaults to origins='*' — all cross-origin requests permitted

# Simple in-memory data store for demonstration
users = {
    1: {
        'id': 1,
        'email': 'alice@example.com',
        'phone': '+1-555-0101',
        'ssn': '123-45-6789',
        'balance': 10000.00,
    },
    2: {
        'id': 2,
        'email': 'bob@example.com',
        'phone': '+1-555-0102',
        'ssn': '987-65-4321',
        'balance': 25000.00,
    },
}


# ----------------------------------------------------------------
# ISSUE 2: No global security headers applied
# Missing: @app.after_request hook that sets HSTS, CSP, X-Frame-Options,
#          X-Content-Type-Options, Referrer-Policy, Permissions-Policy
# CWE-693, CWE-319, CWE-16, CWE-1021, CWE-200 | A05:2021, A02:2021
#
# What is missing:
#   @app.after_request
#   def set_security_headers(response):
#       response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
#       response.headers['Content-Security-Policy'] = "default-src 'self'"
#       response.headers['X-Content-Type-Options'] = 'nosniff'
#       response.headers['X-Frame-Options'] = 'DENY'
#       response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
#       response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
#       return response
# ----------------------------------------------------------------


@app.route('/')
def index():
    """
    ISSUE 3: HTML response with no CSP header and XSS-prone template rendering
    CWE-693 | A05:2021 — no Content-Security-Policy sent
    """
    name = request.args.get('name', 'guest')
    # render_template_string used with user input — no CSP to limit XSS impact
    html = render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Flask App</title></head>
        <body>
            <h1>Hello, {{ name }}!</h1>
            <p>Welcome to the example application.</p>
        </body>
        </html>
    """, name=name)
    # Response sent with:
    #   Server: Werkzeug/2.x.x Python/3.x.x  (version disclosure — CWE-200)
    #   (no Content-Security-Policy)           (missing — CWE-693)
    #   (no X-Frame-Options)                   (missing — CWE-1021)
    #   (no Strict-Transport-Security)         (missing — CWE-319)
    return html


# ----------------------------------------------------------------
# ISSUE 4: Sensitive user profile endpoint with no Cache-Control
# CWE-524 | A04:2021 — PII may be cached by browser or proxy
# Fix: response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
# ----------------------------------------------------------------
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Return user profile including PII — no caching protection."""
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # No Cache-Control header — sensitive PII (SSN, phone, balance) is cacheable
    # No HSTS — response does not enforce HTTPS
    return jsonify(user)


# ----------------------------------------------------------------
# ISSUE 5: Financial data endpoint — no Cache-Control, no HSTS
# CWE-524, CWE-319 | A04:2021, A02:2021
# ----------------------------------------------------------------
@app.route('/api/user/<int:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    """Return account balance — sensitive financial data with no cache protection."""
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    response = jsonify({'balance': user['balance'], 'currency': 'USD'})
    # Missing: response.headers['Cache-Control'] = 'no-store, no-cache'
    # Missing: response.headers['Strict-Transport-Security'] = 'max-age=63072000; ...'
    return response


# ----------------------------------------------------------------
# ISSUE 6: Login endpoint — no CSRF header, no cache control on response
# CWE-319 | A02:2021 — token response may be cached
# ----------------------------------------------------------------
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user — no security headers on response containing auth token."""
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')

    user = next((u for u in users.values() if u['email'] == email), None)
    if user and password == 'password123':
        token = f'fake-jwt-token-{user["id"]}'
        # Auth token returned with no Cache-Control — token may be cached
        # No HSTS — HTTPS not enforced for this sensitive endpoint
        return jsonify({'token': token, 'user_id': user['id']})

    return jsonify({'error': 'Invalid credentials'}), 401


# ----------------------------------------------------------------
# ISSUE 7: Manual CORS header — permissive and combined with credentials flag
# CWE-942 | A05:2021 — wildcard origin + credentials is a critical misconfiguration
# ----------------------------------------------------------------
@app.route('/api/data')
def public_data():
    """Public data endpoint with dangerous manual CORS configuration."""
    response = jsonify({'data': [1, 2, 3], 'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # Dangerous with wildcard
    return response


if __name__ == '__main__':
    # Debug mode on — also exposes stack traces in responses
    app.run(debug=True, host='0.0.0.0', port=5000)
