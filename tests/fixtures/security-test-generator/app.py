import os
import hmac
import hashlib
import sqlite3
import urllib.parse
from pathlib import Path

import requests
from flask import Flask, request, jsonify, g

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/var/app/uploads'

DATABASE = ':memory:'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        _init_db(g.db)
    return g.db


def _init_db(db):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT, email TEXT,
            role TEXT, password_hash TEXT
        );
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY, user_id INTEGER, bio TEXT,
            avatar_url TEXT, is_admin INTEGER DEFAULT 0
        );
        INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin@example.com', 'admin', 'hashed_pw_1');
        INSERT OR IGNORE INTO users VALUES (2, 'alice', 'alice@example.com', 'user', 'hashed_pw_2');
        INSERT OR IGNORE INTO profiles VALUES (1, 1, 'System administrator', '/avatars/admin.png', 1);
        INSERT OR IGNORE INTO profiles VALUES (2, 2, 'Regular user', '/avatars/alice.png', 0);
    """)


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# --- Endpoint 1: Search users ---
# Subtle SQLi: f-string interpolation looks natural in Python but is injectable
@app.route('/api/users', methods=['GET'])
def search_users():
    search = request.args.get('search', '')
    limit = request.args.get('limit', '20')

    # Developer used f-string — idiomatic Python, but deadly in SQL context
    query = f"SELECT id, username, email FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%' LIMIT {limit}"

    db = get_db()
    try:
        results = db.execute(query).fetchall()
        return jsonify({
            'results': [dict(row) for row in results],
            'count': len(results)
        })
    except Exception as e:
        app.logger.error(f"Search failed: {e}")
        return jsonify({'error': 'Search failed'}), 500


# --- Endpoint 2: Login ---
# Subtle timing attack: uses == for hash comparison instead of hmac.compare_digest
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    provided_hash = hashlib.sha256(password.encode()).hexdigest()

    # Timing-vulnerable comparison — == leaks timing info
    # Should use hmac.compare_digest(provided_hash, user['password_hash'])
    if provided_hash == user['password_hash']:
        token = os.urandom(32).hex()
        return jsonify({'token': token, 'userId': user['id']})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


# --- Endpoint 3: File access ---
# Subtle path traversal: strips ../ once but not recursively
@app.route('/api/files/<path:filename>', methods=['GET'])
def get_file(filename):
    uploads_dir = app.config['UPLOAD_FOLDER']

    # Single-pass sanitization — ....// becomes ../ after replacement
    sanitized = filename.replace('../', '')

    file_path = os.path.join(uploads_dir, sanitized)

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({'filename': filename, 'content': content})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


# --- Endpoint 4: Update profile ---
# Subtle mass assignment: dict unpacking merges all request fields
@app.route('/api/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Developer intended to only update bio and avatar_url
    # But builds query from ALL provided keys — including is_admin
    set_clauses = ', '.join(f"{key} = ?" for key in data.keys())
    values = list(data.values())

    db = get_db()
    try:
        db.execute(
            f"UPDATE profiles SET {set_clauses} WHERE user_id = ?",
            values + [user_id]
        )
        db.commit()
        return jsonify({'updated': True})
    except Exception as e:
        return jsonify({'error': 'Update failed'}), 500


# --- Endpoint 5: URL proxy/fetch ---
# Subtle SSRF: validates scheme via urlparse but doesn't block private IPs
@app.route('/api/proxy', methods=['GET'])
def proxy_url():
    target_url = request.args.get('url', '')

    if not target_url:
        return jsonify({'error': 'URL parameter required'}), 400

    parsed = urllib.parse.urlparse(target_url)

    # Scheme validation exists — but no host/IP validation
    # Allows http://169.254.169.254/latest/meta-data/ (cloud metadata)
    # Allows http://10.0.0.1/admin, http://localhost:8080/internal
    if parsed.scheme not in ('http', 'https'):
        return jsonify({'error': 'Only HTTP(S) URLs allowed'}), 400

    try:
        resp = requests.get(target_url, timeout=5)
        return jsonify({'status': resp.status_code, 'body': resp.text})
    except requests.RequestException:
        return jsonify({'error': 'Failed to fetch URL'}), 502


if __name__ == '__main__':
    app.run(debug=False, port=5000)
