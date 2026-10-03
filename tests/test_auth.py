import base64
from pathlib import Path
import sys
import time
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
import jwt
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import auth
from main import app

ISSUER = "https://test-instance.clerk.accounts.dev"
ORIGIN = "https://infoflow-ai.onrender.com"
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
client = TestClient(app)


@pytest.fixture(autouse=True)
def configure(monkeypatch, tmp_path):
    key = "pk_test_" + base64.b64encode((ISSUER.removeprefix("https://") + "$").encode()).decode()
    monkeypatch.setenv("CLERK_PUBLISHABLE_KEY", key)
    monkeypatch.setenv("CLERK_AUTHORIZED_PARTIES", ORIGIN)
    monkeypatch.setattr(auth, "signing_keys", lambda issuer: SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=PRIVATE_KEY.public_key())
    ))


def headers(key=PRIVATE_KEY, **changes):
    now = int(time.time())
    claims = {"iss": ISSUER, "sub": "user_test", "sid": "sess_test", "azp": ORIGIN,
              "iat": now, "nbf": now, "exp": now + 60}
    claims.update(changes)
    token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test"})
    return {"Authorization": "Bearer " + token}


@pytest.mark.parametrize("method,path,payload", [
    ("get", "/api/auth/me", {}),
    ("post", "/api/chat/query", {"json": {"query": "hello"}}),
    ("post", "/api/it/query", {"json": {"query": "hello"}}),
    ("post", "/api/ingest/upload", {"files": {"file": ("test.txt", b"test")}}),
    ("get", "/api/ingest/test-init", {}),
    ("get", "/api/admin/stats", {}),
    ("get", "/api/admin/vector-store-status", {}),
])
def test_all_api_routes_require_auth(method, path, payload):
    assert getattr(client, method)(path, **payload).status_code == 401


def test_valid_session_defaults_to_employee():
    response = client.get("/api/auth/me", headers=headers())
    assert response.json() == {"user_id": "user_test", "role": "Employee"}


@pytest.mark.parametrize("changes", [
    {"exp": int(time.time()) - 60},
    {"iss": "https://attacker.example"},
    {"azp": "https://attacker.example"},
    {"nbf": int(time.time()) + 120},
    {"sts": "pending"},
    {"sub": "not-a-user"},
])
def test_invalid_claims_rejected(changes):
    assert client.get("/api/auth/me", headers=headers(**changes)).status_code == 401


def test_bad_signature_rejected():
    assert client.get("/api/auth/me", headers=headers(key=OTHER_KEY)).status_code == 401


def test_malformed_token_rejected():
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_employee_cannot_upload_or_read_admin_stats():
    assert client.post("/api/ingest/upload", headers=headers(), files={"file": ("test.txt", b"test")}).status_code == 403
    assert client.get("/api/admin/stats", headers=headers()).status_code == 403
    assert client.post("/api/it/query", headers=headers(), json={"query": "hello"}).status_code == 403


@pytest.mark.parametrize("role", ["HR", "Admin"])
def test_signed_privileged_role_can_access_stats(role):
    assert client.get("/api/admin/stats", headers=headers(role=role)).status_code == 200


def test_unsafe_metadata_cannot_grant_privileges():
    assert client.get("/api/admin/stats", headers=headers(unsafe_metadata={"role": "Admin"})).status_code == 403


def test_no_key_fails_closed(monkeypatch):
    monkeypatch.delenv("CLERK_PUBLISHABLE_KEY")
    assert client.get("/api/auth/me", headers=headers()).status_code == 503
