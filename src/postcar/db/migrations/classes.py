import typing as t
from postcar.errors import MigrationError


if t.TYPE_CHECKING:
    from psycopg.abc import Query
    from postcar._types import Connection, Module


class Migration:
    @t.final
    def __init__(self, module: "Module", connection: "Connection") -> None:
        self.module = module
        self.connection = connection

    @t.final
    async def run(self, rollback: bool = False) -> None:
        coro = self.rollback if rollback else self.migrate

        try:
            return await coro()
        except NotImplementedError:
            pass

        getter = self.get_rollback if rollback else self.get_forward

        if (query := getter()) is None:
            raise MigrationError(f"{self.module}: nothing to do")

        await self.connection.execute(query=query)

    async def migrate(self) -> None:
        raise NotImplementedError()

    async def rollback(self) -> None:
        raise NotImplementedError()

    def get_forward(self) -> t.Optional["Query"]:
        return None

    def get_rollback(self) -> t.Optional["Query"]:
        return None
