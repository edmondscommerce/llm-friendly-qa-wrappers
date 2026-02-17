"""Tests that fail."""


def test_bad_math():
    assert 1 + 1 == 3


def test_bad_string():
    assert "hello" == "world"


def test_passes():
    assert True
