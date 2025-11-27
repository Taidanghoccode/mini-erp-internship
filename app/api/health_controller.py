from flask import Blueprint, jsonify
from app.db.db import db
from sqlalchemy import text

bp = Blueprint("health", __name__)

@bp.route("/health", methods=["GET"])
def health_check():
    try: 
        db.session.execute(text("SELECT 1"))
        return jsonify({"status":"ok", "database":"PostgresSQL connected"}), 200
    except Exception as e:
        return jsonify({"status":"error", "details":str(e)})