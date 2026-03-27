"""
Inventory Service — main Flask application.

Provides REST endpoints for managing warehouse inventory,
running pricing calculations, and generating reports.
"""

import logging

from flask import Flask, jsonify, request

from auth import authenticate_request
from cache import cache
from config import get_config
from math_parser import evaluate
from utils import generate_report, ping_host

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    cfg = get_config()
    app = Flask(cfg.APP_NAME)
    app.config.from_object(cfg)

    @app.before_request
    def require_auth():
        open_paths = ("/health", "/ready")
        if request.path in open_paths:
            return
        if not authenticate_request(dict(request.headers)):
            return jsonify({"error": "unauthorized"}), 401

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "version": cfg.VERSION})

    @app.route("/ready")
    def readiness():
        db_ok = ping_host("localhost")
        return jsonify({"ready": db_ok}), 200 if db_ok else 503

    @app.route("/api/items", methods=["GET"])
    def list_items():
        page = request.args.get("page", 1, type=int)
        cached = cache.get(f"items:page:{page}")
        if cached is not None:
            return jsonify(cached)

        items = _fetch_items(page)
        cache.set(f"items:page:{page}", items)
        return jsonify(items)

    @app.route("/api/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        cached = cache.get(f"item:{item_id}")
        if cached is not None:
            return jsonify(cached)
        item = _fetch_item(item_id)
        if item is None:
            return jsonify({"error": "not found"}), 404
        cache.set(f"item:{item_id}", item)
        return jsonify(item)

    @app.route("/api/pricing/calculate", methods=["POST"])
    def calculate_price():
        body = request.get_json(force=True)
        expr = body.get("expression", "0")
        variables = {k: v for k, v in body.items() if k != "expression"}
        try:
            result = evaluate(expr, variables)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"result": result})

    @app.route("/api/reports/<report_name>", methods=["POST"])
    def create_report(report_name):
        fmt = request.args.get("format", "csv")
        path = generate_report(report_name, fmt)
        return jsonify({"path": path}), 201

    return app


def _fetch_items(page, per_page=20):
    """Placeholder for database query."""
    return {"page": page, "per_page": per_page, "items": []}


def _fetch_item(item_id):
    """Placeholder for single-item database lookup."""
    return {"id": item_id, "name": f"Item {item_id}", "quantity": 0}


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=8080)
