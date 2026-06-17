from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response

from app.api.routers import auth
from app.models import UserRole
from app.schemas import LoginRequest


def _user(role: UserRole) -> SimpleNamespace:
    return SimpleNamespace(
        id="user-1",
        full_name="Test User",
        phone="+77000000000",
        email=None,
        password_hash="hash",
        role=role,
        created_at=None,
    )


def test_admin_login_issues_token_for_admin_phone(monkeypatch):
    admin_user = _user(UserRole.ADMIN)
    payload = LoginRequest(phone=admin_user.phone, password="password")
    expected = {
        "accessToken": "token",
        "tokenType": "Bearer",
        "expiresIn": 1800,
        "role": "admin",
        "user": {"id": admin_user.id, "role": "admin"},
        "_refreshToken": "refresh",
        "_remember": True,
    }

    monkeypatch.setattr(auth.auth_service, "login_admin", lambda db, payload: expected)

    result = auth.login_admin(payload, Response(), object())
    assert result["accessToken"] == "token"
    assert result["role"] == "admin"


def test_admin_login_issues_token_for_admin_email(monkeypatch):
    admin_user = _user(UserRole.ADMIN)
    payload = LoginRequest(phone="admin@beatris.kz", password="password")
    captured = {}

    def mock_login_admin(db, payload):
        captured["identifier"] = payload.phone
        return {
            "accessToken": "token",
            "tokenType": "Bearer",
            "expiresIn": 1800,
            "role": "admin",
            "user": {"id": admin_user.id, "role": "admin"},
            "_refreshToken": "refresh",
            "_remember": True,
        }

    monkeypatch.setattr(auth.auth_service, "login_admin", mock_login_admin)

    result = auth.login_admin(payload, Response(), object())

    assert captured["identifier"] == "admin@beatris.kz"
    assert result["user"]["role"] == "admin"


@pytest.mark.parametrize("role", [UserRole.PATIENT, UserRole.DOCTOR])
def test_admin_login_rejects_non_admin_roles(monkeypatch, role):
    non_admin_user = _user(role)
    payload = LoginRequest(phone=non_admin_user.phone, password="password")

    monkeypatch.setattr(auth.auth_service, "login_admin", lambda db, payload: (_ for _ in ()).throw(ValueError("invalid_credentials")))

    with pytest.raises(HTTPException) as exc:
        auth.login_admin(payload, Response(), object())

    assert exc.value.status_code == 401


def test_admin_login_rejects_wrong_password(monkeypatch):
    admin_user = _user(UserRole.ADMIN)
    payload = LoginRequest(phone=admin_user.phone, password="wrong")

    monkeypatch.setattr(auth.auth_service, "login_admin", lambda db, payload: (_ for _ in ()).throw(ValueError("invalid_credentials")))

    with pytest.raises(HTTPException) as exc:
        auth.login_admin(payload, Response(), object())

    assert exc.value.status_code == 401
