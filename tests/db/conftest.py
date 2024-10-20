import typing as t
import pytest
from postcar import config


if t.TYPE_CHECKING:
    from postcar._types import Connection


@pytest.fixture(scope="session")
def namespace() -> str:
    return "_tests"


@pytest.fixture(scope="session")
def conninfo() -> str:
    # TODO: fix, read from env or something
    return config.ConnectionInfo(
        host="127.0.0.1",
        dbname="test",
        username="postgres",
        password="1234",
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
