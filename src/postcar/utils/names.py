import re
import typing as t


MIGRATION_REGEX: t.Final[str] = r"^[0-9]{4}_\w+$"
MIGRATION_PATTERN: t.Final[re.Pattern[str]] = re.compile(MIGRATION_REGEX)
