from flask import Blueprint, request, jsonify, g
from app.utils.auth_middleware import require_auth
from app.utils.uc_provider import provide_project_uc

project_bp = Blueprint("project_bp", __name__, url_prefix="/api/projects")


@project_bp.route("/", methods=["POST"])
@require_auth
def create_project():
    uc = provide_project_uc()
    user = g.current_user
    data = request.get_json() or {}
    try:
        result = uc.create_project(user.id, data)
        return jsonify(result), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/", methods=["GET"])
@require_auth
def get_all_projects():
    uc = provide_project_uc()
    user = g.current_user
    try:
        result = uc.get_all_projects(user.id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/<int:project_id>", methods=["GET"])
@require_auth
def get_project_by_id(project_id):
    uc = provide_project_uc()
    user = g.current_user
    try:
        result = uc.get_project_by_id(user.id, project_id)
        return jsonify(result), 200 if result else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/<int:project_id>", methods=["PUT"])
@require_auth
def update_project(project_id):
    uc = provide_project_uc()
    user = g.current_user
    data = request.get_json() or {}
    try:
        updated = uc.update_project(user.id, project_id, data)
        return jsonify(updated), 200 if updated else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@require_auth
def delete_project(project_id):
    uc = provide_project_uc()
    user = g.current_user
    soft = request.args.get("soft", "true").lower() == "true"
    try:
        ok = uc.delete_project(user.id, project_id, soft=soft)
        return jsonify({"deleted": ok}), 200 if ok else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@project_bp.route("/<int:project_id>/interns", methods=["GET"])
@require_auth
def get_interns_of_project(project_id):
    uc = provide_project_uc()
    user = g.current_user
    try:
        result = uc.get_interns_of_project(user.id, project_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
