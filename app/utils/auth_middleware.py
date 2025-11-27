from functools import wraps
from flask import request, jsonify, g
from app.utils.token_service import decode_access_token
from app.repo.user_repo import UserRepo
from app.repo.permission_repo import PermissionRepo


permission_repo = PermissionRepo()
user_repo = UserRepo()

def get_current_user_from_token():
    token = None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise PermissionError("Missing or invalid Authorization header")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise PermissionError("Invalid token payload")

    user = user_repo.get_by_id(user_id)
    if not user or user.is_deleted or not user.is_active:
        raise PermissionError("User not found or inactive")

    g.current_user = user
    g.current_permissions = payload.get("permissions", [])
    g.current_intern = user.intern_profile

    return user


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            get_current_user_from_token()
        except PermissionError as e:
            return jsonify({"error": str(e)}), 401
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


def require_permission(permission_code):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                user = get_current_user_from_token()
                if not permission_repo.user_has(user.id, permission_code):
                    return jsonify({"error": f"No permission: {permission_code}"}), 403
            except PermissionError as e:
                return jsonify({"error": str(e)}), 401
            except Exception:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator
