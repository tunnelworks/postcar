import typing as t
from postcar._types import InternalMigration, Version


MIGRATIONS: t.Final[t.Sequence[InternalMigration]] = [
    InternalMigration(
        version=Version(major=0, minor=0),
        query="""--sql
          create table {namespace}."_migration" (
            "pk" integer generated always as identity primary key,
            "package" text not null,
            "name" text not null,
            "created_at" timestamptz not null default current_timestamp,
            "reverted_at" timestamptz
          );

          create unique index "_distinct_migration_name"
            on {namespace}."_migration" ("package", "name")
              where "reverted_at" is null;
        """,
    ),
]


def get_migrations(version: t.Optional[Version]) -> t.Iterable[InternalMigration]:
    if version is None:
        return MIGRATIONS

    def predicate(migration: InternalMigration) -> t.TypeGuard[InternalMigration]:
        return version < migration.version

    return filter(predicate, MIGRATIONS)
