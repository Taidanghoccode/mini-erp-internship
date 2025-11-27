from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_user_uc
from app.utils.auth_middleware import require_auth

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")


@user_bp.route("/", methods=["GET"])
@require_auth
def get_all_users():
    uc = provide_user_uc()
    user = g.current_user
    try:
        users = uc.get_all_users(user.id)
        return jsonify(users), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    uc = provide_user_uc()
    user = g.current_user
    try:
        result = uc.get_user_by_id(user.id, user_id)
        return (jsonify(result), 200) if result else (jsonify({"error": "User not found"}), 404)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/", methods=["POST"])
@require_auth
def create_user():
    uc = provide_user_uc()
    user = g.current_user

    try:
        data = request.get_json() or {}

        rid = data.get("role_id")
        if rid in ("", None, "null"):
            data["role_id"] = None
        else:
            data["role_id"] = int(rid)

        created = uc.create_user(user.id, data)
        return jsonify(created), 201

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/<int:user_id>", methods=["PUT"])
@require_auth
def update_user(user_id):
    uc = provide_user_uc()
    user = g.current_user

    try:
        data = request.get_json() or {}

        rid = data.get("role_id", "__keep__")

        if rid != "__keep__":
            if rid in ("", None, "null"):
                data["role_id"] = None
            else:
                data["role_id"] = int(rid)

        updated = uc.update_user(user.id, user_id, data)
        return (jsonify(updated), 200) if updated else (jsonify({"error": "User not found"}), 404)

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@require_auth
def delete_user(user_id):
    uc = provide_user_uc()
    user = g.current_user

    try:
        deleted = uc.delete_user(user.id, user_id)
        return (jsonify({"deleted": deleted}), 200) if deleted else (jsonify({"error": "User not found"}), 404)

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/profile", methods=["GET"])
@require_auth
def get_my_profile():
    uc = provide_user_uc()
    user = g.current_user
    try:
        result = uc.get_profile(user.id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
