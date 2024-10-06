import re

import pytest

import backup.utils as backup_utils
import utils as base_utils
from tests.fixtures import module


class TestClass:
    pass


def test_to_bool():
    """Test that the to_bool function converts a string to a boolean."""
    assert base_utils.to_bool("true") is True
    assert base_utils.to_bool("false") is False
    assert base_utils.to_bool("True") is True
    assert base_utils.to_bool("False") is False
    assert base_utils.to_bool("1") is True
    assert base_utils.to_bool("0") is False
    assert base_utils.to_bool("yes") is True
    assert base_utils.to_bool("no") is False
    assert base_utils.to_bool("on") is True
    assert base_utils.to_bool("off") is False


def test_to_upper():
    """Test that the to_upper function converts a string to uppercase."""
    assert base_utils.to_upper("hello, world!") == "HELLO, WORLD!"


def test_get_class_success():
    """Test that the get_class function can import a class from a module."""
    assert backup_utils.get_class("tests.utils.test_utils.TestClass") == TestClass


def test_get_class_invalid_module():
    """Test that the get_class function raises an ImportError when the module
    cannot be imported.
    """
    with pytest.raises(ImportError):
        backup_utils.get_class("tests.utils.module_does_not_exist.TestClass")


def test_get_class_invalid_class():
    """Test that the get_class function raises an ImportError when the class
    cannot be found in the imported module.
    """
    with pytest.raises(ImportError):
        backup_utils.get_class("tests.utils.test_utils.TestClassDoesNotExist")


def test_get_backup_name():
    """Test that the get_backup_name function returns the correct backup name."""
    name = backup_utils.get_backup_name("test")

    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}", name) is not None
    assert "." not in name


def test_mask_sensitive_data():
    """Test that the mask_sensitive_data function masks sensitive data in a string."""
    # simple dict.
    assert backup_utils.mask_sensitive_data({"password": "secret"}) == {
        "password": "********"
    }
    # nested dict.
    assert backup_utils.mask_sensitive_data({"api": {"key": "secret"}}) == {
        "api": {"key": "********"}
    }
    # nested list.
    assert backup_utils.mask_sensitive_data({"api": [{"key": "secret"}]}) == {
        "api": [{"key": "********"}]
    }
    # simple data (like a string present).
    assert backup_utils.mask_sensitive_data(
        {"password": "secret", "scopes": ["read", "write"]}
    ) == {
        "password": "********",
        "scopes": ["read", "write"],
    }


def test_format_object():
    """Test that the format_object function formats objects as a string."""
    assert (
        backup_utils.format_object(module)
        == "\n'MODULE_VAR_ONE': 1, 'MODULE_VAR_TWO': 2"
    )
