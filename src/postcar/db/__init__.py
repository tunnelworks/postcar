import typing as t
from postcar.utils import fs
from postcar._types import Module
from postcar.db import queries


if t.TYPE_CHECKING:
    from postcar._types import Connection, StrOrHandler


async def _find_missing_migrations(
    connection: "Connection",
    package: str,
    namespace: str,
) -> t.Sequence[Module]:
    from psycopg.rows import class_row

    query = queries.preformat(query=queries.MISSING_MIGRATIONS, namespace=namespace)

    modules = fs.find_migrations(package=package)

    params = dict(package=package, files=[module.name for module in modules])

    async with connection.cursor(row_factory=class_row(Module)) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return await cursor.fetchall()


async def _namespace_exists(connection: "Connection", namespace: str) -> bool:
    from psycopg.rows import scalar_row

    query = queries.NAMESPACE_EXISTS

    params = dict(namespace=namespace)

    async with connection.cursor(row_factory=scalar_row) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return bool(await cursor.fetchone())


async def _ensure_base(connection: "Connection", namespace: str) -> None:
    if await _namespace_exists(connection=connection, namespace=namespace):
        # TODO logging: use logger
        return print(f"INFO: namespace '{namespace}' already exists, skipping")

    query = queries.preformat(query=queries.BOOKKEEPING_INIT, namespace=namespace)

    # TODO logging: use logger
    print(f"INFO: creating core schema '{namespace}'")
    await connection.execute(query)


async def _lock(connection: "Connection", namespace: str) -> None:
    query = queries.preformat(query=queries.LOCK, namespace=namespace)

    await connection.execute(query)


async def _run_operation(connection: "Connection", operation: "StrOrHandler") -> None:
    if not isinstance(operation, str):
        return await operation(connection=connection)

    await connection.execute(query=operation)


async def _one(
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
        await _lock(connection=connection, namespace=namespace)

        migrations = await _find_missing_migrations(
            connection=connection,
            package=package,
            namespace=namespace,
        )

        # TODO logging: use logger
        _suffix = "" if len(migrations) == 1 else "s"
        print(f"INFO: found {len(migrations)} pending migration{_suffix}")

        for migration in migrations:
            await _one(
                connection=connection,
                namespace=namespace,
                module=migration,
            )
