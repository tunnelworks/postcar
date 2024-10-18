from postcar._types import Module
from postcar.utils import fs


def test_find_migrations(package: str, migration_name: str) -> None:
    result = fs.find_migrations(package=package)

    assert Module(name=migration_name, package=package) in result
    assert Module(name="__init__", package=package) not in result
