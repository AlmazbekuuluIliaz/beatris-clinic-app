from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response

from app.api.routers import admin_auth
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
        "user": {"id": admin_user.id, "role": "admin"},
    }

    monkeypatch.setattr(admin_auth.repositories, "get_user_by_phone_or_email", lambda db, identifier: admin_user)
    monkeypatch.setattr(admin_auth, "verify_password", lambda password, password_hash: True)
    monkeypatch.setattr(admin_auth, "_issue_auth_response", lambda db, response, user, remember=True: expected)

    assert admin_auth.login_admin(payload, Response(), object()) == expected


def test_admin_login_issues_token_for_admin_email(monkeypatch):
    admin_user = _user(UserRole.ADMIN)
    payload = LoginRequest(phone="admin@beatris.kz", password="password")
    captured = {}

    def get_user_by_phone_or_email(db, identifier):
        captured["identifier"] = identifier
        return admin_user

    monkeypatch.setattr(admin_auth.repositories, "get_user_by_phone_or_email", get_user_by_phone_or_email)
    monkeypatch.setattr(admin_auth, "verify_password", lambda password, password_hash: True)
    monkeypatch.setattr(
        admin_auth,
        "_issue_auth_response",
        lambda db, response, user, remember=True: {
            "accessToken": "token",
            "tokenType": "Bearer",
            "expiresIn": 1800,
            "user": {"id": user.id, "role": "admin"},
        },
    )

    result = admin_auth.login_admin(payload, Response(), object())

    assert captured["identifier"] == "admin@beatris.kz"
    assert result["user"]["role"] == "admin"


@pytest.mark.parametrize("role", [UserRole.PATIENT, UserRole.DOCTOR])
def test_admin_login_rejects_non_admin_roles(monkeypatch, role):
    non_admin_user = _user(role)
    payload = LoginRequest(phone=non_admin_user.phone, password="password")

    monkeypatch.setattr(admin_auth.repositories, "get_user_by_phone_or_email", lambda db, identifier: non_admin_user)
    monkeypatch.setattr(admin_auth, "verify_password", lambda password, password_hash: True)

    with pytest.raises(HTTPException) as exc:
        admin_auth.login_admin(payload, Response(), object())

    assert exc.value.status_code == 401


def test_admin_login_rejects_wrong_password(monkeypatch):
    admin_user = _user(UserRole.ADMIN)
    payload = LoginRequest(phone=admin_user.phone, password="wrong")

    monkeypatch.setattr(admin_auth.repositories, "get_user_by_phone_or_email", lambda db, identifier: admin_user)
    monkeypatch.setattr(admin_auth, "verify_password", lambda password, password_hash: False)

    with pytest.raises(HTTPException) as exc:
        admin_auth.login_admin(payload, Response(), object())

    assert exc.value.status_code == 401
