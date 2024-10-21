import typing as t


class ConnectionInfo(t.NamedTuple):
    host: t.Optional[str] = None
    hostaddr: t.Optional[str] = None
    port: t.Optional[int] = None
    dbname: t.Optional[str] = None
    username: t.Optional[str] = None
    password: t.Optional[str] = None

    @property
    def conninfo(self) -> str:
        from psycopg.conninfo import make_conninfo

        return make_conninfo(
            host=self.host,
            hostaddr=self.hostaddr,
            port=self.port,
            dbname=self.dbname,
            user=self.username,
            password=self.password,
        )
