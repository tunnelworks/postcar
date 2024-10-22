import argparse
import typing as t


if t.TYPE_CHECKING:
    from postcar.cli._types import Subparsers


NAME: t.Final[str] = "make"


def add_parser(subparsers: "Subparsers") -> None:
    parser = subparsers.add_parser(name=NAME)

    parser.add_argument(
        "-n",
        "--name",
        type=str,
    )

    parser.add_argument(
        nargs=1,
        metavar="PACKAGE",
        dest="packages",
    )


def _get_last_sequence(package: str) -> int:
    from postcar._types import MigrationName
    from postcar.utils import fs

    if latest := fs.find_latest_migration(package=package):
        return MigrationName.fromstring(name=latest.name).sequence

    return 0


def _format_version(sequence: int) -> str:
    return f"{sequence:04d}"


async def handler(args: argparse.Namespace) -> None:
    from postcar.templates import render
    from postcar.utils import fs

    # TODO: fix
    package = t.cast(str, args.packages[0])

    _sequence = _get_last_sequence(package=package) + 1
    _version = _format_version(sequence=_sequence)

    _name = args.name or "auto"
    name = f"{_version}_{_name}"

    path = fs.get_path(package=package).joinpath(name).with_suffix(".py")

    with path.open("w") as handle:
        handle.write(render("migration"))

    print(f"generated empty migration at '{path}'")
