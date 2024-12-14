import contextlib
import importlib
import pathlib
import sys
import typing as t
from postcar._types import Module
from postcar.db.migrations.classes import Migration
from postcar.errors import MigrationError
from postcar.utils.names import MIGRATION_PATTERN


if t.TYPE_CHECKING:
    P = t.ParamSpec("P")
    R = t.TypeVar("R")

    F = t.Callable[P, t.Coroutine[object, object, R]]


@contextlib.contextmanager
def _sys_path(path: str) -> t.Generator[None, None, None]:
    if path in sys.path:
        yield
        return

    sys.path.insert(0, path)

    yield

    try:
        sys.path.remove(path)
    except ValueError:
        pass


def add_path(f: "F[P, R]", *, path: str) -> "F[P, R]":
    async def inner(*args: "P.args", **kwargs: "P.kwargs") -> "R":
        with _sys_path(path=path):
            return await f(*args, **kwargs)

    return inner


def find_migrations(package: str) -> t.Sequence[Module]:
    _module = importlib.import_module(name=package)

    # NOTE: since we already successfully imported the module,
    # this condition should never be true.
    if (path := _module.__file__) is None:
        raise FileNotFoundError(f"package {package} not found")

    root = pathlib.Path(path).parent

    def is_file(path: pathlib.Path) -> t.TypeGuard[pathlib.Path]:
        return path.is_file()

    def to_stem(path: pathlib.Path) -> str:
        return path.stem

    def predicate(stem: str) -> t.TypeGuard[str]:
        return MIGRATION_PATTERN.match(stem) is not None

    names = filter(predicate, map(to_stem, filter(is_file, root.iterdir())))

    def to_module(name: str) -> Module:
        return Module(name=name, package=package)

    return sorted(map(to_module, names))


def load_migration(module: Module) -> t.Type[Migration]:
    _module = importlib.import_module(name=f".{module.name}", package=module.package)

    try:
        cls = getattr(_module, "Migration")
    except AttributeError:
        raise MigrationError(f"{module}: no migration class found")

    if not isinstance(cls, type):
        raise MigrationError(f"{module}: migration is not a class")

    if not issubclass(cls, Migration):
        raise MigrationError(f"{module}: migration must inherit from `Migration`")

    return cls
