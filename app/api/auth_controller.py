from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_auth_uc
from app.utils.token_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.repo.user_repo import UserRepo
from app.utils.auth_middleware import require_auth

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")
user_repo = UserRepo()

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        identifier = data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            return jsonify({"error": "identifier and password are required"}), 400

        uc = provide_auth_uc()
        result = uc.login(identifier, password)

        user = result["user"]
        permissions = result["permissions"]
        token = result["token"]      
        refresh_token = create_refresh_token(user["id"])

        resp = jsonify({
            "token": token,
            "user": user,
            "permissions": permissions,
            "role_code": user["role_code"],
            "intern_id": user["intern_id"]
        })

        resp.set_cookie("access_token", token, httponly=True, samesite="Lax")
        resp.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")

        return resp

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    try:
        token = request.cookies.get("refresh_token")
        if not token:
            return jsonify({"error": "Missing refresh token"}), 401

        payload = decode_refresh_token(token)
        user_id = payload.get("sub")

        user = user_repo.get_by_id(user_id)
        if not user or user.is_deleted or not user.is_active:
            return jsonify({"error": "User invalid"}), 403

        permissions = user.permission_codes
        new_access_token = create_access_token(user.id, user.username, permissions)
        new_refresh_token = create_refresh_token(user.id)  # THÊM DÒNG NÀY

        resp = jsonify({
            "token": new_access_token,
            "user": user.to_dict(),
            "permissions": permissions,
            "role_code": user.role.code,
            "intern_id": user.intern_profile.id if user.intern_profile else None,
        })

        resp.set_cookie("access_token", new_access_token, httponly=True, samesite="Lax")
        resp.set_cookie("refresh_token", new_refresh_token, httponly=True, samesite="Lax")  # THÊM DÒNG NÀY
        
        return resp

    except Exception as e:
        print("REFRESH ERROR:", e)
        return jsonify({"error": "SESSION_EXPIRED"}), 401


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user = g.current_user
    perms = g.current_permissions

    return jsonify({
        "user": user.to_dict(),
        "permissions": perms,
        "role_code": user.role.code if user.role else None,
        "intern_id": user.intern_profile.id if user.intern_profile else None,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    resp = jsonify({"message": "Logged out"})
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp


@auth_bp.route("/change-password", methods=["POST"])
@require_auth
def change_password():
    try:
        data = request.get_json() or {}
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not old_password or not new_password:
            return jsonify({"error": "old_password and new_password are required"}), 400

        uc = provide_auth_uc()
        result = uc.change_password(g.current_user.id, old_password, new_password)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("CHANGE PASSWORD ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500