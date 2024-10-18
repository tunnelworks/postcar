import typing as t
import pytest
from postcar.db import lookups, migrations
from postcar._types import Module


if t.TYPE_CHECKING:
    from postcar._types import Connection
    from postcar.config import Config


@pytest.mark.db
async def test_migrate_one(
    connection: "Connection",
    config: "Config",
    package: str,
    migration_name: str,
) -> None:
    module = Module(name=migration_name, package=package)

    async with connection.transaction(force_rollback=True):
        result = await lookups.find_missing_migrations(
            connection=connection,
            package=package,
            namespace=config.namespace,
        )

        assert module in result

        await migrations.migrate(
            connection=connection,
            namespace=config.namespace,
            module=module,
        )

        result = await lookups.find_missing_migrations(
            connection=connection,
            package=package,
            namespace=config.namespace,
        )
        assert module not in result

        await migrations.migrate(
            connection=connection,
            namespace=config.namespace,
            module=module,
            revert=True,
        )

        result = await lookups.find_missing_migrations(
            connection=connection,
            package=package,
            namespace=config.namespace,
        )
        assert module in result


@pytest.mark.db
async def test_migrate(
    connection: "Connection", config: "Config", package: str
) -> None:
    await migrations.run(
        connection=connection,
        package=package,
        namespace=config.namespace,
        dry_run=True,
    )
