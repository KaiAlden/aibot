from fastapi.testclient import TestClient

from app.api.v1.routes import auth as auth_route
from app.main import app
from app.models.tenant import User, UserRole
from app.services.auth import AuthError, create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_roundtrip() -> None:
    password_hash = hash_password("secret123")

    assert verify_password("secret123", password_hash) is True
    assert verify_password("wrong", password_hash) is False


def test_access_token_roundtrip() -> None:
    token = create_access_token("8", UserRole.merchant_admin.value, tenant_id=7)

    payload = decode_access_token(token)

    assert payload["sub"] == "8"
    assert payload["role"] == UserRole.merchant_admin.value
    assert payload["tenant_id"] == 7


def test_access_token_rejects_tampering() -> None:
    token = create_access_token("8", UserRole.merchant_admin.value, tenant_id=7)
    bad_token = token[:-1] + ("a" if token[-1] != "a" else "b")

    try:
        decode_access_token(bad_token)
    except AuthError:
        pass
    else:
        raise AssertionError("tampered token should be rejected")


def test_login_returns_token(monkeypatch) -> None:
    user = User(
        id=3,
        username="merchant",
        password_hash=hash_password("secret123"),
        role=UserRole.merchant_admin,
        tenant_id=7,
        is_active=True,
    )
    monkeypatch.setattr(auth_route, "get_user_by_username", lambda db, username: user)
    client = TestClient(app)

    response = client.post("/api/v1/auth/login", json={"username": "merchant", "password": "secret123"})

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["role"] == UserRole.merchant_admin.value
    assert data["tenant_id"] == 7
    assert decode_access_token(data["access_token"])["sub"] == "3"
