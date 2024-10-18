import pytest


@pytest.fixture(scope="session")
def package() -> str:
    return "tests.example.migrations"


@pytest.fixture(scope="session")
def invalid_package() -> str:
    return "tests.example.invalid"


@pytest.fixture(scope="session")
def migration_name() -> str:
    return "0001_init"
