import contextlib
import typing as t


if t.TYPE_CHECKING:
    from postcar._types import Connection


@contextlib.asynccontextmanager
async def connect(conninfo: str) -> t.AsyncIterator["Connection"]:
    from psycopg import AsyncConnection

    async with await AsyncConnection.connect(conninfo=conninfo) as connection:
        yield connection
