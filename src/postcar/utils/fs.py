import importlib
import pathlib
import typing as t
from postcar._types import Module
from postcar.db.migrations.classes import Migration
from postcar.errors import MigrationError
from postcar.utils.names import MIGRATION_PATTERN


def get_path(package: str) -> pathlib.Path:
    _module = importlib.import_module(name=package)

    # NOTE: since we already successfully imported the module,
    # this condition should never be true.
    if (path := _module.__file__) is None:
        raise FileNotFoundError(f"package {package} not found")

    return pathlib.Path(path).parent


def _find_migrations(package: str) -> t.Iterable[Module]:
    root = get_path(package=package)

    def is_file(path: pathlib.Path) -> t.TypeGuard[pathlib.Path]:
        return path.is_file()

    def to_stem(path: pathlib.Path) -> str:
        return path.stem

    def predicate(stem: str) -> t.TypeGuard[str]:
        return MIGRATION_PATTERN.match(stem) is not None

    names = filter(predicate, map(to_stem, filter(is_file, root.iterdir())))

    def to_module(name: str) -> Module:
        return Module(name=name, package=package)

    return map(to_module, names)


def find_migrations(package: str) -> t.Sequence[Module]:
    return sorted(_find_migrations(package=package))


def find_latest_migration(package: str) -> t.Optional[Module]:
    try:
        return max(_find_migrations(package=package))
    except ValueError:
        return None


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
