import typing as t
from postcar.cli import migrate
from postcar.cli._parser import parser, subparsers


if t.TYPE_CHECKING:
    from postcar.cli._types import Handler


migrate.add_parser(subparsers=subparsers)


handlers: t.Final[t.Mapping[str, "Handler"]] = dict(
    migrate=migrate.handler,
)


__all__ = (
    "parser",
    "handlers",
)
