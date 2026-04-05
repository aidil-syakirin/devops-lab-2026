from flask import Blueprint, request, jsonify, send_from_directory
from app.db import get_db
from sqlalchemy import text
import uuid


routes = Blueprint("routes",__name__)

#Serve resume page
@routes.route("/")
def home():
    return send_from_directory("../static", "index.html")

#Log visitor
@routes.route("/visit", methods=["POST"])
def add_visit():
    try:
        data = request.get_json()

        name = data.get("name", "visitor")
        ip_address = request.headers.get("X-Forwarder-For",request.remote_addr)
        visit_id = str(uuid.uuid4())

        conn = get_db()

        query = text("""
            INSERT INTO visits (id, name, ip_address)
            VALUES (:id, :name, :ip)
        """)

        conn.execute(query, {
            "id": visit_id,
            "name": name,
            "ip": ip_address
         })

        conn.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/visits", methods=["GET"])
def get_visits():
    with get_db() as conn:
        result = conn.execute(text("SELECT * FROM visits"))
        rows = [dict(row._mapping) for row in result]

@app.route("/health")
def health():
    try:
        db.session.execute("SELECT 1")
        return {"status": "ok"}, 200
    except Exception:
        return {"status": "fail"}, 500
