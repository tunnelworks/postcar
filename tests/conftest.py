import pytest


@pytest.fixture
def package() -> str:
    return "tests.example.migrations"


@pytest.fixture
def migration_name() -> str:
    return "0001_init"
