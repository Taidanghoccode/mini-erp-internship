import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

def create_access_token(user_id, username, permissions, expires_in_hours=8 ):
    secret = current_app.config.get("SECRET_KEY", "dev-secrect-key")
    now = datetime.now(timezone.utc)
    payload={
        "sub": str(user_id),
        "username": username,
        "permissions": permissions,
        "iat": now,
        "exp": now + timedelta(hours=expires_in_hours)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def decode_access_token(token: str):
    secret = current_app.config.get("SECRET_KEY", "dev-secrect-key")
    try:
        payload=jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("Token expired")
    except jwt.InvalidTokenError:
        raise PermissionError("Invalid token")
    
