import typing as t
from postcar.config.database import ConnectionInfo
from postcar.config.defaults import DEFAULT_NAMESPACE


class Config(t.NamedTuple):
    connection: ConnectionInfo
    namespace: str = DEFAULT_NAMESPACE
    packages: t.Sequence[str] = tuple()
