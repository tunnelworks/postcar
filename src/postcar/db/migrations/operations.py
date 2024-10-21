import typing as t
from postcar.config import defaults
from postcar.db import lookups, queries


if t.TYPE_CHECKING:
    from postcar._types import Connection, Module, Version


# MARK: routines


async def lock(connection: "Connection", namespace: str) -> None:
    query = queries.preformat(query=queries.LOCK, namespace=namespace)

    await connection.execute(query)


async def _ensure_namespace(connection: "Connection", namespace: str) -> None:
    if await lookups.namespace_exists(connection=connection, namespace=namespace):
        # TODO logging: use logger
        return print(f"DEBUG: namespace '{namespace}' exists, skipping")

    # TODO logging: use logger
    print(f"DEBUG: creating core schema '{namespace}'")

    query = queries.preformat(query=queries.CREATE_NAMESPACE, namespace=namespace)
    await connection.execute(query=query)


async def _ensure_versioning(connection: "Connection", namespace: str) -> None:
    if await lookups.table_exists(connection, namespace=namespace, table="_version"):
        # TODO logging: use logger
        return print(f"DEBUG: versioning for '{namespace}' exists, skipping")

    # TODO logging: use logger
    print(f"DEBUG: creating versioning table for '{namespace}'")

    query = queries.preformat(query=queries.CREATE_VERSIONING, namespace=namespace)
    await connection.execute(query=query)


async def _update_version(
    connection: "Connection",
    namespace: str,
    version: "Version",
) -> None:
    # TODO logging: use logger
    print(f"DEBUG: updating version for '{namespace}' to {version}")

    query = queries.preformat(query=queries.UPDATE_VERSION, namespace=namespace)
    await connection.execute(
        query=query,
        params=dict(
            major=version.major,
            minor=version.minor,
        ),
    )


async def _run_internal_migrations(connection: "Connection", namespace: str) -> None:
    from postcar.db.migrations import versions

    version = await lookups.find_version(connection=connection, namespace=namespace)

    for migration in versions.get_migrations(version=version):
        # TODO logging: use logger
        print(f"DEBUG: migrating '{namespace}' to {version}")
        query = queries.preformat(query=migration.query, namespace=namespace)
        await connection.execute(query=query)

        await _update_version(
            connection=connection,
            namespace=namespace,
            version=migration.version,
        )


async def _ensure_base(connection: "Connection", namespace: str) -> None:
    await _ensure_namespace(connection=connection, namespace=namespace)
    await _ensure_versioning(connection=connection, namespace=namespace)


async def migrate(
    connection: "Connection",
    namespace: str,
    module: "Module",
    revert: bool = False,
) -> None:
    from postcar.utils import fs

    cls = fs.load_migration(module=module)
    migration = cls(module=module, connection=connection)

    _query = queries.UPDATE_BOOKKEEPING
    query = queries.preformat(
        query=_query.rollback if revert else _query.forward,
        namespace=namespace,
    )

    # TODO logging: use logger
    print(f"INFO: running migration '{module}'")

    await migration.run(rollback=revert)

    await connection.execute(
        query=query,
        params=dict(
            package=module.package,
            name=module.name,
        ),
    )


async def run(
    connection: "Connection",
    package: str,
    namespace: str = defaults.DEFAULT_NAMESPACE,
    dry_run: bool = False,
) -> None:
    if dry_run:
        # TODO logging: use logger
        print("INFO: dry-run enabled")

    async with connection.transaction(force_rollback=dry_run):
        await _ensure_base(connection=connection, namespace=namespace)
        await lock(connection=connection, namespace=namespace)
        await _run_internal_migrations(connection=connection, namespace=namespace)

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
