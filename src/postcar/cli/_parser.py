import argparse
import pathlib
import typing as t
from postcar.config import defaults


if t.TYPE_CHECKING:
    from postcar.cli._types import Subparsers


parser: t.Final[argparse.ArgumentParser] = argparse.ArgumentParser(prog="postcar")
parser.add_argument(
    "--version",
    action="store_true",
    help="show the version and exit",
)
parser.add_argument(
    "-c",
    "--conf",
    type=pathlib.Path,
    metavar="CONFIG_FILE",
)
parser.add_argument(
    "-H",
    "--host",
    type=str,
)
parser.add_argument(
    "-p",
    "--port",
    type=int,
)
parser.add_argument(
    "-U",
    "--user",
    type=str,
)
parser.add_argument(
    "-P",
    "--password",
    type=str,
)
parser.add_argument(
    "-d",
    "--dbname",
    type=str,
)
parser.add_argument(
    "-s",
    "--namespace",
    type=str,
    default=defaults.DEFAULT_NAMESPACE,
)


subparsers: t.Final["Subparsers"] = parser.add_subparsers(dest="command")
