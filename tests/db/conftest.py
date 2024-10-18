import typing as t
import pytest
from postcar.config import Config
from postcar.db import migrations


if t.TYPE_CHECKING:
    from postcar._types import Connection


@pytest.fixture(scope="session")
def namespace() -> str:
    return "_tests"


@pytest.fixture(scope="session")
def config(package: str, namespace: str) -> Config:
    # TODO: fix
    return Config(
        package=package,
        host="127.0.0.1",
        port=5432,
        password="1234",
        username="postgres",
        dbname="test",
        namespace=namespace,
    )


@pytest.fixture(scope="session")
async def connection(config: Config) -> t.AsyncGenerator["Connection", None]:
    from psycopg import AsyncConnection

    async with await AsyncConnection.connect(conninfo=config.conninfo) as connection:
        await migrations._ensure_base(connection=connection, namespace=config.namespace)

        yield connection

        await connection.execute(f"drop schema {config.namespace} cascade")
