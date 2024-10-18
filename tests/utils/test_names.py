import typing as t
import pytest
from postcar.utils import names


_VALID_NAMES = (
    "0000_zero",
    "0001_whatever",
    "0001_with_multiple_words",
    "9999_last",
)


_INVALID_NAMES = (
    "just_a_string",
    "111_short",
    "11_shorter",
    "1_shortest",
    "1234_hyphenated-name",
    "_underscore",
    "word",
    "1234_with.period",
)


@pytest.fixture(params=_VALID_NAMES)
def valid_name(request: "pytest.FixtureRequest") -> str:
    return t.cast(str, request.param)


@pytest.fixture(params=_INVALID_NAMES)
def invalid_name(request: "pytest.FixtureRequest") -> str:
    return t.cast(str, request.param)


def test_valid_patterns(valid_name: str) -> None:
    assert names.MIGRATION_PATTERN.match(valid_name) is not None


def test_invalid_patterns(invalid_name: str) -> None:
    assert names.MIGRATION_PATTERN.match(invalid_name) is None
