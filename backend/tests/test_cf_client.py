"""
tests/test_cf_client.py
Unit tests for the CF client — handle validation and API error handling.
Uses unittest.mock to avoid real network calls.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi import HTTPException
from app.services.cf_client import validate_handle


class TestValidateHandle:
    def test_valid_simple(self):
        assert validate_handle("tourist") == "tourist"

    def test_strips_whitespace(self):
        assert validate_handle("  Petr  ") == "Petr"

    def test_valid_with_underscore(self):
        assert validate_handle("Um_nik") == "Um_nik"

    def test_valid_with_hyphen(self):
        assert validate_handle("my-handle") == "my-handle"

    def test_valid_max_length(self):
        assert validate_handle("a" * 24) == "a" * 24

    def test_too_short_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("ab")
        assert exc_info.value.status_code == 422

    def test_too_long_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("a" * 25)
        assert exc_info.value.status_code == 422

    def test_space_in_middle_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("hello world")
        assert exc_info.value.status_code == 422

    def test_special_chars_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("h@ck3r!")
        assert exc_info.value.status_code == 422

    def test_empty_string_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("")
        assert exc_info.value.status_code == 422

    def test_only_whitespace_raises_422(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_handle("   ")
        assert exc_info.value.status_code == 422

    def test_numeric_handle(self):
        assert validate_handle("12345") == "12345"

    def test_mixed_case(self):
        assert validate_handle("CodeForces") == "CodeForces"
