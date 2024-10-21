import typing as t
from postcar._types import Module, Version
from postcar.config import defaults
from postcar.db import queries
from postcar.utils import fs


if t.TYPE_CHECKING:
    from postcar._types import Connection
    from postcar.db.queries import TableName


async def _exists(
    connection: "Connection",
    query: str,
    params: t.Mapping[str, str],
) -> bool:
    from psycopg.rows import scalar_row

    async with connection.cursor(row_factory=scalar_row) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return bool(await cursor.fetchone())


async def namespace_exists(connection: "Connection", namespace: str) -> bool:
    return await _exists(
        connection=connection,
        query=queries.NAMESPACE_EXISTS,
        params=dict(namespace=namespace),
    )


async def table_exists(
    connection: "Connection",
    namespace: str,
    table: "TableName",
) -> bool:
    return await _exists(
        connection=connection,
        query=queries.TABLE_EXISTS,
        params=dict(namespace=namespace, table=table),
    )


async def find_version(
    connection: "Connection",
    namespace: str = defaults.DEFAULT_NAMESPACE,
) -> t.Optional[Version]:
    from psycopg.rows import class_row

    _query = """--sql
      select "major", "minor" from {namespace}."_version"
      order by "major" desc, "minor" desc
      limit 1;
    """

    query = queries.preformat(query=_query, namespace=namespace)

    async with connection.cursor(row_factory=class_row(Version)) as cursor:
        await cursor.execute(query=query, prepare=True)
        return await cursor.fetchone()


async def find_missing_migrations(
    connection: "Connection",
    package: str,
    namespace: str = defaults.DEFAULT_NAMESPACE,
) -> t.Sequence[Module]:
    from psycopg.rows import class_row

    query = queries.preformat(query=queries.MISSING_MIGRATIONS, namespace=namespace)

    modules = fs.find_migrations(package=package)

    params = dict(package=package, files=[module.name for module in modules])

    async with connection.cursor(row_factory=class_row(Module)) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return await cursor.fetchall()
