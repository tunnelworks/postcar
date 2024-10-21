import argparse
import typing as t


if t.TYPE_CHECKING:
    from postcar.cli._types import Subparsers


NAME: t.Final[str] = "migrate"


def add_parser(subparsers: "Subparsers") -> None:
    parser = subparsers.add_parser(name=NAME)
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    parser.add_argument(
        "packages",
        nargs="*",
    )


async def handler(args: argparse.Namespace) -> None:
    from postcar.cli._config import get_config
    from postcar.db import connections, migrations

    config = get_config(args=args)

    conninfo = config.connection.conninfo

    async with connections.connect(conninfo=conninfo) as connection:
        for package in config.packages:
            await migrations.run(
                connection=connection,
                package=package,
                namespace=config.namespace,
                dry_run=args.dry_run,
            )
