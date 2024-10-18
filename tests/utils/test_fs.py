import pytest
import postcar
from postcar._types import Module
from postcar.errors import MigrationError
from postcar.utils import fs


def test_find_migrations(package: str, migration_name: str) -> None:
    result = fs.find_migrations(package=package)

    assert Module(name=migration_name, package=package) in result
    assert Module(name="__init__", package=package) not in result


def test_load_migration(package: str, migration_name: str) -> None:
    module = Module(name=migration_name, package=package)
    migration = fs.load_migration(module=module)

    assert isinstance(migration, type)
    assert issubclass(migration, postcar.Migration)


def test_load_migration_no_revert(invalid_package: str, migration_name: str) -> None:
    module = Module(name=migration_name, package=invalid_package)

    with pytest.raises(MigrationError):
        fs.load_migration(module=module)
