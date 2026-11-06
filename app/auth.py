import hashlib
import secrets
import hmac
import time
import base64
import json
from typing import Optional
from fastapi import HTTPException, Header, Depends, status
from .database import get_db
from .config import SECRET_KEY

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()
    return f"{salt}:{pwd_hash}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    try:
        salt, stored_hash = stored_password.split(":", 1)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            provided_password.encode(),
            salt.encode(),
            100000
        ).hex()
        return hmac.compare_digest(pwd_hash, stored_hash)
    except Exception:
        return False

def create_access_token(user_id: int, email: str, role: str, name: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "name": name,
        "exp": int(time.time()) + 86400 * 7  # 7 days
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"

def decode_access_token(token: str) -> Optional[dict]:
    try:
        if not token or "." not in token:
            return None
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        # Add padding back if necessary
        pad = len(payload_b64) % 4
        if pad:
            payload_b64 += '=' * (4 - pad)
        data = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())
        if data.get("exp", 0) < int(time.time()):
            return None
        return data
    except Exception:
        return None

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, role, branch, year, section, department FROM users WHERE id = ?",
        (payload["sub"],)
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return dict(user)

def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        return None
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:].strip()
    payload = decode_access_token(token)
    if not payload:
        return None
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, role, branch, year, section, department FROM users WHERE id = ?",
        (payload["sub"],)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def require_role(allowed_roles: list):
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of roles {allowed_roles}, but current role is '{current_user.get('role')}'"
            )
        return current_user
    return role_checker

require_faculty_or_admin = require_role(["faculty", "admin"])
require_admin = require_role(["admin"])
require_student_or_higher = require_role(["student", "faculty", "admin"])

