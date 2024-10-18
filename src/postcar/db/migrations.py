import typing as t
from postcar.utils import fs
from postcar._types import Module
from postcar.db import lookups, queries


if t.TYPE_CHECKING:
    from postcar._types import Connection, StrOrHandler


async def lock(connection: "Connection", namespace: str) -> None:
    query = queries.preformat(query=queries.LOCK, namespace=namespace)

    await connection.execute(query)


async def _ensure_base(connection: "Connection", namespace: str) -> None:
    if await lookups.namespace_exists(connection=connection, namespace=namespace):
        # TODO logging: use logger
        return print(f"INFO: namespace '{namespace}' already exists, skipping")

    query = queries.preformat(query=queries.BOOKKEEPING_INIT, namespace=namespace)

    # TODO logging: use logger
    print(f"INFO: creating core schema '{namespace}'")
    await connection.execute(query)


async def _run_operation(connection: "Connection", operation: "StrOrHandler") -> None:
    if not isinstance(operation, str):
        return await operation(connection=connection)

    await connection.execute(query=operation)


async def migrate(
    connection: "Connection",
    namespace: str,
    module: Module,
    revert: bool = False,
) -> None:
    migration = fs.load_migration(module=module)
    operation = migration.revert if revert else migration.forward

    _query = queries.BOOKKEEPING_UPDATE
    query = queries.preformat(
        query=_query.rollback if revert else _query.forward,
        namespace=namespace,
    )

    # TODO logging: use logger
    print(f"INFO: running migration '{module}'")

    await _run_operation(connection=connection, operation=operation)
    await connection.execute(
        query=query,
        params=dict(name=module.name),
    )


async def run(
    connection: "Connection",
    package: str,
    namespace: str,
    dry_run: bool = False,
) -> None:
    if dry_run:
        # TODO logging: use logger
        print("INFO: dry-run enabled")

    async with connection.transaction(force_rollback=dry_run):
        await _ensure_base(connection=connection, namespace=namespace)
        await lock(connection=connection, namespace=namespace)

        migrations = await lookups.find_missing_migrations(
            connection=connection,
            package=package,
            namespace=namespace,
        )

        # TODO logging: use logger
        _suffix = "" if len(migrations) == 1 else "s"
        print(f"INFO: found {len(migrations)} pending migration{_suffix}")

        for migration in migrations:
            await migrate(
                connection=connection,
                namespace=namespace,
                module=migration,
            )
