"""Юнит-тесты функций создания и проверки JWT-токенов."""

import time

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    decode_token,
    hash_token,
)


def test_access_token_has_three_segments_separated_by_dots():
    token = create_access_token("user-123", "admin")
    assert token.count(".") == 2


def test_access_token_round_trip_preserves_user_id_and_role():
    token = create_access_token("user-abc", "patient")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["role"] == "patient"
    assert payload["type"] == "access"


def test_refresh_token_round_trip_preserves_user_id():
    token = create_refresh_token("user-xyz")
    payload = decode_refresh_token(token)
    assert payload["sub"] == "user-xyz"
    assert payload["type"] == "refresh"


def test_access_token_cannot_be_decoded_as_refresh():
    token = create_access_token("user-1", "admin")
    with pytest.raises(ValueError):
        decode_refresh_token(token)


def test_refresh_token_cannot_be_decoded_as_access():
    token = create_refresh_token("user-1")
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_token_with_tampered_signature_is_rejected():
    token = create_access_token("user-1", "admin")
    tampered = token[:-4] + "XXXX"
    with pytest.raises(ValueError):
        decode_token(tampered)


def test_token_with_tampered_payload_is_rejected():
    token = create_access_token("user-1", "patient")
    header, _payload, signature = token.split(".")
    fake_payload = "eyJzdWIiOiJoYWNrZXIiLCJyb2xlIjoiYWRtaW4ifQ"
    forged_token = f"{header}.{fake_payload}.{signature}"
    with pytest.raises(ValueError):
        decode_token(forged_token)


def test_malformed_token_with_wrong_segment_count_is_rejected():
    with pytest.raises(ValueError):
        decode_token("only.two-segments")


def test_two_tokens_for_same_user_are_different_due_to_iat():
    first = create_access_token("user-1", "admin")
    time.sleep(1.1)
    second = create_access_token("user-1", "admin")
    assert first != second


def test_hash_token_is_deterministic():
    raw = "some-refresh-token-value"
    assert hash_token(raw) == hash_token(raw)


def test_hash_token_changes_with_input():
    assert hash_token("token-a") != hash_token("token-b")


def test_hash_token_returns_hex_string_of_correct_length():
    digest = hash_token("any-token")
    assert len(digest) == 64
    int(digest, 16)
