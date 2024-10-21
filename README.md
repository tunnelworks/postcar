# postcar

[![PyPI - Version](https://img.shields.io/pypi/v/postcar.svg)](https://pypi.org/project/postcar)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/postcar.svg)](https://pypi.org/project/postcar)

---

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install postcar
```

## License

`postcar` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

## Usage

### Migrations

#### Migration packages

Each migration package needs to be importable.
Migration modules must be named starting with a four digit sequence number,
followed by an underscore, and a (short) description.

Here's a sample structure of a migration directory:

```
migrations
├── __init__.py
├── 0001_init.py
├── 0002_authorization.py
└── 0003_create_extensions.py
```

#### Migration modules

The migration modules must contain a class named `Migration`,
which must inherit from `postcar.Migration`.

A minimal migration file might look as follows:

```python
import postcar


class Migration(postcar.Migration):
    def get_forward(self) -> str:
        return """
            create extension pg_trgm;
        """

    def get_rollback(self) -> str:
        return """
            drop extension pg_trgm;
        """
```

### CLI

The package comes with a minimal CLI.

See `postcar --help` for available commands.

### Configuration

> NOTE: this isn't implemented yet, so use the CLI for the time being

Sample configuration file:

```python
# postcar.conf.py

import os
from postcar import config


connection = config.ConnectionInfo(
    host="127.0.0.1",
    port=5432,
    dbname="mydb",
    username="postcar",
    password=os.getenv("POSTGRES_PASSWORD"),
)

namespace = "_bookkeeping"

packages = ["myapp.migrations"]
```

### Configuration parameters

The below table is an exhaustive list of the available parameters.
More detailed descriptions below the table.

| Name                  | CLI                | Type            | Default      |
| --------------------- | ------------------ | --------------- | ------------ |
| —                     | `-c`/`--conf`      | `Optional[str]` | `None`       |
| `connection.host`     | `-H`/`--host`      | `Optional[str]` | `None`       |
| `connection.port`     | `-p`/`--port`      | `Optional[int]` | `None`       |
| `connection.dbname`   | `-D`/`--dbname`    | `Optional[str]` | `None`       |
| `connection.username` | `-U`/`--user`      | `Optional[str]` | `None`       |
| `connection.password` | `-P`/`--password`  | `Optional[str]` | `None`       |
| `namespace`           | `-s`/`--namespace` | `str`           | `"_postcar"` |
| `packages`            | —                  | `Sequence[str]` | `()`         |

#### `connection.[x]`

Connection info parameters, very similar to the Postgres defaults.

#### `namespace`

The database schema to use for bookkeeping.

#### `packages`

The migration packages to run migrations for by default.

## Development

### Internal migrations

For the sake of consistency, and keeping things "simple",
internal schema migrations are designated by minor versions.
In short, a bump from `1.2.3` to `1.2.4` must never migrate the internal schema,
whereas `1.2.3` to `1.3.0` or `2.0.0` may.

Ultimately, the goal is to enable effortless upgrades between versions,
without unnecessarily complicated manual intervention.

Regardless: this is a rather experimental package, at least until version 1.0.0.
Until then: expect things to break, without any guarantees.

## TODO

- [ ] Implement rollback
- [ ] Migration dependencies
- [ ] CLI command for generating a new migration skeleton
