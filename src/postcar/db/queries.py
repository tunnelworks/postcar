import typing as t


if t.TYPE_CHECKING:
    from psycopg.sql import Composed

    TableName = t.Literal[
        "_version",
        "_migration",
    ]


class RevertibleQuery(t.NamedTuple):
    forward: str
    rollback: str


def preformat(query: str, namespace: str) -> "Composed":
    from psycopg import sql

    return sql.SQL(query).format(namespace=sql.Identifier(namespace))


# MARK: internal

CREATE_NAMESPACE: t.Final[str] = """--sql
  create schema {namespace};
"""

CREATE_VERSIONING: t.Final[str] = """--sql
  create table {namespace}."_version" (
    "major" integer not null,
    "minor" integer not null,
    "created_at" timestamptz not null default current_timestamp
  );

  create unique index "_distinct_schema_version"
    on {namespace}."_version" ("major", "minor");
"""


# MARK: bookkeeping


UPDATE_BOOKKEEPING: t.Final[RevertibleQuery] = RevertibleQuery(
    forward="""--sql
      insert into {namespace}."_migration" ("package", "name")
        values (%(package)s, %(name)s);
    """,
    rollback="""--sql
      update {namespace}."_migration"
        set "reverted_at" = current_timestamp
        where "package" = %(package)s
          and "name" = %(name)s
          and "reverted_at" is null;
    """,
)

UPDATE_VERSION: t.Final[str] = """--sql
  insert into {namespace}."_version" ("major", "minor")
    values (%(major)s, %(minor)s);
"""


# MARK: lookup queries

NAMESPACE_EXISTS: t.Final[str] = """--sql
  select count(*) from "pg_namespace" where "nspname" = %(namespace)s;
"""

TABLE_EXISTS: t.Final[str] = """--sql
  select count(*) from "pg_tables"
    where "schemaname" = %(namespace)s
      and "tablename" = %(table)s;
"""

MISSING_MIGRATIONS: t.Final[str] = """--sql
  with "_f" as (select unnest(%(files)s::text[]) as "name")
  select
    %(package)s as "package",
    "_f"."name"
  from "_f"
  left join {namespace}."_migration" as "_m"
    on "_m"."package" = %(package)s
      and "_m"."name" = "_f"."name"
      and "_m"."reverted_at" is null
  where "_m"."name" is null;
"""


# MARK: transactions

LOCK: t.Final[str] = """--sql
  lock table {namespace}."_version" in access exclusive mode nowait;
"""
