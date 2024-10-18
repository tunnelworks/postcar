import typing as t


if t.TYPE_CHECKING:
    from psycopg.sql import Composed


class RevertibleQuery(t.NamedTuple):
    forward: str
    rollback: str


def preformat(query: str, namespace: str) -> "Composed":
    from psycopg import sql

    return sql.SQL(query).format(namespace=sql.Identifier(namespace))


# MARK: bookkeeping

BOOKKEEPING_INIT: t.Final[str] = """--sql
  create schema {namespace};

  create table {namespace}."_migration" (
    "pk" integer generated always as identity primary key,
    "package" text not null,
    "name" text not null,
    "created_at" timestamptz not null default CURRENT_TIMESTAMP,
    "reverted_at" timestamptz
  );

  create unique index "_distinct_migration_name"
    on {namespace}."_migration" ("package", "name")
      where "reverted_at" is null;
"""

# TODO: add package to queries
BOOKKEEPING_UPDATE: t.Final[RevertibleQuery] = RevertibleQuery(
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


# MARK: lookup queries

NAMESPACE_EXISTS: t.Final[str] = """--sql
  select count(*) from "pg_namespace" where "nspname" = %(namespace)s;
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
  lock table {namespace}."_migration" in access exclusive mode nowait;
"""
