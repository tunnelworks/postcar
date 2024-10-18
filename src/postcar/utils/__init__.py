import importlib
import typing as t
from psycopg import sql
from postcar.utils import fs
from postcar._types import Module


if t.TYPE_CHECKING:
    from postcar._types import Connection
    from postcar.config import Config

    class _Handler(t.Protocol):
        async def __call__(self, connection: Connection) -> None: ...

    StrOrHandler = t.Union[str, _Handler]

    class _Migration(t.NamedTuple):
        forward: StrOrHandler
        revert: StrOrHandler


async def _find_missing_migrations(
    connection: "Connection",
    package: str,
    namespace: str,
) -> t.Sequence["Module"]:
    from psycopg.rows import class_row

    query = sql.SQL("""--sql
      with "_f" as (select unnest(%(files)s::text[]) as "name")
      select
        %(package)s as "package",
        "_f"."name"
      from "_f"
      left join {namespace}."_migration" as "_m"
        on "_f"."name" = "_m"."name"
          and "_m"."reverted_at" is null
      where "_m"."name" is null;
    """).format(namespace=sql.Identifier(namespace))

    modules = fs.find_migrations(package=package)

    params = dict(package=package, files=[module.name for module in modules])

    async with connection.cursor(row_factory=class_row(Module)) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return await cursor.fetchall()


async def _namespace_exists(connection: "Connection", namespace: str) -> bool:
    from psycopg.rows import scalar_row

    query = """--sql
      select count(*) from "pg_namespace" where "nspname" = %(namespace)s;
    """

    params = dict(namespace=namespace)

    async with connection.cursor(row_factory=scalar_row) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return bool(await cursor.fetchone())


def _get_migration(module: Module) -> "_Migration":
    _module = importlib.import_module(name=f".{module.name}", package=module.package)

    if not (hasattr(_module, "forward") and hasattr(_module, "revert")):
        raise AttributeError(f"{module}: both forward and revert must exist")

    return t.cast("_Migration", _module)


def _get_bookkeeping_update(revert: bool) -> sql.SQL:
    if revert:
        return sql.SQL("""--sql
          update {namespace}."_migration"
            set "reverted_at" = current_timestamp
            where "name" = %(name)s
              and "reverted_at" is null;
        """)

    return sql.SQL("""--sql
      insert into {namespace}."_migration" ("name")
        values (%(name)s);
    """)


async def _ensure_base(connection: "Connection", namespace: str) -> None:
    if await _namespace_exists(connection=connection, namespace=namespace):
        # TODO logging: use logger
        return print(f"INFO: namespace '{namespace}' already exists, skipping")

    template = sql.SQL("""--sql
    create schema {namespace};

    create table {namespace}."_migration" (
      "pk" integer generated always as identity primary key,
      "name" text not null,
      "created_at" timestamptz not null default CURRENT_TIMESTAMP,
      "reverted_at" timestamptz
    );

    create unique index "_distinct_migration_name"
      on {namespace}."_migration" ("name")
        where "reverted_at" is null;
    """).format(namespace=sql.Identifier(namespace))

    # TODO logging: use logger
    print(f"INFO: creating core schema '{namespace}'")
    await connection.execute(template)


async def _lock(connection: "Connection", namespace: str) -> None:
    template = sql.SQL("""--sql
      lock table {namespace}."_migration" in access exclusive mode nowait;
    """).format(namespace=sql.Identifier(namespace))

    await connection.execute(template)


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
    migration = _get_migration(module=module)
    operation = migration.revert if revert else migration.forward
    bookkeeping = _get_bookkeeping_update(revert=revert)

    # TODO logging: use logger
    print(f"INFO: running migration '{module}'")

    await _run_operation(connection=connection, operation=operation)
    await connection.execute(
        query=bookkeeping.format(namespace=sql.Identifier(namespace)),
        params=dict(name=module.name),
    )


async def run(
    connection: "Connection",
    config: "Config",
    dry_run: bool = False,
) -> None:
    if dry_run:
        # TODO logging: use logger
        print("INFO: dry-run enabled")

    async with connection.transaction(force_rollback=dry_run):
        await _ensure_base(connection=connection, namespace=config.namespace)
        await _lock(connection=connection, namespace=config.namespace)

        migrations = await _find_missing_migrations(
            connection=connection,
            package=config.package,
            namespace=config.namespace,
        )

        # TODO logging: use logger
        _suffix = "" if len(migrations) == 1 else "s"
        print(f"INFO: found {len(migrations)} pending migration{_suffix}")

        for migration in migrations:
            await _one(
                connection=connection,
                namespace=config.namespace,
                module=migration,
            )
