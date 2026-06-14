"""Юнит-тесты функций хеширования и проверки пароля."""

import pytest

from app.core.security import (
    PASSWORD_ITERATIONS,
    PASSWORD_SCHEME,
    get_password_hash,
    verify_password,
)


def test_hash_does_not_contain_plain_password():
    password = "secret-password-123"
    hashed = get_password_hash(password)
    assert password not in hashed


def test_hash_format_contains_scheme_and_iterations():
    hashed = get_password_hash("any-password")
    parts = hashed.split("$")
    assert len(parts) == 4
    scheme, iterations, salt, digest = parts
    assert scheme == PASSWORD_SCHEME
    assert int(iterations) == PASSWORD_ITERATIONS
    assert len(salt) > 0
    assert len(digest) > 0


def test_repeated_hashing_produces_different_results_due_to_salt():
    password = "same-password"
    first = get_password_hash(password)
    second = get_password_hash(password)
    assert first != second


def test_correct_password_verifies_successfully():
    password = "correct-horse-battery-staple"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True


def test_incorrect_password_fails_verification():
    hashed = get_password_hash("real-password")
    assert verify_password("fake-password", hashed) is False


def test_empty_password_does_not_match_real_one():
    hashed = get_password_hash("real-password")
    assert verify_password("", hashed) is False


def test_malformed_hash_returns_false():
    assert verify_password("any-password", "not-a-valid-hash") is False


def test_unsupported_scheme_returns_false():
    fake_hash = f"argon2$1000$salt$digest"
    assert verify_password("any-password", fake_hash) is False


@pytest.mark.parametrize(
    "password",
    [
        "a",
        "short",
        "MediumLength123",
        "a-very-long-password-with-special-chars-!@#$%^&*()",
        "пароль-на-русском",
        "пароль с пробелами и символами №%:?*",
    ],
)
def test_hash_and_verify_round_trip_for_various_passwords(password):
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
