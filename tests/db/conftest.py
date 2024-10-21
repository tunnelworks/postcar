import os
import typing as t
import pytest
from postcar import config


if t.TYPE_CHECKING:
    from postcar._types import Connection


@pytest.fixture(scope="session")
def namespace() -> str:
    return "_tests"


@pytest.fixture(scope="session")
def host() -> str:
    return os.getenv("POSTGRES_HOST", "127.0.0.1")


@pytest.fixture(scope="session")
def dbname() -> str:
    return os.getenv("POSTGRES_DB", "test")


@pytest.fixture(scope="session")
def username() -> str:
    return os.getenv("POSTGRES_USER", "postgres")


@pytest.fixture(scope="session")
def password() -> str:
    return os.getenv("POSTGRES_PASSWORD", "1234")


@pytest.fixture(scope="session")
def conninfo(
    host: str,
    dbname: str,
    username: str,
    password: str,
) -> str:
    return config.ConnectionInfo(
        host=host,
        dbname=dbname,
        username=username,
        password=password,
    ).conninfo


@pytest.fixture(scope="session")
async def connection(
    conninfo: str,
    namespace: str,
) -> t.AsyncGenerator["Connection", None]:
    from postcar.db.connections import connect
    from postcar.db.migrations.operations import (
        _ensure_base,
        _run_internal_migrations,
        lock,
    )

    async with connect(conninfo=conninfo) as connection:
        async with connection.transaction():
            await _ensure_base(connection=connection, namespace=namespace)
            await lock(connection=connection, namespace=namespace)
            await _run_internal_migrations(connection=connection, namespace=namespace)

        yield connection

        await connection.execute(f"drop schema {namespace} cascade")
