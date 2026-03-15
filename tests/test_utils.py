import pytest
from links.database import generate_code, SHORT_CODE_LEN
from links.router import is_valid_url
import string


def test_generate_code(client):
    code = generate_code()
    assert len(code) == SHORT_CODE_LEN
    for c in code:
        if c not in string.ascii_letters and c not in string.digits:
            pytest.fail("Code chars should be ascii letters or digits")


def test_valid_url(client):
    assert is_valid_url("http://localhost/test") is True
    assert is_valid_url("https://localhost/test") is True
    assert is_valid_url("//localhost/test") is False
    assert is_valid_url("123") is False
    assert is_valid_url(None) is False
