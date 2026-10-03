"""Verify Clerk session JWTs using the instance's public signing keys."""
import base64
from functools import lru_cache
import os
import re

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWKClient

bearer = HTTPBearer(auto_error=False)


def clerk_issuer():
    key = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    if not key.startswith(("pk_test_", "pk_live_")):
        raise HTTPException(503, "Clerk authentication is not configured.")
    try:
        encoded = key.split("_", 2)[2]
        domain = base64.b64decode(encoded + "=" * (-len(encoded) % 4), validate=True).decode()
        if not domain.endswith("$"):
            raise ValueError("Invalid publishable key")
        domain = domain[:-1]
        if not re.fullmatch(r"[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+", domain):
            raise ValueError("Invalid Clerk domain")
        return "https://" + domain
    except (ValueError, UnicodeError):
        raise HTTPException(503, "Clerk authentication is not configured.") from None


@lru_cache(maxsize=4)
def signing_keys(issuer):
    return PyJWKClient(issuer + "/.well-known/jwks.json", timeout=10)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        raise HTTPException(401, "Sign in to continue.", headers={"WWW-Authenticate": "Bearer"})
    issuer = clerk_issuer()
    try:
        key = signing_keys(issuer).get_signing_key_from_jwt(credentials.credentials).key
        claims = jwt.decode(
            credentials.credentials, key, algorithms=["RS256"], issuer=issuer,
            options={"require": ["exp", "nbf", "iat", "iss", "sub", "sid", "azp"], "verify_aud": False},
            leeway=5,
        )
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "Authentication is temporarily unavailable.") from None
    except jwt.PyJWTError:
        raise HTTPException(401, "Your session is invalid or expired. Sign in again.") from None
    origins = {origin.strip().rstrip("/") for origin in os.getenv(
        "CLERK_AUTHORIZED_PARTIES",
        "https://infoflow-ai.onrender.com,http://localhost:8501,http://127.0.0.1:8501",
    ).split(",") if origin.strip()}
    if claims.get("azp") not in origins or claims.get("sts") == "pending":
        raise HTTPException(401, "This session is not authorized for this application.")
    if not isinstance(claims["sub"], str) or not claims["sub"].startswith("user_"):
        raise HTTPException(401, "Invalid user session.")
    role = claims.get("role", "Employee")
    if role not in ("Employee", "HR", "IT", "Admin"):
        role = "Employee"
    return {"user_id": claims["sub"], "role": role}


def require_roles(*roles):
    def check(user=Depends(current_user)):
        if user["role"] not in roles:
            raise HTTPException(403, "You do not have permission to perform this action.")
        return user
    return check
