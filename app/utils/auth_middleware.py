from functools import wraps
from flask import request, jsonify, g
from sqlalchemy.orm import joinedload
from app.models.role import Role
from app.utils.token_service import decode_access_token
from app.models.user import User
from app.utils.exception import Unauthorized, PermissionDenied
from app.repo.permission_repo import PermissionRepo

permission_repo = PermissionRepo()


def load_user():
    if hasattr(g, "current_user") and g.current_user:
        return g.current_user

    token = None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise Unauthorized("Missing access token")

    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))

    user = (
        User.query.options(joinedload(User.role).joinedload(Role.permissions))
        .filter(
            User.id == user_id,
            User.is_deleted == False,
            User.is_active == True
        )
        .first()
    )

    if not user:
        raise Unauthorized("User inactive or deleted")

    g.current_user = user
    g.current_permissions = [p.code for p in user.role.permissions] if user.role else []

    return user


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            load_user()
        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception:
            return jsonify({"error": "SESSION_EXPIRED"}), 401

        return f(*args, **kwargs)

    return wrapper


def require_permission(code):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                user = load_user()

                if code in g.current_permissions:
                    return f(*args, **kwargs)

                has_perm = permission_repo.user_has_permission(user.role_id, code)
                if not has_perm:
                    raise PermissionDenied(f"Missing permission: {code}")

            except Unauthorized as e:
                return jsonify({"error": str(e)}), 401

            except PermissionDenied as e:
                return jsonify({"error": str(e)}), 403

            except Exception:
                return jsonify({"error": "SESSION_EXPIRED"}), 401

            return f(*args, **kwargs)

        return wrapper
    return decorator
