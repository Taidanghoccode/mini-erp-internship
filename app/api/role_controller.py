from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_role_uc
from app.utils.auth_middleware import require_auth

role_bp = Blueprint("role_bp", __name__, url_prefix="/api/roles")


@role_bp.route("/", methods=["GET"])
@require_auth
def get_all_roles():
    uc = provide_role_uc()
    user = g.current_user
    try:
        result = uc.get_all_roles(user.id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/", methods=["POST"])
@require_auth
def create_role():
    uc = provide_role_uc()
    user = g.current_user
    data = request.get_json()
    try:
        role = uc.create_role(user.id, data)
        return jsonify(role), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/<int:role_id>", methods=["GET"])
@require_auth
def get_role(role_id):
    uc = provide_role_uc()
    user = g.current_user
    try:
        role = uc.get_role_by_id(user.id, role_id)
        return jsonify(role), 200 if role else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/<int:role_id>", methods=["PUT"])
@require_auth
def update_role(role_id):
    uc = provide_role_uc()
    user = g.current_user
    data = request.get_json()
    try:
        role = uc.update_role(user.id, role_id, data)
        return jsonify(role), 200 if role else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/<int:role_id>", methods=["DELETE"])
@require_auth
def delete_role(role_id):
    uc = provide_role_uc()
    user = g.current_user
    try:
        ok = uc.delete_role(user.id, role_id)
        return jsonify({"deleted": ok}), 200 if ok else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/<int:role_id>/permissions/<int:permission_id>", methods=["POST"])
@require_auth
def assign_permission(role_id, permission_id):
    uc = provide_role_uc()
    user = g.current_user
    try:
        result = uc.assign_permission(user.id, role_id, permission_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@role_bp.route("/<int:role_id>/permissions/<int:permission_id>", methods=["DELETE"])
@require_auth
def remove_permission(role_id, permission_id):
    uc = provide_role_uc()
    user = g.current_user
    try:
        result = uc.remove_permission(user.id, role_id, permission_id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
