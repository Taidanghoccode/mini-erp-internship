from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_permission_uc
from app.utils.auth_middleware import require_auth

permission_bp = Blueprint("permission_bp", __name__, url_prefix="/api/permissions")


@permission_bp.route("/", methods=["GET"])
@require_auth
def get_all_permissions():
    uc = provide_permission_uc()
    user = g.current_user
    try:
        result = uc.get_all_permissions(user.id)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/<int:permission_id>", methods=["GET"])
@require_auth
def get_permission(permission_id):
    uc = provide_permission_uc()
    user = g.current_user
    try:
        perm = uc.get_permission_by_id(user.id, permission_id)
        return jsonify(perm), 200 if perm else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/", methods=["POST"])
@require_auth
def create_permission():
    uc = provide_permission_uc()
    user = g.current_user
    data = request.get_json()
    try:
        perm = uc.create_permission(user.id, data)
        return jsonify(perm), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/<int:permission_id>", methods=["PUT"])
@require_auth
def update_permission(permission_id):
    uc = provide_permission_uc()
    user = g.current_user
    data = request.get_json() or {}
    try:
        perm = uc.update_permission(user.id, permission_id, data)
        return jsonify(perm), 200 if perm else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/<int:permission_id>", methods=["DELETE"])
@require_auth
def delete_permission(permission_id):
    uc = provide_permission_uc()
    user = g.current_user
    try:
        ok = uc.delete_permission(user.id, permission_id)
        return jsonify({"deleted": ok}), 200 if ok else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/search", methods=["GET"])
@require_auth
def search_permissions():
    uc = provide_permission_uc()
    user = g.current_user
    q = request.args.get("q", "").strip()
    try:
        result = uc.search_permissions(user.id, q)
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@permission_bp.route("/code/<string:code>", methods=["GET"])
@require_auth
def get_permission_by_code(code):
    uc = provide_permission_uc()
    user = g.current_user
    try:
        perm = uc.get_permission_by_code(user.id, code)
        return jsonify(perm), 200 if perm else 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
