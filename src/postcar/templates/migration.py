import ast
import typing as t


MIGRATION_AST: t.Final[ast.AST] = ast.Module(
    body=[
        ast.Import(names=[ast.alias(name="postcar")]),
        ast.ClassDef(
            name="Migration",
            bases=[
                ast.Attribute(
                    value=ast.Name(id="postcar", ctx=ast.Load()),
                    attr="Migration",
                    ctx=ast.Load(),
                )
            ],
            keywords=[],
            body=[
                ast.AsyncFunctionDef(
                    name="migrate",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg="self")],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[ast.Pass()],
                    decorator_list=[],
                    returns=ast.Constant(value=None),
                    type_params=[],
                    lineno=0,
                ),
                ast.AsyncFunctionDef(
                    name="rollback",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg="self")],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[ast.Pass()],
                    decorator_list=[],
                    returns=ast.Constant(value=None),
                    type_params=[],
                    lineno=0,
                ),
            ],
            decorator_list=[],
            type_params=[],
        ),
    ],
    type_ignores=[],
)
