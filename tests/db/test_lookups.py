import typing as t
import pytest
from postcar.db import lookups
from postcar._types import Module


if t.TYPE_CHECKING:
    from postcar._types import Connection
    from postcar.config import Config


@pytest.mark.db
async def test_find_missing_migrations(
    connection: "Connection",
    config: "Config",
    package: str,
    migration_name: str,
) -> None:
    result = await lookups.find_missing_migrations(
        connection=connection,
        package=package,
        namespace=config.namespace,
    )

    assert Module(name=migration_name, package=package) in result
