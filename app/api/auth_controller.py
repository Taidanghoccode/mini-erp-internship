from flask import Blueprint, request, jsonify, g
from app.utils.uc_provider import provide_auth_uc
from app.utils.auth_middleware import require_auth

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


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

        resp = jsonify(result)
        resp.set_cookie(
            "access_token",
            result["token"],
            httponly=True,
            samesite="Lax"
        )
        return resp

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    user = g.current_user
    perms = getattr(g, "current_permissions", [])
    return jsonify({
        "user": user.to_dict(),
        "permissions": perms
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    resp = jsonify({"message": "Logged out"})
    resp.delete_cookie("access_token")
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
        
        user = g.current_user
        uc = provide_auth_uc()
        result = uc.change_password(user.id, old_password, new_password)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        print("CHANGE PASSWORD ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500