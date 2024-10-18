import importlib
import pathlib
import typing as t
from postcar._types import Module
from postcar.utils.names import MIGRATION_PATTERN


if t.TYPE_CHECKING:
    from postcar._types import _Migration


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


def load_migration(module: Module) -> "_Migration":
    _module = importlib.import_module(name=f".{module.name}", package=module.package)

    if not (hasattr(_module, "forward") and hasattr(_module, "revert")):
        raise AttributeError(f"{module}: both forward and revert must exist")

    return t.cast("_Migration", _module)