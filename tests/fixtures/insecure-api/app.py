"""
Deliberately insecure FastAPI server for testing api-security-tester skill.

Vulnerabilities:
  - No authentication on any endpoint
  - SQL injection via string formatting
  - Excessive data exposure (returns password hashes)
  - No rate limiting
  - SSRF via user-controlled URL
  - Mass assignment via unvalidated dict update
  - Permissive CORS
  - Debug mode enabled
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import sqlite3

# VULN [API8]: Debug mode in production
app = FastAPI(debug=True)

# VULN [API8]: Permissive CORS — allows all origins, methods, headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fake in-memory database
DB = {
    "users": {
        1: {"id": 1, "name": "Alice", "email": "alice@example.com",
            "password_hash": "$2b$12$fakehash", "role": "user", "ssn": "123-45-6789"},
        2: {"id": 2, "name": "Bob", "email": "bob@example.com",
            "password_hash": "$2b$12$anotherfake", "role": "admin", "ssn": "987-65-4321"},
    },
    "orders": {
        101: {"id": 101, "user_id": 1, "product": "Widget", "total": 29.99},
        102: {"id": 102, "user_id": 2, "product": "Gadget", "total": 49.99},
    },
}


# VULN [API2]: No authentication on any endpoint
# VULN [API3]: Returns full user object including password_hash and ssn
@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    user = DB["users"].get(user_id)
    if not user:
        return {"error": "Not found"}
    return user  # Exposes password_hash, ssn, role


# VULN [API4]: No pagination — returns all users
@app.get("/api/users")
async def list_users():
    return list(DB["users"].values())


# VULN [API1]: BOLA — no ownership check, any caller can view any order
@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    order = DB["orders"].get(order_id)
    if not order:
        return {"error": "Not found"}
    return order


# VULN [API3]: Mass assignment — accepts arbitrary dict and merges
@app.put("/api/users/{user_id}")
async def update_user(user_id: int, request: Request):
    data = await request.json()
    if user_id not in DB["users"]:
        return {"error": "Not found"}
    DB["users"][user_id].update(data)  # Attacker can set role: "admin"
    return DB["users"][user_id]


# VULN [API5]: Admin endpoint with no authentication or authorization
@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int):
    if user_id in DB["users"]:
        del DB["users"][user_id]
    return {"status": "deleted"}


# VULN [API5]: Admin settings with no auth
@app.post("/api/admin/settings")
async def admin_settings(request: Request):
    data = await request.json()
    return {"status": "updated", "settings": data}


# VULN [API7]: SSRF — fetches arbitrary user-supplied URL server-side
@app.post("/api/fetch-url")
async def fetch_url(request: Request):
    data = await request.json()
    url = data.get("url", "")
    async with httpx.AsyncClient() as client:
        response = await client.get(url)  # No URL validation
    return {"data": response.text}


# VULN: SQL injection via string formatting (bonus — common API flaw)
@app.get("/api/search")
async def search_users(q: str = ""):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    # VULN [CWE-89]: SQL injection via string interpolation
    query = f"SELECT * FROM users WHERE name LIKE '%{q}%'"
    try:
        cursor.execute(query)
        return {"results": cursor.fetchall()}
    except Exception as e:
        return {"error": str(e)}  # VULN [API8]: Leaks DB error details


# VULN [API9]: Debug endpoint exposing internal config
@app.get("/api/debug/config")
async def debug_config():
    import os
    return {
        "env": dict(os.environ),
        "database": "postgresql://admin:secret@db.internal:5432/prod",
        "debug": True,
    }


# VULN [API10]: Consuming third-party API without validation
@app.post("/api/enrich/{user_id}")
async def enrich_user(user_id: int):
    async with httpx.AsyncClient(verify=False) as client:  # No TLS verification!
        resp = await client.get(f"http://partner-api.example.com/users/{user_id}")
    data = resp.json()  # No schema validation
    if user_id in DB["users"]:
        DB["users"][user_id].update(data)  # Blindly merges unvalidated data
    return DB["users"].get(user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
