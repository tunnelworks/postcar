import typing as t


if t.TYPE_CHECKING:
    import psycopg
    from psycopg.rows import TupleRow

    Connection = psycopg.AsyncConnection[TupleRow]


class Module(t.NamedTuple):
    name: str
    package: t.Optional[str] = None

    def __str__(self) -> str:
        if self.package is None:
            return self.name
        return f"{self.package}:{self.name}"
