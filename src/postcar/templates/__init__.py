import ast
import typing as t
from postcar.templates.migration import MIGRATION_AST


if t.TYPE_CHECKING:
    Template = t.Literal["migration",]


_TEMPLATES: t.Final[t.Mapping["Template", ast.AST]] = {
    "migration": MIGRATION_AST,
}


def render(template: "Template") -> str:
    return ast.unparse(_TEMPLATES[template])


__all__ = ("render",)
