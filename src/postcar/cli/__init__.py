import asyncio
import typing as t
from postcar.__about__ import __version__
from postcar.cli import migrate
from postcar.cli._parser import parser, subparsers


if t.TYPE_CHECKING:
    from postcar.cli._types import Handler


migrate.add_parser(subparsers=subparsers)


handlers: t.Final[t.Mapping[str, "Handler"]] = dict(
    migrate=migrate.handler,
)


def main() -> t.Optional[int]:
    args = parser.parse_args()

    if args.version:
        return print(__version__)

    if args.command is None:
        parser.print_help()
        return 1

    if (handler := handlers.get(args.command)) is None:
        print(f"handler for '{args.command}' not found")
        return 2

    return asyncio.run(handler(args=args))


__all__ = (
    "main",
    "parser",
    "handlers",
)
