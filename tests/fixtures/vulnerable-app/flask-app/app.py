# Vulnerable Flask Application — FOR SECURITY TESTING ONLY
# Each endpoint contains a deliberate vulnerability for use with security-test-generator skill

from flask import Flask, request, jsonify, make_response
import sqlite3
import requests as http_requests

app = Flask(__name__)

# In-memory user store (simulates database)
users_db = [
    {"id": 1, "username": "alice", "role": "user", "is_admin": False},
    {"id": 2, "username": "bob", "role": "user", "is_admin": False},
]


# --- CWE-89: SQL Injection ---
# Vulnerable: User input interpolated directly into SQL query via f-string
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER, name TEXT)")
    # VULNERABLE: f-string interpolation in SQL query
    cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")
    results = cursor.fetchall()
    conn.close()
    return jsonify({"results": results})


# --- CWE-918: Server-Side Request Forgery (SSRF) ---
# Vulnerable: User-controlled URL passed directly to requests.get
@app.route("/api/fetch", methods=["POST"])
def fetch_url():
    data = request.get_json()
    url = data.get("url", "")
    # VULNERABLE: No URL validation — allows requests to internal services, cloud metadata
    response = http_requests.get(url)
    return jsonify({"status": response.status_code, "body": response.text[:500]})


# --- CWE-915: Mass Assignment ---
# Vulnerable: All request JSON fields spread directly into user record update
@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    for user in users_db:
        if user["id"] == user_id:
            # VULNERABLE: All fields from request body applied without allowlist
            # Attacker can set is_admin=True, role="superuser", etc.
            user.update(data)
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404


# --- CWE-79: Cross-Site Scripting (Reflected XSS) ---
# Vulnerable: User input rendered in HTML response without escaping
@app.route("/api/profile", methods=["GET"])
def profile():
    name = request.args.get("name", "Guest")
    # VULNERABLE: make_response with unescaped user input in HTML
    html = f"<h1>Welcome {name}</h1><p>Your profile page</p>"
    return make_response(html)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
