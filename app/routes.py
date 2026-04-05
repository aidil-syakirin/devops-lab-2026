from datetime import date, datetime
from flask import Blueprint, request, jsonify, send_from_directory
from app.db import get_db
from sqlalchemy import text
import uuid


routes = Blueprint("routes",__name__)


def _jsonable_value(val):
    if isinstance(val, uuid.UUID):
        return str(val)
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return val


def _row_to_jsonable(row):
    return {k: _jsonable_value(v) for k, v in dict(row._mapping).items()}

#Serve resume page
@routes.route("/")
def home():
    return send_from_directory("../static", "index.html")

#Log visitor
@routes.route("/visit", methods=["POST"])
def add_visit():
    try:
        data = request.get_json(silent=True) or {}

        name = data.get("name", "visitor")
        ip_address = request.headers.get("X-Forwarder-For",request.remote_addr)
        visit_id = str(uuid.uuid4())

        query = text("""
            INSERT INTO visits (id, name, ip_address)
            VALUES (:id, :name, :ip)
        """)

        with get_db() as conn:
            conn.execute(
                query,
                {"id": visit_id, "name": name, "ip": ip_address},
            )
            conn.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/visits", methods=["GET"])
def get_visits():
    with get_db() as conn:
        result = conn.execute(text("SELECT * FROM visits"))
        rows = [_row_to_jsonable(row) for row in result]
    return jsonify(rows), 200


@routes.route("/health")
def health():
    try:
        with get_db() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"status": "fail"}), 503
