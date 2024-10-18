import typing as t
from postcar.utils import fs
from postcar._types import Module
from postcar.db import queries


if t.TYPE_CHECKING:
    from postcar._types import Connection


async def namespace_exists(connection: "Connection", namespace: str) -> bool:
    from psycopg.rows import scalar_row

    query = queries.NAMESPACE_EXISTS

    params = dict(namespace=namespace)

    async with connection.cursor(row_factory=scalar_row) as cursor:
        await cursor.execute(query=query, params=params, prepare=True)
        return bool(await cursor.fetchone())


async def find_missing_migrations(
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
