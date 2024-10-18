import typing as t
import pytest
from postcar._types import Module
from postcar.db import lookups


if t.TYPE_CHECKING:
    from postcar._types import Connection


@pytest.mark.db
async def test_find_missing_migrations(
    connection: "Connection",
    namespace: str,
    package: str,
    migration_name: str,
) -> None:
    result = await lookups.find_missing_migrations(
        connection=connection,
        package=package,
        namespace=namespace,
    )

    assert Module(name=migration_name, package=package) in result
