import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from app.utils.exception import Unauthorized

def _secret():
    return current_app.config.get("SECRET_KEY", "dev-secret-key")


def create_access_token(user_id, username, permissions, expires_in_minutes=30):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "permissions": permissions,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp())
    
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def create_refresh_token(user_id, expires_in_hours=48):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(hours=expires_in_hours)  
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_access_token(token):
    try:
        payload = jwt.decode(token, _secret(), algorithms=["HS256"])
        if payload.get("type") != "access":
            raise Unauthorized("Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise Unauthorized("Token expired")
    except jwt.InvalidTokenError:
        raise Unauthorized("Invalid token")


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, _secret(), algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise PermissionError("Invalid refresh token")
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("Refresh token expired")
    except jwt.InvalidTokenError:
        raise PermissionError("Invalid refresh token")