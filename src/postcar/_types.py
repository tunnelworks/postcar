import typing as t


if t.TYPE_CHECKING:
    import psycopg
    from psycopg.rows import TupleRow
    from typing_extensions import Self

    Connection = psycopg.AsyncConnection[TupleRow]


class Module(t.NamedTuple):
    name: str
    package: t.Optional[str] = None

    def __str__(self) -> str:
        if self.package is None:
            return self.name
        return f"{self.package}:{self.name}"


class Version(t.NamedTuple):
    major: int
    minor: int

    def __str__(self) -> str:
        return ".".join(map(str, self))

    @classmethod
    def fromstring(cls, version: str) -> "Self":
        major, minor, *_ = version.split(".")
        return cls(major=int(major), minor=int(minor))


class InternalMigration(t.NamedTuple):
    version: Version
    query: str
