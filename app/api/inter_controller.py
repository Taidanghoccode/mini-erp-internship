from flask import Blueprint, request, jsonify, g
from app.utils.auth_middleware import require_auth
from app.utils.uc_provider import provide_intern_uc

intern_bp = Blueprint("intern_bp", __name__, url_prefix="/api/interns")

@intern_bp.route("/", methods=["POST"])
@require_auth
def create_intern():
    intern_uc = provide_intern_uc()
    user = g.current_user
    body = request.json

    result = intern_uc.create_intern(user.id, body)
    return jsonify(result), 201

@intern_bp.route("/", methods=["GET"])
@require_auth
def get_all_interns():
    intern_uc = provide_intern_uc()
    user = g.current_user

    result = intern_uc.get_all_interns(user.id)
    return jsonify(result), 200

@intern_bp.route("/<int:intern_id>", methods=["GET"])
@require_auth
def get_intern(intern_id):
    intern_uc = provide_intern_uc()
    user = g.current_user

    result = intern_uc.get_intern_by_id(user.id, intern_id)
    return jsonify(result), 200

@intern_bp.route("/<int:intern_id>", methods=["PUT"])
@require_auth
def update_intern(intern_id):
    intern_uc = provide_intern_uc()
    user = g.current_user
    body = request.json

    result = intern_uc.update_intern(user.id, intern_id, body)
    return jsonify(result), 200

@intern_bp.route("/<int:intern_id>", methods=["DELETE"])
@require_auth
def delete_intern(intern_id):
    intern_uc = provide_intern_uc()
    user = g.current_user

    soft = request.args.get("soft", "true").lower() == "true"
    ok = intern_uc.delete_intern(user.id, intern_id, soft=soft)

    return jsonify({"deleted": ok}), 200

@intern_bp.route("/<int:intern_id>/projects", methods=["GET"])
@require_auth
def get_projects_of_intern(intern_id):
    intern_uc = provide_intern_uc()
    user = g.current_user

    result = intern_uc.get_projects_of_intern(user.id, intern_id)
    return jsonify(result), 200

@intern_bp.route("/email/<string:email>", methods=["GET"])
@require_auth
def get_intern_by_email(email):
    intern_uc = provide_intern_uc()
    user = g.current_user

    result = intern_uc.get_intern_by_email(user.id, email)
    return jsonify(result), 200

@intern_bp.route("/<int:intern_id>/close", methods=["POST"])
@require_auth
def close_internship(intern_id):
    intern_uc = provide_intern_uc()
    user = g.current_user

    result = intern_uc.close_internship(user.id, intern_id)
    return jsonify(result), 200
