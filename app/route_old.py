import uuid
from flask import request, jsonify
from sqlalchemy import text
from .db import engine

def register_routes(app):

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/visits", methods=["POST"])
    def create_visit():
        # Added a safety check for JSON data
        data = request.get_json(silent=True) or {}
        if "name" not in data:
            return jsonify({"error": "Missing name"}), 400

        new_id = str(uuid.uuid4())

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO visits (id, name)
                    VALUES (:id, :name)
                """),
                {
                    "id": new_id,
                    "name": data["name"]
                }
            )

        return jsonify({"message": "Visit created", "id": new_id}), 201

    @app.route("/visits", methods=["GET"])
    def get_visits():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM visits"))
            rows = [dict(row._mapping) for row in result]

        return jsonify(rows)
