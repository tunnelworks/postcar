import os
import typing as t


_DEFAULT_HOST: t.Final[str] = "127.0.0.1"
_DEFAULT_PORT: t.Final[int] = 5432
_DEFAULT_DBNAME: t.Final[str] = "postgres"
_DEFAULT_USERNAME: t.Final[str] = "postgres"
_DEFAULT_NAMESPACE: t.Final[str] = "_postcar"


class Config(t.NamedTuple):
    package: str
    host: str = _DEFAULT_HOST
    port: int = _DEFAULT_PORT
    dbname: str = _DEFAULT_DBNAME
    username: str = _DEFAULT_USERNAME
    password: t.Optional[str] = None
    namespace: str = _DEFAULT_NAMESPACE

    @property
    def conninfo(self) -> str:
        from psycopg.conninfo import make_conninfo

        return make_conninfo(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.username,
            password=self.password,
        )

    @classmethod
    def fromenv(cls) -> "Config":
        if (package := os.getenv("POSTCAR_PACKAGE")) is None:
            raise EnvironmentError("variable POSTCAR_PACKAGE not set")

        return Config(
            package=package,
            host=os.getenv("POSTGRES_HOST", _DEFAULT_HOST),
            port=int(os.getenv("POSTGRES_PORT", _DEFAULT_PORT)),
            dbname=os.getenv("POSTGRES_DB", _DEFAULT_DBNAME),
            username=os.getenv("POSTGRES_USERNAME", _DEFAULT_USERNAME),
            password=os.getenv("POSTGRES_PASSWORD"),
            namespace=os.getenv("POSTCAR_NAMESPACE", _DEFAULT_NAMESPACE),
        )
