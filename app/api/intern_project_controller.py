from flask import Blueprint, request, jsonify, g
from app.utils.auth_middleware import require_auth
from app.utils.uc_provider import provide_intern_project_uc

intern_project_bp = Blueprint("intern_project_bp", __name__, url_prefix="/api/intern-project")


@intern_project_bp.route("/assign", methods=["POST"])
@require_auth
def assign_project():
    uc = provide_intern_project_uc()
    user = g.current_user
    data = request.get_json() or {}

    intern_id = data.get("intern_id")
    project_id = data.get("project_id")
    role = data.get("role", "Member")

    if not intern_id or not project_id:
        return jsonify({"error": "intern_id and project_id are required"}), 400

    try:
        result = uc.assign_project(user.id, intern_id, project_id, role)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@intern_project_bp.route("/remove", methods=["POST"])
@require_auth
def remove_project():
    uc = provide_intern_project_uc()
    user = g.current_user
    data = request.get_json() or {}

    intern_id = data.get("intern_id")
    project_id = data.get("project_id")

    if not intern_id or not project_id:
        return jsonify({"error": "intern_id and project_id are required"}), 400

    try:
        ok = uc.remove_project(user.id, intern_id, project_id)
        return jsonify({"removed": ok}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@intern_project_bp.route("/<int:intern_id>/projects", methods=["GET"])
@require_auth
def get_projects_of_intern(intern_id):
    uc = provide_intern_project_uc()
    user = g.current_user
    try:
        result = uc.get_projects_of_intern(user.id, intern_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@intern_project_bp.route("/<int:project_id>/interns", methods=["GET"])
@require_auth
def get_interns_of_project(project_id):
    uc = provide_intern_project_uc()
    user = g.current_user
    try:
        result = uc.get_interns_of_project(user.id, project_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
